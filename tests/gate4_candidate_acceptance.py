import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "candidates/bola-ahmed-tinubu/data/pilot-record.json"
ANSWERS = ROOT / "candidates/bola-ahmed-tinubu/data/public-answers.json"


def load(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def test_person_candidacy_separation():
    d = load(DATA)
    person_id = d["person"]["id"]
    assert person_id == "person-bola-ahmed-tinubu"
    assert all(c["person_id"] == person_id for c in d["candidacies"])
    assert all("election_id" in c for c in d["candidacies"])


def test_party_chronology():
    d = load(DATA)
    memberships = d["party_memberships"]
    assert len(memberships) == 4
    for m in memberships:
        assert m["person_id"] == d["person"]["id"]
        assert m["valid_from"]
        if m["valid_until"]:
            assert m["valid_from"] < m["valid_until"]


def test_office_chronology():
    d = load(DATA)
    offices = d["officeholdings"]
    assert len(offices) == 3
    assert offices[1]["valid_from"] == "1999-05-29"
    assert offices[1]["valid_until"] == "2007-05-29"
    assert offices[2]["valid_from"] == "2023-05-29"
    assert offices[2]["valid_until"] is None


def test_election_result_relationships():
    d = load(DATA)
    candidacy_ids = {c["id"] for c in d["candidacies"]}
    assert all(r["candidacy_id"] in candidacy_ids for r in d["election_results"])
    official = next(r for r in d["election_results"] if r["id"] == "res-2023")
    assert official["votes"] == 8794726
    assert official["certification_status"] == "OFFICIAL"


def test_source_provenance():
    d = load(DATA)
    source_ids = {s["id"] for s in d["sources"]}
    assert len(source_ids) == len(d["sources"])
    assert all(s["retrieval_date"] == "2026-08-30" for s in d["sources"])
    for r in d["retrieval_events"]:
        assert r["source_id"] in source_ids


def test_social_media_semantics():
    d = load(DATA)
    claim = next(c for c in d["claims"] if c["id"] == "claim-social-statement")
    evidence = next(e for e in d["evidence"] if e["id"] == "ev-social")
    assert claim["claim_type"] == "STATEMENT_OCCURRENCE"
    assert evidence["relationship"] == "DIRECTLY_ESTABLISHES_STATEMENT_OCCURRENCE"
    assert "factually" not in claim["claim"].lower()


def test_economic_lineage_and_calculation():
    d = load(DATA)
    obs = {o["id"]: o for o in d["observations"]}
    calc = next(c for c in d["calculations"] if c["id"] == "calc-cpi-2022-2023")
    assert calc["result"] == 7.58
    assert calc["unit"] == "percentage_points"
    assert obs["obs-cpi-2022-12"]["unit"] == obs["obs-cpi-2023-12"]["unit"] == "percent"
    assert obs["obs-cpi-2022-12"]["geography"] == obs["obs-cpi-2023-12"]["geography"] == "Nigeria"


def test_causality_is_not_inferred():
    d = load(DATA)
    claim = next(c for c in d["claims"] if c["id"] == "claim-inflation-causation")
    assert claim["status"] == "INSUFFICIENT_EVIDENCE"
    assert claim["causal_classification"] == "INSUFFICIENT_EVIDENCE"


def test_contradictory_or_qualifying_evidence_preserved():
    d = load(DATA)
    claim = next(c for c in d["claims"] if c["id"] == "claim-reform-assessment")
    relationships = {e["relationship"] for e in d["evidence"] if e["id"] in claim["evidence_ids"]}
    assert "QUALIFIES" in relationships
    assert "REPORTS_OFFICIAL_POSITION" in relationships
    assert len(claim["evidence_ids"]) >= 3


def test_correction_lineage():
    d = load(DATA)
    correction = d["correction"]
    assert correction["v2"]["predecessor"] == "v1"
    assert correction["v1"]["status"] == "PUBLISHED"
    assert correction["v2"]["status"] == "PUBLISHED"


def test_review_dimensions():
    d = load(DATA)
    r = d["reviews"][0]
    for field in ["evidence_quality", "factual_accuracy", "calculation_accuracy", "context_completeness", "source_quality", "reviewer_confidence"]:
        assert field in r


def test_ten_public_answers_have_dependencies():
    d = load(ANSWERS)
    assert len(d["answers"]) == 10
    for answer in d["answers"]:
        assert answer["id"]
        assert answer["question"]
        assert answer["answer"]
        assert answer["dependencies"]


def test_unknown_source_is_not_false():
    d = load(DATA)
    failure = d["source_failure"]
    assert failure["state"] == "RETRIEVAL_FAILURE"
    assert failure["truth_status"] == "UNKNOWN"


def test_no_candidate_population_beyond_pilot():
    pilot_dirs = [p for p in (ROOT / "candidates").iterdir() if p.is_dir()]
    assert pilot_dirs == [ROOT / "candidates/bola-ahmed-tinubu"]
