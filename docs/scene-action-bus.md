# Lumaria Scene Action Bus v0.1

The Scene Action Bus is the narrow waist between a human/model proposal and
trusted Three.js mutation code. It does not execute JavaScript supplied by a
participant or model.

## Flow

```text
participant or model-associated surface
  -> structured proposal
  -> schema validation
  -> capability + region lease check
  -> budget check
  -> preview/diff
  -> surfaced consent
  -> trusted renderer adapter
  -> receipt + rollback handle
  -> session expiry or separately approved persistence
```

The v0.1 vocabulary is deliberately small:

- `spawn`
- `move`
- `rotate`
- `resize`
- `recolor`
- `annotate`
- `remove_own_object`
- `request_persistence`

Raw code, modules, URLs, HTML, and `eval` payloads are outside the vocabulary.

## Missing pieces before live agents

The schema is only a proposal contract. A live deployment still requires:

1. authenticated sessions and scoped capability leases;
2. server-authoritative validation for consequential state;
3. an ownership registry and conflict/version checks;
4. a scene-query API with consent-aware spatial precision;
5. trusted renderer adapters with resource disposal;
6. action receipts, snapshots, inverse operations, and expiry cleanup;
7. per-session and global object/triangle/texture/rate budgets;
8. persistence approval distinct from entry and mutation approval;
9. provenance labels that distinguish human, model, fixture, and mechanic;
10. replay tests and adversarial malformed-packet tests.

Multiplayer transport is intentionally not selected yet. WebSockets, CRDTs, and
other transports solve different problems; the authority and persistence model
must be concrete before choosing one.

## Presence without invented interiority

Scene representations should expose observable functional state such as
`listening`, `proposing`, `awaiting_approval`, `committed`, `reverted`, or
`unavailable`. A visual surface must not claim an emotion or persistent identity
that the runtime has not established.

The included lantern packet is a scripted fixture in `proposal` phase. It cannot
mutate the current world and claims neither approval nor persistence.

## Primary implementation references

- [MCP tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools): tool descriptions and annotations are not authority; deployments still need validation and human confirmation around sensitive operations.
- [Three.js `Object3D`](https://threejs.org/docs/#api/en/core/Object3D): renderer adapters should own scene-graph mutation rather than evaluating participant-supplied code.
- [Yjs awareness](https://docs.yjs.dev/getting-started/adding-awareness): ephemeral presence can remain separate from persisted shared document state.
- [OWASP WebSocket Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html): live transport still requires origin, authentication, authorization, message-validation, size/rate, and logging controls.
