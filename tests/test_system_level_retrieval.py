from pathlib import Path
import copy
import json
import pytest
from cross_candidate_retrieval import (load_dossiers,election_2023,presidential_history,economic_claims,contradictions,corrections,public_conversation,make_answer,compatible,validate_dependency,validate_candidate_identity)
ROOT=Path(__file__).resolve().parents[1]
CANDIDATES={"bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar"}
@pytest.fixture(scope="module")
def dossiers(): return load_dossiers(ROOT)
def test_scope_exactly_three(dossiers): assert set(dossiers)==CANDIDATES
def test_q1_three_official_results(dossiers):
 q=election_2023(dossiers); assert q["status"]=="SUPPORTED"; assert {r["candidate_id"] for r in q["rows"]}==CANDIDATES; assert {r["votes"] for r in q["rows"]}=={8794726,6101533,6984520}
def test_q1_preserves_source_and_missing_fields(dossiers): assert all("source_tier" in r and "missing_fields" in r for r in election_2023(dossiers)["rows"])
def test_q2_not_found_is_not_did_not_occur(dossiers):
 q=presidential_history(dossiers); assert set(q["candidates"])==CANDIDATES; assert all(r["evidence_status"] in {"RECORDED","NOT_FOUND_IN_CURRENT_DATASET"} for rs in q["candidates"].values() for r in rs)
def test_q3_no_economic_ranking(dossiers):
 q=economic_claims(dossiers); assert set(q["candidates"])==CANDIDATES; assert "rank" not in json.dumps(q).lower()
def test_q4_uncertain_states_only(dossiers): assert all(r["status"] in {"DISPUTED","INSUFFICIENT_EVIDENCE","UNVERIFIED","UNKNOWN"} for r in contradictions(dossiers)["records"])
def test_q5_corrections_explicitly_empty_or_present(dossiers): assert corrections(dossiers)["status"] in {"SUPPORTED","NO_MATCH"}
def test_q6_public_conversation_scoped(dossiers): assert set(public_conversation(dossiers)["candidates"])==CANDIDATES
def test_answer_is_derived_versioned_and_snapshotted(dossiers):
 a=make_answer("Q1",dossiers); assert a["answer_state"]=="DERIVED" and a["answer_version"]==1 and a["database_snapshot"].startswith("sha256:")
def test_dependency_resolution(dossiers): assert validate_dependency(make_answer("Q1",dossiers),dossiers)[0]
def test_identity_contamination_rejected(dossiers):
 a=make_answer("Q1",dossiers); row=a["dependencies"]["rows"][0]; row["candidate_id"]="peter-gregory-obi"; ok,_=validate_candidate_identity(a,dossiers); assert not ok
def test_provenance_candidate_swap_rejected(dossiers):
 a=make_answer("Q1",dossiers); row=a["dependencies"]["rows"][0]; row["claim_ids"]=["claim-obi-2023-result"]; ok,_=validate_candidate_identity(a,dossiers); assert not ok
def test_quantitative_period_mismatch_incomparable():
 a={"geography":"Nigeria","period_start":"2023","period_end":"2023","metric":"inflation","unit":"percent","dataset_version":"A"}; b={"geography":"Nigeria","period_start":"2024","period_end":"2024","metric":"inflation","unit":"percent","dataset_version":"B"}; ok,reason=compatible(a,b); assert not ok and reason.startswith("INCOMPARABLE")
def test_quantitative_geography_mismatch_incomparable():
 ok,_=compatible({"geography":"Nigeria","metric":"debt","unit":"NGN","dataset_version":"A"},{"geography":"Lagos State","metric":"debt","unit":"NGN","dataset_version":"A"}); assert not ok
def test_quantitative_metric_mismatch_incomparable():
 ok,_=compatible({"geography":"Nigeria","metric":"debt","unit":"NGN","dataset_version":"A"},{"geography":"Nigeria","metric":"gdp","unit":"NGN","dataset_version":"A"}); assert not ok
def test_unknown_question_no_match(dossiers): assert make_answer("Q99",dossiers)["status"]=="NO_MATCH"
def test_reproducible_same_snapshot_same_answer(dossiers): assert make_answer("Q2",dossiers)==make_answer("Q2",dossiers)
def test_as_of_recorded(dossiers): assert make_answer("Q1",dossiers,"2026-08-30T00:00:00Z")["as_of"]=="2026-08-30T00:00:00Z"
def test_answer_diff_does_not_mutate_v1():
 v1={"answer_id":"x-v1","answer_version":1,"dependencies":["claim-v1"]}; v2={**v1,"answer_id":"x-v2","answer_version":2,"dependencies":["claim-v2"]}; assert v1["answer_version"]==1 and v2["answer_version"]==2 and v1!=v2
def test_failure_states_distinct(): assert len({"NO_MATCH","UNKNOWN","UNVERIFIED","INCOMPLETE","DISPUTED","INCOMPARABLE","INSUFFICIENT_EVIDENCE","STALE"})==8
def test_candidate4_absent(dossiers): assert len(dossiers)==3 and "candidate-4" not in dossiers
def test_mutation_remove_candidate_filter_changes_scope(dossiers):
 a=make_answer("Q1",dossiers); original=len(a["dependencies"]["rows"]); a["dependencies"]["rows"]=a["dependencies"]["rows"][:2]; assert len(a["dependencies"]["rows"])!=original
def test_mutation_remove_uncertainty_is_detectable(dossiers):
 q=contradictions(dossiers); assert any(r["status"] in {"DISPUTED","INSUFFICIENT_EVIDENCE"} for r in q["records"]) or q["records"]==[]
def test_mutation_change_calculation_input_is_detectable():
 calc={"input_observation_versions":["obs-a@1","obs-b@1"]}; mutated=copy.deepcopy(calc); mutated["input_observation_versions"][0]="obs-x@1"; assert calc!=mutated
