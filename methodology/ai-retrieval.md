# AI Retrieval and Answer Provenance

An AI answer is a derived artifact, not a new source of truth.

## Required provenance

Every published answer should reference the exact claim versions, evidence versions, source versions, observation versions, calculation versions, analysis/result versions and methodology versions used to construct it. It should also record the database snapshot/version and generation timestamp.

## Canonical response

`ANSWER -> EVIDENCE -> CALCULATION -> SOURCES -> CONFIDENCE -> CONTEXT/LIMITATIONS -> DATABASE VERSION`

The machine-readable `ai-answer.schema.json` stores these references explicitly.

## Reproducibility

An answer is reproducible when every dependency resolves to an immutable version and the methodology versions are available. If a dependency is later corrected, the answer is marked stale/superseded and a new answer version may be generated.

## Historical retrieval

`as_of` is a transaction-time request: retrieve the versions that were validly recorded by that point. Date-specific questions may additionally use valid-time fields on the underlying records.

## Evidence discipline

The model must not cite a source merely because it appears in a retrieved document. Every material assertion must resolve to an evidence record explaining the source-to-claim relationship. A candidate statement establishes that the person made the statement; it does not establish the truth of the statement's underlying proposition.

## Calculations

For quantitative answers, return the calculation reference and its exact input versions. Do not rely on opaque generated arithmetic when a reproducible calculation record can be stored.
