# Phase 3 — Evidence Answer Experience

The answer experience is a deterministic presentation layer over the existing query interpreter and retrieval system. It does not decide truth.

## Boundary

Natural language interprets → structured query → deterministic retrieval → evidence → answer presentation.

`answer_experience.py` calls `query_interpreter.interpret_and_validate()` and routes only supported semantic shapes into the existing `system_demo.answer_question()` retrieval functions. It does not contain a parallel factual database.

## Answer states

The contract preserves `ANSWERED`, `PARTIALLY_ANSWERED`, `UNKNOWN`, `UNVERIFIED`, `DISPUTED`, `INSUFFICIENT_EVIDENCE`, `INCOMPLETE`, `INCOMPARABLE`, `NO_MATCH`, and `UNSUPPORTED` as distinct states.

No negative state is rewritten as `FALSE`.

## Why this answer

The presentation includes the interpreted query, candidate scope, domain/entity, period, geography, operation, retrieved evidence, calculations, qualifications, methodology and limitations. This makes the route from question to answer inspectable without allowing the presentation layer to invent a conclusion.

## Evidence chain

Factual: answer → claim → evidence → source.

Quantitative: answer → result/analysis → calculation → observation → dataset/version → source/version.

Public conversation: answer → preserved statement/artifact → source/retrieval event. A statement occurrence is not independent proof of its proposition.

## Source and claim inspection

Source metadata is surfaced where it exists, including tier/type/date/URL/availability and limitations. Source tier is never treated as automatic truth.

Claims retain status, evidence references, contradictions/qualifications and version identifiers.

## Negative knowledge

No match, unknown, unverified, disputed, insufficient evidence, incomplete and incomparable are presented as different conditions. Absence of a record is not converted into proof of non-occurrence.

## Historical `as_of`

The interpreted `as_of` value is carried into the answer contract and retrieval request. The product does not silently substitute present-day state for a historical request.

## Review separation

Review information is explicitly marked `NOT_A_SOURCE` in the current retrieval layer. Reviewer assessment is therefore not displayed as underlying evidence.

## Reproducibility

The answer contains a content-derived query ID, interpreted query, database snapshot hash, methodology version and generation metadata. Runtime performance is recorded separately from deterministic answer content.

## Validation state

The checked-in Phase 3 validation report remains `UNTESTED` until a dedicated CI run evaluates the exact implementation commit. A prior Phase 2 PASS is not reused as Phase 3 evidence.

## Future language models

An LLM could later be placed before this module as an optional interface. Its only permitted output would be a validated structured query. Retrieval and evidence assessment would remain deterministic.
