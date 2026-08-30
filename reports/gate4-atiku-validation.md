# Atiku Abubakar — Gate 4 Validation Record

**Candidate:** Atiku Abubakar  
**Validation status:** VALIDATED  
**Validated against:** actual GitHub Actions CI execution  
**Tested commit:** `0e0647d562706a1c63f6fff18d93a8b69e9cd8d6`

## CI execution

- Workflow: `Gate 4 Candidate Research`
- Workflow run ID: `33322894802`
- Job ID: `99287868835`
- Candidate matrix entry: `atiku-abubakar`
- PostgreSQL: `16.15`
- Python: `3.12.14`
- Test count: `16`
- Passed: `16`
- Failed: `0`
- Result: `SUCCESS`
- Artifact ID: `9735396097`
- Artifact SHA-256 / GitHub artifact digest: `2770dcc9695e2cf02c118c452afbedaf9363139366db6ad3dfd2a8cbfa2b926d`

The uploaded artifact contained the execution identity, PostgreSQL client version, Python version, pytest log, JUnit XML and artifact hash manifest. The pytest log records `16 passed in 0.68s`.

## Acceptance standard

The validator was not modified to accommodate Atiku. The same 16-test acceptance suite used for the controlled Tinubu and Peter Obi validation was executed with `CANDIDATE_ID=atiku-abubakar`.

The workflow matrix simultaneously contains:

- `bola-ahmed-tinubu`
- `peter-gregory-obi`
- `atiku-abubakar`

Atiku's result is independent of the earlier candidate results and is tied to the exact tested commit above.

## Historical evidence preservation

Peter Obi's original `10 passed / 6 failed` execution remains preserved separately and is not overwritten by this validation.

## Decision

Atiku Abubakar satisfies the Gate 4 candidate acceptance requirements at the tested commit and is therefore recorded as **VALIDATED**.

Candidate 4 remains blocked under the sequential scale-control rule.
