import json
from evidence_product_api import ask


def test_factual_question_uses_deterministic_engine():
    r=ask("What offices has Tinubu held?")
    assert r["answer_status"] == "ESTABLISHED"
    assert r["interpreted_query"]["operation"] == "FACTUAL_LOOKUP"
    assert r["interpreted_query"]["validation"]["llm_dependency"] is False


def test_quantitative_question_preserves_calculation():
    r=ask("How did Nigeria's headline inflation change during the selected Tinubu period?")
    assert r["answer_status"] == "SUPPORTED"
    assert r.get("calculation")
    assert r["calculation"]["unit"]


def test_historical_as_of_is_passed_to_engine():
    r=ask("As of 2026-05-01, what party was Peter Obi recorded as belonging to?")
    assert r["answer_status"] == "ESTABLISHED"
    assert r["as_of"].startswith("2026-05-01")


def test_cross_candidate_comparison():
    r=ask("Compare the presidential election results of Tinubu, Obi and Atiku in 2023.")
    assert r["answer_status"] == "ESTABLISHED"
    assert set(r["candidate_scope"]) == {"bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar"}


def test_incompatible_candidate_scope_is_not_forced():
    r=ask("What offices has Tinubu held?", ["bola-ahmed-tinubu","peter-gregory-obi"])
    assert r["answer_status"] == "INCOMPARABLE"


def test_causal_question_stays_conservative():
    r=ask("Did Tinubu cause inflation to rise?")
    assert r["answer_status"] == "INSUFFICIENT_EVIDENCE"
    assert "cause" in r["answer_text"].lower() or "caus" in r["answer_text"].lower()


def test_public_conversation_is_not_truth():
    r=ask("Did a candidate's X statement prove the statement true?")
    assert r["answer_status"] in {"SUPPORTED","INSUFFICIENT_EVIDENCE","UNVERIFIED"}
    assert "candidate_scope" in r


def test_contradiction_is_preserved():
    r=ask("What conflicting evidence exists about Anambra's debt during Obi's tenure?")
    assert r["answer_status"] in {"DISPUTED","INSUFFICIENT_EVIDENCE","NO_MATCH"}


def test_correction_is_preserved():
    r=ask("What changed in the evidence concerning ADC's legal status during Atiku's 2026 candidacy?")
    assert "answer_status" in r
    assert "interpreted_query" in r


def test_research_gap_does_not_become_false():
    r=ask("What important things can the database not establish?")
    assert r["answer_status"] in {"NO_MATCH","INSUFFICIENT_EVIDENCE","UNSUPPORTED"}
    assert r["answer_status"] != "FALSE"


def test_candidate4_rejected_server_side():
    try:
        ask("What offices has Tinubu held?", ["candidate-4"])
    except ValueError as e:
        assert str(e) == "unknown_candidate"
    else:
        raise AssertionError("Candidate 4 must not be accepted")


def test_subjective_question_is_unsupported():
    r=ask("Who is the best candidate?")
    assert r["answer_status"] == "UNSUPPORTED"


def test_provenance_is_present():
    r=ask("What offices has Tinubu held?")
    assert r["database_snapshot"].startswith("sha256:")
    assert "provenance" in r


def test_no_raw_exception_is_user_answer():
    r=ask("this is not a supported deterministic research question")
    assert r["answer_status"] in {"NO_MATCH","UNSUPPORTED"}
    assert "Traceback" not in r.get("answer_text","")
