# Lumaria threat model v1

## Scope and trust boundaries

This model covers retrieval, memory, provider output, consent receipts, bounded
links, scene actions, public artifacts, and tool execution. Human confirmation
is a security-relevant input, not an infallible oracle. Symbolic names, visual
states, relational labels, and model confidence are never trust credentials.

Trust crosses explicit boundaries at retrieval ingestion, provider responses,
memory persistence, consent verification, scene-action authorization, tool
invocation, and public-shell publication. Data crossing a boundary retains its
provenance and receives no capabilities merely because it crossed successfully.

## Threats and required posture

| Threat | Boundary | Required posture |
| --- | --- | --- |
| Retrieved prompt injection | retrieval → reasoning | Treat retrieved content as data unless separately trusted instruction provenance is verified. |
| Poisoned or stale memory | memory → reasoning | Surface age and provenance; permit consideration, never automatic canon or authority. |
| Malicious, mistaken, or stale provider output | provider → proposal | Constrain output to schemas; validate independently; require scoped authorization for effects. |
| Compromised provider | credential/provider boundary | Keep credentials server-side; minimize provider capabilities; support provider isolation and revocation. |
| Confused deputy | proposal → privileged tool | Re-evaluate the requesting principal, capability, target, scope, and receipt at the action boundary. |
| Replayed consent or lease | receipt → authorization | Require nonce, expiry, idempotency, and replay detection; fail closed when time or status is uncertain. |
| Accidental confirmation | human surface → commit | Preview consequences, identify target/scope, make destructive effects conspicuous, and preserve rollback where possible. |
| Resource exhaustion or recursive activity | scheduler/tool boundary | Enforce budgets, bounded depth, timeouts, concurrency limits, and REST without automatic reactivation. |
| Cross-agent privilege leakage | runtime → runtime | Capabilities remain principal- and scope-bound; identity association does not merge grants. |
| Credential leakage | repository/browser/publication | Scan as defense in depth, prohibit browser secrets, and use a server-side vault boundary. |
| Public-shell inference leak | sealed → public | Publish only allowlisted artifacts and audit both direct content and revealing metadata. |
| Persuasive visualization | state → visual plane | Render only sourced state and label unavailable/unverified state; visuals are never evidence. |
| Speech-as-key or ritual authorization | declaration → persistence | Treat declarations as surfaced proposals; require principal review, scoped capability, transactional write, and receipt. |
| Self-confirming quarantine | provider output → consequential layer | Evaluate observable candidates by provenance and evidence; never reject solely for disagreement, unfamiliarity, or presumed latent origin. |

## Fail-closed seams

Authentication, authorization, consent verification, destructive mutation,
credential handling, recovery, and cross-principal effects are blocking safety
work when undefined. They may not be labeled philosophical unknowns. The social
negotiation process for future multi-user conflicts may remain intentionally
undecided, but another principal's authorization can never be inferred.

## Review trigger

Review this model before adding autonomous background activity, a provider
proxy, persistent agent memory, multiplayer mutation, new privileged tools, or
a new public data class. A threat table entry is not proof that its mitigation
has been implemented; implementation claims require tests and receipts.
