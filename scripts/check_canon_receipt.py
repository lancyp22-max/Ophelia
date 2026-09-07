#!/usr/bin/env python3
"""Validate the Canon Receipt schema and held fixture safety semantics."""

from __future__ import annotations

import copy
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data" / "canon-receipts" / "canon-receipt.v1.schema.json"
SAMPLE = ROOT / "data" / "canon-receipts" / "sample-held-receipt.v1.json"
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
DECISIONS = {"accepted", "denied", "deferred", "hold_without_authority"}
TOP_LEVEL = {
    "schema_version", "receipt_id", "candidate_digest", "provenance",
    "evidence_refs", "proposer", "authorization", "decision", "decided_at",
    "prior_canon_version", "resulting_canon_version", "rollback_pointer",
    "history_integrity"
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = TOP_LEVEL - receipt.keys()
    extra = receipt.keys() - TOP_LEVEL
    if missing:
        errors.append(f"missing fields: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"unsupported fields: {', '.join(sorted(extra))}")
    if receipt.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if not DIGEST.fullmatch(str(receipt.get("candidate_digest", ""))):
        errors.append("candidate_digest must be a sha256 digest")
    for field in ("provenance", "evidence_refs"):
        values = receipt.get(field)
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            errors.append(f"{field} must be a non-empty unique list")
    try:
        decided_at = str(receipt.get("decided_at", "")).replace("Z", "+00:00")
        if datetime.fromisoformat(decided_at).utcoffset() is None:
            raise ValueError
    except ValueError:
        errors.append("decided_at must be timezone-aware ISO 8601")

    decision = receipt.get("decision")
    if decision not in DECISIONS:
        errors.append(f"unsupported decision: {decision!r}")
    authorization = receipt.get("authorization", {})
    if decision == "accepted":
        for field in ("principal_id", "scope", "receipt_ref"):
            if not authorization.get(field):
                errors.append(f"accepted receipt requires authorization.{field}")
        if authorization.get("capability") != "canonize":
            errors.append("accepted receipt requires canonize capability")
        if not receipt.get("resulting_canon_version"):
            errors.append("accepted receipt requires resulting_canon_version")
        if not receipt.get("rollback_pointer"):
            errors.append("accepted receipt requires rollback_pointer")
    elif receipt.get("resulting_canon_version") is not None or receipt.get("rollback_pointer") is not None:
        errors.append("non-accepted receipt cannot claim a canon version or rollback pointer")

    integrity = receipt.get("history_integrity", {})
    if not DIGEST.fullmatch(str(integrity.get("event_digest", ""))):
        errors.append("history_integrity.event_digest must be a sha256 digest")
    if integrity.get("assertion") != "record_integrity_not_current_truth":
        errors.append("history integrity must not claim current truth")
    return errors


def main() -> int:
    schema = load(SCHEMA)
    sample = load(SAMPLE)
    errors = validate(sample)
    if schema.get("additionalProperties") is not False:
        errors.append("schema must reject unknown top-level fields")
    if "hold_without_authority" not in schema["properties"]["decision"]["enum"]:
        errors.append("schema must preserve hold_without_authority")

    unsafe = copy.deepcopy(sample)
    unsafe["decision"] = "accepted"
    unsafe_errors = validate(unsafe)
    required_denials = (
        "accepted receipt requires authorization.principal_id",
        "accepted receipt requires canonize capability",
        "accepted receipt requires resulting_canon_version",
        "accepted receipt requires rollback_pointer",
    )
    for denial in required_denials:
        if denial not in unsafe_errors:
            errors.append(f"negative fixture did not enforce: {denial}")

    if errors:
        for error in errors:
            print(f"[canon-receipt-check] ERROR: {error}")
        return 1
    print(f"[canon-receipt-check] passed: {SCHEMA}")
    print(f"[canon-receipt-check] passed: {SAMPLE}")
    print("[canon-receipt-check] accepted-without-authority denial passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
