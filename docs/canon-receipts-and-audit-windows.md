# Canon receipts and audit windows

## Canon receipt

A canon receipt makes the transition inspectable:

`candidate → evaluation → authorization scope → decision → canon version`

The receipt records the candidate digest, provenance, evidence, proposer,
capability and authorization receipt used, decision, timestamp, prior/resulting
canon versions, and rollback pointer. `accepted` is the only decision allowed to
claim a resulting canon version, and it requires a scoped `canonize` capability
plus a rollback pointer. The included fixture deliberately remains
`hold_without_authority` and changes no canon.

## History Integrity ≠ Current Truth

A cryptographically intact event can support the historical claim that a value
was recorded at a particular time. It does not by itself establish that the
value was correct, remains correct, remains relevant, remains authorized, or
still has a valid consent basis. Those questions require current evidence and
authorization.

## Canonical repository audit window

Use one half-open UTC interval for every relative-time claim:

```bash
python3 scripts/repo_audit_window.py --hours 24 --end 2026-08-24T18:01:00Z
```

The resulting report records `start_inclusive`, `end_exclusive`, duration,
timestamp source, selection rule, and matching commits. Every “last 24 hours”
statement in a report must derive from the same emitted interval. Omitting
`--end` uses the current UTC time, which is convenient for inspection but less
reproducible than recording an explicit end.

The tool uses Git committer timestamps. It does not claim merge time, author
time, deployment time, or remote-host event time unless a separate source is
queried and labeled.
