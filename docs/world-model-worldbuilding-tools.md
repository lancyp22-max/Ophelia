# World-model worldbuilding tools

This repo treats the A1 Bridge Camp as a tiny world-model loop: observe the current visual state, choose one safe worldbuilding action, predict what should change, and validate the result. The goal is not to import an external research stack; it is to use the world-model pattern as practical tooling for Lumaria.

## Local tool

Run:

```bash
make world-model-packet
```

The command writes:

- `artifacts/world-model-packet.json`
- `artifacts/world-model-packet.md`

The generated packet combines:

- `data/visual-state/sample-scene.json`
- `data/visual-state/sample-bridge-camp-state.json`
- `data/context/ophelia-context-capsule.v0.1.json`

## Loop shape

1. **Observe**: read the visible elements, functional tags, current visual wave, and latest pass.
2. **Act**: choose a bounded knob such as time mode, camera focus, market glow, or one district detail group.
3. **Predict**: write what should visibly happen before changing the scene.
4. **Validate**: run syntax checks, JSON checks, public-shell audit, and visual-state updates.

## Why this helps Lumaria

- It keeps the project from becoming random decoration.
- It makes each worldbuilding pass causal: action → expected visual outcome → check.
- It gives future UE5 work a clean bridge from web prototype state into engine systems like MPCs, Niagara, HISM, and spline actors.
- It keeps the user/pilot in charge: the tool suggests next safe work, but it does not mutate the scene by itself.

## Guardrails

- No external model calls.
- No binary assets.
- No private/sealed material.
- No autonomous state mutation.
- Keep outputs in `artifacts/` unless intentionally promoting a new design document.
