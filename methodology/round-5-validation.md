# Round 5 — Executable Integrity Validation

## Scope

Adversarial runtime validation only. No candidate research or broad political data is introduced.

## Implementation delivered

A minimal PostgreSQL reference implementation exists at `db/round5_reference.sql`, with executable pytest/property tests at `tests/test_round5_runtime.py`, development dependencies in `requirements-dev.txt`, and GitHub Actions execution defined in `.github/workflows/round5-integrity.yml`.

The implementation covers version-chain constraints, append-only records, single-occupancy temporal exclusion, candidacy/election-result referential integrity, geography compatibility, dependency-cycle prevention, reverse dependency traversal, dataset/observation versioning, methodology immutability, AI-answer content/lineage immutability with separate lifecycle state, bitemporal fixture queries, JSON Schema validation, and property tests.

## Important architectural correction

Round 4 described `transaction_to` as a field while also requiring historical rows to be immutable. Those requirements conflict if `transaction_to` is populated by updating the predecessor when a new version arrives. Round 5 resolves this by storing only immutable `transaction_from` and deriving `transaction_to` with `LEAD(transaction_from)` in `version_bitemporal`. This preserves true append-only history while retaining `[start,end)` transaction semantics.

Likewise, published AI answer content/lineage is immutable, but lifecycle state may change from `published` to `stale`. Round 5 separates immutable `ai_answer` content/lineage from mutable `ai_answer_state`. This is necessary to satisfy both immutability and stale propagation.

## Execution status

**RUNTIME EXECUTION: NOT YET VERIFIED IN THIS ENVIRONMENT.**

The repository workflow was created to run PostgreSQL 16, install the test dependencies, execute the test suite, and upload machine-readable findings. A draft PR was created to trigger pull-request CI, but the available GitHub integration returned no workflow runs or status checks for the trigger commit. The local execution environment also has no PostgreSQL server/client and no Docker runtime.

Therefore no PostgreSQL test is classified as `PASS` merely because the test code exists. The current audit status is `UNTESTED` for runtime/database execution until an actual CI runner or PostgreSQL environment produces execution evidence.

## Required status standard

PASS = executed and observed to satisfy expected behavior.
FAIL = executed and protection failed.
PARTIAL = executed but protection exists only at a weaker layer.
UNTESTED = implementation exists but execution evidence is unavailable.

## Current findings

1. **UNTESTED — PostgreSQL runtime suite.** The executable suite exists, but no workflow result is available from the current GitHub integration.
2. **UNTESTED — direct database immutability attacks.** SQL triggers are implemented but have not been executed here.
3. **UNTESTED — exclusion constraint.** PostgreSQL GiST exclusion is implemented but not executed here.
4. **UNTESTED — dependency cycle trigger.** Recursive cycle guard exists but requires runtime evidence.
5. **UNTESTED — schema CI.** JSON Schema test exists but no CI result is available.
6. **UNTESTED — property tests.** Hypothesis tests exist but no runner result is available.

No failure is silently converted into a pass.

## Research gate

**GATE 2 — RUNTIME INTEGRITY: CLOSED.**

Consequently GATE 3 source ingestion and GATE 4 candidate research remain prohibited.

The implementation is intentionally not declared production-ready. The independent Reviewer must evaluate the eventual runtime evidence.
