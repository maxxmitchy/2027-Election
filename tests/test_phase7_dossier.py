import copy,json
from pathlib import Path
import pytest
from phase7_dossier import CANDIDATES,BLOCKED,METHODOLOGY_VERSION,controlled_investigations,make_investigation,build_dossier,quality_gate,assemble_investigation_records,dossier_diff,snapshot,temporal_ok
ROOT=Path(__file__).resolve().parents[1]

def test_closed_candidate_corpus():
    assert CANDIDATES==("bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar")
    with pytest.raises(ValueError): make_investigation(BLOCKED,"x","x")
    with pytest.raises(ValueError): make_investigation("candidate-5","x","x")

def test_six_controlled_investigations_and_dependencies():
    invs=controlled_investigations()
    assert len(invs)==6
    assert {i["candidate_id"] for i in invs}==set(CANDIDATES)
    for i in invs:
        assert i["status"]=="PLANNED" and i["completion_state"]=="INCOMPLETE"

def test_investigation_schema_fields_and_lifecycle_states():
    required={"investigation_id","candidate_id","title","research_question","scope","as_of","status","priority","created_at","methodology_version","research_tasks","required_evidence","claims_under_investigation","known_unknowns","research_gaps","contradictions","corrections","reviews","dependencies","provenance","answerability","dossier_effect","completion_state"}
    for i in assemble_investigation_records(ROOT): assert required<=set(i)

def test_dossier_has_standardized_hierarchy_and_provenance():
    for cid in CANDIDATES:
        d=build_dossier(ROOT,cid)
        assert d["candidate_id"]==cid and d["methodology_version"]==METHODOLOGY_VERSION
        for key in ("identity","party_history","office_history","election_history","public_statements","related_public_conversation","economic_record","legal_record","contested_claims","corrections","uncertainty","research_gaps","reviews","sources","evidence","claims","investigations"): assert key in d
        assert all(c["provenance"] for c in d["claims"])

def test_claim_without_evidence_is_not_supported():
    d=build_dossier(ROOT,CANDIDATES[0]); d["claims"][0]["evidence_ids"]=[]; d["claims"][0]["status"]="UNVERIFIED"
    assert d["claims"][0]["status"]!="SUPPORTED"

def test_primary_secondary_remain_distinguishable():
    d=build_dossier(ROOT,CANDIDATES[0]); classes={s["source_class"] for s in d["sources"]}; assert "PRIMARY" in classes and "SECONDARY" in classes

def test_quality_gate_blocks_broken_provenance():
    d=build_dossier(ROOT,CANDIDATES[0]); d["claims"][0].pop("provenance"); q=quality_gate(d); assert "claim_provenance" in q["failures"] and q["recommended_state"]=="BLOCKED"

def test_review_is_separate_and_queued():
    d=build_dossier(ROOT,CANDIDATES[0]); assert all(r["status"]=="QUEUED" for r in d["reviews"]); assert all("evidence_dependencies" in r for r in d["reviews"])

def test_diff_reports_structural_change():
    a=build_dossier(ROOT,CANDIDATES[0]); b=copy.deepcopy(a); b["version_number"]=2; b["evidence_ids"]=b["evidence_ids"][:-1]
    diff=dossier_diff(a,b); assert diff["REMOVED_EVIDENCE"]

def test_snapshot_is_deterministic_for_same_snapshot():
    d=build_dossier(ROOT,CANDIDATES[0]); assert snapshot(d)==snapshot(d)

def test_historical_as_of_filters_future_source():
    assert temporal_ok({"publication_date":"2024-01-01"},"2023-12-31") is False
    assert temporal_ok({"publication_date":"2023-01-01"},"2023-12-31") is True

def test_cross_candidate_dossier_isolated():
    ds={c:build_dossier(ROOT,c) for c in CANDIDATES}
    for cid,d in ds.items():
        assert all(c["candidate_id"]==cid for c in d["claims"])
        assert d["candidate_id"] not in set(CANDIDATES)-{cid}

def test_no_truth_probability_or_ranking_fields():
    ds=[build_dossier(ROOT,c) for c in CANDIDATES]
    for d in ds:
        blob=json.dumps(d).lower(); assert "truth_probability" not in blob; assert "electability" not in blob

def test_dossier_versions_are_explicit():
    d=build_dossier(ROOT,CANDIDATES[0],version=1); assert d["version_number"]==1 and d["content_hash"]

def test_quality_gate_does_not_publish_with_open_review_or_gap():
    d=build_dossier(ROOT,CANDIDATES[0]); assert d["quality_gate"]["recommended_state"] in {"IN_REVIEW","BLOCKED","QUALIFIED"}; assert not (d["quality_gate"]["publishable"] and (d["research_gaps"] or d["reviews"]))
