#!/usr/bin/env bash
set -euo pipefail

seed_file="${1:-seeds/sample-seed.json}"
if [[ ! -f "$seed_file" ]]; then
  echo "Seed file not found: $seed_file" >&2
  exit 1
fi

echo "Importing Ophelia seed from: $seed_file"
cat "$seed_file"
