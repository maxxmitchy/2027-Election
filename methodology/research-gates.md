# Research Gates

The research gate is a fail-closed progression. A later gate MUST NOT be treated as open because a preceding document says it is ready; its acceptance evidence must exist.

| Gate | Objective | Prerequisites | Required tests | Acceptance | Approver | Prohibited before approval |
|---|---|---|---|---|---|---|
| GATE 0 — ARCHITECTURE | Establish bounded canonical model and provenance principles | none | architecture review | independent architectural review passes | independent Reviewer | production ingestion |
| GATE 1 — MODEL VALIDATION | Prove scenarios are representable without semantic ambiguity | Gate 0 | Round 3/4 scenario suite | all required conceptual cases represented; weaknesses recorded | independent Reviewer | real research population |
| GATE 2 — RUNTIME INTEGRITY | Prove executable implementation enforces critical invariants | Gate 1 | PostgreSQL attacks, bitemporal queries, dependency engine, schema CI, property tests | all mandatory runtime tests PASS; no unresolved critical integrity findings | independent Reviewer | candidate/source ingestion |
| GATE 3 — SOURCE INGESTION | Prove controlled ingestion preserves provenance and revisions | Gate 2 | source/retrieval/hash fixtures, ingestion rollback/correction tests | provenance complete and fail-closed on broken references | ingestion reviewer + independent Reviewer | candidate research conclusions |
| GATE 4 — CANDIDATE RESEARCH | Permit bounded candidate information population | Gate 3 | candidate-specific provenance/review tests | every material candidate assertion traceable and reviewable | research lead + independent Reviewer | unrestricted publication |
| GATE 5 — PUBLIC RETRIEVAL | Permit external retrieval/API views | Gate 4 | retrieval reproducibility, stale-answer, access-layer tests | public outputs are traceable and stale-safe | independent Reviewer | unsourced public claims |
| GATE 6 — PUBLIC REVIEW | Permit formal public-review operation | Gate 5 | audit/review workflow tests | review corrections are versioned and auditable | independent Reviewer | bypassing correction/review process |

## Runtime gate rule

GATE 2 is closed if any mandatory test is `FAIL`, `UNTESTED`, or `PARTIAL` for a control that the acceptance matrix classifies as database-required, unless the independent Reviewer explicitly records a risk acceptance.

Application-level refusal is not equivalent to database enforcement where direct database writes are in scope.

## State

As of Round 5 implementation work, **GATE 2 remains CLOSED** until a successful CI run proves the PostgreSQL reference implementation and schema/property suite. No candidate research is permitted before GATE 4.
