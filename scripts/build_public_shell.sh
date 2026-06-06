#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/artifacts/public-shell"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/docs" "$OUT_DIR/policies" "$OUT_DIR/scripts" "$OUT_DIR/data/reasoning-loops" "$OUT_DIR/data/visual-state"

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
copy_if_exists "$ROOT_DIR/data/visual-state/sample-scene.json" "$OUT_DIR/data/visual-state/"
copy_if_exists "$ROOT_DIR/data/visual-state/sample-avatar-state.json" "$OUT_DIR/data/visual-state/"
copy_if_exists "$ROOT_DIR/data/visual-state/visual-elements.schema.json" "$OUT_DIR/data/visual-state/"
copy_if_exists "$ROOT_DIR/data/visual-state/sample-bridge-camp-state.json" "$OUT_DIR/data/visual-state/"
copy_if_exists "$ROOT_DIR/data/visual-state/a1-visual-reward-model.json" "$OUT_DIR/data/visual-state/"
copy_if_exists "$ROOT_DIR/docs/split-architecture.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/lumaria-qc-memory-v0.1.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/reasoning-loop-controller.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/visual-semantic-state.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/visual-intelligence-roadmap.md" "$OUT_DIR/docs/"
copy_if_exists "$ROOT_DIR/docs/visual-rl-harness.md" "$OUT_DIR/docs/"
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
