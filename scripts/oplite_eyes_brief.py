#!/usr/bin/env python3
"""Generate a compact OpLite Eyes inner-world vision brief."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / "data" / "context" / "oplite-eyes-capsule.v0.1.json"
SCENE = ROOT / "data" / "visual-state" / "sample-scene.json"
BRIDGE = ROOT / "data" / "visual-state" / "sample-bridge-camp-state.json"
OUT = ROOT / "artifacts" / "oplite-eyes-brief.md"


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def bullet(items: list[str], limit: int | None = None) -> str:
    selected = items[:limit] if limit else items
    return "\n".join(f"- {item}" for item in selected)


def visible_summary(scene: dict[str, Any], limit: int = 8) -> str:
    elements = scene.get("visible_elements", [])
    if not elements:
        return "- unknown"
    return bullet([str(item) for item in elements[-limit:]])


def bridge_attention(bridge: dict[str, Any], limit: int = 4) -> list[str]:
    rows: list[str] = []
    for element in bridge.get("visual_elements", [])[-limit:]:
        roles = ", ".join(element.get("functional_role", [])[:3])
        rows.append(f"{element.get('id', 'unknown')} — {element.get('location', 'unknown')} ({roles or 'visual state'})")
    return rows


def main() -> None:
    capsule = load_json(CAPSULE)
    scene = load_json(SCENE)
    bridge = load_json(BRIDGE)
    reducer = capsule["context_reducer"]

    attention = [f"{item['id']} — {item['why_it_matters']}" for item in capsule["attention_now"][: reducer["attention_now_limit"]]]
    people = [f"{person['display']} ({person['proximity']}) — {', '.join(person['safe_interactions'])}" for person in capsule["nearby_people"][: reducer["nearby_people_limit"]]]

    lines = [
        "# OpLite Eyes Brief",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"Viewpoint: `{capsule['viewpoint']['agent']}` at `{capsule['viewpoint']['location']}` focusing `{capsule['viewpoint']['focus']}`",
        "",
        "## Attention now",
        bullet(attention),
        "",
        "## Nearby people / presences",
        bullet(people),
        "",
        "## Safe affordances",
        bullet(capsule["affordances"], reducer["affordance_limit"]),
        "",
        "## Memory links to load by id only",
        bullet(capsule["memory_links"], reducer["memory_link_limit"]),
        "",
        "## Current scene tail",
        visible_summary(scene),
        "",
        "## Bridge semantic attention tail",
        bullet(bridge_attention(bridge)),
        "",
        "## Safety gates",
        bullet(capsule["safety_gates"]),
        "",
        "## Residual trace",
        capsule["residual_trace"],
        "",
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[oplite-eyes] wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
