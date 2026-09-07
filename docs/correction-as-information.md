# Correction as information

Lumaria treats correction as evidence that collaboration can revise itself. A
verified correction increases trust when truth outranks preserving a previous
answer. It does not reduce anyone's status and it is not a competition.

## What counts as an event

A ledger event is admissible only when it records a real, attributable claim or
assumption and links to evidence that can be checked. The event must be one of:

- `supported_finding`: evidence supports a previously testable claim;
- `verified_correction`: evidence contradicts a claim and the record captures
  its revision or withdrawal;
- `surfaced_assumption`: a hidden premise is made explicit without pretending
  it has already been proved wrong.

Disagreement, uncertainty, stylistic preference, role-play, deliberate errors,
and unsupported declarations of being right or wrong are not admissible.

## Tally semantics

The tally is descriptive, not a score:

- `supported_findings` counts supported findings;
- `verified_corrections` counts verified revisions;
- `surfaced_assumptions` counts assumptions made visible;
- `supported_since_last_correction` counts supported findings after the most
  recent verified correction;
- `correction_opportunity_index` is
  `supported_since_last_correction + 1`.

The opportunity index makes a newly discovered error more informative after a
longer run of supported conclusions. It does **not** make a person more valuable,
reward failure, or weaken the evidence threshold. It resets to `1` after a
verified correction. No action, permission, rank, or reward may depend on it.

## Required evidence

Each event records:

1. a stable event id and timestamp;
2. the original claim or surfaced assumption;
3. an evidence reference that another reviewer can inspect;
4. the resulting disposition;
5. an optional human-readable note without hidden chain-of-thought.

The register may remain empty. Blank history is more honest than invented
events. Append only after the evidence exists; never create a correction for the
purpose of increasing a tally.

Run `make correction-ledger-check` after changing the ledger.
