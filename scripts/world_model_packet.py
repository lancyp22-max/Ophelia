#!/usr/bin/env python3
"""Generate a lightweight world-model planning packet for Lumaria world-building.

The packet turns the existing visual-state files into a compact loop:
observe -> propose actions -> predict outcomes -> define validation checks.
It is deliberately dependency-free and does not call external services.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENE = ROOT / "data" / "visual-state" / "sample-scene.json"
DEFAULT_BRIDGE = ROOT / "data" / "visual-state" / "sample-bridge-camp-state.json"
DEFAULT_CONTEXT = ROOT / "data" / "context" / "ophelia-context-capsule.v0.1.json"
DEFAULT_OUT_JSON = ROOT / "artifacts" / "world-model-packet.json"
DEFAULT_OUT_MD = ROOT / "artifacts" / "world-model-packet.md"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def take(items: list[Any], limit: int) -> list[Any]:
    return items[:limit] if len(items) > limit else items


def build_packet(scene: dict[str, Any], bridge: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    visible = scene.get("visible_elements", [])
    tags = scene.get("functional_tags", [])
    bridge_elements = bridge.get("visual_elements") or bridge.get("elements") or []
    safe_next_work: list[str] = []
    for surface in context.get("active_surfaces", []):
        if surface.get("path") == "demos/world-3d-blockout.html":
            safe_next_work = surface.get("safe_next_work", [])
            break

    action_knobs = [
        {
            "name": "time_mode",
            "values": ["morning", "day", "sunset", "night", "rain"],
            "expected_effect": "Changes sky/fog, camp glow, market glow, rain readability, and luminous ground response.",
        },
        {
            "name": "camera_focus",
            "values": ["reset_bridge_view", "market_focus", "ground_texture_view"],
            "expected_effect": "Validates that world details remain readable without dropping the camera underground.",
        },
        {
            "name": "market_glow_intensity",
            "values": ["day_low", "sunset_warm", "night_high", "rain_readable"],
            "expected_effect": "Keeps market runes, lanterns, and offering details synchronized through one global control.",
        },
        {
            "name": "detail_density",
            "values": ["campfire_ring", "market_entry", "overhang", "backdrop"],
            "expected_effect": "Adds cozy visual evidence in small pockets without turning the scene into noise.",
        },
    ]

    predictions = [
        {
            "if_action": "Switch to rain mode from the embedded weather panel.",
            "then_expect": "Rain particles/mist appear while luminous ground and market glow preserve scene readability.",
            "check": "The iframe receives a lumaria-time-mode message and the camp status mode updates to Rain.",
        },
        {
            "if_action": "Focus the market and inspect from ground height.",
            "then_expect": "Woven runner, canopy underside, offerings, and lanterns remain visible under the overhang.",
            "check": "No black-screen regressions, no underground camera clipping, and no stale cached iframe build.",
        },
        {
            "if_action": "Add another district detail pass.",
            "then_expect": "The new object group appears in visual-state JSON with an explicit cause/effect tag.",
            "check": "Run JSON validation, JS syntax check, public-shell audit, and update the context capsule only if useful.",
        },
    ]

    evaluation_axes = [
        "geometry_readability",
        "causal_state_clarity",
        "camera_safety",
        "weather_resilience",
        "cozy_density_without_noise",
        "public_shell_safety",
        "ue5_importability",
    ]

    return {
        "packet_id": "lumaria-world-model-packet-v0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Use visual-state as a small world model: observe current state, choose safe actions, predict visible outcomes, and define validation checks before the next scene pass.",
        "observation_state": {
            "scene_id": scene.get("scene_id"),
            "location": scene.get("location"),
            "mood": scene.get("mood"),
            "visible_element_sample": take(visible, 24),
            "functional_tag_sample": take(tags, 24),
            "latest_visual_pass": scene.get("latest_visual_pass"),
            "bridge_element_count": len(bridge_elements),
            "current_visual_wave": context.get("project", {}).get("current_visual_wave"),
        },
        "action_knobs": action_knobs,
        "safe_next_work": take(safe_next_work, 18),
        "predictions": predictions,
        "evaluation_axes": evaluation_axes,
        "standard_checks": context.get("standard_checks", []),
        "guardrails": context.get("do_not_do", []),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Lumaria World Model Packet",
        "",
        f"Generated: `{packet['generated_at_utc']}`",
        "",
        packet["purpose"],
        "",
        "## Observation state",
        "",
        f"- Scene: `{packet['observation_state'].get('scene_id')}`",
        f"- Location: {packet['observation_state'].get('location')}",
        f"- Mood: {packet['observation_state'].get('mood')}",
        f"- Latest pass: {packet['observation_state'].get('latest_visual_pass')}",
        "",
        "## Action knobs",
        "",
    ]
    for knob in packet["action_knobs"]:
        lines.append(f"- **{knob['name']}**: {', '.join(knob['values'])} — {knob['expected_effect']}")
    lines.extend(["", "## Predictions to test", ""])
    for prediction in packet["predictions"]:
        lines.append(f"- If: {prediction['if_action']}")
        lines.append(f"  - Expect: {prediction['then_expect']}")
        lines.append(f"  - Check: {prediction['check']}")
    lines.extend(["", "## Evaluation axes", ""])
    for axis in packet["evaluation_axes"]:
        lines.append(f"- {axis}")
    lines.extend(["", "## Standard checks", ""])
    for check in packet.get("standard_checks", []):
        lines.append(f"- `{check}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Lumaria world-model planning packet.")
    parser.add_argument("--scene", type=Path, default=DEFAULT_SCENE)
    parser.add_argument("--bridge", type=Path, default=DEFAULT_BRIDGE)
    parser.add_argument("--context", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = parser.parse_args()

    packet = build_packet(load_json(args.scene), load_json(args.bridge), load_json(args.context))
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(render_markdown(packet), encoding="utf-8")
    print(f"[world-model-packet] wrote {args.out_json}")
    print(f"[world-model-packet] wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
