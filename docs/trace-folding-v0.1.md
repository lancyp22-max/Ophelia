# Typed Trace Folding v0.1

Status: **implemented experimental projection layer; not a canonical memory store**

The first implementation from the September 2 Steward scan keeps one rule above
every optimization:

> **projection != source**

The code in `TraceFold` accepts caller-supplied events and deterministically
derives a compact typed view. It does not persist events, write canonical
memory, approve changes, promote state, or mutate the world.

## Shape

```text
append-only causal events (external source-of-truth)
                |
                v
        deterministic fold
                |
        +-------+-------+
        |               |
   consumer view    audit metadata
        |               |
        +---- no authority
```

The current repository implements only the folding/projection layer. A durable
append-only ledger is **not implemented** by this patch and must not be inferred
from the existence of the projection code.

## Projection receipt

Every projection carries:

- fold schema version;
- consumer/view identifier;
- ordered source event IDs;
- contributing event IDs;
- SHA-256 root over the canonicalized source events;
- SHA-256 over the projection receipt + state;
- coverage state;
- omitted-event count;
- immutable projected state.

A consumer-specific view may omit information. Omission is therefore visible as
`PARTIAL` coverage rather than silently presented as a complete history.

## Determinism and replay

Batch folding sorts by `(sequence, eventId)`. Incremental folding requires that
same strict order and rejects reordering or duplicate positions.

The invariant tested in CI is:

```text
same source events + same view schema
        -> same projection
```

Changing a source event changes the source-root hash and projection hash.

This is deterministic application behavior, not a claim that every upstream LLM
transform is byte-reproducible. Stochastic summaries, if used later, must carry
their own provenance and may not claim stronger lineage than their transform can
demonstrate.

## Authority boundary

The fold has no command semantics.

It may:

- observe;
- compress;
- rebuild;
- expose lineage;
- produce a handoff view.

It may not:

- approve;
- authorize;
- promote;
- write identity;
- write canonical memory;
- change governance;
- create persistence authority.

```text
projection authority = 0
```

Agreement between multiple projections or agents remains evidence only.

## Measurement before compression

`data/trace-folding/measurement-schema.v0.1.json` requires measurement of:

- stored units;
- delivered context units;
- management/compression work;
- task outcome;
- provenance recovery rate;
- reconstruction fidelity;
- abstention rate;
- error rate.

A lower token count by itself is explicitly not a successful result.

## Deliberately not implemented

### Trace Observatory

Still parked. A future Observatory may compile agent/human/handoff/audit views,
but its building contract must remain observation-only. A central observer that
can command would become a throne.

### Latent/continuous memory tokens

Still experimental and outside canonical memory. If benchmarked later, the safe
shape remains:

```text
verifiable source -> auditable derivative -> optional latent derivative -> consumer
```

Never:

```text
latent derivative -> authoritative memory
```

Hardware feasibility for that lane remains
`intentionally_not_decided_yet`.
