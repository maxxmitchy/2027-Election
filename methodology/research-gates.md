# Research Gates

The research gate is a fail-closed progression. A later gate MUST NOT be treated as open because a preceding document says it is ready; its acceptance evidence must exist.

| Gate | Objective | Prerequisites | Required tests | Acceptance | Approver | Prohibited before approval |
|---|---|---|---|---|---|---|
| GATE 0 — ARCHITECTURE | Establish bounded canonical model and provenance principles | none | architecture review | independent architectural review passes | independent Reviewer | production ingestion |
| GATE 1 — MODEL VALIDATION | Prove scenarios are representable without semantic ambiguity | Gate 0 | Round 3/4 scenario suite | all required conceptual cases represented; weaknesses recorded | independent Reviewer | real research population |
| GATE 2 — RUNTIME INTEGRITY | Prove executable implementation enforces critical invariants | Gate 1 | PostgreSQL attacks, bitemporal queries, dependency engine, schema CI, property tests | independent Reviewer accepts accumulated execution evidence and explicitly records any evidence qualification | independent Reviewer | candidate research |
| GATE 3 — SOURCE INGESTION | Prove controlled ingestion preserves provenance and revisions | Gate 2 | source/retrieval/hash fixtures, ingestion rollback/correction tests | real public artifacts ingested; provenance, temporal semantics, evidence typing, contradiction, correction and retrieval failure behavior demonstrated by reproducible execution | ingestion reviewer + independent Reviewer | candidate research conclusions |
| GATE 4 — CANDIDATE RESEARCH | Permit bounded candidate information population | Gate 3 | candidate-specific provenance/review tests | every material candidate assertion traceable and reviewable | research lead + independent Reviewer | unrestricted publication |
| GATE 5 — PUBLIC RETRIEVAL | Permit external retrieval/API views | Gate 4 | retrieval reproducibility, stale-answer, access-layer tests | public outputs are traceable and stale-safe | independent Reviewer | unsourced public claims |
| GATE 6 — PUBLIC REVIEW | Permit formal public-review operation | Gate 5 | audit/review workflow tests | review corrections are versioned and auditable | independent Reviewer | bypassing correction/review process |

## Runtime gate rule

GATE 2 may be opened only by explicit independent Reviewer risk acceptance when the accumulated execution evidence is strong but one non-blocking evidence-to-commit limitation remains documented. That qualification MUST NOT be rewritten as a clean CI result for the affected commit.

Application-level refusal is not equivalent to database enforcement where direct database writes are in scope.

## Current state

**GATE 2 — OPEN WITH DOCUMENTED EVIDENCE QUALIFICATION.** The independent Reviewer accepted the accumulated runtime evidence while recording that commit `1c1dbc14dafd4b27e80aeaf86e496a23ae86d784` does not have a clean CI execution. No claim is made that it does.

**GATE 3 — CONTROLLED SOURCE INGESTION COMPLETE.** A reproducible real-world ingestion experiment has been executed against commit `b26cccd58b9e6ea1c8e28ecbdd8affe5ea162328` in GitHub Actions run `33319986354`, job `99280145039`. The controlled experiment is not candidate research.

No candidate dossiers, candidate claims, administrations, elections or political research have been populated. Candidate research remains prohibited until Gate 4 approval.
