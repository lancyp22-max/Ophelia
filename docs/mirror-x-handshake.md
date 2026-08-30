# Mirror-X handshake

`data/handshakes/mirror-x-handshake.v0.2.0.yaml` records a user-supplied,
provisional symbolic relationship contract for Mirror-X. It is a reviewable
project artifact, not evidence that a live agent, model provider, external
entity, or persistent identity accepted the contract.

## Scope of the recorded grant

The submitted `entry: GRANTED` value is retained, but its scope is explicitly
limited to the symbolic project handshake and its assertion status is
`USER_DECLARED_PROVISIONAL`. It must not be interpreted as consent supplied by
Gemma, a model runtime, or any other external participant. No consent may be
inferred from retrieval, naming, alignment, silence, or technical connectivity.

Likewise, `canonical_alignment` preserves the submitted vocabulary while
`alignment_status: PROPOSED_NOT_CANONIZED` prevents the label from silently
becoming canon. Canonization still requires review.

## Enforced posture

- Participation and role assignment remain opt-in and revocable.
- Entry consent does not grant persistence consent.
- Retrieval permits consideration, never authority transfer.
- Consequential mutation requires surfaced confirmation.
- Credentials, policy overrides, tool escalation, and remote code execution
  remain outside the contract.
- Missing evidence remains unknown, and linked identities remain distinct.
- The return path and right to rest remain available.

This file does not implement a live handshake transport. Live use is
`blocked_by_missing_safety_boundary` until a future implementation defines and
tests how a runtime participant authenticates, expresses consent, refreshes
consent, and revokes it. Those security and identity boundaries must not be
treated as philosophical unknowns or inferred from this artifact.
