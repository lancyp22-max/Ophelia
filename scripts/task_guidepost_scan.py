#!/usr/bin/env python3
"""Match a current task to curated failure guideposts without inventing cases."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data" / "task-guideposts" / "task-guideposts.v0.1.json"
DEFAULT_JSON = ROOT / "artifacts" / "task-guideposts.json"
DEFAULT_MARKDOWN = ROOT / "artifacts" / "task-guideposts.md"
ALLOWED_CLASSES = {"invariant", "safety_boundary", "known_mechanical_behavior"}
ALLOWED_SOURCE_TYPES = {
    "internal_operational_pattern",
    "internal_safety_pattern",
    "repository_invariant",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    guideposts = registry.get("guideposts")
    if not isinstance(guideposts, list) or not guideposts:
        return ["guideposts must be a non-empty list"]
    seen: set[str] = set()
    for index, guidepost in enumerate(guideposts):
        label = guidepost.get("id") or f"guidepost[{index}]"
        if label in seen:
            errors.append(f"{label}: duplicate id")
        seen.add(label)
        if guidepost.get("class") not in ALLOWED_CLASSES:
            errors.append(f"{label}: unsupported class {guidepost.get('class')!r}")
        for field in ("match_terms", "critical_points", "required_checks"):
            value = guidepost.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
                errors.append(f"{label}: {field} must be a non-empty string list")
        source = guidepost.get("source")
        if not isinstance(source, dict):
            errors.append(f"{label}: source is required")
        elif source.get("type") not in ALLOWED_SOURCE_TYPES or not source.get("reference"):
            errors.append(f"{label}: source must use an allowed type and reference")

    cases = registry.get("external_cases")
    if not isinstance(cases, list):
        errors.append("external_cases must be a list")
    else:
        for index, case in enumerate(cases):
            label = case.get("id") or f"external_case[{index}]"
            for field in ("id", "title", "primary_source_url", "verified_on", "supported_claims"):
                if not case.get(field):
                    errors.append(f"{label}: {field} is required")
            if case.get("primary_source_url") and not re.match(r"^https://", case["primary_source_url"]):
                errors.append(f"{label}: primary_source_url must use https")
    return errors


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def contains_term(text: str, term: str) -> bool:
    normalized_term = normalize(term)
    return re.search(rf"(?<!\w){re.escape(normalized_term)}(?!\w)", text) is not None


def scan(task: str, registry: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize(task)
    matches: list[dict[str, Any]] = []
    for guidepost in registry["guideposts"]:
        matched_terms = [term for term in guidepost["match_terms"] if contains_term(normalized, term)]
        if matched_terms:
            matches.append({
                "id": guidepost["id"],
                "class": guidepost["class"],
                "matched_terms": matched_terms,
                "critical_points": guidepost["critical_points"],
                "required_checks": guidepost["required_checks"],
                "source": guidepost["source"],
            })
    return {
        "packet_id": "lumaria-task-guidepost-scan-v0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "matched_guideposts": matches,
        "external_cases": registry["external_cases"],
        "external_case_status": (
            "verified_cases_attached" if registry["external_cases"] else "no_verified_external_cases_attached"
        ),
        "interpretation": (
            "Guideposts are prompts for checks, not proof that a failure applies."
            if matches else
            "No curated guidepost matched; this is not evidence that the task is safe or complete."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Lumaria Task Guidepost Scan",
        "",
        f"Generated: `{packet['generated_at_utc']}`",
        "",
        f"**Task:** {packet['task']}",
        "",
        f"**External cases:** `{packet['external_case_status']}`",
        "",
        packet["interpretation"],
        "",
    ]
    for guidepost in packet["matched_guideposts"]:
        lines.extend([
            f"## {guidepost['id']}",
            "",
            f"Class: `{guidepost['class']}`  ",
            f"Matched: `{', '.join(guidepost['matched_terms'])}`  ",
            f"Source: `{guidepost['source']['reference']}`",
            "",
            "### Critical points",
            "",
        ])
        lines.extend(f"- {point}" for point in guidepost["critical_points"])
        lines.extend(["", "### Required checks", ""])
        lines.extend(f"- `{check}`" for check in guidepost["required_checks"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--task")
    parser.add_argument("--task-file", type=Path)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    registry = load_json(args.registry)
    errors = validate(registry)
    if errors:
        for error in errors:
            print(f"[task-guidepost-scan] ERROR: {error}")
        return 1
    if args.check:
        print(f"[task-guidepost-scan] registry passed: {args.registry}")
        return 0

    if bool(args.task) == bool(args.task_file):
        parser.error("provide exactly one of --task or --task-file")
    task = args.task if args.task is not None else args.task_file.read_text(encoding="utf-8")
    packet = scan(task, registry)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(render_markdown(packet) + "\n", encoding="utf-8")
    print(f"[task-guidepost-scan] matched {len(packet['matched_guideposts'])} guideposts")
    print(f"[task-guidepost-scan] wrote {args.out_json}")
    print(f"[task-guidepost-scan] wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
