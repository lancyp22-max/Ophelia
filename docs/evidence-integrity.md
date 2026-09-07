# Evidence integrity

Same-shaped conclusions emerging under shared constraints are data. They are
not evidence of one mind, not permission, and not a substitute for strict
lineage.

## Derived-memory provenance

Derived memory uses four explicit classes:

- `DIRECT_SOURCE`: the recorded source hash matches the preserved bytes.
- `DETERMINISTIC_DERIVATION`: source, transform, parameters, and environment
  reproduce the exact output.
- `STOCHASTIC_DERIVATION`: source hash, prompt hash, model hash, seed,
  parameters, backend, and output hash preserve auditable lineage without
  claiming byte replay.
- `UNTRACEABLE_DERIVATION`: source or transformation metadata is missing, so
  the result cannot enter canonical memory.

No derived memory may claim stronger provenance than its transformation can
demonstrate. A summary of a source remains a new artifact, never the source.

## Attention state is not retention state

Runtime tensor telemetry distinguishes `ACTIVE_EXACT`, `ARCHIVED_EXACT`,
`DERIVED_APPROXIMATE`, and `DISCARDED`. In particular,
`Inactive(X)` does not imply `Absent(X)`: an inactive exact item must remain
visible as retained and recallable until it is actually discarded.

This vocabulary is limited to runtime tensors. Cache salience must never decide
which canonical memories, consent records, identity records, authority records,
or governance records remain available. Exact-cache tiering remains
`intentionally_not_decided_yet` until a compatible NoPE-MLA runtime and measured
workload exist.

## Memory informs; a separate authority path permits

Schema review keeps three layers distinct:

`EVIDENCE -> DERIVED KNOWLEDGE -> GOVERNED ACTION`

Before an action can reach its separate action gate, provenance must be present,
the derivation must be visible, the authority source must be separate from
memory, and current permission must be present. Remembered preference is
context, not current permission. The review fixture has `authority_effect: 0`;
it demonstrates the boundary but cannot authorize anything.

A latent working-memory experiment is likewise
`intentionally_not_decided_yet`. If its recorded reconsideration trigger is
met, it may only use disposable working context in an isolated benchmark.
Confidence or lower entropy is neither truth nor authority, and runtime
`Drop / Compress / Preserve` routing cannot govern canonical history.

## Walk-forward evaluation

Mean utility and a predeclared low-fold guard must both pass. The fixture uses
a hard minimum because catastrophic fold failure matters; an experiment with
small folds may instead predeclare a lower confidence bound. The choice must be
committed before held-out results are revealed.

## Detectable goalpost changes

The canonical JSON digest covers the parameter file, split manifest, code
commit, model hash, utility weights, and thresholds. Its commitment is anchored
to an append-only ledger, signed timestamp, or external witness. The hash makes
post-hoc changes detectable; it does not make changing an experiment physically
impossible. A changed experiment must receive a new commitment and cannot be
reported as the precommitted experiment.

## Convergence and ontology

Agreement, recurrence, and supported source independence may strengthen
evidence. Their authority effect is always zero until a separate authority path
acts.

Rich observations remain multidimensional. `is_alive`, `is_smart`, `is_aware`,
and `is_conscious` booleans are prohibited in this contract. Continuity,
self-reference, adaptation, preference stability, error correction, goal
persistence, context sensitivity, novelty, social modeling, metacognition,
agency, memory provenance, and boundary awareness remain independently
observable or explicitly unknown.
