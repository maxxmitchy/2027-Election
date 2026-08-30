# Gate 4 — Candidate Research Acceptance Test

## Status

**GATE 4 — EXECUTION IN PROGRESS / NOT YET PASSED**

This report records the controlled pilot dossier for **Bola Ahmed Tinubu** and the exact evidence required to determine whether the pilot passes Gate 4. It must not be treated as a CI PASS until the Gate 4 workflow executes successfully against the final commit and records its checked-out HEAD.

## Pilot selection

Bola Ahmed Tinubu was selected because one real subject exercises multiple normalized dimensions without requiring mass population: person/candidacy separation, historical party affiliation, multiple offices, multiple elections, a presidential election result with an official INEC anchor, executive policy events, economic observations, legal records, social-media statement provenance, contradictory/qualifying evidence, corrections and uncertainty.

Current-status verification was performed against State House and APC records on 30 August 2026. State House records Tinubu as President and publishes his May 2026 acceptance of the APC nomination for the 2027 election. INEC's 2023 election report provides the primary electoral result used in this pilot.

## Evidence model exercised

The pilot implements:

`PERSON → CANDIDACY → ELECTION → ELECTION RESULT`

`PERSON → PARTY MEMBERSHIP`

`PERSON → OFFICEHOLDING → OFFICE → ADMINISTRATION`

`CLAIM → EVIDENCE → SOURCE → RETRIEVAL EVENT`

`OBSERVATION → CALCULATION → CLAIM / ANSWER`

## Key acceptance checks

| Check | Status before CI |
|---|---|
| Person/candidacy separation | IMPLEMENTED |
| Party chronology | IMPLEMENTED |
| Office chronology | IMPLEMENTED |
| Election/result relationship | IMPLEMENTED |
| Official 2023 electoral anchor | IMPLEMENTED |
| Source provenance | IMPLEMENTED |
| Social-media statement semantics | IMPLEMENTED |
| Economic observation lineage | IMPLEMENTED |
| Temporal calculations | IMPLEMENTED |
| Causal classification | IMPLEMENTED |
| Qualifying/contradictory evidence | IMPLEMENTED |
| Correction lineage | IMPLEMENTED |
| Review dimensions | IMPLEMENTED |
| Ten public-answer fixtures | IMPLEMENTED |
| PostgreSQL runtime check | IMPLEMENTED |
| Gate 4 CI execution | SPECIFIED / NOT YET EXECUTED |

## Economic pilot

NBS records headline inflation at 21.34% in December 2022 and 28.92% in December 2023. The controlled calculation is 28.92 − 21.34 = **7.58 percentage points**. NBS records January 2024 headline inflation at 29.90%, giving a further **0.98 percentage-point** increase from December 2023.

These are temporal/observed changes. The pilot explicitly classifies the proposition that Tinubu's presidency caused the change as **INSUFFICIENT_EVIDENCE** rather than inferring causation from chronology.

NBS reports 2023 real GDP growth of 2.74%. DMO reports total public debt of ₦97.341 trillion at 31 December 2023. CBN documents the June 2023 FX-market reform separately from exchange-rate outcomes. These records preserve definition, unit, geography, period and source provenance.

## Social media

The pilot uses an original `@officialABAT` X post as evidence of a statement occurrence. Its evidence relationship is `DIRECTLY_ESTABLISHES_STATEMENT_OCCURRENCE`. It is not represented as evidence that the proposition contained in the post is objectively true.

## Legal record

The pilot includes SC/CV/501/2023 and separates litigation allegations from the judicial/procedural outcome. The record is based on an inspected reproduction of the case record, with the limitation that a primary court-hosted copy is preferred if subsequently located.

## Contradictory / qualifying evidence

The pilot preserves different assessments rather than selecting a preferred narrative. Official statements describe reform progress; the IMF independently records improved macroeconomic outcomes while also documenting difficult living conditions, poverty and food insecurity. Reuters similarly reports the administration's stabilization claim alongside the cost-of-living squeeze. These are retained as distinct evidence relationships and evaluated as contextual/qualifying evidence.

## Correction test

The pilot includes a controlled correction lineage:

`CLAIM v1 → CORRECTION → CLAIM v2`

The original remains present and the correction records its reason and predecessor.

## Retrieval failure

A controlled unavailable-source fixture is represented as `RETRIEVAL_FAILURE` with truth status `UNKNOWN`. Unavailability is never interpreted as falsity.

## Machine-readable records

- `candidates/bola-ahmed-tinubu/data/pilot-record.json`
- `candidates/bola-ahmed-tinubu/data/public-answers.json`
- `tests/gate4_candidate_acceptance.py`
- `tests/gate4_postgres_runtime.py`
- `.github/workflows/gate4-candidate-research.yml`

## CI evidence

**Final tested commit:** to be populated from the workflow's `git rev-parse HEAD` output.

**Workflow:** `Gate 4 Candidate Research`

**Run:** pending execution evidence

**Job:** pending execution evidence

**Artifact:** pending execution evidence

No Gate 4 PASS is claimed until those fields are populated by actual CI execution.
