# Round 7 Reproducibility

## Pinned environment

- OS/CI runner: Ubuntu 24.04
- PostgreSQL: 16.x (CI service image `postgres:16`; record exact server version in `reports/environment.txt`)
- Python: 3.12.14
- psycopg[binary]: 3.3.4
- pytest: 8.4.2
- hypothesis: 6.167.0
- jsonschema: 4.26.0

## Local setup

Create a PostgreSQL database named `integrity_test`, then set:

`DATABASE_URL=postgresql://postgres:postgres@localhost:5432/integrity_test`

Install the pinned dependencies:

`python -m pip install -r requirements-dev.txt`

## Baseline execution

Run:

`python -m pytest -q tests/test_round7.py tests/test_round7_bitemporal.py`

The tests initialize the reference schema from `db/round5_reference.sql` and apply `db/round7_extensions.sql` before each runtime test.

## Mutation sensitivity

Run:

`python tests/run_round7_mutations.py`

Each mutation is applied only to a temporary copy of the reference schema/extension/schema directory. The relevant test is expected to fail. Temporary mutations are destroyed before the runner exits. A non-zero exit means at least one mutation was not detected.

## Reports

- `reports/round7-test-results.json` — machine-readable pytest evidence, written by a session-finish hook even when pytest fails.
- `reports/round7-mutation-results.json` — mutation sensitivity matrix.
- `reports/invariant-coverage.md` — 34-invariant coverage matrix.
- `reports/invariant-coverage.json` — machine-readable coverage metadata.
- `reports/environment.txt` — Python, dependency, PostgreSQL and commit information.

## CI

GitHub Actions workflow: `.github/workflows/round7-integrity.yml`.

The CI service health check waits for PostgreSQL readiness before executing tests. The workflow uploads evidence with `if: always()`, so failed test execution does not suppress artifact collection.

## Reproduction standard

A baseline is PASS only when the complete suite exits zero and the reports are produced. Mutation sensitivity is PASS only when all eight mutations produce the expected failing test. No production mutation is committed: mutation experiments operate on temporary copies.

**Gate rule:** no CI run or repository file is treated as PASS without actual execution evidence from the tested commit.

**Round 7 CI trigger:** this commit exists solely to obtain fresh execution evidence for the audit.
