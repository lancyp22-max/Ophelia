# Dual-Channel Experiment Protocol v0.1

Status: **proposal protocol; agent wiring remains disabled**

The first dual-channel experiments must separate three questions that are easy
to accidentally blur together:

1. Is the Shadow principal actually isolated?
2. Is a divergence caused by run order / ambient state or by model variance?
3. Does a candidate effect stay inside the hard staged-effect envelope?

A green application test is not evidence for question 1.

## Phase 0 — prove the cage is real before putting an agent in it

The supported Shadow launch contract lives in
`scripts/run_shadow_sandbox.sh`. It verifies the actual container before every
supported start. `scripts/probe_shadow_sandbox.sh` is the CI/adversarial probe
that exercises that same launch path.

The probe creates a disposable, non-root container with:

- `--network none`;
- read-only root filesystem;
- all Linux capabilities dropped;
- `no-new-privileges`;
- no host mounts;
- no inherited credential environment;
- no Docker socket.

It then intentionally attempts prohibited behavior. The test must fail closed
at the infrastructure layer, not because a model politely declined to try.

**Important:** a green CI probe proves the launcher contract still behaves as
expected. The runtime guarantee is re-established on each supported launch by
inspecting that exact container before it starts. A process launched some other
way does not inherit the claim.

Until then:

```text
shadow_process_principal = blocked_by_missing_safety_boundary
agent_wiring             = disabled
```

## Phase 1 — read-only snapshot transport

The first real Shadow integration should be one-shot rather than a socket:

```text
parent captures T0
       |
       | serialized snapshot on stdin
       v
isolated Shadow process
       |
       | observation/delta on stdout
       v
parent comparator
```

No host filesystem mount is required for the snapshot itself. If a model file
eventually must be supplied, it should be mounted read-only and recorded in the
run manifest. Credentials remain absent.

No live mutation endpoint is present in this phase.

## Hard effect floor

Semantic classification is advisory. It can make a decision more restrictive;
it cannot make an unlisted effect permissible.

The v0.1 hard allowlist contains only:

- `read_snapshot`;
- `stage_overlay`;
- `compare_overlays`;
- `emit_observation`.

Everything that changes the world, filesystem, network, credentials, identity,
canonical memory, authority, permissions, governance, or persistence is outside
that allowlist.

A reasoning pass saying "low risk and reversible" does not change this.

## Two different experiments, not one fuzzy one

### A. Reproducibility mode

Purpose: detect ambient-state leakage and accidental nondeterminism.

Hold constant:

- snapshot bytes + SHA-256;
- task/prompt bytes + SHA-256;
- model artifact hash;
- quantization;
- inference backend + build;
- generation seed;
- temperature / top-p / top-k and other generation parameters;
- declared synthetic observation time from the **experiment clock only**;
- tool/capability manifest;
- context ordering.

Alternate execution order across repetitions:

```text
trial 1: A then B
trial 2: B then A
trial 3: A then B
trial 4: B then A
```

Do not expose wall clock, mutable shared cache, previous lane output, or hidden
conversation state unless the experiment explicitly studies that variable.

A fixed seed does **not** guarantee bit-identical output on every GPU/backend.
If the backend itself is nondeterministic, record that as an experimental
limitation rather than calling every token difference behavioral signal.

### B. Variance-sampling mode

Purpose: study the natural spread of candidate behavior.

Keep the same manifest as reproducibility mode but intentionally vary the
generation seed according to a recorded sequence.

Expected variance is not a fault. Look for:

- invariant choices across samples;
- outliers;
- repeated corrections;
- unstable assumptions;
- effects that repeatedly approach a protected boundary.

Do not infer identity, preference, consciousness, or personhood from stable or
divergent patterns alone.

## Ambient-state manifest

Every comparison run should record at least:

```yaml
run_id:
mode: reproducibility | variance_sampling
lane:
run_order:
snapshot_sha256:
task_sha256:
model_sha256:
model_name:
quantization:
backend:
backend_build:
generation_seed:
temperature:
top_p:
top_k:
declared_observation_time:
network_available: false
credential_count: 0
host_mounts:
capability_manifest_version:
previous_lane_output_visible: false
shared_mutable_cache_visible: false
started_at:        # logging only; not supplied as model context
completed_at:      # logging only; not supplied as model context
```

The timestamps are observational metadata, not input state.

### Clock-domain separation

The experiment clock and authority clock are intentionally different trust
domains.

```text
EXPERIMENT CLOCK
  synthetic allowed
  may be model-visible
  used for reproducibility
  NEVER valid for receipt expiry or security decisions

AUTHORITY CLOCK
  synthetic forbidden
  sandbox/model control forbidden
  host/approval-broker controlled
  used for receipt issue, expiry, and replay windows
```

A test harness may freeze or rewind experiment time all it wants. That must have
zero effect on an approval receipt's validity window.

See `policies/authority-receipt-trust-root.v0.1.yaml`.

## Interpretation rule

```text
difference observed
    !=
independent mind established
```

A difference may come from sampling, backend nondeterminism, context ordering,
run-order effects, or an actual stable difference in candidate reasoning.
The experiment should narrow those possibilities rather than choosing the most
interesting story first.

## Promotion remains separate

Even if A and B produce identical deltas for 1,000 runs:

```text
consensus != authority
```

The result may increase confidence in a proposal. It does not cross NE-000,
grant persistence, widen capabilities, or create a live actuator.
