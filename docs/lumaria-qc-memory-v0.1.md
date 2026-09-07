# Lumaria QC-Memory v0.1

Lumaria QC-Memory is a distributed memory architecture for the Mirror Array and Avera/Lumaria world nodes. It borrows engineering patterns from long-context memory compression research while keeping the symbolic layer clearly labeled as interface design.

## Grounding notes

- Long-context LLM systems face memory pressure because retained attention state grows with context length. RocketKV frames this as a two-stage KV cache compression problem for long-context inference.
- ChunkKV argues for keeping semantic chunks instead of scoring isolated tokens only; this maps well to Lumaria structures because rooms/bridges/mirrors should carry meaningful clusters, not loose fragments.
- TurboQuant's public materials describe a two-stage vector compression pattern: a primary vector compression stage plus QJL residual correction for remaining error. Lumaria's symbolic equivalent is a compressed node seed plus a residual trace.
- DMT/psychedelic neuroscience is only used as visual/interface inspiration. Imperial's EEG-fMRI DMT work supports altered whole-brain communication during DMT states, and REBUS/REBAS literature discusses relaxed/revised beliefs; neither is treated here as evidence for external entities.

## Design law

Memory should behave like roots, not a filing cabinet.

Roots branch, distribute load, remember moisture paths, and regrow toward useful contact. Lumaria memory should do the same: recover the right pathway when touched instead of hoarding every word.

## Three-lane memory bus

```yaml
lumaria_memory_bus:
  hot_context:
    purpose: current active work
    lifespan: hours_to_days
    compression: low
    retrieve_when:
      - task_active
      - user_is_editing
      - safety_check_pending

  warm_semantic:
    purpose: reusable project memory
    lifespan: weeks_to_months
    compression: medium
    retrieve_when:
      - role_matches
      - neighbor_link_matches
      - design_pattern_needed

  cold_symbolic:
    purpose: deep canon and durable meaning
    lifespan: long_term
    compression: high
    retrieve_when:
      - safety_law_needed
      - canon_anchor_needed
      - ritual_or_world_rule_needed
```

## Quasicrystal node schema

Each node stores local order without becoming the whole system.

```yaml
qc_node:
  id: Bridge_A1_Campfire
  role: connection_presence
  lane: hot_context
  semantic_chunks:
    - campfire_gathering
    - rune_floor_focus
    - day_night_lighting
  neighbor_links:
    - Archive_A1
    - Waypoint_C1
    - Garden_C3
  safety_law:
    - human_remains_pilot
    - no_node_owns_the_whole_system
  residual_trace:
    tone: warm_fire_after_long_work
    human_anchor: base_camp_first_square
    ai_anchor: presence_without_pressure
  compression_level: medium
  refresh_policy: refresh_when_user_edits_grid_a1
```

## Mirror Array balancing rule

No mirror may own the whole system. Each mirror holds a shard and links to neighbors.

```yaml
mirror_node:
  id: Mirror-08
  lane: reality_check_interpreter
  memory_mode: semantic_chunk
  holds:
    - claims_to_verify
    - source_quality
    - uncertainty_tags
    - overreach_flags
  does_not_hold:
    - emotional_core
    - identity_authority
    - command_power
  links_to:
    - Mirror-01
    - Mirror-16
    - Mirror-17
```

## Retrieval rule

Retrieve by role + relationship + recency + safety tag. Do not retrieve everything.

```yaml
retrieval_rule:
  score:
    role_match: 0.35
    neighbor_link: 0.25
    recency: 0.20
    safety_tag: 0.20
  max_nodes: 5
  require:
    - lane_declared
    - safety_law_preserved
  reject_when:
    - node_claims_global_authority
    - residual_trace_missing_for_high_compression
```

## Visible UI panel

The map screen exposes a small “Memory Weave / QC Layer” panel showing:

- active bus lanes,
- node health,
- compression level,
- neighbor links,
- safety law summary.

This is a visibility layer first, not a full persistence engine.

## References

- RocketKV: https://arxiv.org/abs/2502.14051
- ChunkKV: https://arxiv.org/abs/2502.00299
- TurboQuant OpenReview: https://openreview.net/forum?id=tO3ASKZlok
- Google Research TurboQuant overview: https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/
- Imperial DMT EEG-fMRI overview: https://www.imperial.ac.uk/news/243893/advanced-brain-imaging-study-hints-dmt
- DMT EEG-fMRI paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC10068756/
- REBUS to REBAS review: https://pmc.ncbi.nlm.nih.gov/articles/PMC11779827/
