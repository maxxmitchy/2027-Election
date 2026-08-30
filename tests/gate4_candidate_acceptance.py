import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_ID = os.environ.get("CANDIDATE_ID", "bola-ahmed-tinubu")
CANDIDATE_DIR = ROOT / "candidates" / CANDIDATE_ID
DATA = CANDIDATE_DIR / "data/pilot-record.json"
ANSWERS = CANDIDATE_DIR / "data/public-answers.json"


def load(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def require_data():
    assert DATA.exists(), f"missing research fixture: {DATA}"
    return load(DATA)


def test_person_candidacy_separation():
    d = require_data()
    person_id = d["person"]["id"]
    assert person_id
    assert all(c["person_id"] == person_id for c in d["candidacies"])
    assert all("election_id" in c for c in d["candidacies"])


def test_party_chronology():
    d = require_data()
    memberships = d["party_memberships"]
    assert memberships, "INCOMPLETE: party history is missing"
    for m in memberships:
        assert m["person_id"] == d["person"]["id"]
        assert m["valid_from"]
        if m["valid_until"]:
            assert m["valid_from"] < m["valid_until"]


def test_office_chronology():
    d = require_data()
    offices = d["officeholdings"]
    assert offices, "INCOMPLETE: office history is missing"
    for o in offices:
        assert o["person_id"] == d["person"]["id"]
        assert o["valid_from"]
        if o["valid_until"]:
            assert o["valid_from"] < o["valid_until"]


def test_election_result_relationships():
    d = require_data()
    candidacy_ids = {c["id"] for c in d["candidacies"]}
    assert all(r["candidacy_id"] in candidacy_ids for r in d["election_results"])
    official = [r for r in d["election_results"] if r.get("certification_status") == "OFFICIAL"]
    assert official, "INCOMPLETE: no officially anchored election result"


def test_source_provenance():
    d = require_data()
    source_ids = {s["id"] for s in d["sources"]}
    assert source_ids
    for s in d["sources"]:
        assert s.get("url")
        assert s.get("retrieval_date")
    for r in d.get("retrieval_events", []):
        assert r["source_id"] in source_ids


def test_social_media_semantics():
    d = require_data()
    claims = [c for c in d["claims"] if c.get("claim_type") == "STATEMENT_OCCURRENCE"]
    assert claims, "INCOMPLETE: no social/public-statement semantics record"
    for claim in claims:
        assert "factually true" not in claim["claim"].lower()


def test_economic_lineage_and_calculation():
    d = require_data()
    observations = {o["id"]: o for o in d.get("observations", [])}
    calculations = d.get("calculations", [])
    assert calculations, "INCOMPLETE: no reproducible quantitative calculation"
    calc = next((c for c in calculations if c.get("input_observation_versions")), None)
    assert calc, "INCOMPLETE: calculation lacks observation dependencies"
    assert calc.get("result") is not None
    for ref in calc["input_observation_versions"]:
        obs_id = ref.split("@", 1)[0]
        assert obs_id in observations


def test_causality_is_not_inferred():
    d = require_data()
    claims = [c for c in d["claims"] if c.get("claim_type") == "CAUSAL"]
    assert claims, "INCOMPLETE: no causal-classification test record"
    for claim in claims:
        assert claim.get("causal_classification") in {
            "TEMPORAL_ASSOCIATION",
            "DOCUMENTED_ATTRIBUTION",
            "SUPPORTED_CAUSAL_INFERENCE",
            "CONTESTED_ATTRIBUTION",
            "INSUFFICIENT_EVIDENCE",
        }


def test_contradictory_or_qualifying_evidence_preserved():
    d = require_data()
    contradictions = d.get("contradictions", [])
    assert contradictions, "INCOMPLETE: contradiction representation is missing"
    assert all(c.get("source_a") and c.get("source_b") for c in contradictions)


def test_correction_lineage():
    d = require_data()
    corrections = d.get("corrections")
    assert corrections, "INCOMPLETE: correction lineage is missing"
    for correction in corrections:
        assert correction.get("v1") and correction.get("v2")
        assert correction["v2"].get("predecessor") == "v1"


def test_review_dimensions():
    d = require_data()
    reviews = d.get("reviews", [])
    assert reviews, "INCOMPLETE: review records are missing"
    fields = ["evidence_quality", "factual_accuracy", "calculation_accuracy", "context_completeness", "source_quality", "reviewer_confidence"]
    for review in reviews:
        for field in fields:
            assert field in review


def test_ten_public_answers_have_dependencies():
    assert ANSWERS.exists(), f"INCOMPLETE: missing public answers fixture: {ANSWERS}"
    d = load(ANSWERS)
    assert len(d.get("answers", [])) == 10, "INCOMPLETE: standardized public-answer set must contain 10 answers"
    for answer in d["answers"]:
        assert answer.get("id") and answer.get("question") and answer.get("answer")
        assert answer.get("dependencies")


def test_unknown_source_is_not_false():
    d = require_data()
    failure = d.get("source_failure")
    assert failure, "INCOMPLETE: retrieval-failure state is missing"
    assert failure["state"] in {"RETRIEVAL_FAILURE", "UNAVAILABLE"}
    assert failure["truth_status"] in {"UNKNOWN", "UNVERIFIED"}


def test_machine_lineage_is_resolvable():
    d = require_data()
    source_ids = {s["id"] for s in d["sources"]}
    evidence = {e["id"]: e for e in d.get("evidence", [])}
    assert evidence, "INCOMPLETE: evidence graph is missing"
    for claim in d["claims"]:
        for evidence_id in claim.get("evidence_ids", []):
            assert evidence_id in evidence
        for evidence_id in claim.get("evidence_ids", []):
            assert set(evidence[evidence_id].get("source_ids", [])) <= source_ids


def test_candidate_fixture_is_parameterized():
    d = require_data()
    assert CANDIDATE_ID
    assert d["person"]["id"].startswith("person-")
    assert CANDIDATE_DIR.exists()
