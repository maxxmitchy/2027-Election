-- Round 4 conceptual PostgreSQL enforcement contract.
-- This is a design contract, not a production migration.

-- 1. Version identity and transaction-time integrity
-- PRIMARY KEY(version_id)
-- UNIQUE(entity_id, version_number)
-- FOREIGN KEY(previous_version_id) REFERENCES record_version(version_id)
-- CHECK ((version_number = 1 AND previous_version_id IS NULL)
--     OR (version_number > 1 AND previous_version_id IS NOT NULL))
-- CHECK (transaction_to IS NULL OR transaction_to > transaction_from)
-- Trigger/policy: UPDATE/DELETE on record_version are rejected for all rows.
-- Trigger: a new version must reference the immediately preceding version number
-- for the same entity; no alternate predecessor is accepted.

-- 2. Valid-time integrity
-- CHECK (valid_until IS NULL OR valid_until > valid_from)
-- Use [start,end) semantics everywhere. A null end is +infinity.
-- For single-occupancy offices:
-- EXCLUDE USING gist (
--   office_id WITH =,
--   tstzrange(valid_from, COALESCE(valid_until,'infinity'), '[)') WITH &&
-- ) WHERE (office_single_occupancy = true AND state NOT IN ('invalid','superseded'));

-- 3. Referential integrity
-- Foreign keys must exist for person, election, candidacy, office, party,
-- geography, source, evidence, calculation, analysis, result, methodology,
-- dataset version and dependency-version references.

-- 4. Dependency graph
-- PRIMARY KEY(dependency_id)
-- INDEX(dependency_edge.upstream_ref)
-- INDEX(dependency_edge.downstream_ref)
-- UNIQUE(upstream_ref, downstream_ref, relationship, transaction_from)
-- FK(upstream_ref) -> record_version(version_id)
-- FK(downstream_ref) -> record_version(version_id)
-- CHECK(upstream_ref <> downstream_ref)
-- API/CI rejects cycles. Database stores the graph; recursive traversal performs impact analysis.

-- 5. Published AI answers
-- Published answer rows are append-only.
-- UPDATE/DELETE trigger rejects mutation of answer content or dependency refs.
-- A publication transaction must verify that every required dependency exists,
-- is resolvable, and is not stale/invalid.

-- 6. Dataset lineage
-- dataset_id is stable; dataset_version_id is immutable.
-- UNIQUE(dataset_id, version_number)
-- FK(previous_dataset_version_id) -> dataset_version(dataset_version_id)
-- Observation logical identity is stable across dataset releases; revised values
-- create new observation versions rather than new logical IDs.

-- 7. Provenance integrity
-- retrieval_event_id is immutable and linked to source_id.
-- Store hash_algorithm + content_hash + retrieval timestamp + original URL.
-- A later hash mismatch creates an integrity_finding; it never mutates the old event.

-- 8. CI-only graph assertions
-- Assert dependency graph is acyclic.
-- Assert every current derived record has only current/non-invalid dependencies.
-- Assert every published answer has complete quantitative lineage when it contains
-- a quantitative result.
-- Assert no orphan evidence/claim/source references.
