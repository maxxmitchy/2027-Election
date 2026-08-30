# Round 5 Runtime Validation Report

## Verdict

**GATE 2 — RUNTIME INTEGRITY: CLOSED.**

The reference implementation and executable test suite have been committed. Runtime execution evidence is not available from the current execution environment: there is no PostgreSQL server/client or Docker runtime locally, and the GitHub integration returned no workflow run/status for the CI trigger PR. Accordingly, no unexecuted protection is represented as PASS.

## Test matrix

| TEST | EXPECTED | ACTUAL | STATUS | ENFORCEMENT | EVIDENCE |
|---|---|---|---|---|---|
| Duplicate version ID | rejected | no runtime result available | UNTESTED | DB PK | `tests/test_round5_runtime.py` |
| Duplicate entity/version | rejected | no runtime result available | UNTESTED | DB UNIQUE | same |
| Invalid predecessor | rejected | no runtime result available | UNTESTED | FK + trigger | same |
| Missing predecessor | rejected | no runtime result available | UNTESTED | trigger | same |
| Historical UPDATE | rejected | no runtime result available | UNTESTED | DB trigger | same |
| Historical DELETE | rejected | no runtime result available | UNTESTED | DB trigger | same |
| Dependency cycle | rejected | no runtime result available | UNTESTED | recursive DB trigger | same |
| Office overlap | rejected | no runtime result available | UNTESTED | GiST EXCLUDE | same |
| Invalid candidacy relationship | rejected | no runtime result available | UNTESTED | FK | same |
| Invalid election-result relationship | rejected | no runtime result available | UNTESTED | composite FK | same |
| Geographic incompatibility | rejected | no runtime result available | UNTESTED | DB trigger | same |
| Invalid candidacy transition | rejected | no runtime result available | UNTESTED | DB trigger | same |
| Bitemporal valid/transaction query | deterministic A/B result | no runtime result available | UNTESTED | SQL query/view | same |
| Selective reverse dependency | exact descendants only | no runtime result available | UNTESTED | recursive SQL | same |
| Dataset revision identity | stable ID + new observation version | no runtime result available | UNTESTED | FK/UNIQUE | same |
| Methodology coexistence | v1 and v2 independently resolvable | no runtime result available | UNTESTED | immutable methodology versions | same |
| AI content mutation | rejected | no runtime result available | UNTESTED | DB trigger | same |
| AI dependency mutation | rejected | no runtime result available | UNTESTED | DB trigger | same |
| AI stale lifecycle | state changes without content mutation | no runtime result available | UNTESTED | separate state table | same |
| Schema validation | valid fixtures pass; invalid fixture fails | no runtime result available | UNTESTED | CI/jsonschema | same |
| Property tests | generated valid structures satisfy properties | no runtime result available | UNTESTED | Hypothesis/CI | same |

## Defects discovered during implementation review

### D1 — Transaction-time closure conflict
Round 4's combination of immutable historical rows and mutable `transaction_to` was internally inconsistent. Round 5 fixes this by deriving `transaction_to = LEAD(transaction_from)` rather than updating the predecessor.

### D2 — Published-answer state conflict
A published answer must remain immutable while also becoming stale when an upstream dependency changes. Round 5 separates immutable answer content/lineage from mutable `ai_answer_state`.

## Remaining defects / limitations

1. Runtime execution is not yet evidenced.
2. Production authentication/authorization and database role isolation are not implemented.
3. External archive retrieval/hash verification is represented but not externally exercised.
4. Full domain-wide 34-invariant executable coverage remains incomplete; the reference suite targets the critical runtime invariants and must be expanded before a production gate.

## Gate decision

GATE 2 remains CLOSED. GATE 3 and GATE 4 remain prohibited. No candidate research is permitted.
