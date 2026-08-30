# Round 4 Automated Integrity Test Plan

These tests are framework-neutral until the implementation language/database is selected. They are normative acceptance tests for CI.

## Structural tests

1. Load every `schemas/*.json` and validate against JSON Schema 2020-12.
2. Resolve every local `$ref`; fail on missing references.
3. Reject duplicate stable IDs and duplicate version IDs.
4. Reject malformed enums, dates, URIs and required-field omissions.

## Version-chain properties

For every entity version chain:
- exactly one v1 exists;
- v1 has no predecessor;
- every later version has exactly one predecessor;
- predecessor belongs to the same entity;
- predecessor number is exactly `n-1`;
- transaction intervals are ordered and non-overlapping;
- no cycle is reachable by predecessor traversal.

Property test: generate chains of length 1–100, then randomly delete, duplicate, fork or cycle one edge; validator must reject the mutation.

## Bitemporal properties

Generate random `[start,end)` intervals and verify:
- end > start when end exists;
- adjacent intervals sharing a boundary do not overlap;
- same-day transitions resolve to the successor at the exact boundary;
- open-ended intervals contain every later instant;
- `as_of(T)` never returns a version with `transaction_from > T`;
- bitemporal queries select transaction-visible versions before applying valid-time predicates.

## Dependency properties

Generate acyclic DAGs containing observations, calculations, analyses, results and answers. Inject one changed upstream version and verify that the transitive closure contains exactly the expected descendants and no unrelated nodes.

Test cycle injection separately. A cycle must be rejected before publication.

## Dataset properties

For dataset v1 -> v2 generate unchanged, revised, added and removed observations. Assert unchanged logical observation IDs persist; revised observations gain a new version; additions create new IDs; removals never delete history.

## Provenance properties

For every retrievable source artifact assert presence of retrieval timestamp, original URL, hash algorithm and content hash. Change one byte of a fixture artifact and assert a hash mismatch produces an `integrity_finding` rather than a source mutation.

## Evidence properties

Assert every evidence record resolves to a claim and source. Assert `is_subject_statement` evidence cannot automatically change the underlying proposition's verification status. Assert contradictory evidence remains queryable.

## Geographic properties

Attempt comparisons across incompatible geography types/scopes. The application must reject or require an explicit transformation/aggregation definition. Never silently compare country-level and subnational observations.

## AI-answer properties

For every published quantitative answer, traverse all required dependency edges and assert complete lineage to exact observation, dataset/source and methodology versions. Change one upstream dependency and assert old answer becomes stale while remaining reconstructable.

## Immutability attack suite

Attempt UPDATE/DELETE against historical versions, published answers, dependency edges and retrieval events. Expected result: database/application denial. Attempt direct writes bypassing the API in an authorized test database: expected result is denial by database policy/trigger where the contract requires database enforcement.

## CI gate

Production ingestion is blocked unless all structural, temporal, graph, provenance and AI-lineage tests pass. Failures must produce machine-readable integrity findings and a non-zero CI result.
