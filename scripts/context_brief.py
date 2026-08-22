#!/usr/bin/env python3
"""Generate a compact Ophelia handoff brief for low-token coding sessions."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / "data" / "context" / "ophelia-context-capsule.v0.1.json"
SCENE = ROOT / "data" / "visual-state" / "sample-scene.json"
BRIDGE = ROOT / "data" / "visual-state" / "sample-bridge-camp-state.json"
OUT = ROOT / "artifacts" / "context-brief.md"


def run_git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return "unavailable"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def bullet(items: list[str], limit: int | None = None) -> str:
    selected = items[:limit] if limit else items
    return "\n".join(f"- {item}" for item in selected)


def main() -> None:
    capsule = load_json(CAPSULE)
    scene = load_json(SCENE) if SCENE.exists() else {}
    bridge = load_json(BRIDGE) if BRIDGE.exists() else {}

    commit = run_git(["log", "-1", "--oneline"])
    branch = run_git(["branch", "--show-current"])
    status = run_git(["status", "--short"])
    status = status if status else "clean"

    visible = scene.get("visible_elements", [])
    tags = scene.get("functional_tags", [])
    bridge_elements = bridge.get("visual_elements", [])
    latest_bridge_note = ""
    if bridge_elements:
        latest_bridge_note = bridge_elements[-2].get("residual_trace", "") if len(bridge_elements) > 1 else bridge_elements[-1].get("residual_trace", "")

    lines = [
        "# Ophelia Compact Context Brief",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"Branch: `{branch}`",
        f"Latest commit: `{commit}`",
        f"Working tree: `{status}`",
        "",
        "## Use this instead of replaying the whole chat",
        capsule["paste_rule"],
        "",
        "## Current focus",
        f"- Project: {capsule['project']['name']}",
        f"- Frontend focus: {capsule['project']['current_frontend_focus']}",
        f"- Entry flow: {capsule['project']['entry_flow']}",
        f"- Visual wave: {capsule['project']['current_visual_wave']}",
        "",
        "## Active files",
        bullet([f"`{item['path']}` — {item['role']}" for item in capsule["active_surfaces"]]),
        "",
        "## A1 scene state snapshot",
        f"- Mood: {scene.get('mood', 'unknown')}",
        f"- Key visible elements: {', '.join(visible[-10:]) if visible else 'unknown'}",
        f"- Key tags: {', '.join(tags[-8:]) if tags else 'unknown'}",
        f"- Latest visual note: {latest_bridge_note or scene.get('residual_trace', 'unknown')}",
        "",
        "## Rules to preserve",
        bullet(capsule["architecture_rules"]),
        "",
        "## Do not do",
        bullet(capsule["do_not_do"]),
        "",
        "## Standard checks",
        bullet([f"`{cmd}`" for cmd in capsule["standard_checks"]]),
        "",
        "## Next prompt template",
        f"> {capsule['next_prompt_template']}",
        "",
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[context-brief] wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
