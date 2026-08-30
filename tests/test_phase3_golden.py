import pytest
from answer_experience import present
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES=[
("simple factual","What offices has Tinubu held?","ANSWERED"),
("single candidate factual","What parties has Peter Obi been associated with?","ANSWERED"),
("cross candidate comparison","Compare the presidential election results of Tinubu, Obi and Atiku in 2023.","ANSWERED"),
("quantitative count","How many votes did Tinubu get in 2023?","ANSWERED"),
("quantitative change","How did Nigeria's headline inflation change during the selected Tinubu period?","ANSWERED"),
("causal","Did Tinubu cause inflation to rise?","INSUFFICIENT_EVIDENCE"),
("causal debt","Did Peter Obi's administration cause Anambra's debt position?","INSUFFICIENT_EVIDENCE"),
("causal NCP","Did Atiku personally cause the outcomes associated with NCP activity?","INSUFFICIENT_EVIDENCE"),
("contradiction","What conflicting evidence exists about Anambra's debt during Obi's tenure?","DISPUTED"),
("correction","What changed in the evidence concerning ADC's legal status during Atiku's 2026 candidacy?","DISPUTED"),
("public conversation","What did Atiku say about ADC?","ANSWERED"),
("as of","As of 2026-05-01, what party was Peter Obi recorded as belonging to?","ANSWERED"),
("negative knowledge","Does the database establish that Peter Obi left Anambra with zero debt?","PARTIALLY_ANSWERED"),
("subjective","Who was the best candidate?","UNSUPPORTED"),
("incomparable","Compare Anambra debt with Nigeria inflation.","PARTIALLY_ANSWERED"),
("timeline","How many presidential general elections are represented for each candidate in the database?","NO_MATCH"),
("source inspection","How many votes did Tinubu get in 2023?","ANSWERED"),
("why this answer","Did Tinubu cause inflation to rise?","INSUFFICIENT_EVIDENCE"),
("review separation","What did Atiku say about ADC?","ANSWERED"),
("negative UNKNOWN","What happened to an unsupported topic for Atiku?","PARTIALLY_ANSWERED"),
("candidate isolation","How many votes did Peter Obi receive in 2023?","ANSWERED"),
("provenance","How many votes did Tinubu get in 2023?","ANSWERED"),
("reproducibility","How many votes did Tinubu get in 2023?","ANSWERED"),
("social semantics","What did Atiku say about ADC?","ANSWERED"),
]
@pytest.mark.parametrize("name,question,expected",CASES)
def test_phase3_golden(name,question,expected):
    a=present(question,ROOT)
    assert a["answer_status"]==expected, name
    assert a["provenance"]["database_snapshot"].startswith("sha256:")

def test_candidate_isolation():
    a=present("How many votes did Peter Obi receive in 2023?",ROOT)
    assert a["interpreted_query"]["candidate_scope"]==["peter-gregory-obi"]

def test_quantitative_lineage():
    a=present("How did Nigeria's headline inflation change during the selected Tinubu period?",ROOT)
    assert a["calculations"] and a["observations"] and a["methodology"]
    assert a["evidence_status"]=="SUPPORTED"

def test_causal_separates_observation_from_attribution():
    a=present("Did Tinubu cause inflation to rise?",ROOT)
    assert a["answer_status"]=="INSUFFICIENT_EVIDENCE"
    assert any("caus" in x.lower() for x in a["why_this_answer"]["evidence_does_not_establish"])

def test_public_conversation_has_explicit_semantic_boundary():
    a=present("What did Atiku say about ADC?",ROOT)
    assert a["related_public_conversation"]
    assert all(x.get("semantic_rule")=="statement_occurrence_is_not_independent_truth" for x in a["related_public_conversation"])

def test_as_of_is_preserved():
    a=present("As of 2026-05-01, what party was Peter Obi recorded as belonging to?",ROOT)
    assert a["as_of"]=="2026-05-01"
    assert a["interpreted_query"]["as_of"]=="2026-05-01"

def test_review_is_not_evidence():
    a=present("What did Atiku say about ADC?",ROOT)
    assert a["review_information"]["status"]=="NOT_A_SOURCE"

def test_no_candidate4():
    assert not (ROOT/"candidates"/"candidate-4").exists()
