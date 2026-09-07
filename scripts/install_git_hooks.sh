#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

git config core.hooksPath .githooks
chmod +x .githooks/pre-commit

echo "[hooks] installed: .githooks/pre-commit"
echo "[hooks] git config core.hooksPath=$(git config --get core.hooksPath)"
