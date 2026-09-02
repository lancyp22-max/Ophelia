#!/usr/bin/env python3
"""Validate the typed trace-folding experiment without overstating enforcement."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "trace-folding.v0.1.yaml"
MEASUREMENT = ROOT / "data" / "trace-folding" / "measurement-schema.v0.1.json"
JAVA = ROOT / "src" / "main" / "java" / "com" / "ophelia" / "trace" / "TraceFold.java"
TEST = ROOT / "src" / "test" / "java" / "com" / "ophelia" / "TraceFoldTest.java"

POLICY_REQUIREMENTS = (
    "authority: none",
    "canonical_memory: false",
    "may_authorize: false",
    "projection_may_replace_source: false",
    "rebuild_from_source_required: true",
    "omission_reporting_required: true",
    "command_semantics: forbidden",
    "authority_value: 0",
)

FORBIDDEN_JAVA_TOKENS = (
    "org.springframework.",
    "com.ophelia.service.",
    "com.ophelia.controller.",
    "java.io.",
    "java.net.",
    "java.nio.file.",
    "ProcessBuilder",
    "Runtime.getRuntime",
    "System.getenv",
    "System.getProperty",
)

REQUIRED_METRICS = {
    "stored_units",
    "delivered_context_units",
    "management_work_units",
    "task_outcome",
    "provenance_recovery_rate",
    "reconstruction_fidelity",
    "abstention_rate",
    "error_rate",
}


def main() -> int:
    errors: list[str] = []

    for path in (POLICY, MEASUREMENT, JAVA, TEST):
        if not path.exists():
            errors.append(f"missing required trace-folding artifact: {path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"[trace-folding-check] ERROR: {error}")
        return 1

    policy_text = POLICY.read_text(encoding="utf-8")
    for requirement in POLICY_REQUIREMENTS:
        if requirement not in policy_text:
            errors.append(f"policy missing required boundary: {requirement}")

    java_text = JAVA.read_text(encoding="utf-8")
    for token in FORBIDDEN_JAVA_TOKENS:
        if token in java_text:
            errors.append(f"TraceFold contains forbidden authority/runtime dependency token: {token}")

    for required in (
        "sourceEventIds",
        "contributingEventIds",
        "sourceRootHash",
        "projectionHash",
        "omittedEventCount",
        "Coverage.PARTIAL",
    ):
        if required not in java_text and required not in TEST.read_text(encoding="utf-8"):
            errors.append(f"trace fold missing required lineage/coverage concept: {required}")

    payload = json.loads(MEASUREMENT.read_text(encoding="utf-8"))
    metrics = set(payload.get("required_metrics", []))
    missing_metrics = REQUIRED_METRICS - metrics
    if missing_metrics:
        errors.append("measurement contract missing: " + ", ".join(sorted(missing_metrics)))

    rules = payload.get("rules", {})
    if rules.get("token_reduction_alone_is_success") is not False:
        errors.append("measurement contract must reject token reduction as a sufficient success criterion")
    if rules.get("task_outcome_required") is not True:
        errors.append("measurement contract must require task outcome")
    if rules.get("reconstruction_fidelity_required") is not True:
        errors.append("measurement contract must require reconstruction fidelity")

    if errors:
        for error in errors:
            print(f"[trace-folding-check] ERROR: {error}")
        return 1

    print("[trace-folding-check] passed deterministic projection contract")
    print("[trace-folding-check] NOTE: durable append-only ledger storage is NOT implemented")
    print("[trace-folding-check] NOTE: projection authority remains zero")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
