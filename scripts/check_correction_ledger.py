#!/usr/bin/env python3
"""Validate evidence-backed correction events and their derived tally."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "data" / "correction-events" / "correction-ledger.v0.1.json"
EVENT_TYPES = {"supported_finding", "verified_correction", "surfaced_assumption"}
DISPOSITIONS = {
    "supported_finding": {"supported"},
    "verified_correction": {"revised", "withdrawn"},
    "surfaced_assumption": {"made_explicit", "awaiting_evidence"},
}
REQUIRED_GUARDRAILS = {
    "no_synthetic_events",
    "evidence_required",
    "no_status_or_reward_effect",
    "uncertainty_is_not_error",
    "disagreement_alone_is_not_correction",
}


def derive_tally(events: list[dict[str, Any]]) -> dict[str, int]:
    counts = {event_type: 0 for event_type in EVENT_TYPES}
    supported_since_last_correction = 0
    for event in events:
        event_type = event.get("type")
        if event_type in counts:
            counts[event_type] += 1
        if event_type == "verified_correction":
            supported_since_last_correction = 0
        elif event_type == "supported_finding":
            supported_since_last_correction += 1
    return {
        "supported_findings": counts["supported_finding"],
        "verified_corrections": counts["verified_correction"],
        "surfaced_assumptions": counts["surfaced_assumption"],
        "supported_since_last_correction": supported_since_last_correction,
        "correction_opportunity_index": supported_since_last_correction + 1,
    }


def validate(ledger: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    events = ledger.get("events")
    if not isinstance(events, list):
        return ["events must be a list"]

    seen: set[str] = set()
    for index, event in enumerate(events):
        label = event.get("id") or f"event[{index}]"
        if label in seen:
            errors.append(f"{label}: duplicate id")
        seen.add(label)

        event_type = event.get("type")
        if event_type not in EVENT_TYPES:
            errors.append(f"{label}: unsupported type {event_type!r}")
            continue
        for field in ("id", "occurred_at", "claim", "evidence", "disposition"):
            if not event.get(field):
                errors.append(f"{label}: {field} is required")
        if event.get("disposition") not in DISPOSITIONS[event_type]:
            errors.append(
                f"{label}: disposition {event.get('disposition')!r} is invalid for {event_type}"
            )

    guardrails = ledger.get("guardrails")
    if not isinstance(guardrails, list):
        errors.append("guardrails must be a list")
    else:
        missing = REQUIRED_GUARDRAILS - set(guardrails)
        if missing:
            errors.append(f"missing guardrails: {', '.join(sorted(missing))}")

    expected_tally = derive_tally(events)
    if ledger.get("tally") != expected_tally:
        errors.append(f"tally must equal derived value {expected_tally}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", nargs="?", type=Path, default=DEFAULT_LEDGER)
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    errors = validate(ledger)
    if errors:
        for error in errors:
            print(f"[correction-ledger-check] ERROR: {error}")
        return 1
    print(f"[correction-ledger-check] passed: {args.ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
