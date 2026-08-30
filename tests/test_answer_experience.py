import json
from pathlib import Path
from answer_experience import present

ROOT=Path(__file__).resolve().parents[1]

def test_answer_contract_has_inspectable_sections():
    a=present("How many votes did Tinubu get in 2023?",ROOT)
    for k in ("question","interpreted_query","answer_status","answer_text","evidence_status","claims","evidence","sources","observations","calculations","analyses","results","methodology","database_snapshot","limitations","provenance","performance_metadata"):
        assert k in a
    assert a["interpreted_query"]["candidate_scope"]==["bola-ahmed-tinubu"]
    assert a["database_snapshot"].startswith("sha256:")

def test_natural_question_routes_to_existing_deterministic_retrieval():
    a=present("How many votes did Tinubu get in 2023?",ROOT)
    assert a["answer_status"]=="ANSWERED"
    assert "8,794,726" in a["answer_text"]
    assert a["retrieval_plan"]["raw_question_reinterpreted_by_retrieval"] is False

def test_why_this_answer_exposes_interpretation_and_evidence_boundary():
    a=present("Did Tinubu cause inflation to rise?",ROOT)
    w=a["why_this_answer"]
    assert w["operation"]=="CAUSAL_ATTRIBUTION"
    assert w["candidate_scope"]==["bola-ahmed-tinubu"]
    assert w["evidence_does_not_establish"]
    assert a["answer_status"]=="INSUFFICIENT_EVIDENCE"

def test_subjective_question_is_unsupported():
    a=present("Who was the best candidate?",ROOT)
    assert a["answer_status"]=="UNSUPPORTED"

def test_ambiguous_question_does_not_silently_execute():
    a=present("What did Tinubu do about the economy?",ROOT)
    assert a["answer_status"]=="PARTIALLY_ANSWERED"
    assert a["limitations"]

def test_public_conversation_is_not_truth():
    a=present("What did Atiku say about ADC?",ROOT)
    assert a["interpreted_query"]["operation"]=="PUBLIC_CONVERSATION"
    assert a["answer_status"] in {"ANSWERED","INCOMPLETE"}
    assert a["related_public_conversation"]
    assert any("statement" in x.lower() for x in a["evidence"][0].get("semantic_rule","").split("_") if x) if a["evidence"] else True

def test_negative_knowledge_stays_distinct_from_false():
    a=present("Does the database establish that Peter Obi left Anambra with zero debt?",ROOT)
    assert a["answer_status"]!="FALSE"

def test_reproducible_semantics_and_snapshot():
    q="How many votes did Tinubu get in 2023?"
    a=present(q,ROOT); b=present(q,ROOT)
    assert a["interpreted_query"]==b["interpreted_query"]
    assert a["database_snapshot"]==b["database_snapshot"]
    assert a["answer_text"]==b["answer_text"]

def test_candidate4_boundary():
    assert not (ROOT/"candidates"/"candidate-4").exists()
    a=present("How many votes did Tinubu get in 2023?",ROOT)
    assert "candidate-4" not in json.dumps(a)
