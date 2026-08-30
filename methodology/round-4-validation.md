# Round 4 — Implementation-Level Integrity Validation

**Scope:** adversarial integrity testing only. No real political research data is introduced.

## Verdict

**18 conceptual scenarios remain representable, but Round 4 exposes implementation gates that must be enforced before production ingestion.** The principal controls are bitemporal range semantics, append-only version storage, dependency-graph propagation, dataset lineage, cryptographic content metadata, and automated invariant tests.

## 1. Bitemporal fixtures

### Boundary convention

All temporal intervals use **half-open `[start, end)` semantics**. `start` is inclusive; `end` is exclusive. A null end means open-ended future validity. This makes same-day succession deterministic: one holder may end at `2023-05-29T00:00:00Z` and the successor begins at exactly that instant without overlap.

Transaction intervals use the same `[transaction_from, transaction_to)` convention. A version is visible to an `as_of` transaction instant `T` iff `transaction_from <= T` and (`transaction_to IS NULL OR T < transaction_to`).

### Fixtures

| Case | Fixture | Expected result |
|---|---|---|
| 1 normal succession | A `[2019-05-29,2023-05-29)`, B `[2023-05-29,NULL)` | A before boundary; B at/after boundary |
| 2 same-day transition | A ends `2023-05-29T12:00Z`, B starts same instant | B owns the boundary instant; no overlap |
| 3 backdated correction | V1 recorded Aug 2026 says start Jan 2024; V2 recorded Aug 2026 corrects start Dec 2023 | V1 remains historical transaction state; current reconstruction uses V2 |
| 4 late discovery | Fact valid `[2020,2021)` first entered in 2026 | valid-time answer can place fact in 2020; transaction-time answer before 2026 cannot see it |
| 5 two corrections same date | V2 and V3 both entered on same calendar date at distinct timestamps | ordering is by transaction instant, never date-only |
| 6 open validity | `[2023-05-29,NULL)` | contains every later instant until explicitly closed |
| 7 overlapping validity | A `[2020,2024)`, B `[2023,2025)` | representable only where overlap is allowed; otherwise rejected by exclusion rule |
| 8 invalid office overlap | two active holdings for a single-occupancy office overlap | database exclusion constraint rejects transaction |
| 9 transaction correction | fact valid in 2020, corrected in 2026 | valid-time remains 2020; transaction visibility changes in 2026 |
| 10 divergent axes | V1 recorded 2024 represents A valid in 2020; V2 recorded 2026 corrects it to B | `valid_at=2020, as_of=2025` returns A; same valid date with `as_of=2026` returns B |

### Deterministic query rule

For bitemporal retrieval: first select the latest version visible at the transaction cutoff; then evaluate its valid-time interval. Never select the current version first and filter it backward.

## 2. Immutability attack results

| Attack | Result | Required control |
|---|---|---|
| Modify V1 | **BLOCKED** | append-only DB policy + API denies UPDATE |
| Delete V2 | **BLOCKED** | FK protection + DELETE denial/trigger |
| Duplicate V3 | **BLOCKED** | unique `(entity_id,version_number)` and unique `version_id` |
| Invalid predecessor | **BLOCKED** | FK + API sequence check |
| Version cycle | **BLOCKED/DETECTABLE** | predecessor FK plus API cycle check; CI graph check |
| Untracked historical version | **BLOCKED** | all material versions created through version service; DB trigger rejects direct writes lacking audit metadata |
| Change dependencies of published answer | **BLOCKED** | dependency rows append-only; published answer immutable |
| Change methodology referenced by old result | **BLOCKED** | methodology versions immutable; result stores exact methodology version |

A version chain is `V1 -> V2 -> V3`; V1 has null predecessor, V2 references V1, V3 references V2. No alternate predecessor is permitted.

## 3–4. Dependency graph and reverse propagation

Fixture graph:

`OBS-X:v1 -> CALC-A:v1 -> ANALYSIS-A:v1 -> RESULT-A:v1 -> ANSWER-1:v1`

`OBS-X:v1 -> CALC-B:v1 -> ANALYSIS-B:v1 -> RESULT-B:v1 -> ANSWER-2:v1`

`OBS-X:v1 -> CALC-C:v1 -> RESULT-C:v1`

`OBS-Y:v1 -> CALC-Y:v1 -> RESULT-Y:v1 -> ANSWER-Y:v1`

If `OBS-X:v1` is revised to `OBS-X:v2`, the reverse traversal marks exactly the X branch stale: CALC-A/B/C, their downstream analyses/results, and ANSWER-1/2. `OBS-Y` and its descendants remain current.

Algorithm: start with a queue containing the invalidated version ID; query dependency edges where `upstream_ref` equals the dequeued ID; for every active downstream version, record an invalidation event, transition it to `stale` unless policy requires `invalid`, enqueue that downstream version, and continue until the queue is empty. Maintain a visited set keyed by version ID. The operation is graph traversal, not table-wide invalidation.

A calculation revision propagates only to its direct and transitive descendants. A methodology revision propagates through edges of relationship `methodology_dependency`. A source revision propagates only through the observation/evidence descendants that actually reference that source version.

## 5. Dataset revision rules

Distinguish:

`SOURCE -> DATASET -> DATASET VERSION -> OBSERVATION VERSION`.

A dataset is the stable identity of a published series/table. A dataset version is an immutable release/revision. An observation identity is the stable identity of the logical observation key: `(dataset/metric, geography, period, series dimensions)`.

Rules:

1. Unchanged observation: retain the same observation identity; a new observation version may record that it was revalidated against the new dataset version. Do not manufacture a new logical observation ID merely because the dataset release changed.
2. Revised value: same observation ID, new observation version.
3. Added observation: create new observation identity and version 1.
4. Disappeared observation: do not delete it; mark the latest logical observation as `superseded`/`invalid` according to the publisher's semantics and preserve the dataset version that omitted it.
5. Metadata-only dataset change: new dataset version; unchanged observation values do not require new observation versions unless their provenance reference itself materially changes.
6. Methodology change: new methodology version and dataset version; derived calculations using the affected methodology become stale even if raw values are unchanged.

## 6. Methodology versioning

`M-1 + OBS:v1 -> CALC:v1 -> RESULT:v1 -> ANSWER:v1`.

`M-2 + OBS:v1 -> CALC:v2 -> RESULT:v2 -> ANSWER:v2`.

The old chain is immutable. Reproducibility resolves M-1 and the exact observation versions; it does not substitute today's methodology.

## 7. AI answer reconstruction

Complete fixture:

`ANSWER-A:v1 -> RESULT-R:v1 -> ANALYSIS-AN:v1 -> CALC-C:v1 -> OBS-O:v1 -> DATASET-D:v1 -> SOURCE-S:v1 -> METHOD-M:v1`.

After OBS-O changes to v2, ANSWER-A:v1 remains reconstructable and is marked stale. A new chain is created with v2 dependencies. The old answer is **historical**; the newest non-superseded answer whose dependencies are current is the **current answer**. Historical status must never be inferred solely from creation date.

## 8. Provenance integrity

The architecture now reserves a cryptographic provenance chain:

`SOURCE -> RETRIEVAL EVENT -> CONTENT HASH -> EVIDENCE HASH -> RECORD VERSION -> GIT COMMIT`.

Metadata required now: original URL, canonical URL when known, retrieval timestamp, HTTP metadata where available, artifact/media identifier, content hash algorithm, content hash, archive URL/reference, archive capture timestamp, evidence extraction reference, record version ID, and Git commit SHA. A later archival verifier can compare the stored content hash with a retrieved artifact without redesigning the domain model.

A changed archived artifact produces a hash mismatch. The mismatch does not rewrite the source record; it creates a provenance integrity finding and, if necessary, a new source/retrieval version.

## 9. Conflicting sources

A=100, B=110, C later establishes A used an outdated methodology. A and B remain historical source versions. Evidence assessments can change through new evidence/review versions. Historical answers retain their exact A/B dependencies and remain reproducible; new answers may prefer B or explain the methodological conflict.

## 10. Correction cascade

`OBS:v1 -> CALC:v1 -> ANALYSIS:v1 -> RESULT:v1 -> ANSWER:v1`.

Correction proposal targets OBS:v1; review approves; OBS:v2 is created. Reverse traversal marks all affected descendants stale. Recalculation produces CALC:v2, ANALYSIS:v2, RESULT:v2 and ANSWER:v2. No old record is mutated.

## 11. Database enforcement contract

Core constraints are:

- PK on every stable ID and immutable version ID.
- UNIQUE `(entity_id, version_number)`.
- UNIQUE `version_id`.
- FK `previous_version_id -> version.version_id`, nullable only for v1.
- CHECK: v1 => predecessor null; version >1 => predecessor non-null.
- CHECK: `transaction_to IS NULL OR transaction_to > transaction_from`.
- CHECK: valid interval end, where present, is after start.
- EXCLUSION on single-occupancy office holdings using `office_id WITH =` and a `tstzrange(valid_from,valid_until,'[)') WITH &&` equivalent. Exceptions require an explicit office capability flag and API/workflow approval.
- FK from every dependency edge to an existing version ID.
- UNIQUE dependency edge identity `(upstream_ref,downstream_ref,relationship)` for active lineage.
- FK from derived records to exact input versions.
- DELETE denial/trigger on version and published answer records.
- UPDATE denial/trigger on immutable historical/version/dependency records.
- CHECK/trigger preventing a published AI answer from referencing a non-resolvable dependency.
- Index `(upstream_ref)` for reverse traversal and `(downstream_ref)` for impact inspection.

## 12. Automated/property testing

CI must execute deterministic fixtures and property tests for:

- stable-ID uniqueness
- FK/reference closure
- predecessor-chain continuity
- no cycles in version/dependency graphs
- monotonic transaction intervals
- valid interval coherence
- office temporal exclusion
- orphan evidence/claims
- typed source/evidence relationships
- exact dependency-version references
- stale propagation closure
- no stale answer marked current
- complete quantitative AI dependency chain
- geographic/metric compatibility
- dataset revision identity rules
- provenance metadata completeness

Property generators should create random acyclic dependency DAGs, random version chains, random half-open intervals and random corrections. The invariant is that the validator either accepts a valid generated structure or identifies the injected violation deterministically.

## 13. Failure-state semantics

`VALID` = structurally and semantically acceptable at its selected snapshot.

`INVALID` = known to violate or fail a required correctness condition; it must not be used as current evidence/derivation.

`STALE` = previously valid derived artifact whose one or more upstream dependencies changed; retained for history but not current retrieval.

`DISPUTED` = credible conflicting evidence or unresolved proposition exists; not equivalent to false.

`SUPERSEDED` = replaced by a newer valid version or result; historical record remains valid for reconstruction.

`RETRACTED` = assertion withdrawn by its originator or authoritative correction process; distinct from supersession.

`UNVERIFIED` = insufficient verification has been performed; not equivalent to invalid.

`INCOMPLETE` = required provenance/dependency/context is missing; must fail closed for publication where completeness is mandatory.

State applicability is entity-specific. Claims can be disputed/retracted/unverified; derived records can be stale/invalid/superseded; sources can be available/unavailable/removed/archived-only; reviews are review outcomes rather than truth states.

## 14. Round 4 findings

**Passed:** temporal boundary determinism, append-only version model, selective dependency propagation, reverse dependency algorithm, dataset revision semantics, methodology reproducibility, AI reconstruction, conflict preservation, and correction cascade at the architectural-contract level.

**Failed as implementation-ready guarantees:** no executable database exists yet, no CI test runner exists yet, and cryptographic retrieval verification is metadata-ready but not externally exercised. These are deliberate gates, not claims of completed runtime enforcement.

### Newly discovered weaknesses

1. The current repository is still a specification repository; database constraints have not yet been executed against a real DB engine.
2. `Source` needs retrieval-event/content-hash fields before content verification can be operational.
3. Dependency-edge identity must distinguish active lineage from historical edge versions.
4. Dataset versioning needs an explicit stable dataset identity contract rather than relying only on dataset-version records.
5. Failure-state semantics must not be conflated with version status enums.

### Required schema changes

Add `schemas/retrieval-event.schema.json` and extend source provenance with content hash metadata. Add `schemas/integrity-finding.schema.json`. Add stable `dataset.schema.json`. Extend dependency edges with explicit edge identity and transaction interval metadata. Add `state` only where an entity's lifecycle requires it; do not replace existing version status with one universal status enum.

## 15. Research gate

**CLOSED.** Round 4 does not declare production readiness. The independent Reviewer must decide whether the specified controls are sufficient and should require executable database/CI implementation before opening the research gate.
