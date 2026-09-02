#!/usr/bin/env python3
"""Require explicit design/enforcement maturity on every repository policy file."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DESIGN_STATUSES = {
    "specified",
    "partially_specified",
    "intentionally_not_decided_yet",
}

ENFORCEMENT_STATUSES = {
    "not_implemented",
    "partially_implemented",
    "implemented_not_verified",
    "verified_in_ci",
    "verified_at_runtime",
    "blocked_by_missing_safety_boundary",
}


def policy_paths() -> list[Path]:
    paths = list((ROOT / "policies").rglob("*.yaml"))
    paths += list((ROOT / "policies").rglob("*.yml"))
    for path in (ROOT / "data").rglob("*"):
        if not path.is_file():
            continue
        if "policy" not in path.name.casefold():
            continue
        if path.suffix.casefold() in {".json", ".yaml", ".yml"}:
            paths.append(path)
    return sorted(set(paths))


def yaml_scalar(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith(('"', "'")) and value.endswith(('"', "'")):
        value = value[1:-1]
    return value


def yaml_list(text: str, key: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if re.fullmatch(rf"{re.escape(key)}:\s*\[\]\s*", line):
            return []
        if re.fullmatch(rf"{re.escape(key)}:\s*", line):
            values: list[str] = []
            for nested in lines[index + 1 :]:
                if not nested.startswith("  "):
                    break
                match = re.match(r"^\s+-\s+(.+?)\s*$", nested)
                if match:
                    value = match.group(1).strip().strip('"').strip("'")
                    values.append(value)
            return values
    return None


def check_one(path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")

    if path.suffix.casefold() == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            return [f"{rel}: invalid JSON: {exc}"]
        design = payload.get("design_status")
        enforcement = payload.get("enforcement_status")
        scope = payload.get("enforcement_scope")
        evidence = payload.get("enforcement_evidence")
    else:
        design = yaml_scalar(text, "design_status")
        enforcement = yaml_scalar(text, "enforcement_status")
        scope = yaml_scalar(text, "enforcement_scope")
        evidence = yaml_list(text, "enforcement_evidence")

    if design not in DESIGN_STATUSES:
        errors.append(f"{rel}: missing/invalid design_status: {design!r}")
    if enforcement not in ENFORCEMENT_STATUSES:
        errors.append(f"{rel}: missing/invalid enforcement_status: {enforcement!r}")
    if not isinstance(scope, str) or not scope.strip():
        errors.append(f"{rel}: enforcement_scope must state what is and is not enforced")
    if evidence is None or not isinstance(evidence, list):
        errors.append(f"{rel}: enforcement_evidence must be an explicit list (empty is okay only when not implemented)")
        evidence = []

    if enforcement == "not_implemented" and evidence:
        errors.append(f"{rel}: not_implemented policy must not claim enforcement evidence")

    if enforcement in {
        "partially_implemented",
        "implemented_not_verified",
        "verified_in_ci",
        "verified_at_runtime",
    } and not evidence:
        errors.append(f"{rel}: {enforcement} requires at least one enforcement_evidence path")

    for raw in evidence:
        if not isinstance(raw, str) or not raw.strip():
            errors.append(f"{rel}: invalid enforcement evidence entry: {raw!r}")
            continue
        evidence_path = ROOT / raw
        if not evidence_path.exists():
            errors.append(f"{rel}: enforcement evidence path does not exist: {raw}")

    return errors


def main() -> int:
    paths = policy_paths()
    errors: list[str] = []

    if not paths:
        errors.append("no policy files discovered")

    for path in paths:
        errors.extend(check_one(path))

    if errors:
        for error in errors:
            print(f"[policy-maturity-check] ERROR: {error}")
        return 1

    print(f"[policy-maturity-check] passed: {len(paths)} policy files")
    for path in paths:
        print(f"[policy-maturity-check]   {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
