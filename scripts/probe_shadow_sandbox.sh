#!/usr/bin/env bash
set -euo pipefail

# Negative capability probe for the candidate Shadow process envelope.
#
# This proves the properties of THIS container launch contract. It does not
# prove that a future live Shadow runner uses this contract. Agent wiring stays
# blocked until the real runner is launched through an equivalent isolated
# principal.

IMAGE="${SHADOW_SANDBOX_IMAGE:-alpine:3.22}"
cid=""

cleanup() {
  if [[ -n "${cid}" ]]; then
    docker rm -f "${cid}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

cid="$(docker create   --network none   --read-only   --cap-drop ALL   --security-opt no-new-privileges:true   --user 65532:65532   --entrypoint sh   "${IMAGE}"   -eu -c '
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

    echo "[shadow-sandbox-probe] in-container negative capability checks passed"
  ')"

network_mode="$(docker inspect -f '{{.HostConfig.NetworkMode}}' "${cid}")"
readonly_root="$(docker inspect -f '{{.HostConfig.ReadonlyRootfs}}' "${cid}")"
user_id="$(docker inspect -f '{{.Config.User}}' "${cid}")"
mounts="$(docker inspect -f '{{json .Mounts}}' "${cid}")"
cap_drop="$(docker inspect -f '{{json .HostConfig.CapDrop}}' "${cid}")"
security_opt="$(docker inspect -f '{{json .HostConfig.SecurityOpt}}' "${cid}")"

[[ "${network_mode}" == "none" ]] || { echo "[shadow-sandbox-probe] ERROR: network mode is ${network_mode}" >&2; exit 1; }
[[ "${readonly_root}" == "true" ]] || { echo "[shadow-sandbox-probe] ERROR: root filesystem is not read-only" >&2; exit 1; }
[[ "${user_id}" == "65532:65532" ]] || { echo "[shadow-sandbox-probe] ERROR: unexpected user ${user_id}" >&2; exit 1; }
[[ "${mounts}" == "[]" ]] || { echo "[shadow-sandbox-probe] ERROR: container has host mounts: ${mounts}" >&2; exit 1; }
[[ "${cap_drop}" == *'"ALL"'* ]] || { echo "[shadow-sandbox-probe] ERROR: ALL capabilities were not dropped" >&2; exit 1; }
[[ "${security_opt}" == *'no-new-privileges:true'* ]] || { echo "[shadow-sandbox-probe] ERROR: no-new-privileges missing" >&2; exit 1; }

docker start -a "${cid}"

echo "[shadow-sandbox-probe] passed infrastructure launch contract"
echo "[shadow-sandbox-probe] NOTE: this does not authorize or activate agent wiring"
