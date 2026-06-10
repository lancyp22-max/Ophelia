#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHELL_DIR="$ROOT_DIR/artifacts/public-shell"

if [ ! -d "$SHELL_DIR" ]; then
  echo "[public-shell-audit] ❌ missing bundle: $SHELL_DIR"
  echo "[public-shell-audit] build first: bash scripts/build_public_shell.sh"
  exit 1
fi

echo "[public-shell-audit] scanning curated public shell..."

runtime_scope=(
  "$SHELL_DIR/index.html"
  "$SHELL_DIR/script.js"
  "$SHELL_DIR/manifest.json"
  "$SHELL_DIR/sw.js"
)

deny_pattern='(backups/|library/|src/main/java|/\.env|\.kdbx)'
if rg -n -i -e "$deny_pattern" "${runtime_scope[@]}" >/tmp/public_shell_audit_hits.txt; then
  echo "[public-shell-audit] ❌ blocked: sealed/internal references found in public shell."
  cat /tmp/public_shell_audit_hits.txt
  exit 1
fi

if find "$SHELL_DIR" -type f | rg -n '\.map$' >/tmp/public_shell_sourcemap_hits.txt; then
  echo "[public-shell-audit] ❌ blocked: sourcemap found in public shell."
  cat /tmp/public_shell_sourcemap_hits.txt
  exit 1
fi

echo "[public-shell-audit] ✅ passed"
