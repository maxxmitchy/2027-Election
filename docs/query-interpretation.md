# Natural-Language Query Interpretation

The Evidence Product now separates language interpretation from factual determination.

## Boundary

Natural language may identify people, topics, periods, geography, operations, comparison scope and requested evidence type. It never determines truth, causation, source correctness, candidate quality or allegation status.

## Pipeline

USER QUESTION → INTERPRETER → STRUCTURED QUERY → VALIDATION → DETERMINISTIC RETRIEVAL → EVIDENCE → ANSWER

The interpreter has no LLM dependency and does not replace the retrieval engine.

## Entity resolution

Candidate aliases resolve to stable candidate IDs: `bola-ahmed-tinubu`, `peter-gregory-obi`, and `atiku-abubakar`. Candidate scope may also be empty for questions about Nigeria generally.

## Time

Explicit years and ranges are converted to structured temporal constraints. Ambiguous broad temporal language is surfaced rather than silently guessed.

## Administration vs causation

A phrase such as “during Tinubu's presidency” establishes temporal/administrative scope. Causal constructions such as “did Tinubu cause” select `CAUSAL_ATTRIBUTION`. The retrieval/evidence layer determines whether causation is established.

## Ambiguity and subjectivity

Broad questions may return `PARTIALLY_INTERPRETED`. Subjective rankings such as “best candidate” return `UNSUPPORTED` unless a validated methodology defines the measure.

## Public conversation

Questions asking what a person said are classified as `PUBLIC_CONVERSATION`; statements are not treated as independent proof. Questions asking whether the statement was true require evidence assessment instead.

## Provenance

The structured query preserves the raw question, resolved scope, interpretation status, ambiguities, unsupported elements and methodology version. Future optional LLM integration must produce only this structured representation and remain subject to validation before deterministic retrieval.

## Scope

This phase does not introduce Candidate 4, mass ingestion, political ranking, or an LLM factual engine.
