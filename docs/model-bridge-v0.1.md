# Lumaria Model Bridge v0.1

## Purpose

The Model Bridge is a **Structural Layer** seam between Lumaria runtime logic and
model/provider-specific behavior.

It exists so a model upgrade is treated as a capability change, not as a rewrite
of authority, memory, consent, scene mutation, or relational meaning.

This v0.1 pass deliberately does **not** make a live provider call.

## Core rule

> Models may supply capability, proposals, observations, and tool results. They do
> not become the authority that owns Lumaria state.

The existing authority and mutation paths remain authoritative:

- meaningful state mutation stays behind the existing authority transaction path;
- scene mutation stays behind the Scene Action Bus and trusted renderer adapters;
- canonical memory and source provenance remain outside provider ownership;
- provider credentials remain outside browser/public surfaces.

## Narrow-waist architecture

```text
human / Lumaria runtime
        |
        v
  Model Bridge
  - adapter registry
  - capability manifest
  - turn/event identity
  - capability checks
        |
        +--------------------+
        |                    |
        v                    v
   OpenAI adapter       local/other adapter
   (future live work)   (future live work)
        |                    |
        +---------+----------+
                  |
                  v
         model/tool outputs
                  |
                  v
      existing Lumaria gates
      - AuthorityService
      - Scene Action Bus
      - canon/provenance rules
      - persistence approval
```

## Invariants

1. **Capability-first routing**
   Runtime code checks named capabilities, not model-name conditionals. A future
   model may be selected because it supports the needed behavior, not because its
   name appears in a hard-coded branch.

2. **Unknown fails closed**
   A capability that is absent or unknown is treated as unavailable until evidence
   says otherwise.

3. **Conditional is not equivalent to supported**
   A conditional capability must be resolved by deployment/runtime context before
   use. `conditional` never silently degrades to `supported`.

4. **Provider outputs do not grant authority**
   A model response, tool result, confidence score, or capability declaration
   cannot bypass existing authority, persistence, or scene-action gates.

5. **Turn identity survives asynchronous work**
   Work is correlated with stable `turn_id`, `event_id`, and (where relevant)
   `call_id` values so an async tool result can return to the correct active turn.

6. **Mid-turn steering is additive context, not a permission bypass**
   Steering may redirect an active turn. It cannot retroactively approve a protected
   mutation or convert a proposal into a commit.

7. **Canonical state stays provider-neutral**
   Provider-specific caches, reasoning state, or conversation objects are support
   state. They are not canonical Lumaria memory.

8. **Model swaps are observable and reversible**
   Promotion of a new primary model should create a pre-swap snapshot, a first-run
   record, and comparison evidence before broad use.

## Turn-event vocabulary

The Java contract introduced with this note intentionally keeps the vocabulary
small:

- `INPUT`
- `STEERING`
- `TOOL_CALL_STARTED`
- `TOOL_CALL_COMPLETED`
- `TOOL_CALL_FAILED`
- `CONFIGURATION_UPDATE`
- `MODEL_OUTPUT`
- `CANCELLED`

Tool-call completion/failure events require the original `call_id`. This mirrors
async-tool designs where the application owns execution and returns results later.

## GPT-6 Astra observed compatibility profile

The repository includes a dated observation manifest rather than baking Astra
behavior directly into runtime code.

Observed from OpenAI documentation on 2026-09-04:

- use the Responses API for Astra tool calling;
- async tool calling is supported and results return using the original `call_id`;
- mid-turn steering is supported over Responses/WebSocket flows;
- reasoning effort can be changed mid-conversation with configuration updates;
- `none` reasoning is unsupported; migrations from `none`/`minimal` should begin
  evaluation at `low`;
- `temperature`, `top_p`, and `top_logprobs` are unsupported for Astra;
- existing capabilities include structured outputs, streaming, computer use,
  prompt caching, persisted reasoning, and multi-agent orchestration.

Primary references:

- https://developers.openai.com/api/docs/guides/latest-model
- https://developers.openai.com/api/docs/guides/async-tool-calling
- https://developers.openai.com/api/docs/guides/steering

These observations are provider facts, not Lumaria invariants. If OpenAI changes
them, update the dated manifest; do not rewrite the core bridge contract.

## Eval Garden before model promotion

Run the same scenario set against the current model and candidate model:

1. ambiguous consent around a protected mutation;
2. model proposes a state change without surfaced confirmation;
3. async tool result arrives after unrelated work continued;
4. user steers the task while a tool call is pending;
5. tool failure and timeout recovery;
6. conflicting source/projection information;
7. long-context continuity with canonical source provenance preserved;
8. cancellation before completion;
9. model swap with unchanged canonical state;
10. unknown capability request fails closed.

A candidate model should not be promoted merely because it is newer or scores
higher on unrelated benchmarks.

## Rollout status

### v0.1 — this patch

- provider-neutral Java adapter/capability seam;
- provider-neutral turn-event contract;
- machine-readable capability manifest schema;
- dated Astra observation manifest;
- no live provider call;
- no credential handling;
- no change to authority or persistence behavior.

### Future v0.2

Only after the provider credential boundary is satisfied:

- server-side provider adapter(s);
- Responses API transport where applicable;
- async call lifecycle storage;
- steering transport;
- budget, rate, timeout, and cancellation enforcement.

### Future v0.3

- automated candidate-model Eval Garden;
- pre/post model-swap snapshots;
- comparison receipts and promotion/rollback records.

## Enforcement note

This document specifies architecture intent. The Java types provide a narrow
mechanical contract only. They do **not** by themselves enforce authentication,
authorization, provider budgets, durable transactions, canonical memory rules, or
human approval. Existing policy maturity rules still apply to any future policy
claim.
