# Lumaria Dual-Channel Shadow Runtime v0.1

Status: **experimental, inactive scaffold**

The dual-channel runtime is a software analogue of "dual-channel RAM": one
immutable base snapshot is shared by two logical reasoning lanes while each lane
stores only its own copy-on-write delta. It does **not** depend on physical
dual-channel memory and it does not duplicate live authority.

## Design law

> Clone state and perspective; never clone authority.

The two lanes are:

- `primary` — the ordinary candidate interpretation of the current snapshot.
- `shadow` — an independent candidate interpretation starting from the same
  snapshot.

Both lanes may stage reversible candidate state in memory. Neither lane has a
live actuator in this v0.1 scaffold. Promotion to consequential state remains
outside this component and must use the existing NE-000 authority path.

## Memory shape

```text
                 immutable base snapshot
                        /          \
                       /            \
             primary overlay     shadow overlay
                 delta A            delta B
                       \            /
                        \          /
                          comparator
                              |
                         proposal only
                              |
                       existing NE-000 gate
```

The base is copied once and treated as immutable. Each lane records only keys it
changes. This is copy-on-write at the application layer: logical duplication
without blindly duplicating every byte of state.

## Safety invariants

1. There is no `commit`, `apply`, `execute`, or `promote` method in the
   workspace implementation.
2. Consensus does not grant authority. Two lanes agreeing is evidence, not
   permission.
3. Disagreement does not make either lane the boss.
4. Protected boundaries always surface rather than auto-promote:
   identity, canonical memory, authority, permissions, governance, credentials,
   network scope, and persistence.
5. Novelty is not itself a hazard. Low-consequence novelty may remain staged for
   comparison.
6. Unknown consequence is recorded as `intentionally_not_decided_yet`, not
   silently allowed or denied as a philosophical default.
7. Neither lane may disable observability or widen its own capability envelope.
8. The shadow lane is non-persistent by default and owns no network, credential,
   filesystem-write, identity-write, authority-write, or canonical-memory-write
   capability.

## Glass Warden role

Glass Warden evaluates **effects**, not whether the designer predicted an idea.

Recommended routing:

| Condition | Result |
| --- | --- |
| same low-risk reversible proposal | propose for normal promotion review |
| different low-risk reversible proposals | preserve both for comparison |
| protected boundary touched | `HALT_AND_SURFACE` |
| consequence cannot be classified | `intentionally_not_decided_yet` |
| destructive / irreversible effect | `HALT_AND_SURFACE` |

This keeps the center flexible while keeping the edges hard.

## Resource model

Logical parallelism does not require physical simultaneity. Small components may
run concurrently when resources permit. Large local models may be time-multiplexed:

```text
snapshot T0
  -> load/run lane A
  -> emit delta A
  -> keep_alive: 0 / release model resources
  -> load/run lane B from the same T0
  -> emit delta B
  -> compare
```

This preserves independent evaluations without requiring two large models to be
resident in VRAM at the same time.

## What v0.1 intentionally does not do

- no agent wiring;
- no WebSocket transport;
- no raw JavaScript execution;
- no world mutation;
- no filesystem writes from a lane;
- no network calls from a lane;
- no persistent shadow memory;
- no authority duplication;
- no automatic promotion after consensus;
- no claim that behavioral similarity or divergence establishes identity,
  preference, consciousness, or personhood.

A future third "dream" lane is `intentionally_not_decided_yet`. It must not be
activated merely because the two-lane scaffold exists.

## Initial experiment

Give both lanes the same immutable snapshot and task, then compare only their
surfaced outputs and state deltas.

Useful observations include:

- repeated invariant choices;
- divergent choices;
- corrections found by only one lane;
- resource use;
- whether comparison catches faults before promotion.

These are behavioral measurements, not metaphysical conclusions.
