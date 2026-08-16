#!/usr/bin/env python3
"""Generate Project Espresso local work-observability artifacts."""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / "data" / "context" / "project-espresso-capsule.v0.1.json"
STATE_OUT = ROOT / "artifacts" / "project-espresso-state.json"
BRIEF_OUT = ROOT / "artifacts" / "project-espresso-brief.md"


def run_git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def load_capsule() -> dict[str, Any]:
    with CAPSULE.open(encoding="utf-8") as handle:
        return json.load(handle)


def classify(path: str, module_map: list[dict[str, str]]) -> dict[str, str]:
    for item in module_map:
        if path == item["prefix"] or path.startswith(item["prefix"]):
            return item
    return {"module": "uncategorized", "review_hint": "inspect path and ownership before merging", "prefix": "*"}


def parse_status(raw: str, capsule: dict[str, Any]) -> list[dict[str, str]]:
    rules = {item["status"]: item["focus"] for item in capsule["review_focus_rules"]}
    changes: list[dict[str, str]] = []
    for line in raw.splitlines():
        if not line:
            continue
        status = line[:2].strip() or line[:2]
        path = line[2:].strip() if len(line) > 2 else line.strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        module = classify(path, capsule["module_map"])
        rule_key = "??" if status == "??" else status[:1]
        changes.append(
            {
                "status": status,
                "path": path,
                "module": module["module"],
                "review_hint": module["review_hint"],
                "focus": rules.get(rule_key, "review change scope and relevant checks")
            }
        )
    return changes


def recent_commits(limit: int = 6) -> list[dict[str, str]]:
    raw = run_git(["log", f"-{limit}", "--pretty=format:%h%x09%an%x09%ar%x09%s"])
    commits: list[dict[str, str]] = []
    for line in raw.splitlines():
        parts = line.split("\t", 3)
        if len(parts) == 4:
            commits.append({"hash": parts[0], "author": parts[1], "age": parts[2], "subject": parts[3]})
    return commits


def build_state() -> dict[str, Any]:
    capsule = load_capsule()
    raw_status = run_git(["status", "--porcelain=v1"])
    branch = run_git(["branch", "--show-current"]) or "unknown"
    changes = parse_status(raw_status, capsule)
    modules = sorted({change["module"] for change in changes})
    return {
        "id": "project-espresso-state-v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "branch": branch,
        "working_tree": "clean" if not changes else "dirty",
        "active_changes": changes,
        "active_modules": modules,
        "recent_commits": recent_commits(),
        "safety_gates": capsule["safety_gates"],
        "residual_trace": capsule["residual_trace"]
    }


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def write_outputs(state: dict[str, Any]) -> None:
    STATE_OUT.parent.mkdir(parents=True, exist_ok=True)
    STATE_OUT.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    changes = [f"`{item['status']}` `{item['path']}` — {item['module']}; {item['focus']}" for item in state["active_changes"]]
    commits = [f"`{item['hash']}` {item['subject']} ({item['age']})" for item in state["recent_commits"]]
    modules = [str(item) for item in state["active_modules"]]
    lines = [
        "# Project Espresso Brief",
        "",
        f"Generated: {state['generated_at']}",
        f"Branch: `{state['branch']}`",
        f"Working tree: `{state['working_tree']}`",
        "",
        "## Active modules",
        bullet(modules),
        "",
        "## Active changes",
        bullet(changes),
        "",
        "## Recent commits",
        bullet(commits),
        "",
        "## Safety gates",
        bullet(state["safety_gates"]),
        "",
        "## Residual trace",
        state["residual_trace"],
        ""
    ]
    BRIEF_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch", action="store_true", help="refresh artifacts until interrupted")
    parser.add_argument("--interval", type=float, default=4.0, help="watch refresh interval in seconds")
    args = parser.parse_args()

    while True:
        state = build_state()
        write_outputs(state)
        print(f"[espresso] {state['generated_at']} {state['working_tree']} -> {BRIEF_OUT.relative_to(ROOT)}")
        if not args.watch:
            break
        time.sleep(max(args.interval, 1.0))


if __name__ == "__main__":
    main()
