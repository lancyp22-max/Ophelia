#!/usr/bin/env python3
"""Generate deterministic preview metadata artifacts for Ophelia UI capture."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def build_payload(width: int, height: int) -> dict:
    return {
        "project": "Ophelia",
        "capture": {
            "width": width,
            "height": height,
            "aspectRatio": round(width / height, 4),
            "timestampUtc": datetime.now(timezone.utc).isoformat(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Ophelia preview metadata.")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--output", default="artifacts/preview.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args.width, args.height)
    rendered = json.dumps(payload, indent=2)

    if args.dry_run:
        print(rendered)
        return 0

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
