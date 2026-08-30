# AI Retrieval Contract

The eventual retrieval API should return concise answers with traceable structured support.

## Canonical response shape

```text
ANSWER
[Direct answer]

EVIDENCE
[Relevant claims, observations and evidence references]

CALCULATION
[Formula and source values, when applicable]

SOURCES
[Stable source identifiers and URLs]

CONFIDENCE
[Assessment and rationale]

CONTEXT / LIMITATIONS
[Only material limitations]

DATABASE VERSION
[Version identifier / retrieval timestamp]
```

## Retrieval rules

1. Retrieve structured records first.
2. Resolve each material assertion to evidence.
3. Prefer the latest valid version while preserving historical query support.
4. Use the requested date/period rather than silently substituting current information.
5. Return calculations from stored observations, not opaque generated arithmetic.
6. Distinguish observed facts from allegations, statements, analysis and causal claims.
7. Expose uncertainty when evidence is incomplete or disputed.

## Historical queries

The API should support an `as_of` concept so a question can reconstruct the valid record set at a historical timestamp. The current database state must not be the only retrievable state.
