#!/usr/bin/env bash
set -euo pipefail

# Supported Shadow launcher.
# Every invocation validates the actual container configuration BEFORE start.

if [[ $# -lt 3 || "$2" != "--" ]]; then
  echo "usage: $0 <image> -- <command> [args...]" >&2
  exit 2
fi

IMAGE="$1"
shift 2
cid=""

cleanup() {
  if [[ -n "$cid" ]]; then
    docker rm -f "$cid" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

cid="$(docker create \
  --network none \
  --read-only \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --user 65532:65532 \
  --pids-limit 128 \
  --memory 1024m \
  --cpus 2 \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  "$IMAGE" \
  "$@")"

network_mode="$(docker inspect -f '{{.HostConfig.NetworkMode}}' "$cid")"
readonly_root="$(docker inspect -f '{{.HostConfig.ReadonlyRootfs}}' "$cid")"
user_id="$(docker inspect -f '{{.Config.User}}' "$cid")"
binds="$(docker inspect -f '{{json .HostConfig.Binds}}' "$cid")"
mounts="$(docker inspect -f '{{json .Mounts}}' "$cid")"
cap_drop="$(docker inspect -f '{{json .HostConfig.CapDrop}}' "$cid")"
security_opt="$(docker inspect -f '{{json .HostConfig.SecurityOpt}}' "$cid")"
privileged="$(docker inspect -f '{{.HostConfig.Privileged}}' "$cid")"
env_json="$(docker inspect -f '{{json .Config.Env}}' "$cid")"

[[ "$network_mode" == "none" ]] || { echo "[shadow-launch] ERROR: network mode is $network_mode" >&2; exit 1; }
[[ "$readonly_root" == "true" ]] || { echo "[shadow-launch] ERROR: root filesystem is not read-only" >&2; exit 1; }
[[ "$user_id" == "65532:65532" ]] || { echo "[shadow-launch] ERROR: unexpected user $user_id" >&2; exit 1; }
[[ "$binds" == "null" || "$binds" == "[]" ]] || { echo "[shadow-launch] ERROR: host bind mounts present: $binds" >&2; exit 1; }
[[ "$mounts" == "[]" ]] || { echo "[shadow-launch] ERROR: unexpected mounted host resources: $mounts" >&2; exit 1; }
[[ "$cap_drop" == *'"ALL"'* ]] || { echo "[shadow-launch] ERROR: ALL capabilities were not dropped" >&2; exit 1; }
[[ "$security_opt" == *'no-new-privileges:true'* ]] || { echo "[shadow-launch] ERROR: no-new-privileges missing" >&2; exit 1; }
[[ "$privileged" == "false" ]] || { echo "[shadow-launch] ERROR: privileged container requested" >&2; exit 1; }

if printf '%s' "$env_json" | grep -Eiq '"[^"]*(TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY)[^"]*='; then
  echo "[shadow-launch] ERROR: credential-like environment variable present in image/config" >&2
  exit 1
fi

echo "[shadow-launch] launch contract verified for container $cid"
docker start -a "$cid"
