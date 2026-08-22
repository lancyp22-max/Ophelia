#!/usr/bin/env python3
"""Keep Ophelia workflows on Node 24-compatible official action releases."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = [
    ROOT / ".github" / "workflows" / "ci-build-push.yml",
    ROOT / ".github" / "workflows" / "pages.yml",
    ROOT / "ci-build-push.yml",
]
MINIMUM_MAJOR = {
    "actions/checkout": 7,
    "actions/setup-node": 7,
    "actions/setup-java": 5,
    "actions/configure-pages": 6,
    "actions/upload-pages-artifact": 5,
    "actions/deploy-pages": 5,
}
ACTION_PATTERN = re.compile(r"uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@v(\d+)\b")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" not in text:
        errors.append(f"{path}: missing explicit Node 24 action runtime environment")
    if re.search(r"node-version:\s*['\"]?20(?:['\"]|\s|$)", text):
        errors.append(f"{path}: Node 20 toolchain is not allowed")
    if "setup-node" in text and not re.search(r"node-version:\s*['\"]?24(?:['\"]|\s|$)", text):
        errors.append(f"{path}: setup-node workflow must select Node 24")
    if "setup-node" in text and "apt-get install -y ripgrep" not in text:
        errors.append(f"{path}: validation workflow must install ripgrep")

    for action, major_text in ACTION_PATTERN.findall(text):
        minimum = MINIMUM_MAJOR.get(action)
        if minimum is not None and int(major_text) < minimum:
            errors.append(f"{path}: {action}@v{major_text} must be v{minimum} or newer")
    return errors


def main() -> int:
    errors: list[str] = []
    for workflow in WORKFLOWS:
        if not workflow.is_file():
            errors.append(f"missing workflow: {workflow}")
            continue
        errors.extend(validate(workflow))
    if errors:
        for error in errors:
            print(f"[actions-runtime-check] ERROR: {error}")
        return 1
    print("[actions-runtime-check] passed: workflows use Node 24-compatible action/toolchain versions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
