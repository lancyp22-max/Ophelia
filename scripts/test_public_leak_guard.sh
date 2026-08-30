#!/usr/bin/env bash
set -euo pipefail

if ! command -v rg >/dev/null 2>&1; then
  echo "[public-leak-guard-test] ERROR: ripgrep (rg) is required but not installed." >&2
  exit 127
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GUARD="$ROOT_DIR/scripts/public_leak_guard.sh"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

init_case() {
  local name="$1"
  local path="$TMP_DIR/$name"
  mkdir -p "$path"
  git -C "$path" init -q
  git -C "$path" config user.email test@example.invalid
  git -C "$path" config user.name "Leak Guard Test"
  printf '%s\n' '# test fixture' >"$path/README.md"
  git -C "$path" add README.md
  printf '%s' "$path"
}

expect_pass() {
  local path="$1"
  PUBLIC_LEAK_GUARD_ROOT="$path" bash "$GUARD" >/dev/null
}

expect_fail() {
  local path="$1"
  local expected="$2"
  if PUBLIC_LEAK_GUARD_ROOT="$path" bash "$GUARD" >"$path/result.txt" 2>&1; then
    echo "[public-leak-guard-test] expected failure for $path" >&2
    return 1
  fi
  rg -q "$expected" "$path/result.txt"
}

safe="$(init_case safe)"
printf '%s\n' 'OPENAI_API_KEY=${OPENAI_API_KEY}' >"$safe/.env.example"
git -C "$safe" add .env.example
expect_pass "$safe"

google="$(init_case google)"
printf 'const key = "%s%s";\n' 'AIza' '1234567890abcdefghijklmnopqrstuvwxy' >"$google/app.js"
git -C "$google" add app.js
expect_fail "$google" 'GLG-003'

browser="$(init_case browser)"
printf 'VITE_PROVIDER_API_KEY="%s%s"\n' 'browser_visible_' 'credential_value' >"$browser/config.txt"
git -C "$browser" add config.txt
expect_fail "$browser" 'GLG-005'

private_file="$(init_case private-file)"
printf '%s\n' 'placeholder' >"$private_file/.env"
git -C "$private_file" add -f .env
expect_fail "$private_file" 'GLG-002'

echo "[public-leak-guard-test] all cases passed"
