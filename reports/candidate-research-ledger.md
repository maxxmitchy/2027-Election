# Candidate Research Ledger

**Scale-up phase:** Gate 4 controlled research — Round 2

**Rule:** Candidates are processed sequentially. A candidate must reach `VALIDATED` before the next candidate is started.

| Candidate | Identity | Candidacy | Party | Sources | Claims | Evidence | Reviews | Party History | Office History | Election History | Public Statements | Related Public Conversation | Economic | Legal | Contradictions | Corrections | Uncertainty | Validation | CI | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bola Ahmed Tinubu | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | PASS | PASS | PUBLISHED |
| Peter Gregory Obi | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | PASS | PASS | VALIDATED |
| Atiku Abubakar | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | NOT_STARTED | NOT_STARTED | RESEARCH_COMPLETE |

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

## Atiku research completion

Atiku's standardized dossier is now **RESEARCH_COMPLETE**. The machine-readable fixture contains temporal party memberships, officeholdings, candidacies, primary contests, official election-result anchors, sources, retrieval events, evidence relationships, quantitative observations/calculations, causal classification, contradictions, correction lineage, uncertainty states, review dimensions, RELATED PUBLIC CONVERSATION records, and a ten-answer provenance fixture.

The Adamawa record explicitly distinguishes elected governor/governor-elect from sworn officeholder. The ADC record preserves the June 15 Federal High Court order, June 16 stay, July 2 leadership judgment, and July 28 appellate nullification as separate legal events. The dossier does not collapse those events into a binary deregistration label.

## Current controlled candidate

**Atiku Abubakar — RESEARCH_COMPLETE**

Candidate 4 remains blocked. No Candidate 4 research, ingestion or validation has begun.

## Gate discipline

The common validator remains unchanged. The workflow matrix now contains Tinubu, Peter Obi and Atiku. Atiku has **not** been marked `VALIDATED`; CI evidence must establish the independent result before that transition can occur. A Candidate 3 failure must remain visible and must not be hidden by altering common acceptance criteria.
