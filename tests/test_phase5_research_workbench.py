from pathlib import Path
import pytest
from research_workbench import CANDIDATES, BLOCKED, METHODOLOGY_VERSION, make_question, decompose, evidence_requirements, investigate, task_queue

ROOT=Path(__file__).resolve().parents[1]


def test_complex_question_is_decomposed_and_traceable():
    rq=make_question("What evidence exists for Tinubu's economic record during his presidency?")
    subs=decompose(rq)
    assert rq.question_type in {"QUANTITATIVE","ECONOMIC","COMPOSITE"}
    assert len(subs)>=5
    assert all(s["parent_question_id"]==rq.question_id for s in subs)
    req=evidence_requirements(rq,subs)
    assert len(req)==len(subs)
    assert all(r["required_provenance"] for r in req)


def test_missing_primary_source_is_explicit_requirement_not_false():
    rq=make_question("What evidence supports or contradicts claims about Peter Obi's Anambra debt record?")
    req=evidence_requirements(rq,decompose(rq))
    assert any(r["preferred_primary_source"] for r in req)


def test_source_discovery_never_becomes_verified_evidence():
    inv=investigate(ROOT,"What public statements by Peter Obi are independently verifiable?")
    assert all(s["verification_state"]=="RETRIEVED" for s in inv["sources"])
    assert inv["evidence"]==[]


def test_candidate_scope_is_closed():
    assert set(CANDIDATES)=={"bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar"}
    with pytest.raises(ValueError): make_question("research candidate-4",candidate_scope=(BLOCKED,))
    with pytest.raises(ValueError): make_question("research unknown",candidate_scope=("candidate-5",))


def test_no_truth_probability_and_review_boundary():
    inv=investigate(ROOT,"Did policy X improve economic outcome Y?")
    assert inv["answerability"]["reason"].lower().find("truth probability")>=0
    assert inv["review"]["review_is_not_source"] is True
    assert inv["review"]["status"]=="NOT_REVIEWED"


def test_causal_questions_require_explicit_causal_stage():
    inv=investigate(ROOT,"Did policy X cause inflation to fall?")
    kinds={x["kind"] for x in inv["investigation"]["sub_questions"]}
    assert "causal" in kinds
    assert inv["investigation"]["status"]=="READY_FOR_REVIEW"


def test_legal_and_election_semantics_are_separate():
    legal=investigate(ROOT,"What is the documentary record of a candidate's court judgment?")
    election=investigate(ROOT,"What is the candidate's nomination and election result?")
    assert any(x["kind"]=="legal" for x in legal["investigation"]["sub_questions"])
    assert any(x["kind"]=="election" for x in election["investigation"]["sub_questions"])


def test_task_queue_is_deterministic_and_prioritizes_blockers():
    inv=investigate(ROOT,"What evidence exists for Tinubu's economic record during his presidency?")
    a=task_queue(inv); b=task_queue(inv)
    assert a==b
    assert a
    assert all(t["state"]=="OPEN" for t in a)
    assert a[0]["priority"]>=a[-1]["priority"]


def test_reproducibility_metadata_present():
    inv=investigate(ROOT,"What evidence exists for Atiku's role in the National Council on Privatisation?",as_of="2026-08-30")
    p=inv["provenance"]
    assert p["methodology_version"]==METHODOLOGY_VERSION
    assert p["interpretation_version"]=="interpretation-v1"
    assert p["as_of"]=="2026-08-30"
    assert p["generation_timestamp"]
