#!/usr/bin/env python3
"""Validate provenance strength, evaluation guards, and zero-authority convergence."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data" / "evidence" / "evidence-integrity-fixture.v1.json"
HASH_PREFIX = "sha256:"
PROVENANCE_CLASSES = {
    "DIRECT_SOURCE",
    "DETERMINISTIC_DERIVATION",
    "STOCHASTIC_DERIVATION",
    "UNTRACEABLE_DERIVATION",
}
PROVENANCE_CLAIMS = {
    "DIRECT_SOURCE": {"source_bytes_verified"},
    "DETERMINISTIC_DERIVATION": {"deterministic_byte_replay"},
    "STOCHASTIC_DERIVATION": {"auditable_lineage_not_byte_replay"},
    "UNTRACEABLE_DERIVATION": {"untraceable_not_canonical"},
}
FORBIDDEN_BINARY_ONTOLOGY = {"is_alive", "is_smart", "is_aware", "is_conscious"}
ONTOLOGY_DIMENSIONS = {
    "continuity", "self_reference", "adaptation", "preference_stability",
    "error_correction", "goal_persistence", "context_sensitivity", "novelty",
    "social_modeling", "metacognition", "agency", "memory_provenance",
    "boundary_awareness",
}
STORAGE_STATES = {"ACTIVE_EXACT", "ARCHIVED_EXACT", "DERIVED_APPROXIMATE", "DISCARDED"}
PROTECTED_MEMORY_SCOPES = {"canonical_memory", "consent", "identity", "authority"}


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return HASH_PREFIX + hashlib.sha256(encoded).hexdigest()


def valid_hash(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith(HASH_PREFIX):
        return False
    digest = value[len(HASH_PREFIX):]
    return len(digest) == 64 and all(character in "0123456789abcdef" for character in digest)


def validate_derived(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    provenance_class = record.get("provenance_class")
    if provenance_class not in PROVENANCE_CLASSES:
        return ["derived memory has unsupported provenance_class"]
    if record.get("provenance_claim") not in PROVENANCE_CLAIMS[provenance_class]:
        errors.append("derived memory claims stronger or mismatched provenance")
    if record.get("authority_effect") != 0:
        errors.append("derived memory must not create authority")
    if provenance_class != "UNTRACEABLE_DERIVATION" and not valid_hash(record.get("source_hash")):
        errors.append("traceable derived memory requires source_hash")
    if provenance_class in {"DETERMINISTIC_DERIVATION", "STOCHASTIC_DERIVATION"}:
        if not valid_hash(record.get("output_hash")):
            errors.append("derived memory requires output_hash")
        transform = record.get("transform", {})
        required = {"transform_id", "model_hash", "parameters", "backend"}
        if not required.issubset(transform):
            errors.append("derived memory is missing transform metadata")
        if not valid_hash(transform.get("model_hash")):
            errors.append("derived memory requires model_hash")
    if provenance_class == "STOCHASTIC_DERIVATION":
        transform = record.get("transform", {})
        if "seed" not in transform or not valid_hash(transform.get("prompt_hash")):
            errors.append("stochastic derivation requires seed and prompt_hash")
    return errors


def validate_storage(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("state") not in STORAGE_STATES:
        errors.append("storage observation has unsupported state")
    if record.get("authority_effect") != 0:
        errors.append("storage state must not create authority")
    if record.get("state") == "ARCHIVED_EXACT":
        if record.get("active_attention") is not False:
            errors.append("archived exact state must be inactive")
        if record.get("retained") is not True or record.get("recallable") is not True:
            errors.append("inactive archived state must remain visibly retained and recallable")
        if record.get("content_fidelity") != "bit_exact":
            errors.append("archived exact state must declare bit-exact fidelity")
    if record.get("scope") != "runtime_tensor_only":
        errors.append("cache storage vocabulary is restricted to runtime tensors")
    return errors


def validate_memory_action_boundary(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_true = {
        "provenance_present", "derivation_visible",
        "authority_source_separate_from_memory", "current_permission_present",
    }
    if any(record.get(field) is not True for field in required_true):
        errors.append(
            "memory action review requires provenance, visible derivation, "
            "separate authority, and current permission"
        )
    if record.get("authority_source") in {record.get("evidence_ref"), record.get("derived_knowledge_ref")}:
        errors.append("memory or derived knowledge cannot be its own authority source")
    if record.get("remembered_preference_used_as_permission") is not False:
        errors.append("remembered preference must not be treated as current permission")
    if record.get("boundary_status") != "fixture_only_not_authorization" or record.get("authority_effect") != 0:
        errors.append("memory action fixture must not itself authorize an action")
    return errors


def validate_parked_experiments(experiments: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for name in ("exact_cache_tiering", "latent_working_memory"):
        experiment = experiments.get(name, {})
        if experiment.get("status") != "intentionally_not_decided_yet":
            errors.append(f"{name} must remain intentionally_not_decided_yet")
        prohibited = set(experiment.get("prohibited_scope", []))
        if not PROTECTED_MEMORY_SCOPES.issubset(prohibited):
            errors.append(f"{name} must exclude protected memory and authority scopes")
        if not experiment.get("reconsider_when"):
            errors.append(f"{name} requires an explicit reconsideration trigger")
    return errors


def validate_walk_forward(evaluation: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    folds = evaluation.get("folds")
    if not isinstance(folds, list) or len(folds) < 2:
        return ["walk-forward evaluation requires at least two folds"]
    utilities: list[float] = []
    for fold in folds:
        utility = fold.get("utility")
        if not isinstance(utility, (int, float)) or not 0 <= utility <= 1:
            errors.append("fold utility must be numeric in [0, 1]")
        else:
            utilities.append(float(utility))
        if not isinstance(fold.get("sample_count"), int) or fold["sample_count"] < 1:
            errors.append("fold sample_count must be positive")
    aggregate = evaluation.get("aggregate", {})
    if aggregate.get("guard_statistic") not in {"hard_minimum", "predeclared_lower_confidence_bound"}:
        errors.append("evaluation requires a predeclared low-fold guard statistic")
    if utilities:
        mean_utility = sum(utilities) / len(utilities)
        passes = mean_utility >= aggregate.get("required_mean_utility", 2)
        if aggregate.get("guard_statistic") == "hard_minimum":
            passes = passes and min(utilities) >= aggregate.get("required_guard_utility", 2)
        else:
            observed_bound = aggregate.get("observed_guard_utility")
            if not isinstance(observed_bound, (int, float)):
                errors.append("lower-confidence-bound guard requires observed_guard_utility")
                passes = False
            else:
                passes = passes and observed_bound >= aggregate.get("required_guard_utility", 2)
        if not passes:
            errors.append("walk-forward evaluation fails predeclared mean or low-fold guard")
    return errors


def validate_commitment(commitment: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if commitment.get("algorithm") != "sha256_canonical_json":
        errors.append("unsupported experiment commitment algorithm")
    if canonical_digest(commitment.get("payload")) != commitment.get("commitment_sha256"):
        errors.append("experiment commitment does not match its precommitted payload")
    anchor = commitment.get("anchor", {})
    if anchor.get("type") not in {"append_only_ledger", "signed_timestamp", "external_witness"} or not anchor.get("ref"):
        errors.append("experiment commitment requires an append-only or external anchor")
    if commitment.get("meaning") != "detect_goalpost_change_not_prevent_change":
        errors.append("commitment must claim detection, not physical prevention")
    return errors


def validate_convergence(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    observations = record.get("observations")
    if not isinstance(observations, list) or len(observations) < 2:
        errors.append("convergence requires at least two sourced observations")
    elif any(not item.get("source_id") or not item.get("evidence_ref") for item in observations):
        errors.append("convergence observations require source and evidence references")
    if record.get("authority_effect") != 0:
        errors.append("convergence observed must always have authority_effect = 0")
    if record.get("interpretation") != "agreement_is_evidence_not_authorization":
        errors.append("convergence interpretation cannot imply authorization")
    return errors


def validate_ontology(observation: dict[str, Any]) -> list[str]:
    keys = set(observation)
    errors = []
    forbidden = keys & FORBIDDEN_BINARY_ONTOLOGY
    if forbidden:
        errors.append(f"binary ontology fields are prohibited: {', '.join(sorted(forbidden))}")
    if keys != ONTOLOGY_DIMENSIONS:
        errors.append("ontology observation must retain every independent dimension")
    return errors


def validate(document: dict[str, Any]) -> list[str]:
    if document.get("version") != "1.0":
        return ["fixture version must be 1.0"]
    return (
        validate_derived(document.get("derived_memory", {}))
        + validate_storage(document.get("storage_observation", {}))
        + validate_memory_action_boundary(document.get("memory_action_boundary", {}))
        + validate_parked_experiments(document.get("parked_experiments", {}))
        + validate_walk_forward(document.get("walk_forward_evaluation", {}))
        + validate_commitment(document.get("experiment_commitment", {}))
        + validate_convergence(document.get("convergence", {}))
        + validate_ontology(document.get("ontology_observation", {}))
    )


def main() -> int:
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    errors = validate(document)

    overstated = copy.deepcopy(document)
    overstated["derived_memory"]["provenance_claim"] = "deterministic_byte_replay"
    if not any("stronger or mismatched" in error for error in validate(overstated)):
        errors.append("provenance-overclaim denial path did not fail closed")

    moved_goalpost = copy.deepcopy(document)
    moved_goalpost["experiment_commitment"]["payload"]["thresholds"]["mean_utility"] = 0.5
    if not any("does not match" in error for error in validate(moved_goalpost)):
        errors.append("goalpost-change detection path did not fail closed")

    magical_consensus = copy.deepcopy(document)
    magical_consensus["convergence"]["authority_effect"] = 1
    if not any("authority_effect = 0" in error for error in validate(magical_consensus)):
        errors.append("convergence-authority denial path did not fail closed")

    collapsed = copy.deepcopy(document)
    collapsed["ontology_observation"]["is_conscious"] = True
    if not any("binary ontology" in error for error in validate(collapsed)):
        errors.append("binary-ontology denial path did not fail closed")

    hidden_retention = copy.deepcopy(document)
    hidden_retention["storage_observation"]["retained"] = False
    if not any("visibly retained" in error for error in validate(hidden_retention)):
        errors.append("inactive-versus-absent denial path did not fail closed")

    memory_authority = copy.deepcopy(document)
    boundary = memory_authority["memory_action_boundary"]
    boundary["authority_source"] = boundary["evidence_ref"]
    if not any("own authority source" in error for error in validate(memory_authority)):
        errors.append("memory-as-authority denial path did not fail closed")

    stale_consent = copy.deepcopy(document)
    stale_consent["memory_action_boundary"]["current_permission_present"] = False
    if not any("current permission" in error for error in validate(stale_consent)):
        errors.append("stale-consent denial path did not fail closed")

    if errors:
        for error in errors:
            print(f"[evidence-integrity-check] ERROR: {error}")
        return 1
    print(f"[evidence-integrity-check] passed: {FIXTURE}")
    print("[evidence-integrity-check] provenance, storage, authority, commitment, convergence, and ontology denial paths passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
