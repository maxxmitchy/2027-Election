# Candidate Research Ledger

**Scale-up phase:** Gate 4 controlled research — Round 2

**Rule:** Candidates are processed sequentially. A candidate must reach `VALIDATED` before the next candidate is started.

| Candidate | Identity | Candidacy | Party | Sources | Claims | Evidence | Reviews | Party History | Office History | Election History | Public Statements | Related Public Conversation | Economic | Legal | Contradictions | Corrections | Uncertainty | Validation | CI | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bola Ahmed Tinubu | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | PASS | PASS | PUBLISHED |
| Peter Gregory Obi | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | PASS | PASS | VALIDATED |
| Atiku Abubakar | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | NOT_STARTED | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | IN_PROGRESS | NOT_STARTED | NOT_STARTED | IN_PROGRESS |

## Candidate status vocabulary

- `NOT_STARTED` — no research work has begun.
- `IN_PROGRESS` — controlled research is underway; the dossier is not yet eligible for validation.
- `RESEARCH_COMPLETE` — substantive research is complete and ready for acceptance testing.
- `VALIDATION_EXECUTED` — acceptance testing has run against a specific commit; result may be pass or fail.
- `VALIDATION_FAILED` — acceptance testing found a defect or unresolved requirement.
- `VALIDATED` — candidate dossier passed candidate-specific acceptance testing against a specific tested commit.
- `PUBLISHED` — validated dossier approved for public retrieval.

## Gate 4 Round 2 completion

Bola Ahmed Tinubu and Peter Gregory Obi independently passed the unchanged generalized Gate 4 validator at commit `1be31059ace0bed6ef31de11fe3389132b912d27`: **16 passed / 0 failed** each. Tinubu job `99285686044`; Obi job `99285686144`; workflow run `33322075297`.

The first Peter Obi execution at commit `d22adfd03470046fb72644109dcac6a1f203e4e8` remains permanently preserved as historical evidence: **10 passed / 6 failed**. The subsequent successful execution is separately identified by its own commit, job and artifact.

## Candidate 3 selection

**Selected candidate:** Atiku Abubakar (`atiku-abubakar`)

**Reason for selection:** methodological diversity, not political preference. Atiku introduces a federal vice-presidential record, a governor-elect-to-vice-president transition, a long sequence of presidential contests, federal policy/economic evidence and a live 2027 candidacy whose party/legal provenance requires temporal reconstruction.

**Difference from Tinubu:** Atiku's central executive record is the federal vice presidency rather than a state governorship followed by the presidency; his governor-elect status changed into a vice-presidential office before he took the governorship; and his presidential history spans substantially more contests and party configurations.

**Difference from Obi:** Atiku's core executive evidence is federal rather than state-governorship evidence; his office history has a governor-elect → vice-president transition rather than Obi's court-resolved Anambra governorship; and his current 2027 candidacy is on ADC rather than Obi's NDC. His dossier also introduces a substantially longer presidential-candidacy chronology.

**Expected research challenges:** long-span party/candidacy reconstruction; separation of primary contests from general-election candidacies; governor-elect versus officeholding semantics; federal economic/policy attribution; social-media provenance; reproducible quantitative evidence; and the 2026 ADC registration/leadership litigation and nomination record.

Selection details are recorded in `reports/candidate-3-selection.md`.

## Atiku initial research state

The standardized dossier has been opened at `candidates/atiku-abubakar/`. Initial research anchors cover identity, office history, presidential-election history, party history, 2027 candidacy, RELATED PUBLIC CONVERSATION, federal policy/economic research and the ADC legal record.

The 2027 ADC status is being treated as a temporal research problem. ADC and INEC-related records identify Atiku as its 2027 presidential candidate, while the 2026 deregistration litigation and related party leadership proceedings are retained as separate legal/procedural evidence. No single narrative is being promoted as fact before the underlying records are reconciled.

The machine-readable candidate scaffold is intentionally `IN_PROGRESS`. No validation claim has been made.

## Current controlled candidate

**Atiku Abubakar**

Candidate 4 remains blocked. No Candidate 4 research, ingestion or validation has begun.

## Gate discipline

Only Atiku Abubakar is active in this controlled-ingestion round. The generalized validator will be run only after the candidate's standardized research requirements are genuinely complete. A Candidate 3 failure must remain visible and must not be hidden by altering common acceptance criteria.
