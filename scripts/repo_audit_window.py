#!/usr/bin/env python3
"""Report commits inside one explicit half-open UTC audit window."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def git_commits() -> list[dict[str, str]]:
    output = subprocess.check_output(
        ["git", "log", "--all", "--format=%H%x00%cI%x00%s"], cwd=ROOT, text=True
    )
    commits: list[dict[str, str]] = []
    for line in output.splitlines():
        commit, committed_at, subject = line.split("\0", 2)
        commits.append({"commit": commit, "committed_at": committed_at, "subject": subject})
    return commits


def report(end: datetime, hours: int) -> dict[str, Any]:
    if hours < 1 or hours > 24 * 31:
        raise ValueError("hours must be between 1 and 744")
    start = end - timedelta(hours=hours)
    selected = [
        commit for commit in git_commits()
        if start <= parse_utc(commit["committed_at"]) < end
    ]
    return {
        "audit_window_utc": {
            "start_inclusive": iso_utc(start),
            "end_exclusive": iso_utc(end),
            "duration_hours": hours,
        },
        "selection_rule": "start_inclusive <= commit_timestamp < end_exclusive",
        "timestamp_source": "git_committer_iso8601",
        "commit_count": len(selected),
        "commits": selected,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument(
        "--end",
        help="window end as timezone-aware ISO 8601; defaults to the current UTC time",
    )
    parser.add_argument("--check", action="store_true", help="validate deterministic window semantics")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        end = parse_utc(args.end) if args.end else datetime.now(timezone.utc)
        result = report(end, args.hours)
        if args.check:
            window = result["audit_window_utc"]
            start = parse_utc(window["start_inclusive"])
            finish = parse_utc(window["end_exclusive"])
            if finish - start != timedelta(hours=args.hours):
                raise ValueError("derived window duration is inconsistent")
            for commit in result["commits"]:
                timestamp = parse_utc(commit["committed_at"])
                if not start <= timestamp < finish:
                    raise ValueError("commit escaped the canonical half-open interval")
            print("[repo-audit-window] canonical UTC window check passed")
        print(json.dumps(result, indent=2))
    except (ValueError, subprocess.CalledProcessError) as error:
        print(f"[repo-audit-window] ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
