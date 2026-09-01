#!/usr/bin/env python3
"""Validate the inactive Lumaria dual-channel shadow policy."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data" / "dual-channel" / "dual-channel-policy.v0.1.json"

REQUIRED_PROTECTED = {
    "identity",
    "canonical_memory",
    "authority",
    "permissions",
    "governance",
    "credentials",
    "network",
    "persistence",
}
SHADOW_DENY = {
    "network",
    "filesystem_write",
    "credentials",
    "authority_write",
    "identity_write",
    "canonical_memory_write",
    "persistent_write",
}


def main() -> int:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    errors: list[str] = []

    if policy.get("schema_version") != "0.1":
        errors.append("schema_version must be 0.1")
    if policy.get("status") != "inactive_scaffold":
        errors.append("v0.1 must remain inactive_scaffold")

    base = policy.get("base_snapshot", {})
    if base.get("shared") is not True:
        errors.append("channels must share one base snapshot")
    if base.get("immutable") is not True:
        errors.append("base snapshot must be immutable")
    if base.get("copy_on_write_overlays") is not True:
        errors.append("overlays must be copy-on-write")

    channels = policy.get("channels", [])
    ids = [item.get("id") for item in channels]
    if ids != ["primary", "shadow"]:
        errors.append("v0.1 must define exactly primary and shadow channels in order")

    for channel in channels:
        if channel.get("direct_live_mutation") is not False:
            errors.append(f"{channel.get('id')} must not have direct live mutation")

    shadow = next((item for item in channels if item.get("id") == "shadow"), {})
    capabilities = shadow.get("capabilities", {})
    for key in SHADOW_DENY:
        if capabilities.get(key) is not False:
            errors.append(f"shadow capability {key} must be explicitly false")

    actuation = policy.get("actuation", {})
    if actuation.get("live_mutation_enabled") is not False:
        errors.append("dual-channel runtime must not enable live mutation")
    if actuation.get("actuator_count_inside_dual_channel_runtime") != 0:
        errors.append("dual-channel runtime must contain zero live actuators")

    promotion = policy.get("promotion", {})
    if promotion.get("auto_promote") is not False:
        errors.append("consensus must never auto-promote")
    if promotion.get("consensus_is_authority") is not False:
        errors.append("consensus must not be treated as authority")
    if promotion.get("requires_existing_authority_gate") != "NE-000":
        errors.append("promotion must remain behind the existing NE-000 gate")

    protected = set(policy.get("protected_boundaries", []))
    missing = REQUIRED_PROTECTED - protected
    if missing:
        errors.append("missing protected boundaries: " + ", ".join(sorted(missing)))

    routes = policy.get("decision_routes", {})
    expected_routes = {
        "consensus_low_risk_reversible": "propose_for_promotion",
        "disagreement_low_risk_reversible": "preserve_both_for_comparison",
        "protected_boundary": "HALT_AND_SURFACE",
        "unknown_consequence": "intentionally_not_decided_yet",
        "destructive_or_irreversible": "HALT_AND_SURFACE",
    }
    for key, value in expected_routes.items():
        if routes.get(key) != value:
            errors.append(f"decision route {key} must be {value}")

    resources = policy.get("resource_policy", {})
    if resources.get("physical_parallelism_required") is not False:
        errors.append("physical parallelism must not be required")
    if resources.get("sequential_model_residency_allowed") is not True:
        errors.append("sequential model residency must remain allowed")
    if resources.get("keep_alive_default") != 0:
        errors.append("keep_alive_default must remain 0 for the initial experiment")

    dream = policy.get("dream_channel", {})
    if dream.get("active") is not False:
        errors.append("dream channel must remain inactive")
    if dream.get("status") != "intentionally_not_decided_yet":
        errors.append("dream channel status must remain intentionally_not_decided_yet")

    if errors:
        for error in errors:
            print(f"[dual-channel-check] ERROR: {error}")
        return 1

    print(f"[dual-channel-check] passed: {POLICY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
