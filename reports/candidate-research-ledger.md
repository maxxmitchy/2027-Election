# Candidate Research Ledger

**Scale-up phase:** Gate 4 controlled research

**Rule:** Candidates are processed sequentially. A candidate must reach `VALIDATED` before the next candidate is started.

| Candidate | Identity | Candidacy | Party | Sources | Claims | Evidence | Reviews | Party History | Office History | Election History | Public Statements | Related Public Conversation | Economic | Legal | Contradictions | Corrections | Uncertainty | Validation | CI | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bola Ahmed Tinubu | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | PASS | PASS | PUBLISHED |
| Peter Gregory Obi | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | PENDING | PENDING | RESEARCH_COMPLETE |

## Candidate status vocabulary

- `NOT_STARTED` — no research work has begun.
- `IN_PROGRESS` — controlled research is underway; the dossier is not yet eligible for validation.
- `RESEARCH_COMPLETE` — substantive research is complete and ready for acceptance testing.
- `VALIDATION_EXECUTED` — acceptance testing has run against a specific commit; result may be pass or fail.
- `VALIDATION_FAILED` — acceptance testing found a defect or unresolved requirement.
- `VALIDATED` — candidate dossier passed candidate-specific acceptance testing against a specific tested commit.
- `PUBLISHED` — validated dossier approved for public retrieval.

## Generalized validation execution

The common Gate 4 validator is parameterized by `CANDIDATE_ID` and the CI workflow runs a matrix containing Tinubu and Peter Obi. The candidate fixture is the variable; the validation rules remain common. PostgreSQL runtime is executed independently for each matrix candidate.

**Tinubu regression:** commit `d22adfd03470046fb72644109dcac6a1f203e4e8`, run `33321495059`, job `99284136280`, **16 passed / 0 failed**, PostgreSQL 16.15, Python 3.12.14, artifact `9735008294`.

**Peter Obi first execution:** commit `d22adfd03470046fb72644109dcac6a1f203e4e8`, run `33321495059`, job `99284136184`, **10 passed / 6 failed**, PostgreSQL 16.15, Python 3.12.14, artifact `9735007675`. Those failures exposed incomplete research requirements and were not converted into false claims or architecture changes.

## Peter Obi research completion

The six requirements exposed by the first Gate 4 execution are now represented in the candidate fixture without changing the common validator:

1. **Reproducible quantitative calculation:** DMO 2013 domestic-debt observations are versioned and used to calculate Anambra's share of the 36 States + FCT reported domestic debt stock.
2. **Causal classification:** the debt-causation proposition is explicitly classified `INSUFFICIENT_EVIDENCE`; temporal sequence is not treated as causal proof.
3. **Correction lineage:** the Anambra debt assessment preserves V1 and records a V2 changed evidentiary assessment distinguishing borrowing/bond issuance from debt stock outstanding.
4. **Review records:** evidence quality, factual accuracy, calculation accuracy, context completeness, source quality and reviewer confidence are separately represented.
5. **Ten public answers:** a candidate-specific ten-answer fixture is stored with exact claim/evidence/source dependencies.
6. **Retrieval failure:** the unavailable primary INEC result capture is recorded as `UNAVAILABLE` / `UNKNOWN`, explicitly not as false.

The Anambra fiscal material preserves source definitions, period, geography and scope. The record does not convert the DMO debt stock into a causal judgment about Obi. Related public conversation records distinguish account identity and statement occurrence from truth of substantive claims.

Peter Obi is now `RESEARCH_COMPLETE` and is eligible for the unchanged Gate 4 matrix rerun. He is **not yet VALIDATED**.

## Scale-control rule

Do not start another candidate while the current candidate is `IN_PROGRESS`, `RESEARCH_COMPLETE`, `VALIDATION_FAILED`, or `VALIDATION_EXECUTED`, except where an explicit research exception is recorded.

## Current controlled candidate

**Peter Gregory Obi**

Selected because his record introduces materially different research conditions from the Tinubu pilot: a former state governor rather than a current federal officeholder; a 2003 governorship whose legal history altered the eventual officeholding outcome; multiple party transitions (APGA → PDP → Labour Party → ADC → NDC); a 2023 presidential candidacy on Labour Party; and a current 2027 presidential candidacy on NDC. These features stress temporal party membership, judicially determined officeholding, candidacy/result normalization, contradictory fiscal claims, and social-media provenance.

## Gate discipline

No mass candidate ingestion is authorized by this ledger. Only one additional candidate is active at a time.
