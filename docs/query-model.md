# Query Model

The structured query is the contract between natural-language interpretation and deterministic retrieval. The interpreter resolves language only; it does not decide truth, causation, source correctness, candidate quality, or allegation status.

The contract is defined in `schemas/query.schema.json` and includes candidate/person scope, domain, entity, operation, geography, time range, as-of state, comparison scope, evidence type, causal request, requested output, interpretation status, ambiguities, unsupported elements and methodology version.

Pipeline:

USER QUESTION → INTERPRETER → STRUCTURED QUERY → VALIDATION → DETERMINISTIC RETRIEVAL → EVIDENCE → ANSWER

The existing retrieval engine remains the factual authority. The language layer cannot reinterpret a structured query after validation.
