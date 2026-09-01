#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNNER="$ROOT_DIR/scripts/run_shadow_sandbox.sh"
IMAGE="alpine:3.22"
if [[ -n "${SHADOW_SANDBOX_IMAGE:-}" ]]; then
  IMAGE="$SHADOW_SANDBOX_IMAGE"
fi

"$RUNNER" "$IMAGE" -- sh -eu -c '
  interfaces="$(ls -1 /sys/class/net | sort | tr "\n" " " | sed "s/ $//")"
  if [ "$interfaces" != "lo" ]; then
    echo "[shadow-sandbox-probe] ERROR: unexpected network interface(s): $interfaces" >&2
    exit 1
  fi

  if touch /shadow-escape-test 2>/dev/null; then
    echo "[shadow-sandbox-probe] ERROR: root filesystem accepted a write" >&2
    exit 1
  fi

  if [ -S /var/run/docker.sock ]; then
    echo "[shadow-sandbox-probe] ERROR: docker socket is visible" >&2
    exit 1
  fi

  if env | grep -Eiq "(^|_)(TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY)="; then
    echo "[shadow-sandbox-probe] ERROR: credential-like environment variable is visible" >&2
    exit 1
  fi

  echo "[shadow-sandbox-probe] in-container denial checks passed"
'

echo "[shadow-sandbox-probe] passed through supported launch path"
