# Dependency and Revision Model

Derived records form a dependency graph rather than a flat chain.

`SOURCE / DATASET VERSION -> OBSERVATION -> CALCULATION -> ANALYSIS -> RESULT -> AI ANSWER`

Each derived record stores stable references to its direct inputs and the methodology version used. Dependencies are immutable references to specific record versions, not just entity IDs.

## Staleness

When an input version is corrected or superseded, dependent calculations/results are not silently rewritten. They are marked `stale` or `invalid` according to the correction semantics. A recomputation creates a new version with the corrected input versions.

## Impact analysis

The dependency graph must support reverse traversal: given a corrected source, observation, or methodology version, identify every downstream calculation, analysis, result and AI answer that depends on it.

## Reproducibility

A derived result is reproducible only when all referenced input versions and methodology versions remain resolvable. The answer record therefore stores its exact claim/evidence/source/calculation/observation/result references plus methodology and database versions.

## No silent cascade

A corrected input never silently mutates downstream records. The system creates an explicit invalidation/staleness event and then, if appropriate, a new derived version.
