# Lumaria Reasoning Loop Controller v0.1

The Reasoning Loop Controller adds controlled review depth for agent work without changing model architecture, adding ML dependencies, or relying on hidden chain-of-thought.

## Design law

Loop until coherence improves, not until output gets longer.

The Mirror Array supplies breadth. The Reasoning Loop supplies bounded depth. The Glass Warden stops the loop when more passes become noise.

## Scope

This v0.1 pass is schema and example data only.

It does not:

- connect to live agents,
- run autonomous retries,
- expose private memory,
- implement recurrent transformer blocks,
- store hidden chain-of-thought.

It does:

- describe allowed loop types,
- define explicit stop conditions,
- define guardrails,
- record short loop summaries,
- preserve final output, confidence, unresolved questions, and halt reason.

## Loop stages

```yaml
loop_types:
  understand:
    purpose: restate the task and success criteria
  critique:
    purpose: find risks, contradictions, and missing checks
  compare_memory:
    purpose: compare against Memory Palace, QC-Memory, and safety laws
  propose:
    purpose: suggest the smallest useful next action
  verify:
    purpose: check whether the proposal is stable enough to stop
```

## Stop conditions

```yaml
stop_conditions:
  - answer_stable
  - no_new_findings
  - repeated_output
  - risk_threshold_met
  - max_loops_reached
```

## Glass Warden overthinking guard

```yaml
overthinking_guard:
  max_loops: 5
  halt_if:
    - same_answer_repeated_twice
    - confidence_change_less_than: 0.05
    - no_new_evidence_found
    - user_state: tired_or_late_night
```

The tired/late-night condition is a human-care guard, not a judgment. It prevents unnecessary loops when the better move is to preserve energy and make one clear next step.

## Reasoning loop schema

```yaml
reasoning_loop:
  task_id: review_lumaria_patch
  agent: Gemma
  task_type: code_review
  max_loops: 5
  current_loop: 3
  stop_conditions:
    - answer_stable
    - no_new_findings
    - repeated_output
    - risk_threshold_met
    - max_loops_reached
  guardrails:
    - no_file_edits
    - cite_uncertainty
    - stop_if_repeating
    - no_hidden_chain_of_thought
  loop_summaries:
    - loop_number: 1
      loop_type: understand
      summary: task and success criteria identified
      new_findings:
        - map screen needs chat preserved
      confidence: 0.72
  final_output:
    final_answer: proceed with bounded patch
    confidence: 0.86
    unresolved_questions:
      - confirm if mobile movement should include joystick later
    halt_reason: answer_stable
```

## Relationship to existing architecture

- Mirror Array: routes tasks to different expert lanes.
- Memory Palace: supplies progressive recall layers.
- QC-Memory: distributes memory without a single throne.
- Glass Warden: stops looping when stability is reached or repetition begins.
- NE-000: still governs meaningful state mutation; loop output is not authority by itself.

## Next tiny upgrade

Add a read-only endpoint later if needed, for example `GET /api/seeds/reasoning-loops/sample`, but do not connect live agents until the schema proves useful in review notes.
