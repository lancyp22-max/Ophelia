# Steward Archive Note — 2026-09-01

## Accepted observation

The first Lumaria Steward scan surfaced a useful memory-governance distinction:
a textual or summarized representation must not be treated as exhaustive of the
originating observation.

Accepted invariants:

- `summary_of(X) != X`
- `representation_type != authority`
- provenance describes lineage, not truth rank or permission
- richer representation does not itself authorize new persistence
- unknown provenance may remain `unknown`

## Implemented

A documentation-only architectural rule was added at
`docs/memory-source-provenance.md`.

No runtime, schema, retention, authority, canonization, or multimodal-storage
behavior was changed.

## Deferred

The following remain `intentionally_not_decided_yet`:

- exact `source_relation` schema
- `transformation_receipt` fields
- retention behavior for originating media
- dual-channel or multimodal persistence
- enforcement path in the local daemon

These require later discussion and separate human approval.

## Steward posture

OBSERVE.

No consent inferred from speech beyond this documentation/archive action.
No throne created. No persistence expanded beyond the requested archive record.
