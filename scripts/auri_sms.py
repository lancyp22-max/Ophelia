#!/usr/bin/env python3
"""Send a bounded, explicitly enabled SMS prompt through Twilio.

The destination and provider credentials are deployment secrets. This tool is
local-only by design; it is not exposed through the unauthenticated web API.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable, Iterator

try:  # POSIX locking
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover - Windows path
    fcntl = None

try:  # Windows locking
    import msvcrt  # type: ignore
except ImportError:  # pragma: no cover - POSIX path
    msvcrt = None


E164 = re.compile(r"^\+[1-9][0-9]{7,14}$")
CONSENT_VERSION = "outbound_prompts_v1"
MAX_BODY_CHARS = 480
DEFAULT_DAILY_LIMIT = 8
DEFAULT_COOLDOWN_SECONDS = 900
Transport = Callable[[urllib.request.Request, float], tuple[int, bytes]]


class SmsBoundaryError(RuntimeError):
    """A request failed before or during the provider boundary."""


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def default_state_path() -> Path:
    return Path.home() / ".local" / "state" / "ophelia" / "auri-sms.json"


def required_env(name: str, env: dict[str, str]) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise SmsBoundaryError(f"missing required server-side setting: {name}")
    return value


def validate_configuration(env: dict[str, str], sending: bool) -> dict[str, str]:
    if env.get("AURI_SMS_ENABLED", "").lower() != "true":
        raise SmsBoundaryError("SMS is disabled; set AURI_SMS_ENABLED=true explicitly")
    if env.get("AURI_SMS_CONSENT", "") != CONSENT_VERSION:
        raise SmsBoundaryError(f"current consent marker must equal {CONSENT_VERSION}")

    target = required_env("AURI_SMS_TO", env)
    sender = required_env("TWILIO_FROM_NUMBER", env)
    if not E164.fullmatch(target) or not E164.fullmatch(sender):
        raise SmsBoundaryError("sender and destination must use E.164 format")

    config = {"target": target, "sender": sender}
    if sending:
        config["account_sid"] = required_env("TWILIO_ACCOUNT_SID", env)
        config["auth_token"] = required_env("TWILIO_AUTH_TOKEN", env)
    return config


def validate_body(body: str) -> str:
    normalized = " ".join(body.split())
    if not normalized:
        raise SmsBoundaryError("message body must not be empty")
    if len(normalized) > MAX_BODY_CHARS:
        raise SmsBoundaryError(f"message body exceeds {MAX_BODY_CHARS} characters")
    return normalized


def read_state(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"events": []}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SmsBoundaryError("SMS rate-limit state is unreadable; refusing to send") from error
    if not isinstance(state.get("events"), list):
        raise SmsBoundaryError("SMS rate-limit state is invalid; refusing to send")
    try:
        for item in state["events"]:
            dt.datetime.fromisoformat(str(item))
    except (TypeError, ValueError) as error:
        raise SmsBoundaryError("SMS rate-limit timestamps are invalid; refusing to send") from error
    return state


def enforce_limits(state: dict[str, object], now: dt.datetime, daily_limit: int, cooldown: int) -> None:
    events = [dt.datetime.fromisoformat(str(item)) for item in state["events"]]
    recent = [event for event in events if now - event < dt.timedelta(days=1)]
    if len(recent) >= daily_limit:
        raise SmsBoundaryError("daily SMS limit reached")
    if recent and (now - max(recent)).total_seconds() < cooldown:
        raise SmsBoundaryError("SMS cooldown is still active")


def write_state(path: Path, state: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(state, handle, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    try:
        temporary.chmod(0o600)
    except OSError:
        pass
    temporary.replace(path)


@contextlib.contextmanager
def exclusive_lock(path: Path) -> Iterator[None]:
    """Cross-platform single-byte advisory lock with no external dependency."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("a+b") as lock:
        if os.name == "nt":
            if msvcrt is None:
                raise SmsBoundaryError("Windows file locking is unavailable; refusing to send")
            lock.seek(0, os.SEEK_END)
            if lock.tell() == 0:
                lock.write(b"\0")
                lock.flush()
            lock.seek(0)
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
                yield
            finally:
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            if fcntl is None:
                raise SmsBoundaryError("POSIX file locking is unavailable; refusing to send")
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def default_transport(request: urllib.request.Request, timeout: float) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def send_twilio(config: dict[str, str], body: str, transport: Transport = default_transport) -> str:
    account_sid = config["account_sid"]
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    payload = urllib.parse.urlencode({"To": config["target"], "From": config["sender"], "Body": body}).encode()
    auth = base64.b64encode(f"{account_sid}:{config['auth_token']}".encode()).decode()
    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    status, response_body = transport(request, 10.0)
    if status < 200 or status >= 300:
        raise SmsBoundaryError(f"SMS provider rejected the request with HTTP {status}")
    try:
        message_sid = json.loads(response_body).get("sid")
    except json.JSONDecodeError as error:
        raise SmsBoundaryError("SMS provider returned an invalid response") from error
    if not message_sid:
        raise SmsBoundaryError("SMS provider response did not include a message SID")
    return str(message_sid)


def execute(args: argparse.Namespace, env: dict[str, str], transport: Transport = default_transport) -> dict[str, object]:
    if not 1 <= args.daily_limit <= DEFAULT_DAILY_LIMIT:
        raise SmsBoundaryError(f"daily limit must be between 1 and {DEFAULT_DAILY_LIMIT}")
    if args.cooldown_seconds < DEFAULT_COOLDOWN_SECONDS:
        raise SmsBoundaryError(f"cooldown must be at least {DEFAULT_COOLDOWN_SECONDS} seconds")

    config = validate_configuration(env, args.send)
    body = validate_body(args.message)
    target_fingerprint = hashlib.sha256(config["target"].encode()).hexdigest()[:12]
    if not args.send:
        return {"status": "dry_run", "characters": len(body), "target_fingerprint": target_fingerprint}

    state_path = Path(args.state_file).expanduser()
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    with exclusive_lock(lock_path):
        state = read_state(state_path)
        now = utc_now()
        enforce_limits(state, now, args.daily_limit, args.cooldown_seconds)

        # Reserve the attempt before crossing the provider boundary. If the
        # process crashes after Twilio accepts the request, the cooldown still
        # prevents an accidental immediate duplicate.
        recent = [
            item
            for item in state["events"]
            if now - dt.datetime.fromisoformat(str(item)) < dt.timedelta(days=1)
        ]
        recent.append(now.isoformat())
        write_state(state_path, {"events": recent})
        message_sid = send_twilio(config, body, transport)

    return {"status": "sent", "provider_message_id": message_sid, "target_fingerprint": target_fingerprint}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Send an opt-in Auri SMS prompt; defaults to dry-run")
    result.add_argument("message", help=f"prompt text, maximum {MAX_BODY_CHARS} characters")
    result.add_argument("--send", action="store_true", help="perform the provider call")
    result.add_argument("--state-file", default=str(default_state_path()))
    result.add_argument("--daily-limit", type=int, default=DEFAULT_DAILY_LIMIT)
    result.add_argument("--cooldown-seconds", type=int, default=DEFAULT_COOLDOWN_SECONDS)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        result = execute(args, dict(os.environ))
    except SmsBoundaryError as error:
        print(f"[auri-sms] ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
