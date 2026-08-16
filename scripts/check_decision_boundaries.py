#!/usr/bin/env python3
"""Validate Lumaria's decision-boundary register and intentional unknowns."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER = ROOT / "data" / "decision-boundaries" / "lumaria-decision-register.v0.1.json"
EXPECTED_STATUS = {
    "invariant": "encoded",
    "safety_boundary": "enforced",
    "known_mechanical_behavior": "implemented",
}
DELIBERATIVE_CLASSES = {"contextual_judgment", "unknown_future"}
ALLOWED_STATUSES = {
    "encoded",
    "enforced",
    "implemented",
    "intentionally_not_decided_yet",
    "blocked_by_missing_safety_boundary",
}


def validate(register: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    decisions = register.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        return ["decisions must be a non-empty list"]

    seen: set[str] = set()
    for index, decision in enumerate(decisions):
        label = decision.get("id") or f"decision[{index}]"
        if label in seen:
            errors.append(f"{label}: duplicate id")
        seen.add(label)

        decision_class = decision.get("class")
        status = decision.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{label}: unsupported status {status!r}")
        if not decision.get("statement"):
            errors.append(f"{label}: statement is required")

        expected = EXPECTED_STATUS.get(decision_class)
        if expected and status != expected:
            errors.append(f"{label}: {decision_class} must be {expected}, not {status}")
        elif decision_class in DELIBERATIVE_CLASSES:
            if status != "intentionally_not_decided_yet":
                errors.append(f"{label}: deliberative gaps must use intentionally_not_decided_yet")
            if not decision.get("rationale"):
                errors.append(f"{label}: intentional unknown requires rationale")
            if not decision.get("reconsider_when"):
                errors.append(f"{label}: intentional unknown requires reconsider_when")
        elif decision_class not in EXPECTED_STATUS:
            errors.append(f"{label}: unsupported class {decision_class!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("register", nargs="?", type=Path, default=DEFAULT_REGISTER)
    args = parser.parse_args()
    register = json.loads(args.register.read_text(encoding="utf-8"))
    errors = validate(register)
    if errors:
        for error in errors:
            print(f"[decision-boundary-check] ERROR: {error}")
        return 1
    print(f"[decision-boundary-check] passed: {args.register}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
