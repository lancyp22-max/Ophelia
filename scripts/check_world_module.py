#!/usr/bin/env python3
"""Extract and syntax-check the inline Three.js module used by the world demo."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORLD = ROOT / "demos" / "world-3d-blockout.html"
MODULE_OPEN = '<script type="module">'
MODULE_CLOSE = "</script>"


def extract_module(document: str) -> str:
    start = document.find(MODULE_OPEN)
    if start < 0:
        raise ValueError("world document does not contain a module script")
    start += len(MODULE_OPEN)
    end = document.find(MODULE_CLOSE, start)
    if end < 0:
        raise ValueError("world module script is not closed")
    module = document[start:end].strip()
    if not module:
        raise ValueError("world module script is empty")
    return module + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("world", nargs="?", type=Path, default=DEFAULT_WORLD)
    args = parser.parse_args()

    module = extract_module(args.world.read_text(encoding="utf-8"))
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8") as handle:
        handle.write(module)
        handle.flush()
        subprocess.run(["node", "--check", handle.name], check=True)

    print(f"[world-module-check] passed: {args.world}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
