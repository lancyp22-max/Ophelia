#!/usr/bin/env python3
"""Validate the inactive Lumaria dual-channel shadow policy.

This checker enforces application-level purity and policy consistency. It does
NOT claim OS/process isolation. Infrastructure isolation is tested separately.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data" / "dual-channel" / "dual-channel-policy.v0.1.json"
ALLOWLIST = ROOT / "data" / "dual-channel" / "effect-allowlist.v0.1.json"
RUNTIME_DIR = ROOT / "src" / "main" / "java" / "com" / "ophelia" / "runtime"

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
EXPECTED_STAGE_ONLY = {
    "read_snapshot",
    "stage_overlay",
    "compare_overlays",
    "emit_observation",
}
EXPECTED_SURFACE = {
    "world_mutation",
    "network_call",
    "filesystem_write",
    "credential_access",
    "identity_write",
    "canonical_memory_write",
    "authority_change",
    "permission_change",
    "governance_change",
    "persistence_write",
}

# Application-purity lint. This is defense in depth, not a process sandbox.
ALLOWED_IMPORT_PREFIXES = ("java.util.",)
FORBIDDEN_RUNTIME_TOKENS = (
    "java.io.",
    "java.net.",
    "java.nio.file.",
    "java.lang.reflect.",
    "javax.net.",
    "ProcessBuilder",
    "Runtime.getRuntime",
    "System.getenv",
    "System.getProperty",
    "Class.forName",
    "org.springframework.",
    "com.ophelia.service.",
    "com.ophelia.controller.",
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_runtime_purity(errors: list[str]) -> None:
    for path in sorted(RUNTIME_DIR.glob("*.java")):
        source = path.read_text(encoding="utf-8")
        imports = re.findall(r"^import\s+([^;]+);", source, flags=re.MULTILINE)
        for imported in imports:
            if not imported.startswith(ALLOWED_IMPORT_PREFIXES):
                errors.append(
                    f"{path.relative_to(ROOT)} imports non-allowlisted dependency: {imported}"
                )
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in source:
                errors.append(
                    f"{path.relative_to(ROOT)} contains privileged/runtime token: {token}"
                )


def main() -> int:
    policy = load(POLICY)
    allowlist = load(ALLOWLIST)
    errors: list[str] = []

    if policy.get("schema_version") != "0.2":
        errors.append("policy schema_version must be 0.2")
    if policy.get("status") != "inactive_scaffold":
        errors.append("v0.1 experiment must remain inactive_scaffold")

    guarantees = policy.get("guarantee_levels", {})
    if guarantees.get("workspace_purity") != "code_and_ci_boundary":
        errors.append("workspace purity must be described as a code_and_ci_boundary")
    if guarantees.get("shadow_process_principal") != "blocked_by_missing_safety_boundary":
        errors.append("live shadow principal must remain blocked until isolation exists")
    if guarantees.get("live_authority_isolation") != "not_claimed":
        errors.append("policy must not claim live authority isolation before it is proven")

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
    if shadow.get("capability_semantics") != "not_exposed_by_workspace_api_only":
        errors.append("shadow capability flags must be scoped to workspace API, not infra claims")
    capabilities = shadow.get("capabilities", {})
    for key in SHADOW_DENY:
        if capabilities.get(key) is not False:
            errors.append(f"shadow workspace capability {key} must be explicitly false")

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
    if promotion.get("semantic_classifier_may_expand_allowlist") is not False:
        errors.append("semantic classifier must not be able to expand the hard allowlist")
    if promotion.get("requires_existing_authority_gate") != "NE-000":
        errors.append("promotion must remain behind the existing NE-000 gate")

    effect_gate = policy.get("effect_gate", {})
    if effect_gate.get("allowlist_file") != "data/dual-channel/effect-allowlist.v0.1.json":
        errors.append("policy must point at the checked hard effect allowlist")
    if effect_gate.get("default_for_unlisted_effect") != "intentionally_not_decided_yet":
        errors.append("unlisted effects must park as intentionally_not_decided_yet")
    if effect_gate.get("semantic_low_risk_verdict_is_not_permission") is not True:
        errors.append("semantic low-risk verdict must not itself grant permission")

    if allowlist.get("schema_version") != "0.1":
        errors.append("effect allowlist schema_version must be 0.1")
    if set(allowlist.get("allowed_stage_only", [])) != EXPECTED_STAGE_ONLY:
        errors.append("hard staged-only effect allowlist changed unexpectedly")
    if set(allowlist.get("protected_always_surface", [])) != EXPECTED_SURFACE:
        errors.append("protected effect surface list changed unexpectedly")
    if allowlist.get("default_for_unlisted_effect") != "intentionally_not_decided_yet":
        errors.append("allowlist must park unlisted effects")
    if allowlist.get("semantic_classifier_may_expand_allowlist") is not False:
        errors.append("effect allowlist must reject semantic expansion")
    if allowlist.get("live_effect_permission_granted") is not False:
        errors.append("v0.1 effect allowlist must grant no live effect permission")

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

    launch = policy.get("launch_contract", {})
    if launch.get("supported_launcher") != "scripts/run_shadow_sandbox.sh":
        errors.append("Shadow launch contract must name the supported per-launch verifier")
    if launch.get("verify_actual_container_before_every_start") is not True:
        errors.append("every supported Shadow launch must verify the actual container before start")
    if launch.get("direct_unverified_launch_supported") is not False:
        errors.append("direct unverified Shadow launch must remain unsupported")
    if launch.get("ci_probe") != "scripts/probe_shadow_sandbox.sh":
        errors.append("Shadow launch contract must retain the CI negative probe")
    if not (ROOT / "scripts" / "run_shadow_sandbox.sh").exists():
        errors.append("supported Shadow launcher is missing")
    if not (ROOT / "scripts" / "probe_shadow_sandbox.sh").exists():
        errors.append("Shadow launch probe is missing")

    modes = policy.get("experiment_modes", {})
    for mode_name in ("reproducibility", "variance_sampling"):
        mode = modes.get(mode_name, {})
        if mode.get("same_snapshot") is not True:
            errors.append(f"{mode_name} must use the same starting snapshot")
        if mode.get("ambient_state_manifest_required") is not True:
            errors.append(f"{mode_name} must record an ambient-state manifest")
        if mode.get("alternate_run_order") is not True:
            errors.append(f"{mode_name} must alternate A/B run order to expose order effects")

    wiring = policy.get("agent_wiring", {})
    if wiring.get("enabled") is not False:
        errors.append("agent wiring must remain disabled in this scaffold")
    unblock = set(wiring.get("unblock_requires", []))
    for requirement in {
        "infrastructure_negative_probe_green",
        "isolated_shadow_principal_defined",
        "no_ambient_credentials",
        "no_network_route",
        "read_only_or_no_host_filesystem_mount",
        "explicit_review_of_snapshot_transport",
        "supported_launcher_is_only_shadow_launch_path",
        "per_launch_contract_verification_enabled",
        "authority_and_experiment_clocks_separated",
    }:
        if requirement not in unblock:
            errors.append(f"agent wiring missing unblock requirement: {requirement}")

    dream = policy.get("dream_channel", {})
    if dream.get("active") is not False:
        errors.append("dream channel must remain inactive")
    if dream.get("status") != "intentionally_not_decided_yet":
        errors.append("dream channel status must remain intentionally_not_decided_yet")

    check_runtime_purity(errors)

    if errors:
        for error in errors:
            print(f"[dual-channel-check] ERROR: {error}")
        return 1

    print(f"[dual-channel-check] passed policy: {POLICY}")
    print(f"[dual-channel-check] passed allowlist: {ALLOWLIST}")
    print("[dual-channel-check] runtime application-purity lint passed")
    print("[dual-channel-check] NOTE: process/OS isolation is NOT proven by this checker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
