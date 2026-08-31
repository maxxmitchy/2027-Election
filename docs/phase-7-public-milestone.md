# Phase 7 — Research Investigation & Dossier Assembly

## Public milestone language

**IMPLEMENTED:** Deterministic research investigations, dossier assembly, immutable version metadata, claim provenance, research-gap integration, review queues, dossier diffs, snapshots and historical/as-of controls are implemented as the orchestration layer above the Phase 5 Research Workbench and Phase 6 Evidence Acquisition systems.

**EXECUTED:** The controlled Phase 7 CI workflow executes representative investigations for the three validated candidates, assembles standardized dossiers, performs a controlled V1 → V2 evidence update, rebuilds a dossier at multiple as-of dates, produces deterministic diffs and snapshots, and executes the Phase 7 mutation audit.

**VALIDATED:** Validation requires Phase 3, Phase 4, Phase 5 and Phase 6 regressions plus Phase 7 investigation, assembly, historical, diff, snapshot, review-queue, schema, candidate-isolation and mutation gates in the same exact CI execution.

**PASS:** Phase 7 must not be described as PASS until the actual Phase 7 CI run has passed all fail-closed gates and produced the required evidence artifact.

The governing boundary remains:

> A dossier is a derived research product.
>
> The evidence database remains the source of truth.
>
> A dossier is not a biography.
>
> Discovery is not verification.
>
> Source is not evidence.
>
> Evidence is not review.
>
> Statement is not truth.
>
> Retrieval failure is not falsity.
>
> Missing evidence is not negative evidence.
>
> Temporal association is not causation.
