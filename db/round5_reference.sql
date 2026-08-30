-- Round 5 executable reference implementation.
-- Intentionally minimal. No production application assumptions.
-- Temporal convention: [start,end). Transaction visibility is derived from
-- immutable transaction_from values using LEAD(); old rows are never closed by UPDATE.
CREATE EXTENSION IF NOT EXISTS btree_gist;

DROP TABLE IF EXISTS ai_answer_dependency, ai_answer, result, analysis, calculation, dependency_edge,
  observation_version, observation, dataset_version, dataset, methodology_version, evidence, claim,
  retrieval_event, source, election_result, candidacy, election, person, office_holding, office,
  geography, record_version CASCADE;

CREATE TABLE record_version (
  version_id text PRIMARY KEY,
  entity_id text NOT NULL,
  entity_type text NOT NULL,
  version_number integer NOT NULL CHECK (version_number >= 1),
  transaction_from timestamptz NOT NULL,
  status text NOT NULL CHECK (status IN ('current','superseded','stale','invalid')),
  change_type text NOT NULL,
  previous_version_id text NULL REFERENCES record_version(version_id),
  UNIQUE(entity_id, version_number)
);

CREATE OR REPLACE FUNCTION enforce_version_chain() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE p record;
BEGIN
  IF NEW.version_number = 1 AND NEW.previous_version_id IS NOT NULL THEN
    RAISE EXCEPTION 'v1 cannot have predecessor';
  END IF;
  IF NEW.version_number > 1 THEN
    IF NEW.previous_version_id IS NULL THEN RAISE EXCEPTION 'later version requires predecessor'; END IF;
    SELECT entity_id, version_number INTO p FROM record_version WHERE version_id=NEW.previous_version_id;
    IF NOT FOUND OR p.entity_id <> NEW.entity_id OR p.version_number <> NEW.version_number-1 THEN
      RAISE EXCEPTION 'predecessor must be immediate predecessor of same entity';
    END IF;
  END IF;
  IF EXISTS (SELECT 1 FROM record_version WHERE entity_id=NEW.entity_id AND transaction_from=NEW.transaction_from) THEN
    RAISE EXCEPTION 'transaction timestamp must be unique within entity';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER version_chain BEFORE INSERT ON record_version FOR EACH ROW EXECUTE FUNCTION enforce_version_chain();
CREATE OR REPLACE FUNCTION deny_version_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'record_version is append-only'; END $$;
CREATE TRIGGER version_immutable BEFORE UPDATE OR DELETE ON record_version FOR EACH ROW EXECUTE FUNCTION deny_version_mutation();

CREATE TABLE person(person_id text PRIMARY KEY);
CREATE TABLE election(election_id text PRIMARY KEY, office_id text NOT NULL);
CREATE TABLE office(office_id text PRIMARY KEY, single_occupancy boolean NOT NULL DEFAULT false);
ALTER TABLE election ADD CONSTRAINT election_office_fk FOREIGN KEY(office_id) REFERENCES office(office_id);
CREATE TABLE candidacy(candidacy_id text PRIMARY KEY, person_id text NOT NULL REFERENCES person(person_id), election_id text NOT NULL REFERENCES election(election_id), status text NOT NULL DEFAULT 'potential', UNIQUE(candidacy_id,election_id));
CREATE TABLE election_result(election_result_id text PRIMARY KEY, election_id text NOT NULL, candidacy_id text NOT NULL, geography_id text NOT NULL, version_id text NOT NULL REFERENCES record_version(version_id), UNIQUE(election_result_id,election_id), FOREIGN KEY(candidacy_id,election_id) REFERENCES candidacy(candidacy_id,election_id));

CREATE TABLE office_holding(office_holding_id text PRIMARY KEY, person_id text NOT NULL REFERENCES person(person_id), office_id text NOT NULL REFERENCES office(office_id), valid_from timestamptz NOT NULL, valid_until timestamptz NULL, version_id text NOT NULL REFERENCES record_version(version_id), state text NOT NULL DEFAULT 'current', CHECK(valid_until IS NULL OR valid_until > valid_from));
ALTER TABLE office_holding ADD CONSTRAINT office_single_occupancy_excl EXCLUDE USING gist (office_id WITH =, tstzrange(valid_from,coalesce(valid_until,'infinity'),'[)') WITH &&) WHERE (state NOT IN ('invalid','superseded'));

CREATE TABLE geography(geography_id text PRIMARY KEY, geo_type text NOT NULL, parent_id text REFERENCES geography(geography_id));
CREATE TABLE source(source_id text PRIMARY KEY);
CREATE TABLE retrieval_event(retrieval_event_id text PRIMARY KEY, source_id text NOT NULL REFERENCES source(source_id), retrieved_at timestamptz NOT NULL, original_url text, hash_algorithm text NOT NULL CHECK(hash_algorithm IN ('sha256','sha512')), content_hash text NOT NULL, version_id text REFERENCES record_version(version_id));
CREATE TABLE claim(claim_id text PRIMARY KEY, version_id text NOT NULL REFERENCES record_version(version_id));
CREATE TABLE evidence(evidence_id text PRIMARY KEY, claim_id text NOT NULL REFERENCES claim(claim_id), source_id text NOT NULL REFERENCES source(source_id), version_id text NOT NULL REFERENCES record_version(version_id));

CREATE TABLE methodology_version(methodology_version_id text PRIMARY KEY, methodology_id text NOT NULL, version_number integer NOT NULL, previous_methodology_version_id text REFERENCES methodology_version(methodology_version_id), UNIQUE(methodology_id,version_number), UNIQUE(methodology_version_id));
CREATE OR REPLACE FUNCTION deny_methodology_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'methodology versions are immutable'; END $$;
CREATE TRIGGER methodology_immutable BEFORE UPDATE OR DELETE ON methodology_version FOR EACH ROW EXECUTE FUNCTION deny_methodology_mutation();

CREATE TABLE dataset(dataset_id text PRIMARY KEY, stable_identity_key text NOT NULL UNIQUE);
CREATE TABLE dataset_version(dataset_version_id text PRIMARY KEY, dataset_id text NOT NULL REFERENCES dataset(dataset_id), version_number integer NOT NULL, previous_dataset_version_id text REFERENCES dataset_version(dataset_version_id), UNIQUE(dataset_id,version_number));
CREATE TABLE observation(observation_id text PRIMARY KEY, dataset_id text NOT NULL REFERENCES dataset(dataset_id), logical_key text NOT NULL, UNIQUE(dataset_id,logical_key));
CREATE TABLE observation_version(observation_version_id text PRIMARY KEY, observation_id text NOT NULL REFERENCES observation(observation_id), version_number integer NOT NULL, dataset_version_id text NOT NULL REFERENCES dataset_version(dataset_version_id), value numeric NOT NULL, previous_observation_version_id text REFERENCES observation_version(observation_version_id), UNIQUE(observation_id,version_number));

CREATE TABLE calculation(calculation_id text PRIMARY KEY, version_id text NOT NULL REFERENCES record_version(version_id), methodology_version_id text NOT NULL REFERENCES methodology_version(methodology_version_id));
CREATE TABLE analysis(analysis_id text PRIMARY KEY, version_id text NOT NULL REFERENCES record_version(version_id), methodology_version_id text NOT NULL REFERENCES methodology_version(methodology_version_id));
CREATE TABLE result(result_id text PRIMARY KEY, version_id text NOT NULL REFERENCES record_version(version_id), methodology_version_id text NOT NULL REFERENCES methodology_version(methodology_version_id), status text NOT NULL DEFAULT 'current');
CREATE TABLE dependency_edge(dependency_id text PRIMARY KEY, upstream_ref text NOT NULL REFERENCES record_version(version_id), downstream_ref text NOT NULL REFERENCES record_version(version_id), relationship text NOT NULL, transaction_from timestamptz NOT NULL DEFAULT now(), status text NOT NULL DEFAULT 'active', UNIQUE(upstream_ref,downstream_ref,relationship));
CREATE INDEX dependency_upstream_idx ON dependency_edge(upstream_ref);
CREATE INDEX dependency_downstream_idx ON dependency_edge(downstream_ref);
ALTER TABLE dependency_edge ADD CONSTRAINT no_self_dependency CHECK(upstream_ref <> downstream_ref);
CREATE OR REPLACE FUNCTION deny_dependency_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'dependency edges are append-only'; END $$;
CREATE TRIGGER dependency_immutable BEFORE UPDATE OR DELETE ON dependency_edge FOR EACH ROW EXECUTE FUNCTION deny_dependency_mutation();
CREATE OR REPLACE FUNCTION reject_dependency_cycle() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF EXISTS (WITH RECURSIVE walk(v) AS (SELECT NEW.downstream_ref UNION SELECT d.downstream_ref FROM dependency_edge d JOIN walk w ON d.upstream_ref=w.v) SELECT 1 FROM walk WHERE v=NEW.upstream_ref) THEN
    RAISE EXCEPTION 'dependency cycle detected';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER dependency_cycle_guard BEFORE INSERT ON dependency_edge FOR EACH ROW EXECUTE FUNCTION reject_dependency_cycle();

CREATE TABLE ai_answer(answer_id text PRIMARY KEY, answer_text text NOT NULL, status text NOT NULL CHECK(status IN ('draft','published','stale','superseded')), generated_at timestamptz NOT NULL, database_snapshot_ref text NOT NULL, as_of timestamptz, version integer NOT NULL DEFAULT 1);
CREATE TABLE ai_answer_dependency(answer_id text NOT NULL REFERENCES ai_answer(answer_id), version_id text NOT NULL REFERENCES record_version(version_id), PRIMARY KEY(answer_id,version_id));
CREATE OR REPLACE FUNCTION deny_published_answer_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF OLD.status='published' THEN RAISE EXCEPTION 'published AI answers are immutable'; END IF; RETURN NEW; END $$;
CREATE TRIGGER published_answer_immutable BEFORE UPDATE OR DELETE ON ai_answer FOR EACH ROW EXECUTE FUNCTION deny_published_answer_mutation();

CREATE OR REPLACE FUNCTION allowed_status_transition(old_status text,new_status text) RETURNS boolean LANGUAGE sql IMMUTABLE AS $$
SELECT (old_status,new_status) IN (('potential','declared'),('declared','nominated'),('nominated','registered'),('registered','withdrawn'),('registered','disqualified'),('registered','elected'),('registered','potential')) $$;
CREATE OR REPLACE FUNCTION candidacy_transition_guard() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF TG_OP='UPDATE' AND NEW.status<>OLD.status AND NOT allowed_status_transition(OLD.status,NEW.status) THEN RAISE EXCEPTION 'invalid candidacy status transition'; END IF; RETURN NEW; END $$;
CREATE TRIGGER candidacy_status_guard BEFORE UPDATE ON candidacy FOR EACH ROW EXECUTE FUNCTION candidacy_transition_guard();

CREATE OR REPLACE FUNCTION geo_compare_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE a text; b text; BEGIN SELECT geo_type INTO a FROM geography WHERE geography_id=NEW.left_geography_id; SELECT geo_type INTO b FROM geography WHERE geography_id=NEW.right_geography_id; IF a IS NULL OR b IS NULL THEN RAISE EXCEPTION 'unknown geography'; END IF; IF a<>b THEN RAISE EXCEPTION 'incompatible geography types'; END IF; RETURN NEW; END $$;
CREATE TABLE comparison(comparison_id text PRIMARY KEY,left_geography_id text NOT NULL REFERENCES geography(geography_id),right_geography_id text NOT NULL REFERENCES geography(geography_id));
CREATE TRIGGER comparison_geo_guard BEFORE INSERT OR UPDATE ON comparison FOR EACH ROW EXECUTE FUNCTION geo_compare_guard();

-- Derived transaction-time visibility for immutable versions.
CREATE VIEW version_bitemporal AS
SELECT v.*, lead(transaction_from) OVER(PARTITION BY entity_id ORDER BY version_number) AS transaction_to
FROM record_version v;

-- Minimal reverse traversal function.
CREATE OR REPLACE FUNCTION dependent_versions(seed text) RETURNS TABLE(version_id text) LANGUAGE sql AS $$
WITH RECURSIVE walk(v) AS (
  SELECT seed
  UNION
  SELECT d.downstream_ref FROM dependency_edge d JOIN walk w ON d.upstream_ref=w.v WHERE d.status='active'
) SELECT v FROM walk WHERE v<>seed;
$$;
