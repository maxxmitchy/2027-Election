-- Round 5 executable enforcement contract.
-- This file is now aligned with db/round5_reference.sql.
-- Temporal convention: [start,end).
-- Critical correction: transaction_to is DERIVED with LEAD(transaction_from),
-- not maintained by mutating old rows. This preserves append-only history.

-- RECORD VERSION
-- PRIMARY KEY(version_id)
-- UNIQUE(entity_id,version_number)
-- FK(previous_version_id) -> record_version(version_id)
-- CHECK(v1 => predecessor IS NULL; v>1 => predecessor IS NOT NULL)
-- Trigger: predecessor must be same entity and exactly n-1.
-- Trigger/policy: UPDATE/DELETE on record_version rejected.
-- Bitemporal view derives transaction_to with LEAD(transaction_from).

-- VALID TIME
-- CHECK(valid_until IS NULL OR valid_until > valid_from)
-- [start,end) semantics; NULL end = +infinity.
-- Single-occupancy office holdings use PostgreSQL EXCLUDE USING gist over
-- office_id and tstzrange(valid_from,COALESCE(valid_until,'infinity'),'[)').

-- REFERENTIAL INTEGRITY
-- Foreign keys cover person, election, candidacy, office, geography, source,
-- evidence, methodology, dataset version and exact dependency-version references.
-- Election result uses a composite FK(candidacy_id,election_id) so a result
-- cannot attach a candidacy from another election.

-- DEPENDENCY GRAPH
-- PRIMARY KEY(dependency_id)
-- INDEX(upstream_ref), INDEX(downstream_ref)
-- UNIQUE(upstream_ref,downstream_ref,relationship)
-- FK both endpoints -> record_version(version_id)
-- CHECK(upstream_ref <> downstream_ref)
-- INSERT trigger performs recursive cycle detection.
-- UPDATE/DELETE on dependency_edge rejected.

-- PUBLISHED AI ANSWERS
-- Answer content, generation metadata and dependency rows are immutable.
-- Lifecycle state is deliberately separate in ai_answer_state and may transition
-- published -> stale/superseded without changing historical answer content or lineage.

-- DATASET LINEAGE
-- dataset_id stable; dataset_version_id immutable.
-- UNIQUE(dataset_id,version_number); predecessor FK.
-- observation_id is stable logical identity; observation_version captures revisions.

-- PROVENANCE
-- retrieval_event is immutable and linked to source_id.
-- Preserve retrieval timestamp, original URL, hash algorithm and content hash.
-- Hash mismatches create integrity findings; they do not mutate historical events.

-- GEOGRAPHIC COMPATIBILITY
-- Comparison trigger rejects different geo_type values. More sophisticated
-- aggregation/metric compatibility remains an API/domain rule.

-- CI
-- Structural JSON Schema validation, reference closure, graph-cycle detection,
-- temporal properties, stale propagation and AI lineage completeness are CI gates.
