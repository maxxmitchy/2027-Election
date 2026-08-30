# Query Interpretation Validation

## Scope

Phase 2 adds deterministic natural-language interpretation above the validated retrieval system. No Candidate 4 work and no LLM dependency were introduced.

## Acceptance coverage

- Natural-language interpretation: implemented.
- Stable candidate entity resolution: implemented for the three validated IDs.
- Candidate isolation: explicit scope extraction; no candidate is inferred for general Nigeria questions.
- Temporal interpretation: explicit years/ranges and as-of expressions are parsed.
- Operation classification: factual, timeline, comparison, count, change, causal attribution, public conversation and provenance paths are recognized.
- Causal detection: causal constructions map to `CAUSAL_ATTRIBUTION`; no truth claim follows from language.
- Ambiguity: broad unsupported scope returns `PARTIALLY_INTERPRETED`.
- Subjective rejection: ranking/evaluation questions return `UNSUPPORTED`.
- Comparison safety: comparison scope is explicit and compatibility remains downstream.
- Public conversation: statement lookup is distinct from factual assessment.
- Provenance: raw question and interpretation metadata are retained in the structured contract.
- Reproducibility: identical input produces identical interpretation.
- Deterministic retrieval boundary: interpreter is separate from factual retrieval.

## Golden semantics

The test suite includes semantic-equivalence variants for vote questions, candidate aliases, causal language, administration-vs-causation, public conversation, subjective questions, broad ambiguity, general economic questions, adversarial instructions, comparison and reproducibility.

## Mutation sensitivity

The implementation is prepared for mutation testing of candidate resolution, causal detection, temporal constraints, operation classification, ambiguity rejection, subjective rejection, provenance and raw-question isolation. The final CI mutation output is authoritative and is not transferred from an earlier run.

## Limitations

The first interpreter is intentionally narrow and deterministic. It is not unrestricted natural-language understanding. Questions outside the supported vocabulary are surfaced as partially interpreted or unsupported rather than guessed. Full integration of interpreted queries into every retrieval operation remains subject to the final CI demonstration.
