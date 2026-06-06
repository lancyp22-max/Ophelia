#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[public-leak-guard] scanning tracked files for high-risk exposure patterns..."

tracked_files="$(git ls-files)"
ignore_file=".public-leak-guard-ignore"

if [ -z "$tracked_files" ]; then
  echo "[public-leak-guard] no tracked files found."
  exit 0
fi

apply_ignore_filter() {
  local input_file="$1"
  if [ -f "$ignore_file" ]; then
    rg -n -v -f "$ignore_file" "$input_file" || true
  else
    cat "$input_file"
  fi
}

fail_with_reason() {
  local severity="$1"
  local code="$2"
  local message="$3"
  local hit_file="${4:-}"
  echo "[public-leak-guard] ❌ ${severity} :: ${code} :: ${message}"
  if [ -n "$hit_file" ] && [ -f "$hit_file" ]; then
    apply_ignore_filter "$hit_file"
  fi
  exit 1
}

# 1) Block sourcemaps/debug payloads from public repo payloads.
if echo "$tracked_files" | rg -n '\.map$' >/dev/null; then
  echo "$tracked_files" | rg -n '\.map$' >/tmp/public_leak_guard_sourcemap_hits.txt || true
  fail_with_reason "critical" "GLG-001" "tracked sourcemap files (*.map) detected" /tmp/public_leak_guard_sourcemap_hits.txt
fi

# 1b) Block known private material extensions from being tracked.
if echo "$tracked_files" | rg -n '(^|/)(\.env(\..*)?|.*\.(pem|p12|pfx|key|kdbx))$' >/tmp/public_leak_guard_private_files.txt; then
  fail_with_reason "critical" "GLG-002" "tracked private material file type detected" /tmp/public_leak_guard_private_files.txt
fi

# 2) Block obvious private key / token leaks.
secret_regex='(BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36,}|xox[baprs]-[A-Za-z0-9-]{20,}|AIza[0-9A-Za-z\\-_]{35})'
if rg -n --hidden --glob '!target/**' --glob '!.git/**' -e "$secret_regex" >/tmp/public_leak_guard_hits.txt; then
  fail_with_reason "critical" "GLG-003" "possible secret/token material detected" /tmp/public_leak_guard_hits.txt
fi

# 3) Block direct mention of unreleased/internal secret artifacts in public docs/policies.
meta_regex='(internal only|do not publish|confidential key|secret prompt|unreleased model)'
if rg -n --glob 'README.md' --glob 'docs/**' --glob 'policies/**' -i -e "$meta_regex" >/tmp/public_leak_guard_meta_hits.txt; then
  fail_with_reason "protected" "GLG-004" "sensitive publication marker found in docs/policies" /tmp/public_leak_guard_meta_hits.txt
fi

echo "[public-leak-guard] ✅ passed"
