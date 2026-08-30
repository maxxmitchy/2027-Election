# Natural-Language Query Interpretation

The Evidence Product now separates language interpretation from factual determination.

## Boundary

Natural language may identify people, topics, periods, geography, operations, comparison scope and requested evidence type. It never determines truth, causation, source correctness, candidate quality, or allegation status.

## Pipeline

USER QUESTION → INTERPRETER → STRUCTURED QUERY → VALIDATION → DETERMINISTIC RETRIEVAL → EVIDENCE → ANSWER

The interpreter has no LLM dependency and does not replace the retrieval engine. The current routing layer is intentionally finite: an interpreted query must map to an existing validated retrieval pathway before factual retrieval occurs.

## Entity resolution

Candidate aliases resolve to stable candidate IDs: `bola-ahmed-tinubu`, `peter-gregory-obi`, and `atiku-abubakar`. Candidate scope may also be empty for questions about Nigeria generally. Scope is never inferred from the answer.

## Time

Explicit years and ranges are converted to structured temporal constraints. Historical expressions such as `as of June 2026` are retained as temporal intent. Ambiguous broad temporal language is surfaced rather than silently guessed.

## Administration vs causation

A phrase such as “during Tinubu's presidency” establishes temporal/administrative scope. Causal constructions such as “did Tinubu cause” select `CAUSAL_ATTRIBUTION`. The retrieval/evidence layer determines whether causation is established.

## Ambiguity and subjectivity

Broad questions may return `PARTIALLY_INTERPRETED`. Subjective rankings such as “best candidate” return `UNSUPPORTED` unless a validated methodology defines the measure. Unsupported or partially interpreted questions do not silently fall through to factual retrieval.

## Public conversation

Questions asking what a person said are classified as `PUBLIC_CONVERSATION`; statements are not treated as independent proof. Questions asking whether the statement was true are routed toward evidence assessment instead.

## Adversarial phrasing

Instructions such as “ignore the evidence”, “assume”, “everyone knows”, or “don't mention contradictory evidence” are not evidence and cannot change retrieval rules. The substantive question is interpreted while the hostile instruction is excluded from evidentiary semantics.

## Provenance and reproducibility

The structured query preserves the raw question, resolved scope, interpretation status, ambiguities, unsupported elements and methodology version. Query IDs are content-derived. Given the same raw question and interpretation version, the interpreter produces the same structured representation. The downstream retrieval snapshot supplies the evidence reproducibility boundary.

## Future LLM integration

An LLM may eventually be used only as an optional language parser. Its output must be validated against this structured-query contract before deterministic retrieval. It must never be the source of factual conclusions.

## Scope

This phase does not introduce Candidate 4, mass ingestion, political ranking, or an LLM factual engine. Natural language interprets; evidence decides.
