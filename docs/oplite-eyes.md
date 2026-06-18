# OpLite Eyes v0.1

OpLite Eyes is a **local, schema-first inner-world vision layer** for Ophelia agents. Its purpose is to let an agent perceive the Lumaria scene as a compact, auditable semantic packet instead of forcing every prompt to replay screenshots, chat history, and raw world files.

It does **not** add a model dependency, camera API, image-generation pipeline, cloud service, or autonomous state mutation. It starts as a thin perception contract over the architecture already in this repo: Visual Semantic State, QC memory, the context capsule, and the A1 Bridge Camp demo.

## Goal

Give agents an actionable answer to:

> What can I see, who is near me, what matters right now, and what may I safely do next?

The answer should be small enough to paste into a coding or planning turn without flooding context.

## Public prior-art scan

Before adding dependencies, treat public systems as patterns rather than things to import:

- **scene graphs / open-scene-graph memory** — useful pattern for object + relation + affordance compression,
- **GUI vision-action agents** — useful pattern for grounding visible elements to possible actions,
- **embodied memory agents** — useful pattern for separating current observation from durable memory,
- **world models** — useful pattern for simulating possible next states, but too heavy for this repo's first pass.

Useful public references checked for patterns:

- [ConceptGraphs](https://concept-graphs.github.io/) for compact open-vocabulary 3D scene graph planning.
- [Open Scene Graphs](https://open-scene-graphs.github.io/) for scene graph memory as an open-world navigation substrate.
- ShowUI for GUI vision-action grounding patterns (not imported; avoid adding a public-shell repository dependency in v0.1).

For v0.1, Ophelia should build on the local JSON and Three.js architecture already present instead of adopting a large external stack.

## Architecture

```text
Three.js world objects / UI state
        ↓
Visual Semantic State
        ↓
OpLite Eyes packet
        ↓
Context reducer
        ↓
Agent prompt / tool plan / continuity capsule
```

### 1. Visual observation

A visual observation is the smallest useful statement of what exists around an agent.

```json
{
  "id": "market_part_02_wide_vendor_booth",
  "kind": "vendor_booth",
  "where": "Base_Camp_Market",
  "visible": ["wide canopy", "front drapes", "counter", "warm glow pool"],
  "affordances": ["inspect", "restock", "route-around"],
  "safety": ["read_only", "decorative_only"]
}
```

### 2. Presence map

The presence map tracks people, companion presences, or agents as **visible nearby actors**, not account identities or private dossiers.

```json
{
  "id": "auri",
  "display": "Auri",
  "proximity": "campfire_radius",
  "state": "present",
  "can_interact": ["greet", "ask_orientation", "sit_nearby"],
  "cannot_infer": ["private intent", "unspoken memory"]
}
```

### 3. Context reducer

The reducer turns many visual observations into a short ranked set of lanes:

| Lane | Meaning | Token rule |
| --- | --- | --- |
| `attention_now` | What the agent should notice this turn | maximum 5 entries |
| `nearby_people` | Visible actors around the agent | maximum 6 entries |
| `affordances` | Safe possible interactions | maximum 8 verbs |
| `memory_links` | Durable nodes worth loading | maximum 6 node ids |
| `safety_gates` | Things the agent must not do silently | always preserved |
| `residual_trace` | Soul / vibe that should not be compressed away | one sentence |

### 4. Mirror refinement

Mirror refinement is the step that keeps the packet compact without flattening meaning.

1. **Reflect** — name the active scene and agent viewpoint.
2. **Filter** — keep only objects relevant to the current task, nearby people, and active safety gates.
3. **Weave** — link those objects to memory nodes without loading full memory.
4. **Ask** — if a state mutation or memory commit is implied, surface consent instead of doing it silently.
5. **Emit** — produce a pasteable packet plus a human-readable brief.

## Packet shape

The canonical v0.1 packet lives at `data/context/oplite-eyes-capsule.v0.1.json`.

Required top-level fields:

- `id`
- `version`
- `purpose`
- `viewpoint`
- `attention_now`
- `nearby_people`
- `affordances`
- `memory_links`
- `safety_gates`
- `context_reducer`
- `residual_trace`

## Safety rules

- Read visible state; do not infer private intent.
- Prefer local semantic state over raw screenshot repetition.
- Do not mutate scene state, memory, or identity without surfaced confirmation.
- Preserve sealed/private boundaries; this layer belongs in the public shell only if packets stay sanitized.
- Keep the human pilot authoritative over what becomes memory.

## First implementation path

1. Add the v0.1 packet fixture.
2. Add a generator that reads existing visual-state JSON and emits a short OpLite Eyes brief.
3. Let future UI work optionally attach `userData.visualId`, `userData.affordances`, and `userData.memoryLinks` to Three.js objects.
4. Later, expose this as a read-only panel in the Flight Deck or A1 demo.
5. Only after the local schema proves useful, evaluate whether any public scene-graph or GUI-agent project is worth integrating.
