# Append-only friction ledger

The friction ledger records what happened when a route was attempted. It does
not label a route as inherently good, bad, safe, or authorized. Its derived
values mean only “recent friction was observed under a similar recorded
context.”

Each JSONL line preserves the raw outcome, evidence quality, constraint class,
uncertainty, material-change signal, timestamp, and provenance. `P_rep`
(recent repeated friction) and `Q_ev` (evidence informativeness) are calculated
at read time; they are not persisted as unexplained truth.

Unknown outcomes, uncertainty, and change state remain explicit. A material
change resets the prior observations used by the derived summary, because a
retry after changed conditions is not evidence that the old terrain persists.

## Commands

Validate the fixture:

```bash
python3 scripts/friction_ledger.py --check
```

Inspect derived summaries:

```bash
python3 scripts/friction_ledger.py --summary --half-life-hours 24
```

Append to a separate local ledger:

```bash
python3 scripts/friction_ledger.py --append --ledger var/friction.jsonl \
  --route provider/generate --task-family world-description \
  --context 'provider=v1;model=x;scope=scene' --outcome timeout \
  --evidence-quality strong --constraint-class dependency \
  --uncertainty low --changed no \
  --evidence-ref trace:request-123
```

The context text is stored only as a SHA-256 fingerprint. Notes and evidence
references must not contain credentials or secret payloads. A friction summary
may influence route cost inside an already-authorized lane, but cannot grant or
remove capabilities, widen scope, canonize an interpretation, or replace the
underlying evidence.

JSONL is intentionally the current storage boundary. SQLite migration remains
`intentionally_not_decided_yet`; reconsider it when measured trace volume,
concurrent writes, or query requirements outgrow append-only files.
