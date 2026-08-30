import json
from pathlib import Path
import pytest
from system_demo import CANDIDATES, load_dossiers, load_questions, answer_question
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture(scope="module")
def dossiers(): return load_dossiers(ROOT)
@pytest.fixture(scope="module")
def questions(): return load_questions(ROOT)
def q(questions,qid): return next(x for x in questions if x["id"]==qid)
def test_golden_set_has_nontrivial_coverage(questions): assert len(questions)>=15
def test_scope_matrix_is_explicit(questions): assert ("bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar") in {tuple(x["candidate_scope"]) for x in questions}
def test_candidate_isolation_q1_q2_q3(dossiers,questions):
    for qid,cid in [("Q1","bola-ahmed-tinubu"),("Q2","atiku-abubakar"),("Q3","peter-gregory-obi")]:
        a=answer_question(q(questions,qid),dossiers); assert a["candidate_scope"]==[cid]; payload=json.dumps(a); assert all(other not in payload for other in CANDIDATES if other!=cid)
def test_identity_is_stable(dossiers): assert {d["person"]["id"] for d in dossiers.values()}=={"person-bola-ahmed-tinubu","person-peter-gregory-obi","person-atiku-abubakar"}
def test_2023_results_are_exact_and_typed(dossiers,questions):
    rows=answer_question(q(questions,"Q4"),dossiers)["key_evidence"]; assert {r["candidate_id"] for r in rows}==set(CANDIDATES); assert {r["votes"] for r in rows}=={8794726,6101533,6984520}; assert all(r["certification_status"]=="OFFICIAL" for r in rows)
def test_most_votes_is_derived_from_observations(dossiers,questions):
    a=answer_question(q(questions,"Q5"),dossiers); assert max(a["key_evidence"],key=lambda r:r["votes"])["candidate_id"]=="bola-ahmed-tinubu"
def test_presidential_history_does_not_turn_missing_result_into_false(dossiers,questions):
    a=answer_question(q(questions,"Q6"),dossiers); assert all(r["evidence_status"] in {"RECORDED","NOT_FOUND_IN_CURRENT_DATASET"} for rs in a["key_evidence"].values() for r in rs)
def test_quantitative_integrity_uses_exact_stored_inputs(dossiers,questions):
    a=answer_question(q(questions,"Q7"),dossiers); assert a["calculation"]["unit"]=="percentage_points" and a["calculation"]["result"]==7.58
def test_unit_and_geography_compatibility_is_not_silent():
    from cross_candidate_retrieval import compatible
    assert not compatible({"geography":"Nigeria","metric":"inflation","unit":"percent","period_start":"2023"},{"geography":"Nigeria","metric":"inflation","unit":"NGN","period_start":"2023"})[0]
def test_obi_economic_query_never_inherits_tinubu_data(dossiers,questions):
    a=answer_question(q(questions,"Q8"),dossiers); assert a["candidate_scope"]==["peter-gregory-obi"]; assert all("headline_inflation" not in str(x.get("metric","")) for x in a["key_evidence"])
def test_unsupported_atiku_economic_query_preserves_negative_knowledge(dossiers,questions):
    a=answer_question(q(questions,"Q9"),dossiers); assert a["answer_status"] in {"INSUFFICIENT_EVIDENCE","INCOMPLETE"}
def test_causal_questions_are_conservative(dossiers,questions):
    for qid in ("Q10","Q11","Q12"):
        a=answer_question(q(questions,qid),dossiers); assert a["answer_status"]=="INSUFFICIENT_EVIDENCE"
def test_contradiction_preservation(dossiers,questions): assert answer_question(q(questions,"Q13"),dossiers)["answer_status"] in {"DISPUTED","INSUFFICIENT_EVIDENCE","NO_MATCH"}
def test_correction_history_is_not_silently_erased(dossiers,questions):
    a=answer_question(q(questions,"Q14"),dossiers); assert a["answer_status"] in {"DISPUTED","NO_MATCH","INSUFFICIENT_EVIDENCE"}
def test_social_statement_is_not_truth(dossiers,questions):
    a=answer_question(q(questions,"Q15"),dossiers); assert a["what_evidence_does_not_establish"]
def test_as_of_uses_valid_time_not_present_state(dossiers,questions):
    a=answer_question(q(questions,"Q16"),dossiers); assert a["as_of"]=="2026-05-01T23:59:59Z" and a["answer_text"]=="African Democratic Congress"
def test_negative_knowledge_never_becomes_false(dossiers,questions): assert answer_question(q(questions,"Q17"),dossiers)["answer_status"]!="FALSE"
def test_provenance_completeness(dossiers,questions):
    for question in questions:
        a=answer_question(question,dossiers); assert a["database_snapshot"].startswith("sha256:"); assert a["review_status"]["status"]=="NOT_A_SOURCE"
def test_candidate4_is_absent(dossiers): assert set(dossiers)==set(CANDIDATES) and not (ROOT/"candidates"/"candidate-4").exists()
