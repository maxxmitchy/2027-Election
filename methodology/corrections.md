# Corrections and Historical Integrity

## Rule

Never silently rewrite a material historical record.

When a record changes materially, preserve the prior version and record the previous value/text, new value/text, change timestamp, reason, supporting evidence, proposer or system actor, reviewer when applicable, new version identifier and predecessor version identifier.

## Correction types

- `factual_correction`
- `source_correction`
- `calculation_correction`
- `context_correction`
- `classification_correction`
- `methodological_revision`
- `source_revision`

## Git and application history

Git commit history is the repository-level audit trail. Structured version records provide domain-level provenance so downstream databases and APIs can reconstruct what the system knew at a given time.

## Reproducibility

A correction should make it possible for a reviewer to identify both the old state and the evidence that justified the new state. Derived values should be recalculated from corrected source observations rather than manually patched.
