#!/usr/bin/env python3
"""Validate the bounded Scene Action Bus schema and its fixture proposal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data" / "scene-actions" / "scene-action-bus.v0.1.schema.json"
SAMPLE = ROOT / "data" / "scene-actions" / "sample-lantern-proposal.v0.1.json"
ACTION_TYPES = {"spawn", "move", "rotate", "resize", "recolor", "annotate", "remove_own_object", "request_persistence"}
FORBIDDEN_PAYLOAD_KEYS = {"code", "javascript", "script", "eval", "module", "url", "html"}
TOP_LEVEL_KEYS = {"schema_version", "action_id", "phase", "actor", "action", "scope", "consent", "persistence", "budget", "rollback"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def forbidden_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).casefold()
            if normalized in FORBIDDEN_PAYLOAD_KEYS:
                found.add(normalized)
            found.update(forbidden_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            found.update(forbidden_keys(nested))
    return found


def validate(sample: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = TOP_LEVEL_KEYS - sample.keys()
    extra = sample.keys() - TOP_LEVEL_KEYS
    if missing:
        errors.append(f"missing top-level fields: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"unsupported top-level fields: {', '.join(sorted(extra))}")
    if sample.get("schema_version") != "0.1":
        errors.append("schema_version must be 0.1")
    if sample.get("phase") != "proposal":
        errors.append("fixture must remain a proposal; it is not an approved mutation")

    actor = sample.get("actor", {})
    for field in ("participant_id", "runtime_id", "provenance"):
        if not actor.get(field):
            errors.append(f"actor.{field} is required")

    action = sample.get("action", {})
    action_type = action.get("type")
    if action_type not in ACTION_TYPES:
        errors.append(f"unsupported action type: {action_type!r}")
    payload = action.get("payload")
    if not isinstance(payload, dict):
        errors.append("action.payload must be an object")
    else:
        forbidden = forbidden_keys(payload)
        if forbidden:
            errors.append(f"executable or remote payload keys are forbidden: {', '.join(sorted(forbidden))}")

    scope = sample.get("scope", {})
    for field in ("scene_id", "region_id", "lease_id", "expires_at"):
        if not scope.get(field):
            errors.append(f"scope.{field} is required")

    consent = sample.get("consent", {})
    if consent.get("required") is not True:
        errors.append("scene mutation proposals must require consent")
    if consent.get("surface_ack") is not False:
        errors.append("proposal fixture must not claim surfaced approval")

    persistence = sample.get("persistence", {})
    if persistence.get("mode") != "session" or persistence.get("requested") is not False:
        errors.append("spawn fixture must default to non-persistent session scope")

    budget = sample.get("budget", {})
    limits = {"triangle_estimate": 50000, "texture_bytes": 4194304, "ttl_seconds": 3600}
    for field, maximum in limits.items():
        value = budget.get(field)
        if not isinstance(value, int) or value < 0 or value > maximum:
            errors.append(f"budget.{field} must be an integer between 0 and {maximum}")
    if budget.get("object_delta") != 1:
        errors.append("spawn fixture object_delta must be 1")

    if sample.get("rollback", {}).get("strategy") != "remove_spawned_object":
        errors.append("spawn fixture must define remove_spawned_object rollback")
    return errors


def main() -> int:
    schema = load(SCHEMA)
    sample = load(SAMPLE)
    errors = validate(sample)
    if schema.get("additionalProperties") is not False:
        errors.append("schema must reject unknown top-level properties")
    action_schema = schema["properties"]["action"]["properties"]
    if "javascript" in action_schema["type"].get("enum", []):
        errors.append("schema must not expose raw JavaScript as an action")
    blocked_payload_names = set(action_schema["payload"]["propertyNames"]["not"]["enum"])
    if blocked_payload_names != FORBIDDEN_PAYLOAD_KEYS:
        errors.append("schema forbidden payload keys must match validator policy")
    if errors:
        for error in errors:
            print(f"[scene-action-bus-check] ERROR: {error}")
        return 1
    print(f"[scene-action-bus-check] passed: {SCHEMA}")
    print(f"[scene-action-bus-check] passed: {SAMPLE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
