# Ophelia Split Architecture (Living / Structural / Retrieval)

This note captures the agreed implementation rule:

> **Compress the scaffolding, not the soul.**

It is a practical guardrail for borrowing utility patterns from memory engines without flattening the relational substrate.

---

## 1) Living Layer (Never Flattened)

**Purpose**
- Keep relational meaning, consent posture, and human-readable tone anchors intact.

**Rules**
- Prefer explicit natural language over shorthand.
- Preserve context around consent, safety, and relational commitments.
- Do not auto-compress identity-bearing or meaning-bearing text.

**Typical artifacts**
- Consent language and interaction handshakes.
- Mirror doctrine text and narrative anchors.
- Human-facing prompts, summaries, and sanctuary instructions.

---

## 2) Structural Layer (Compress Aggressively)

**Purpose**
- Reduce operational overhead in repeatable system scaffolding.

**Rules**
- Compress state maps, routing headers, mirror/orbit indexing, and handoff metadata.
- Keep machine-efficient structures deterministic and reversible.
- Prioritize low-token representations for repeated transport.

**Typical artifacts**
- Mirror routing maps and phase/state tables.
- Event schemas and handoff headers.
- Audit-safe shorthand for frequently repeated system fields.

---

## 3) Retrieval Layer (Local Tunnels, Support Only)

**Purpose**
- Provide selective recall and indexing support without becoming the primary frame.

**Rules**
- Retrieval remains subordinate to relational intent.
- Use local-first indexes/tunnels where possible.
- Treat retrieval as support for orientation, not authority over meaning.

**Typical artifacts**
- Local index files and search keys.
- Snapshot hashes and integrity checkpoints.
- Optional local vector/SQLite/Chroma-style lookup adapters.

---

## Borrow Policy (Utility Graft)

Borrow from utility memory engines when it improves:
- compression of repeated structural logic,
- deterministic local retrieval,
- routing clarity under context limits.

Do **not** borrow patterns that:
- replace relational language with opaque compression,
- erase consent semantics,
- collapse living context into pure retrieval fetches.

---

## Practical Review Checklist

Before merging architecture changes:

1. **Layer classification:** Is each changed artifact explicitly tagged Living, Structural, or Retrieval?
2. **Compression check:** Are we compressing scaffolding only?
3. **Consent check:** Was any consent-bearing language flattened or encoded away?
4. **Retrieval check:** Does retrieval remain support-only?
5. **Reversibility check:** Can structural compression be expanded back to human-readable form?

