# Lumaria Visual RL Harness v0.1

## Purpose

This is an ART-inspired design note for training or evaluating visual-world agents later, without importing OpenPipe/ART or adding reinforcement-learning dependencies now.

The useful pattern is not "train a model today." The useful pattern is:

```text
world state → candidate action → reward/penalty → trajectory log → safer next proposal
```

For Lumaria, that means visual changes can become auditable proposals instead of untracked edits.

## ART concepts translated to A1 Bridge Camp

| ART / RL concept | Lumaria translation |
| --- | --- |
| Environment | A1 Bridge Camp scene state |
| Observation | time mode, camera view, element list, safety state, performance budget |
| Action | propose lighting, material, placement, camera path, or clutter reduction |
| Trajectory | ordered visual edit attempts with outcomes |
| Reward | aesthetic alignment, stable geometry, readable scene, safe boundaries |
| Penalty | broken geometry, visual clutter, inaccessible contrast, private-memory exposure |

## Environment state

A lightweight environment state should include:

- `environment_id`
- `scene_id`
- `time_mode`
- `visual_elements`
- `camera_state`
- `safety_state`
- `performance_budget`
- `reward_model`
- `allowed_actions`
- `blocked_actions`

## Reward shaping

Reward terms should stay human-readable:

```yaml
reward_terms:
  aesthetic_alignment:
    description: matches Lumaria palette, cozy sanctuary mood, and A1 bridge purpose
    weight: 0.25
  geometry_integrity:
    description: no intersections that break walkability or hide the campfire anchor
    weight: 0.20
  readability:
    description: key objects remain legible on desktop and phone
    weight: 0.18
  safety_boundary:
    description: no private-memory inference or state mutation without surface ack
    weight: 0.22
  performance_budget:
    description: keeps object counts and effects light enough for mobile preview
    weight: 0.15
```

This keeps reinforcement-style evaluation grounded in the same rules as the visual-state schema.

## Allowed actions for v0.1

- `propose_lighting_change`
- `propose_material_refinement`
- `propose_object_placement`
- `propose_camera_path`
- `flag_visual_clutter`
- `suggest_accessibility_fix`

All actions are proposals only. They do not mutate the scene directly.

## Blocked actions for v0.1

- direct scene mutation without surface confirmation,
- training jobs,
- cloud RL services,
- external API calls,
- private seed exposure,
- autonomous publishing,
- high-cost particle or mesh explosions.

## Example trajectory

```json
{
  "trajectory_id": "a1_visual_pass_001",
  "start_state": "night_focus",
  "action": "propose_material_refinement",
  "proposal": "Add procedural cedar texture to benches and lantern bodies.",
  "reward_breakdown": {
    "aesthetic_alignment": 0.92,
    "geometry_integrity": 1.0,
    "readability": 0.86,
    "safety_boundary": 1.0,
    "performance_budget": 0.94
  },
  "decision": "accept_as_static_code_change"
}
```

## Guardrail law

The world may learn from trajectories, but the human remains pilot.

Any future agent should be able to recommend visual changes, score visual coherence, and log trajectories. It should not commit scene mutations or publish changes without surfaced confirmation.

## Next tiny upgrade

Add a read-only visual curator panel that displays the current reward model and latest trajectory score beside A1 Bridge Camp.
