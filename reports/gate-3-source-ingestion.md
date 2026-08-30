# Gate 3 — Source Ingestion Final Evidence Report

## Decision

**GATE 3 — PASS RECOMMENDED** for the controlled source-ingestion experiment.

This recommendation is based on actual GitHub Actions execution against a specific commit. It does **not** authorize candidate research. Gate 4 remains required before candidate population.

## Evidence-to-commit binding

**TESTED COMMIT:** `b26cccd58b9e6ea1c8e28ecbdd8affe5ea162328`

**WORKFLOW:** `Gate 3 Source Ingestion`

**WORKFLOW RUN:** `33319986354`

**JOB:** `99280145039`

**RESULT:** `success`

**RUNNER:** `ubuntu-24.04`

**PYTHON:** `3.12.14`

**PYTEST:** `8.4.2`

**TEST RESULT:** `7 passed, 0 failed, 0 errors, 0 skipped`

**ARTIFACT:** `gate3-source-ingestion-evidence`

**ARTIFACT ID:** `9734598011`

**ARTIFACT SHA-256:** `ac349422b075ddce8b924985d0d38a744749c0bc3c13affa0c1ca6bb7ca11ef`

The CI log independently records `git rev-parse HEAD = b26cccd58b9e6ea1c8e28ecbdd8affe5ea162328` immediately before test execution.

## Sources used

1. **Official government publication:** National Bureau of Statistics July 2026 CPI report. The NBS catalog identifies the July 2026 release and its download. citeturn0search0
2. **Official statistical dataset/catalog:** NBS Consumer Price Index and Inflation catalog, identifier `NGA-NBS-CPI`. citeturn0search1
3. **Reputable news report:** Reuters, *Nigerians' cost of living pain deepens as election looms*, published 10 August 2026. Reuters reports petrol prices of roughly N1,600/litre and describes inflation as near 16% at that time. citeturn2view1
4. **Social-media statement:** Proshare X post dated 24 March 2026 stating that February 2026 headline inflation held at 15.06%. citeturn1search4
5. **Independent corroborating report:** Premium Times reports the NBS July headline inflation figure of 15.43%. citeturn4search7
6. **Official display snapshot:** CBN homepage displayed an inflation-rate figure of 15.93% when inspected. citeturn4search6

## Test results

| Test | Result |
|---|---|
| Source → RetrievalEvent → hash linkage | PASS |
| Social-media statement separated from factual proposition | PASS |
| Contradictory evidence preserved | PASS |
| Correction preserves predecessor and supersedes downstream analysis | PASS |
| Source revision preserves V1 | PASS |
| Retrieval failure represented as unavailable/unknown rather than false | PASS |
| Canonical capture hashes deterministic | PASS |

## Social-media semantic test

Two separate claims were created:

**Statement:** Proshare's account published a statement saying February 2026 headline inflation was 15.06%.

**Proposition:** February 2026 headline inflation was 15.06%.

The statement evidence uses `is_subject_statement`. It does not automatically establish the proposition. This distinction is enforced by the executable test suite.

## Contradictory evidence

The CBN homepage snapshot displayed 15.93%, while the later NBS July release reported 15.43% year-on-year. Both source records remain preserved. The system records the latter as typed contradictory evidence against the undated interpretation of the CBN display.

The conflict is not silently collapsed into one value. Temporal context remains part of the assessment.

## Source revision

The repository contains V1 and an explicitly labelled **simulated** V2 source state. The V1 record remains reconstructable. The experiment does not claim that NBS actually revised the publication.

## Correction

A controlled ingestion error initially labelled 15.43% as the July month-on-month rate. The correction changes the interpretation to:

- 15.43% year-on-year headline inflation;
- 1.57% month-on-month headline inflation.

V1 remains `superseded`; V2 points to V1 through `previous_version_id`. A downstream analysis record also changes from `superseded` to the corrected valid record.

## Retrieval failure

The direct NBS July download request timed out during inspection while the NBS catalog remained accessible. The failure is recorded as `retrieval_failure` / `availability_status=unknown`. It is **not** converted into a claim that the source is false.

## Hash semantics

The remote artifacts were inspected through public web resources. Where raw remote bytes were not persisted by this experiment, the recorded SHA-256 hashes cover canonical captured representations stored in the fixtures. The repository explicitly records this limitation rather than pretending to possess byte-level hashes of remote responses.

## Earlier failed execution

An earlier Gate 3 run on commit `1e8ed23128045656ecae521ccd01aa974397cc6b` failed one contradiction-reference test. The failure was real and observable; the CI artifact was still uploaded. The defect was corrected by changing the claim's contradictory-evidence reference to the evidence record whose typed relationship is actually `contradicts_claim`.

The corrected commit `b26cccd58b9e6ea1c8e28ecbdd8affe5ea162328` then produced the clean 7/7 execution documented above.

## Gate 2 qualification retained

Gate 2 remains **OPEN WITH DOCUMENTED EVIDENCE QUALIFICATION**. This report does not claim that `1c1dbc14dafd4b27e80aeaf86e496a23ae86d784` has a clean CI execution. The independent Reviewer explicitly accepted that limitation as technical debt. Gate 3 evidence is separate and commit-specific.

## Gate 3 conclusion

The controlled ingestion experiment demonstrates that the system can ingest real public information while preserving:

- source identity;
- retrieval metadata;
- hash metadata;
- source versions;
- typed evidence semantics;
- social-media statement/fact separation;
- contradictory evidence;
- corrections and historical versions;
- downstream stale state;
- retrieval failure state;
- reproducible execution evidence.

**Recommendation: GATE 3 — PASS.**

This does **not** open Gate 4. Candidate research remains prohibited until the separate Gate 4 acceptance criteria are satisfied and independently approved.
