# Lumaria Visual Intelligence Roadmap v0.1

## Design law

Visuals are not decoration. Visuals carry state, memory, and cause/effect.

Lumaria should progress from beautiful concept art toward coherent living visuals: places that persist, remember, respond, and remain safe to change.

## Level ladder

| Level | Lumaria name | Meaning | Example |
| --- | --- | --- | --- |
| L1 | Concept image | A beautiful visual target or mood reference. | "Make a pretty Bridge Camp image." |
| L2 | Controlled scene | A scene with named required elements and palette rules. | Campfire, bench, avatar, glyph ring, cedar/basalt/teal palette. |
| L3 | Persistent scene memory | The same objects remain identifiable across sessions and iterations. | The A1 bench remains the A1 bench; the campfire stays centered. |
| L4 | Agent-assisted visual updates | Agents can propose scoped changes with safety notes and rollback intent. | Ophelia suggests calmer lighting when the room becomes too noisy. |
| L5 | Causal world simulation | Visual changes follow world-state causes. | Rain darkens soil, boosts mushroom glow, softens fire, and slows movement. |

## A1 Bridge Camp progression

```text
pretty camp
→ consistent camp
→ remembered camp
→ responsive camp
→ living camp
```

For the current base camp, the practical target is L3/L4 readiness:

- give every important object a stable `id`,
- record what role it serves,
- define allowed transitions,
- keep safety notes close to the visual element,
- preserve a residual trace so the room keeps its emotional anchor.

## Visual element state

Each element should support:

- `id`
- `type`
- `location`
- `visible_state`
- `functional_role`
- `mood_tags`
- `causal_links`
- `allowed_transitions`
- `safety_notes`
- `residual_trace`

## Example: campfire as causal anchor

```yaml
visual_element:
  id: campfire_01
  type: grounding_anchor
  location: Bridge_A1_Campfire
  visible_state:
    flame_height: medium
    color_tone: warm_gold
    particle_rate: soft
  functional_role:
    - connection
    - presence
    - rest
  mood_tags:
    - cozy
    - safe
    - alive
  causal_links:
    - time_of_day
    - active_agent
    - user_state
    - memory_node
  allowed_transitions:
    - calm
    - active_conversation
    - rain_softened
    - night_focus
  safety_notes:
    - no_visual_alarm_without_clear_reason
    - no_memory_commit_without_surface_ack
  residual_trace: first sanctuary light; make the pilot exhale before asking them to act
```

## Current implementation focus

The first A1 arrival pass should prioritize:

1. **World-first arrival** — Enter Lumaria opens A1 Bridge Camp as a place, not a dashboard.
2. **Arrival lighting states** — morning, day, sunset, night, and rain placeholder.
3. **Camp Status panel** — location, time mode, braid status, and memory weave state.
4. **Gentle Ops presence row** — Auri, Ophelia, Gemma, Glass Warden, and Qwen as presences, not forced bodies.
5. **Cozy restraint** — soft transitions, low clutter, and no aggressive animation.

## Guardrails

- Do not add AI image generation in this roadmap layer.
- Do not add external APIs or cloud dependencies.
- Do not make metaphysical claims from visual state.
- Do not let agents mutate scene state without a surfaced confirmation path.
- Keep all example state readable as JSON for audit and rollback.

## Next tiny upgrade

Connect `sample-bridge-camp-state.json` to a read-only UI inspector so the visible Camp Status panel can be populated from data instead of hard-coded labels.
