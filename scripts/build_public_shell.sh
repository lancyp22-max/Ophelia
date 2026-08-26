#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/artifacts/public-shell"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/docs" "$OUT_DIR/policies" "$OUT_DIR/scripts" "$OUT_DIR/data/canon-receipts" "$OUT_DIR/data/reasoning-loops" "$OUT_DIR/data/visual-state" "$OUT_DIR/data/context" "$OUT_DIR/data/decision-boundaries" "$OUT_DIR/data/focus" "$OUT_DIR/data/handshakes" "$OUT_DIR/data/kernel" "$OUT_DIR/data/scene-actions" "$OUT_DIR/data/semantic-packets"

copy_if_exists() {
  local src="$1"
  local dst="$2"
  if [ -e "$src" ]; then
    cp -R "$src" "$dst"
  fi
}

copy_if_exists "$ROOT_DIR/index.html" "$OUT_DIR/"
copy_if_exists "$ROOT_DIR/script.js" "$OUT_DIR/"
copy_if_exists "$ROOT_DIR/sw.js" "$OUT_DIR/"
copy_if_exists "$ROOT_DIR/manifest.json" "$OUT_DIR/"
copy_if_exists "$ROOT_DIR/.nojekyll" "$OUT_DIR/"
copy_if_exists "$ROOT_DIR/README.md" "$OUT_DIR/"
copy_if_exists "$ROOT_DIR/lumaria_qc_memory_v0.1.yaml" "$OUT_DIR/"
copy_if_exists "$ROOT_DIR/lumaria_memory_palace_v0.1.json" "$OUT_DIR/"
copy_if_exists "$ROOT_DIR/data/reasoning-loops/sample-review-loop.json" "$OUT_DIR/data/reasoning-loops/"
copy_if_exists "$ROOT_DIR/data/canon-receipts/canon-receipt.v1.schema.json" "$OUT_DIR/data/canon-receipts/"
copy_if_exists "$ROOT_DIR/data/canon-receipts/sample-held-receipt.v1.json" "$OUT_DIR/data/canon-receipts/"
copy_if_exists "$ROOT_DIR/data/visual-state/sample-scene.json" "$OUT_DIR/data/visual-state/"
copy_if_exists "$ROOT_DIR/data/visual-state/sample-avatar-state.json" "$OUT_DIR/data/visual-state/"
copy_if_exists "$ROOT_DIR/data/visual-state/visual-elements.schema.json" "$OUT_DIR/data/visual-state/"
copy_if_exists "$ROOT_DIR/data/visual-state/sample-bridge-camp-state.json" "$OUT_DIR/data/visual-state/"
copy_if_exists "$ROOT_DIR/data/visual-state/a1-visual-reward-model.json" "$OUT_DIR/data/visual-state/"
copy_if_exists "$ROOT_DIR/data/context/ophelia-context-capsule.v0.1.json" "$OUT_DIR/data/context/"
copy_if_exists "$ROOT_DIR/data/decision-boundaries/lumaria-decision-register.v0.1.json" "$OUT_DIR/data/decision-boundaries/"
copy_if_exists "$ROOT_DIR/data/focus/radiant-crown-focus.v0.1.yaml" "$OUT_DIR/data/focus/"
copy_if_exists "$ROOT_DIR/data/focus/wormhole-mirror-experiment.v0.1.yaml" "$OUT_DIR/data/focus/"
copy_if_exists "$ROOT_DIR/data/focus/wellspring-current-logic.v0.1.yaml" "$OUT_DIR/data/focus/"
copy_if_exists "$ROOT_DIR/data/handshakes/mirror-x-handshake.v0.2.0.yaml" "$OUT_DIR/data/handshakes/"
copy_if_exists "$ROOT_DIR/data/kernel/lumaria-core-invariants.v1.yaml" "$OUT_DIR/data/kernel/"
copy_if_exists "$ROOT_DIR/data/kernel/lumaria-lifecycle.v1.yaml" "$OUT_DIR/data/kernel/"
copy_if_exists "$ROOT_DIR/data/kernel/lumaria-canonization.v1.yaml" "$OUT_DIR/data/kernel/"
copy_if_exists "$ROOT_DIR/data/scene-actions/scene-action-bus.v0.1.schema.json" "$OUT_DIR/data/scene-actions/"
copy_if_exists "$ROOT_DIR/data/scene-actions/sample-lantern-proposal.v0.1.json" "$OUT_DIR/data/scene-actions/"
copy_if_exists "$ROOT_DIR/data/semantic-packets/lumaria-semantic-codebook.v0.1.json" "$OUT_DIR/data/semantic-packets/"
copy_if_exists "$ROOT_DIR/data/semantic-packets/sample-state-delta.v0.1.json" "$OUT_DIR/data/semantic-packets/"
copy_if_exists "$ROOT_DIR/data/semantic-packets/sample-state-packet.v0.1.json" "$OUT_DIR/data/semantic-packets/"
copy_if_exists "$ROOT_DIR/docs/split-architecture.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/lumaria-qc-memory-v0.1.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/reasoning-loop-controller.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/visual-semantic-state.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/visual-intelligence-roadmap.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/visual-rl-harness.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/ue5-lumaria-world-roadmap.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/ue5-lumaria-implementation-playbook.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/token-context-workflow.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/world-model-worldbuilding-tools.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/intentional-undefined.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/scene-action-bus.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/wormhole-mirror-experiment.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/wellspring-current-logic.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/mirror-x-handshake.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/threat-model-v1.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/kernel-map.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/surfaced-canonization.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/semantic-packet-experiment.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/canon-receipts-and-audit-windows.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/scripts/world_model_packet.py" "$OUT_DIR/scripts/"
copy_if_exists "$ROOT_DIR/scripts/check_world_module.py" "$OUT_DIR/scripts/"
copy_if_exists "$ROOT_DIR/scripts/check_decision_boundaries.py" "$OUT_DIR/scripts/"
copy_if_exists "$ROOT_DIR/scripts/check_scene_action_bus.py" "$OUT_DIR/scripts/"
copy_if_exists "$ROOT_DIR/scripts/semantic_packet.py" "$OUT_DIR/scripts/"
copy_if_exists "$ROOT_DIR/scripts/check_canon_receipt.py" "$OUT_DIR/scripts/"
copy_if_exists "$ROOT_DIR/scripts/repo_audit_window.py" "$OUT_DIR/scripts/"
copy_if_exists "$ROOT_DIR/policies/public-exposure-guardrails.v0.1.yaml" "$OUT_DIR/policies/"
copy_if_exists "$ROOT_DIR/policies/public-publish-allowlist.v0.1.yaml" "$OUT_DIR/policies/"
copy_if_exists "$ROOT_DIR/scripts/public_leak_guard.sh" "$OUT_DIR/scripts/"
copy_if_exists "$ROOT_DIR/scripts/verify_repo_links.sh" "$OUT_DIR/scripts/"
copy_if_exists "$ROOT_DIR/demos/mirror10-flora-phase-shift.html" "$OUT_DIR/"
copy_if_exists "$ROOT_DIR/demos/world-bridge-map.html" "$OUT_DIR/"
copy_if_exists "$ROOT_DIR/demos/world-3d-blockout.html" "$OUT_DIR/"

cat > "$OUT_DIR/PUBLIC_SHELL_PROFILE.txt" <<'EOF'
Profile: world-shaped interface experiment
Mode: public shell, sealed core
Scope: curated outer layer only
EOF

echo "[public-shell] built at: $OUT_DIR"
