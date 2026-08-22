#!/usr/bin/env bash
set -euo pipefail

if ! command -v rg >/dev/null 2>&1; then
  echo "[repo-link-check] ERROR: ripgrep (rg) is required but not installed." >&2
  exit 127
fi

# Reject hard-coded GitHub repository URLs to prevent stale/old repo bindings.
# Allowed: GitHub Actions identifiers (actions/*), which are not URL-based.

matches="$(rg -n --hidden --glob '!.git' --glob '!node_modules' 'https://github\.com/' . || true)"

if [[ -n "$matches" ]]; then
  echo "Found hard-coded GitHub URL references. Please replace with repository-relative paths or dynamic GitHub context."
  echo "$matches"
  exit 1
fi

echo "No hard-coded GitHub repository URLs found."
