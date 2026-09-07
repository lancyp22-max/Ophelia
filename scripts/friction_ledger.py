#!/usr/bin/env python3
"""Validate, append to, and summarize the append-only Lumaria friction ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "data" / "friction" / "sample-friction-ledger.v1.jsonl"
SCHEMA = ROOT / "data" / "friction" / "friction-event.v1.schema.json"
OUTCOMES = {"resolved", "partial", "timeout", "constraint_hit", "degraded", "unknown"}
EVIDENCE = {"none", "weak", "moderate", "strong"}
CONSTRAINTS = {"none", "capability", "authorization", "policy", "resource", "dependency", "environment", "unknown"}
UNCERTAINTY = {"low", "medium", "high", "unknown"}
CHANGED = {"yes", "no", "unknown"}
SOURCES = {"runtime_observation", "operator_report", "test_result", "imported_record"}
FINGERPRINT = re.compile(r"^sha256:[a-f0-9]{64}$")
FRICTION = {"resolved": 0.0, "partial": 0.45, "degraded": 0.6, "timeout": 0.85, "constraint_hit": 1.0}
EVIDENCE_WEIGHT = {"none": 0.0, "weak": 0.3, "moderate": 0.65, "strong": 1.0}


def aware_timestamp(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.utcoffset() is not None else None
    except ValueError:
        return None


def validate_event(event: Any, line: int) -> list[str]:
    prefix = f"line {line}"
    if not isinstance(event, dict):
        return [f"{prefix}: event must be an object"]
    required = {
        "schema_version", "event_id", "route_id", "task_family", "context_fingerprint",
        "attempt_n", "outcome", "evidence_quality", "constraint_class", "uncertainty",
        "changed_since_last_attempt", "timestamp", "provenance"
    }
    allowed = required | {"notes"}
    errors = []
    missing = required - event.keys()
    extra = event.keys() - allowed
    if missing:
        errors.append(f"{prefix}: missing {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"{prefix}: unsupported {', '.join(sorted(extra))}")
    if event.get("schema_version") != "1.0":
        errors.append(f"{prefix}: schema_version must be 1.0")
    if not re.fullmatch(r"fr_[a-z0-9][a-z0-9._-]{2,63}", str(event.get("event_id", ""))):
        errors.append(f"{prefix}: invalid event_id")
    for field in ("route_id", "task_family"):
        if not isinstance(event.get(field), str) or not event[field] or len(event[field]) > 128:
            errors.append(f"{prefix}: invalid {field}")
    if not FINGERPRINT.fullmatch(str(event.get("context_fingerprint", ""))):
        errors.append(f"{prefix}: context_fingerprint must be sha256:<64 lowercase hex>")
    if not isinstance(event.get("attempt_n"), int) or event.get("attempt_n", 0) < 1:
        errors.append(f"{prefix}: attempt_n must be a positive integer")
    for field, vocabulary in (("outcome", OUTCOMES), ("evidence_quality", EVIDENCE),
                              ("constraint_class", CONSTRAINTS), ("uncertainty", UNCERTAINTY),
                              ("changed_since_last_attempt", CHANGED)):
        if event.get(field) not in vocabulary:
            errors.append(f"{prefix}: unsupported {field}")
    if aware_timestamp(event.get("timestamp")) is None:
        errors.append(f"{prefix}: timestamp must include a timezone")
    provenance = event.get("provenance")
    if not isinstance(provenance, dict) or set(provenance) != {"source_type", "evidence_refs"}:
        errors.append(f"{prefix}: provenance requires only source_type and evidence_refs")
    else:
        refs = provenance.get("evidence_refs")
        if provenance.get("source_type") not in SOURCES:
            errors.append(f"{prefix}: unsupported provenance source_type")
        if not isinstance(refs, list) or not all(isinstance(ref, str) and ref for ref in refs):
            errors.append(f"{prefix}: evidence_refs must be a string list")
        if event.get("evidence_quality") in {"moderate", "strong"} and not refs:
            errors.append(f"{prefix}: moderate/strong evidence requires evidence_refs")
    if event.get("outcome") == "resolved" and event.get("constraint_class") != "none":
        errors.append(f"{prefix}: resolved outcome must use constraint_class none")
    return errors


def read_ledger(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    events, errors = [], []
    if not path.exists():
        return events, [f"ledger not found: {path}"]
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            errors.append(f"line {line_number}: blank lines are not allowed")
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as error:
            errors.append(f"line {line_number}: invalid JSON: {error.msg}")
            continue
        errors.extend(validate_event(event, line_number))
        if isinstance(event, dict):
            events.append(event)
    ids = [event.get("event_id") for event in events]
    if len(ids) != len(set(ids)):
        errors.append("event_id values must be unique")
    keys: dict[tuple[str, str, str], int] = {}
    for event in events:
        key = (event.get("route_id", ""), event.get("task_family", ""), event.get("context_fingerprint", ""))
        previous = keys.get(key, 0)
        if event.get("attempt_n", 0) <= previous:
            errors.append(f"{event.get('event_id')}: attempt_n must increase within matching context")
        keys[key] = event.get("attempt_n", 0)
    return events, errors


def summarize(events: list[dict[str, Any]], half_life_hours: float) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for event in events:
        grouped.setdefault((event["route_id"], event["task_family"], event["context_fingerprint"]), []).append(event)
    summaries = []
    for key, group in grouped.items():
        group.sort(key=lambda event: aware_timestamp(event["timestamp"]) or datetime.min.replace(tzinfo=timezone.utc))
        latest = aware_timestamp(group[-1]["timestamp"]) or datetime.now(timezone.utc)
        weighted_friction = weighted_evidence = total = evidence_total = 0.0
        for event in group:
            if event["changed_since_last_attempt"] == "yes":
                weighted_friction = weighted_evidence = total = evidence_total = 0.0
            observed = aware_timestamp(event["timestamp"]) or latest
            recency = math.pow(0.5, max(0.0, (latest - observed).total_seconds() / 3600) / half_life_hours)
            evidence = EVIDENCE_WEIGHT[event["evidence_quality"]]
            evidence_total += recency
            weight = recency * max(0.1, evidence)
            if event["outcome"] != "unknown":
                weighted_friction += FRICTION[event["outcome"]] * weight
                weighted_evidence += evidence * recency
                total += weight
        summaries.append({
            "route_id": key[0], "task_family": key[1], "context_fingerprint": key[2],
            "attempts": len(group), "P_rep": round(weighted_friction / total, 4) if total else None,
            "Q_ev": round(weighted_evidence / evidence_total, 4) if evidence_total else None,
            "latest_outcome": group[-1]["outcome"], "latest_change": group[-1]["changed_since_last_attempt"],
            "interpretation": "observational_route_friction_not_authority"
        })
    return summaries


def context_fingerprint(context: str) -> str:
    return "sha256:" + hashlib.sha256(context.encode("utf-8")).hexdigest()


def append_event(path: Path, args: argparse.Namespace) -> None:
    events, errors = read_ledger(path) if path.exists() else ([], [])
    if errors:
        raise ValueError("existing ledger is invalid; refusing append")
    fingerprint = context_fingerprint(args.context)
    matching = [event for event in events if (event["route_id"], event["task_family"], event["context_fingerprint"]) == (args.route, args.task_family, fingerprint)]
    event = {
        "schema_version": "1.0", "event_id": f"fr_{uuid.uuid4().hex}", "route_id": args.route,
        "task_family": args.task_family, "context_fingerprint": fingerprint, "attempt_n": len(matching) + 1,
        "outcome": args.outcome, "evidence_quality": args.evidence_quality,
        "constraint_class": args.constraint_class, "uncertainty": args.uncertainty,
        "changed_since_last_attempt": args.changed, "timestamp": datetime.now(timezone.utc).isoformat(),
        "notes": args.notes, "provenance": {"source_type": args.source_type, "evidence_refs": args.evidence_ref}
    }
    errors = validate_event(event, len(events) + 1)
    if errors:
        raise ValueError("; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as ledger:
        ledger.write(json.dumps(event, separators=(",", ":"), sort_keys=True) + "\n")
        ledger.flush()
        os.fsync(ledger.fileno())
    print(event["event_id"])


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    actions = cli.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--summary", action="store_true")
    actions.add_argument("--append", action="store_true")
    cli.add_argument("--half-life-hours", type=float, default=24.0)
    cli.add_argument("--route")
    cli.add_argument("--task-family")
    cli.add_argument("--context")
    cli.add_argument("--outcome", choices=sorted(OUTCOMES))
    cli.add_argument("--evidence-quality", choices=sorted(EVIDENCE), default="none")
    cli.add_argument("--constraint-class", choices=sorted(CONSTRAINTS), default="unknown")
    cli.add_argument("--uncertainty", choices=sorted(UNCERTAINTY), default="unknown")
    cli.add_argument("--changed", choices=sorted(CHANGED), default="unknown")
    cli.add_argument("--source-type", choices=sorted(SOURCES), default="runtime_observation")
    cli.add_argument("--evidence-ref", action="append", default=[])
    cli.add_argument("--notes", default="")
    return cli


def main() -> int:
    args = parser().parse_args()
    if args.half_life_hours <= 0:
        print("half-life-hours must be positive", file=sys.stderr)
        return 2
    if args.append:
        if not all((args.route, args.task_family, args.context, args.outcome)):
            print("append requires --route, --task-family, --context, and --outcome", file=sys.stderr)
            return 2
        try:
            append_event(args.ledger, args)
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        return 0
    events, errors = read_ledger(args.ledger)
    if args.check and args.ledger.resolve() == DEFAULT_LEDGER.resolve():
        try:
            schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid schema: {error}")
        else:
            if schema.get("additionalProperties") is not False:
                errors.append("schema must reject unsupported fields")
        if events:
            unsafe = json.loads(json.dumps(events[0]))
            unsafe["provenance"]["evidence_refs"] = []
            if not any("requires evidence_refs" in error for error in validate_event(unsafe, 1)):
                errors.append("evidence denial path did not fail closed")
            derived = summarize(events, args.half_life_hours)
            if not derived or derived[0]["P_rep"] != 0.0 or derived[0]["Q_ev"] != 1.0:
                errors.append("material-change reset did not isolate the new evidence regime")
    if errors:
        for error in errors:
            print(f"[friction-ledger] ERROR: {error}", file=sys.stderr)
        return 1
    if args.summary:
        print(json.dumps(summarize(events, args.half_life_hours), indent=2))
    else:
        print(f"[friction-ledger] passed: {args.ledger} ({len(events)} events)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
