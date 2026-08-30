# Corrections, Invalidation and Historical Integrity

A correction changes the evidentiary state; it does not erase history.

## Correction record

A material correction should identify the affected entity/version, previous version, new version, reason, supporting evidence, actor, reviewer when applicable, timestamp and Git commit. The correction type should be explicit: factual, source, calculation, context, classification, methodological, or source-revision.

## Dependency effects

If a corrected observation or source changes a calculation input, dependent calculations and downstream results become `stale` or `invalid` until recomputed. Recalculation creates new versions using the corrected dependencies. The old derived records remain available for historical reconstruction.

## Historical questions

Two time axes matter:

- **Valid time:** when the represented fact/measurement applied in the world.
- **Transaction time:** when the repository/database accepted a version.

`as_of` retrieval should resolve records by transaction time; date-specific factual questions should also evaluate valid time.
