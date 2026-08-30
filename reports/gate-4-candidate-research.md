# Gate 4 — Candidate Research Acceptance Test

## Status

**GATE 4 — PASS RECOMMENDED**

The single controlled pilot dossier for **Bola Ahmed Tinubu** has been executed through the Gate 4 acceptance workflow. The PASS is tied to the exact source commit below; later repository commits do not inherit this execution evidence.

## Execution evidence

- **TESTED COMMIT:** `4ee713dd1c50829ff11742a31dbc56b7a5953dc0`
- **WORKFLOW:** `Gate 4 Candidate Research`
- **WORKFLOW RUN:** `33320688303`
- **JOB:** `99282001594`
- **RESULT:** `success`
- **RUNNER:** Ubuntu 24.04.4 LTS
- **PYTHON:** 3.12.14
- **POSTGRESQL:** 16.15
- **PYTEST:** 8.4.2
- **TESTS:** 15 passed, 0 failed
- **ARTIFACT:** `gate4-candidate-research-evidence-c7837a0f909216a133eb02c413fd48df96f44f02`
- **ARTIFACT ID:** `9734793770`
- **ARTIFACT ZIP SHA-256:** `6f39eef65112170e762409114ad37af2286fc7207254e68aafb97f26e89a1076`

The workflow log independently shows `actions/checkout` using ref `4ee713dd1c50829ff11742a31dbc56b7a5953dc0` and `git rev-parse HEAD` returning the same SHA. PostgreSQL initialization, pilot fixture loading, test execution and artifact upload all completed successfully.

## Pilot selection

Bola Ahmed Tinubu was selected because one real subject exercises multiple normalized dimensions without requiring mass population: person/candidacy separation, historical party affiliation, multiple offices, multiple elections, a presidential election result with an official INEC anchor, executive policy events, economic observations, legal records, social-media statement provenance, qualifying evidence, corrections and uncertainty.

Current-status verification was performed against State House and APC records on 30 August 2026. State House records Tinubu as President and publishes his May 2026 acceptance of the APC nomination for the 2027 election. INEC's 2023 election report provides the primary electoral result used in this pilot.

## Evidence model exercised

`PERSON → CANDIDACY → ELECTION → ELECTION RESULT`

`PERSON → PARTY MEMBERSHIP`

`PERSON → OFFICEHOLDING → OFFICE → ADMINISTRATION`

`CLAIM → EVIDENCE → SOURCE → RETRIEVAL EVENT`

`OBSERVATION → CALCULATION → CLAIM / ANSWER`

## Acceptance results

| Check | Result |
|---|---|
| Person/candidacy separation | PASS |
| Party chronology | PASS |
| Office chronology | PASS |
| Election/result relationship | PASS |
| Official 2023 electoral anchor | PASS |
| Source provenance | PASS |
| Social-media statement semantics | PASS |
| Economic observation lineage | PASS |
| Temporal calculations | PASS |
| Causal classification | PASS |
| Qualifying/contradictory evidence | PASS |
| Correction lineage | PASS |
| Review dimensions | PASS |
| Ten public-answer fixtures | PASS |
| PostgreSQL runtime/schema check | PASS |

## Economic pilot

NBS records headline inflation at 21.34% in December 2022 and 28.92% in December 2023. The controlled calculation is 28.92 − 21.34 = **7.58 percentage points**. NBS records January 2024 headline inflation at 29.90%, giving a further **0.98 percentage-point** increase from December 2023.

These are temporal/observed changes. The pilot explicitly classifies the proposition that Tinubu's presidency caused the change as **INSUFFICIENT_EVIDENCE** rather than inferring causation from chronology.

NBS reports 2023 real GDP growth of 2.74%. DMO reports total public debt of ₦97.341 trillion at 31 December 2023. CBN documents the June 2023 FX-market reform separately from exchange-rate outcomes. These records preserve definition, unit, geography, period and source provenance.

## Social media

The pilot uses an original `@officialABAT` X post as evidence of a statement occurrence. Its evidence relationship is `DIRECTLY_ESTABLISHES_STATEMENT_OCCURRENCE`. It is not represented as evidence that the proposition contained in the post is objectively true.

## Legal record

The pilot includes SC/CV/501/2023 and separates litigation allegations from the judicial/procedural outcome. The record is based on an inspected reproduction of the case record, with the limitation that a primary court-hosted copy is preferred if subsequently located.

## Qualifying evidence

The pilot preserves different assessments rather than selecting a preferred narrative. Official statements describe reform progress; the IMF independently records improved macroeconomic outcomes while also documenting difficult living conditions, poverty and food insecurity. Reuters similarly reports the administration's stabilization claim alongside the cost-of-living squeeze. These remain distinct evidence relationships.

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

## Limitations

The pilot intentionally does not claim that every historical biographical, political, legal or economic fact about Tinubu has been exhaustively researched. The 1999 and 2003 Lagos election vote counts are retained with secondary-source certification rather than being promoted to primary electoral anchors. The court record uses an inspected reproduction where a primary court-hosted copy is preferred. Retrieval hashes for remote web artifacts are marked as canonical-capture metadata rather than falsely representing unavailable raw bytes.

## Gate recommendation

The controlled pilot has survived real-world source complexity under the executable acceptance suite. **GATE 4 — PASS RECOMMENDED.**

This recommendation opens the methodology for controlled scale, not unrestricted mass population. Expansion should proceed incrementally with the same source, provenance, temporal, review, contradiction and causality controls.
