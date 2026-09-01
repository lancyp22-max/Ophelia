# Memory Source Provenance v0.1

Status: accepted architectural rule. Runtime/schema enforcement is intentionally deferred.

## Purpose

Lumaria must not assume that a textual summary exhausts the observation, record,
or representation from which it was derived.

Two compact rules govern this layer:

`summary_of(X) != X`

`representation_type != authority`

Provenance describes lineage. It does not rank truth, create authority, expand
retention, or grant permission to collect additional material.

## Minimal provenance classes

When the source relationship is actually known, a memory or record may carry one
of these descriptive classes:

- `observed_directly` — the stored representation is the originating
  observation available to the recording process.
- `textualized_from_observation` — prose or structured text was produced from
  a non-text or richer originating observation.
- `summary_of_prior_record` — the representation condenses an already existing
  record rather than the originating observation.

If the relationship is not established, record `unknown`. Do not infer a
provenance class from confidence, familiarity, fluency, or role.

## Governance boundary

This rule is metadata-only at v0.1.

- A provenance label cannot authorize collection or persistence.
- A provenance label cannot canonize content.
- `textualized_from_observation` does not authorize retention of the source
  image, audio, sensor stream, or other originating material.
- A summary remains a transformation of a source even when it is accurate.
- Missing source material must not be silently reconstructed and presented as
  the original.
- Richer representation is not evidence of identity continuity, consciousness,
  or higher authority.
- No memory node becomes authoritative merely because it holds more modalities.

Existing consent, capability, retention, and canonization gates remain unchanged.

## Transformation lineage

Future versions may add a `source_relation` or `transformation_receipt` that
records how one representation was derived from another. Exact fields,
retention behavior, and cross-modal storage rules are
`intentionally_not_decided_yet`.

The important invariant is already fixed:

> Preserve the distinction between the originating record and a transformation
> of that record.

## Initial evaluation target

Before any dual-channel or multimodal persistence is considered, test whether
the provenance distinction improves auditability using records that are already
authorized to exist.

A successful test should make it easier to answer:

1. What representation originated this record?
2. Was this item transformed or summarized?
3. Can the source still be inspected?
4. What information may have been lost in transformation?
5. Does any downstream claim incorrectly treat the transformed record as the
   complete source?

No new storage behavior follows from a successful test. Any persistence change
requires separate human approval.
