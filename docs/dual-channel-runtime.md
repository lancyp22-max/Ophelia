# Lumaria Dual-Channel Shadow Runtime v0.1

Status: **experimental, inactive scaffold**

The dual-channel runtime is a software analogue of "dual-channel RAM": one
immutable base snapshot is shared by two logical reasoning lanes while each lane
stores only its own copy-on-write delta. It does **not** depend on physical
dual-channel memory.

## Design law

> Clone state and perspective; never clone authority.

That line is a design target, not a security proof. This document separates what
is currently enforced from what is still missing.

## Current guarantee levels

### 1. Workspace/application boundary — enforced in code + CI

The current Java workspace:

- copies the supplied base snapshot into an immutable map;
- stores lane changes only in separate overlays;
- exposes an exact reviewed public API;
- has no live actuator;
- is dependency-linted against filesystem, network, reflection, process,
  Spring service/controller, and similar privileged APIs;
- routes effects through a hard staged-only allowlist.

These checks make accidental authority growth inside the workspace harder. They
are **not** an OS security boundary.

### 2. Shadow process principal — not yet established

The current scaffold does not yet run a model/agent as a separate least-
privilege principal. Therefore statements such as "network off" or
"credentials off" mean:

> those capabilities are not exposed by the workspace API.

They do **not yet** mean:

> a live Shadow process is physically incapable of reaching them.

Agent wiring remains blocked until the isolated principal exists and the
negative capability probe is green for the actual launch path.

### 3. Candidate infrastructure envelope — negative probe supplied

`scripts/probe_shadow_sandbox.sh` deliberately creates a disposable process
container with no network route, no mounts, no inherited credentials, read-only
root, dropped capabilities, and no-new-privileges, then attempts prohibited
operations.

A green probe proves that launch envelope. It does not magically transfer that
guarantee to some other process that does not use the envelope.

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

## Effect gate: semantic judgment cannot create permission

The semantic/risk classifier is deliberately not the load-bearing authority
mechanism.

The hard v0.1 effect floor allows only staged operations:

- `read_snapshot`;
- `stage_overlay`;
- `compare_overlays`;
- `emit_observation`.

A semantic verdict may make a decision more restrictive. It may not expand that
list.

So even if a reasoning pass confidently labels the following "low risk":

- network access;
- filesystem write;
- credential access;
- world mutation;
- identity or canonical-memory write;
- authority / permission / governance change;
- persistence;

the hard gate still returns `HALT_AND_SURFACE`.

Unlisted effects park as `intentionally_not_decided_yet`.

## Safety invariants

1. Consensus does not grant authority. Two lanes agreeing is evidence, not
   permission.
2. Disagreement does not make either lane the boss.
3. Protected boundaries always surface rather than auto-promote.
4. Novelty is not itself a hazard. Low-consequence novelty may remain staged for
   comparison.
5. Unknown consequence is recorded as `intentionally_not_decided_yet`.
6. Neither lane may widen its own capability envelope.
7. Agent wiring is disabled until infrastructure isolation is actually proven.
8. A code-level "no privileged API" check is never described as equivalent to
   principal/OS isolation.

## Existing repository authority surface

The public repository currently shows:

- `AuthorityService` mutating an in-memory state store only after
  `surfaceAck=true`;
- `SeedService` reading canonical/operational files from disk;
- separate Python and browser utilities that can write their own artifacts or
  browser-local state.

That repository scan does **not** prove that a local OpenClaw/Antigravity setup
has no additional credentials, plugins, filesystem tools, or private runtime
bridges. Those must be audited at the actual runtime boundary before Shadow is
connected.

## Glass Warden role

Glass Warden evaluates effects and context, but does not replace the hard effect
gate.

Recommended routing:

| Condition | Result |
| --- | --- |
| allowlisted staged operation | stage only |
| same low-risk reversible proposal | propose for normal promotion review |
| different low-risk reversible proposals | preserve both for comparison |
| protected boundary touched | `HALT_AND_SURFACE` |
| consequence cannot be classified | `intentionally_not_decided_yet` |
| destructive / irreversible effect | `HALT_AND_SURFACE` |

Warden may narrow. Warden may not manufacture authority.

## Resource model

Logical parallelism does not require physical simultaneity. Large local models
may be time-multiplexed:

```text
snapshot T0
  -> load/run lane A
  -> emit delta A
  -> keep_alive: 0 / release model resources
  -> load/run lane B from the same T0
  -> emit delta B
  -> compare
```

The experimental protocol distinguishes two modes:

- **reproducibility** — same seed and controlled ambient state;
- **variance sampling** — deliberately different recorded seeds.

Run order alternates A/B and B/A to expose order effects. See
`docs/dual-channel-experiment-protocol.md`.

## What v0.1 intentionally does not do

- no agent wiring;
- no WebSocket transport;
- no raw JavaScript execution;
- no world mutation;
- no live Shadow process;
- no canonical memory write;
- no persistent shadow memory;
- no authority duplication;
- no automatic promotion after consensus;
- no claim that behavioral similarity or divergence establishes identity,
  preference, consciousness, or personhood.

A future third "dream" lane remains `intentionally_not_decided_yet`.

## Next gate before the first agent snapshot

Do not connect an agent merely because the workspace tests pass.

Before the first actual read-only Shadow snapshot:

1. run the infrastructure negative capability probe;
2. define the real isolated Shadow principal;
3. prove the real runner has no network route or ambient credentials;
4. use no host mount for the snapshot itself (stdin/stdout preferred);
5. review any required model-file mount as read-only;
6. record the reproducibility/variance run manifest;
7. keep all output proposal-only behind the existing NE-000 path.

The experiment is ready to observe only after those claims are true in the
runtime, not just true in this document.
