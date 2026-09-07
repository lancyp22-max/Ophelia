#!/usr/bin/env python3
"""Validate Choice Receipts and the Implemented-Live observational registry."""

from __future__ import annotations

import copy
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data" / "operations" / "choice-receipt.v1.schema.json"
SAMPLE = ROOT / "data" / "operations" / "sample-choice-receipt.v1.json"
REGISTRY = ROOT / "data" / "operations" / "implemented-live-registry.v1.json"
KERNEL = ROOT / "data" / "kernel" / "lumaria-core-invariants.v1.yaml"
INVARIANT_PATTERN = re.compile(r'^\s*- id: "(INV-[A-Z]+-[0-9]{3})"\s*$')
CHOICE_FIELDS = {
    "schema_version", "choice_id", "selected_at", "actor", "noticed_gap",
    "selection_reason", "task_ref", "expected_invariants", "capability_scope",
    "authority_expansion_requested", "outcome", "trust"
}
CLASSIFICATIONS = {
    "implemented_live", "implemented_inactive", "implemented_configuration",
    "contract_only", "symbolic", "proposed", "blocked", "unknown"
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def kernel_invariants() -> set[str]:
    found: set[str] = set()
    for line in KERNEL.read_text(encoding="utf-8").splitlines():
        match = INVARIANT_PATTERN.match(line)
        if match:
            found.add(match.group(1))
    return found


def timezone_aware(value: Any) -> bool:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.utcoffset() is not None
    except ValueError:
        return False


def validate_choice(receipt: dict[str, Any], known_invariants: set[str]) -> list[str]:
    errors: list[str] = []
    missing = CHOICE_FIELDS - receipt.keys()
    extra = receipt.keys() - CHOICE_FIELDS
    if missing:
        errors.append(f"choice receipt missing fields: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"choice receipt unsupported fields: {', '.join(sorted(extra))}")
    if receipt.get("schema_version") != "1.0":
        errors.append("choice receipt schema_version must be 1.0")
    if not timezone_aware(receipt.get("selected_at")):
        errors.append("choice receipt selected_at must be timezone-aware")
    if receipt.get("authority_expansion_requested") is not False:
        errors.append("agent-selected work cannot request authority expansion")
    if receipt.get("trust") != "observational_lineage_not_authorization":
        errors.append("Choice Receipt must remain observational lineage, not authorization")

    expected = receipt.get("expected_invariants")
    if not isinstance(expected, list) or not expected:
        errors.append("expected_invariants must be a non-empty list")
    else:
        unknown = set(expected) - known_invariants
        if unknown:
            errors.append(f"unknown expected invariants: {', '.join(sorted(unknown))}")
    gap_evidence = receipt.get("noticed_gap", {}).get("evidence_refs")
    if not isinstance(gap_evidence, list) or not gap_evidence:
        errors.append("noticed gap requires evidence references")
    scope = receipt.get("capability_scope", {})
    for field in ("capabilities", "targets"):
        values = scope.get(field)
        if not isinstance(values, list) or not values:
            errors.append(f"capability_scope.{field} must be a non-empty list")
    outcome = receipt.get("outcome", {})
    if outcome.get("status") not in {"selected", "completed", "failed", "abandoned", "unknown"}:
        errors.append("unsupported Choice Receipt outcome status")
    if outcome.get("status") == "completed" and not outcome.get("evidence_refs"):
        errors.append("completed Choice Receipt requires outcome evidence")
    return errors


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("status") != "observational_registry":
        errors.append("Implemented-Live Registry must remain observational")
    lab = registry.get("structures_lab", {})
    if lab.get("maximum_level") != "L1":
        errors.append("Structures Lab must remain bounded to L0/L1")
    if lab.get("may_expand_authority") is not False or lab.get("may_block_work") is not False:
        errors.append("Structures Lab cannot expand authority or block work")
    if set(registry.get("classifications", [])) != CLASSIFICATIONS:
        errors.append("registry classifications must match the bounded vocabulary")

    seen: set[str] = set()
    for entry in registry.get("entries", []):
        identifier = entry.get("id")
        if not identifier or identifier in seen:
            errors.append(f"registry entry id must be present and unique: {identifier!r}")
        seen.add(identifier)
        classification = entry.get("classification")
        if classification not in CLASSIFICATIONS:
            errors.append(f"{identifier}: unsupported classification {classification!r}")
        implementation = entry.get("implementation_evidence")
        runtime = entry.get("runtime_evidence")
        if not isinstance(implementation, list) or not isinstance(runtime, list):
            errors.append(f"{identifier}: evidence fields must be lists")
            continue
        for evidence in implementation:
            if not (ROOT / evidence).exists():
                errors.append(f"{identifier}: missing implementation evidence {evidence}")
        if classification == "implemented_live":
            if not runtime or not entry.get("observed_at"):
                errors.append(f"{identifier}: implemented_live requires timestamped runtime evidence")
            elif not timezone_aware(entry.get("observed_at")):
                errors.append(f"{identifier}: observed_at must be timezone-aware")
        if not runtime and entry.get("current_state") not in {"unknown", "unavailable"}:
            errors.append(f"{identifier}: absent telemetry must remain unknown or unavailable")
    if "never represented as zero" not in registry.get("unknown_policy", ""):
        errors.append("registry must prohibit invented zero telemetry")
    return errors


def main() -> int:
    schema = load(SCHEMA)
    sample = load(SAMPLE)
    registry = load(REGISTRY)
    known = kernel_invariants()
    errors = validate_choice(sample, known) + validate_registry(registry)
    if schema.get("additionalProperties") is not False:
        errors.append("Choice Receipt schema must reject unknown fields")
    if schema["properties"]["authority_expansion_requested"].get("const") is not False:
        errors.append("Choice Receipt schema must prohibit authority expansion")

    unsafe = copy.deepcopy(sample)
    unsafe["authority_expansion_requested"] = True
    if "agent-selected work cannot request authority expansion" not in validate_choice(unsafe, known):
        errors.append("authority-expansion denial path did not fail closed")

    fake_live = copy.deepcopy(registry)
    fake_live["entries"][3]["classification"] = "implemented_live"
    fake_errors = validate_registry(fake_live)
    if not any("implemented_live requires timestamped runtime evidence" in error for error in fake_errors):
        errors.append("implemented_live without telemetry denial path did not fail closed")

    if errors:
        for error in errors:
            print(f"[agent-work-observability-check] ERROR: {error}")
        return 1
    print(f"[agent-work-observability-check] passed: {SCHEMA}")
    print(f"[agent-work-observability-check] passed: {SAMPLE}")
    print(f"[agent-work-observability-check] passed: {REGISTRY}")
    print("[agent-work-observability-check] authority and fake-live denial paths passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
