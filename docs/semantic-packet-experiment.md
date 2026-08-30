# Lumaria Semantic Packet experiment v0.1

This experiment tests whether a tiny versioned codebook plus state deltas can
reduce repeated API payloads. It does **not** compress API keys. Credentials
remain server-only and never belong in packets, prompts, browser storage, logs,
or the codebook.

## Packet shape

```json
{"v":"0.1","b":"bridge-a1@1842","n":1843,"d":[["=","f","c"],["=","t","n"],["=","r","k"]]}
```

- `v` selects the exact codebook version.
- `b` identifies the shared base state.
- `n` is the monotonic delta sequence.
- `d` contains ordered `[operator, path, value]` atoms.

The local compiler expands the packet before trusted application code uses it.
Unknown atoms, version mismatch, missing base state, invalid sequence, and
oversized operation lists fail closed. Decoded content remains
`untrusted_context_data`: compact notation never grants consent, authority,
persistence, or canonization.

Replay/regression rejection requires the consumer's authoritative prior
sequence. Pass it with `--prior-sequence` when decoding; a packet cannot prove
its own freshness.

## Why this is intentionally small

The first codebook covers only repeated world-state facts with enumerated
values. It excludes arbitrary literals, credentials, authorization receipts,
consent receipts, and system instructions. It is not compressed English and it
does not attempt to represent every thought.

Opaque atoms can make model reasoning worse and require codebook instructions
that cost tokens themselves. Provider prompt caching, server-side conversation
state, retrieval, output limits, and sending only relevant context may save more
than a custom language. The experiment should survive only if measurement shows
a net benefit without reducing correctness.

## Honest measurement

`python3 scripts/semantic_packet.py --benchmark` reports UTF-8 payload size, not
provider tokens. Byte or character reduction does not prove billed-token
reduction. Exact evaluation must use the tokenizer or token-count endpoint for
each target model and include:

1. codebook instruction overhead;
2. cache hit and miss cases;
3. input and output tokens;
4. decode failures and retries;
5. task correctness versus plain structured input;
6. provider/model-specific tokenization.

Tokenizer-native atom selection is therefore
`intentionally_not_decided_yet`. Reconsider it only after a target provider and
model are selected and an exact token counter is available. Atom meanings must
never silently change in an existing codebook version.
