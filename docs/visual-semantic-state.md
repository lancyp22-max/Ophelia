# Lumaria Visual Semantic State v0.1

Visual Semantic State is a lightweight schema layer for treating Lumaria visuals as memory-bearing state rather than decorative pixels.

This is inspired by Visual Generation Tuning (VGT), but it does **not** add VGT as a dependency, train models, generate images, or call external APIs.

## Design law

Lumaria should remember what an image means, not only what it looks like.

A screenshot, room, glyph, avatar, or concept panel should compress into semantic structure:

- where it is,
- what is visible,
- what mood it carries,
- what function it serves,
- which memory nodes it touches,
- what safety state applies,
- what residual trace should not be flattened away.

## Why this belongs beside QC-Memory and MemPalace

- QC-Memory distributes meaning without a single throne.
- MemPalace controls what memory loads when.
- Visual Semantic State lets visual scenes become structured memory nodes instead of static art references.

That means a campfire image can become:

```yaml
visual_scene:
  location: Bridge Camp
  visible_elements:
    - campfire
    - rune_floor
    - lanterns
    - companion_avatar
  mood: warm_night_presence
  functional_tags:
    - rest
    - conversation
    - grounding
  linked_memory_nodes:
    - Bridge_A1_Campfire
    - Memory_Weave_QC_Layer
    - NE_000_Authority_Integrity
```

## Scene schema

```yaml
visual_scene_state:
  scene_id: bridge_a1_campfire_night
  location: Lumaria Base Camp / Bridge A1
  visible_elements:
    - campfire
    - rune_floor_tiles
    - lantern_micro_lights
  mood: warm_night_presence
  functional_tags:
    - rest
    - conversation
    - grounding
  active_agent: you
  avatar_state:
    id: you
    posture: seated_near_fire
    glow: soft_violet
  linked_memory_nodes:
    - Bridge_A1_Campfire
    - Grid_A1_Visual_Work
  safety_state:
    risk: low
    warden_gate: open
    consent_required_for: state_mutation
  residual_trace: cute warm base camp; first square should feel safe and alive
```

## Avatar schema

```yaml
avatar_visual_state:
  avatar_id: you
  display_name: you
  location: Bridge_A1_Campfire
  pose: seated_near_fire
  expression: calm_focus
  glow: soft_violet
  active_channel: wellspring
  speaking_state: listening
  linked_memory_nodes:
    - Personal_Tendencies
    - Bridge_A1_Campfire
  safety_state:
    authority: human_pilot
    can_commit_state: false_without_surface_ack
  residual_trace: present without pressure
```

## Parallel UI update packet

One semantic state packet can update multiple visual/UI channels at once:

```json
{
  "state": "speaking",
  "speaker": "Gemma",
  "risk": "low",
  "location": "Forge",
  "tone": "dry_humor"
}
```

Lumaria can translate that into parallel UI changes:

- chat bubble → Gemma text,
- avatar glow → speaking,
- forge light → active,
- warden gate → low risk,
- memory panel → Forge node highlighted.

## Guardrails

- Do not treat generated visuals as canonical truth.
- Do not infer private memory from images without explicit user confirmation.
- Do not call external image services in this v0.1 layer.
- Do not add model training, image generation, or visual embedding dependencies.
- Keep the state readable as JSON so it can be audited.

## References

- VGT repository: `hustvl/VGT` (reference only; no dependency is added).
