# Candidate Research Ledger

**Scale-up phase:** Gate 4 controlled research

**Rule:** Candidates are processed sequentially. A candidate must reach `VALIDATED` before the next candidate is started.

| Candidate | Identity | Candidacy | Party | Sources | Claims | Evidence | Reviews | Party History | Office History | Election History | Public Statements | Related Public Conversation | Economic | Legal | Contradictions | Corrections | Uncertainty | Validation | CI | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bola Ahmed Tinubu | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | PASS | PASS | PUBLISHED |
| Peter Gregory Obi | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | NOT_STARTED | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | NOT_STARTED | VALIDATION_EXECUTED | FAILED | VALIDATION_FAILED |

## Candidate status vocabulary

- `NOT_STARTED` — no research work has begun.
- `IN_PROGRESS` — controlled research is underway; the dossier is not yet eligible for validation.
- `RESEARCH_COMPLETE` — substantive research is complete and ready for acceptance testing.
- `VALIDATION_FAILED` — acceptance testing found a defect or unresolved requirement.
- `VALIDATED` — candidate dossier passed candidate-specific acceptance testing against a specific tested commit.
- `PUBLISHED` — validated dossier approved for public retrieval.

## Generalized validation execution

The common Gate 4 validator is now parameterized by `CANDIDATE_ID` and the CI workflow runs a matrix containing Tinubu and Peter Obi. The candidate fixture is the variable; the validation rules remain common. The PostgreSQL runtime is also executed independently for each matrix candidate.

**Tinubu regression:** tested commit `d22adfd03470046fb72644109dcac6a1f203e4e8`, workflow run `33321495059`, job `99284136280`, **16 passed / 0 failed**, PostgreSQL 16.15, Python 3.12.14, artifact `9735008294`.

**Peter Obi execution:** tested commit `d22adfd03470046fb72644109dcac6a1f203e4e8`, workflow run `33321495059`, job `99284136184`, **10 passed / 6 failed**, PostgreSQL 16.15, Python 3.12.14, artifact `9735007675`. The failures are classified as incomplete research, not false propositions or an architectural failure.

### Peter Obi missing acceptance requirements exposed by execution

1. reproducible quantitative calculation;
2. causal-classification record;
3. correction lineage;
4. review records;
5. ten public answers with exact dependencies;
6. retrieval-failure/unavailable-source state.

Peter Obi therefore remains `VALIDATION_FAILED` / research incomplete and must not be marked `VALIDATED` until these records are completed and the matrix is rerun.

## Scale-control rule

Do not start another candidate while the current candidate is `IN_PROGRESS`, `RESEARCH_COMPLETE`, or `VALIDATION_FAILED`, except where an explicit research exception is recorded.

## Current controlled candidate

**Peter Gregory Obi**

Selected because his record introduces materially different research conditions from the Tinubu pilot: a former state governor rather than a current federal officeholder; a 2003 governorship whose legal history altered the eventual officeholding outcome; multiple party transitions (APGA → PDP → Labour Party → ADC → NDC); a 2023 presidential candidacy on Labour Party; and a current 2027 presidential candidacy on NDC. These features stress temporal party membership, judicially determined officeholding, candidacy/result normalization, contradictory fiscal claims, and social-media provenance.

## Gate discipline

No mass candidate ingestion is authorized by this ledger. Only one additional candidate is active at a time.
