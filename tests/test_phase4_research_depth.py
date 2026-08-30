import json
from pathlib import Path
from answer_experience import present
from evidence_coverage import coverage_report, validate_coverage, VALID_CANDIDATES
from query_interpreter import interpret_and_validate
ROOT=Path(__file__).resolve().parents[1]

CASES=[
("Tinubu economic coverage","What evidence do you have about Tinubu's economic record?"),
("Obi economic coverage","What evidence do you have about Obi's economic record?"),
("Atiku economic coverage","What evidence do you have about Atiku's economic record?"),
("Tinubu poor periods","What periods of Tinubu's record are poorly documented?"),
("Obi poor periods","What periods of Obi's record are poorly documented?"),
("Atiku poor periods","What periods of Atiku's record are poorly documented?"),
("Tinubu primary sources","Which of Tinubu's records have primary-source evidence?"),
("Obi primary sources","Which of Obi's records have primary-source evidence?"),
("Atiku primary sources","Which of Atiku's election results have primary-source evidence?"),
("secondary only","What records are based only on secondary sources for Obi?"),
("missing evidence","What evidence is missing for Atiku's 2007 election?"),
("public statements","What public statements by Tinubu have independent evidence attached?"),
("corrections","What corrections have been made to Obi's dossier?"),
("unavailable","What information is unavailable for Atiku?"),
("disputed","Which claims about Obi remain disputed?"),
("cross coverage","What is the evidence coverage for Tinubu, Obi and Atiku?"),
("broad coverage","What evidence do you have about the three candidates?"),
("research gap","What research gaps exist for Tinubu?"),
("primary coverage","What is Obi's primary-source coverage?"),
("economic indicators","What economic indicators can you reliably compare across Tinubu's administration?"),
("source coverage","How well documented is Atiku's record?"),
("period coverage","What periods of Obi are well documented?"),
("coverage limitation","What evidence is missing from Tinubu's economic record?"),
("candidate isolation","What evidence do you have about Obi's economic record?")
]

def test_phase4_golden_coverage_questions():
    for name,q in CASES:
        a=present(q,ROOT)
        assert a["interpreted_query"]["operation"]=="COVERAGE", name
        assert a["answer_status"] in {"ANSWERED","PARTIALLY_ANSWERED"}, name
        assert a["coverage"]["is_truth_probability"] is False, name
        assert a["why_this_answer"]["operation"]=="COVERAGE", name
        assert a["limitations"], name

def test_coverage_matrix_has_all_three_candidates_and_all_domains():
    report=coverage_report(ROOT); ok,msg=validate_coverage(report); assert ok,msg
    assert set(report)==VALID_CANDIDATES
    for r in report.values(): assert len(r["domains"])>=15

def test_source_composition_and_primary_upgrade_are_visible():
    report=coverage_report(ROOT)
    for r in report.values():
        assert r["source_composition"]["PRIMARY"]>0
        assert r["primary_source_coverage"] in {"HIGH","MODERATE"}

def test_quantitative_coverage_is_not_a_truth_score():
    report=coverage_report(ROOT)
    for r in report.values():
        assert "score" not in r and "truth_probability" not in r
        assert r["coverage_is_not_truth_probability"] is True

def test_tinubu_research_depth_contains_economic_series_and_rounding_qualification():
    d=json.loads((ROOT/"candidates/bola-ahmed-tinubu/data/phase4-depth.json").read_text())
    assert len(d["observations"])>=6
    assert any("5.87" in c.get("qualification","") for c in d["calculations"])
    assert any(o["metric"]=="nfem_average_exchange_rate" for o in d["observations"])

def test_obi_research_depth_preserves_source_disagreement():
    d=json.loads((ROOT/"candidates/peter-gregory-obi/data/phase4-depth.json").read_text())
    assert any("NGN 9.00" in o.get("qualification","") for o in d["observations"])
    assert any(o["metric"]=="state_igr" and o["period"]=="2013" for o in d["observations"])

def test_atiku_research_depth_keeps_2007_primary_gap_explicit():
    d=json.loads((ROOT/"candidates/atiku-abubakar/data/phase4-depth.json").read_text())
    assert any(x["status"]=="PRIMARY_RESULT_SHEET_NOT_LOCATED" for x in d["election_primary_source_upgrades"])
    assert any(o["period"]=="2007" for o in d["observations"])

def test_price_history_is_not_fabricated():
    report=coverage_report(ROOT)
    for r in report.values(): assert r["economic_metrics"]["selected_consumer_prices"]["status"]=="UNKNOWN"

def test_research_gaps_are_not_negative_facts():
    report=coverage_report(ROOT)
    for r in report.values():
        for g in r["research_gaps"]: assert g["status"] in {"OPEN","PARTIALLY_RESOLVED","RESOLVED","BLOCKED","UNAVAILABLE"}

def test_candidate_isolation():
    a=present("What evidence do you have about Obi's economic record?",ROOT)
    assert a["interpreted_query"]["candidate_scope"]==["peter-gregory-obi"]
    assert "bola-ahmed-tinubu" not in json.dumps(a["evidence"])

def test_all_candidate_scope_is_explicit_and_non_ranking():
    a=present("What is the evidence coverage for Tinubu, Obi and Atiku?",ROOT)
    assert set(a["coverage"]["candidates"])==VALID_CANDIDATES
    assert "ranking" not in json.dumps(a).lower()
    assert "best candidate" not in json.dumps(a).lower()

def test_performance_baseline_exists():
    a=present("What evidence do you have about Tinubu's economic record?",ROOT)
    p=a["performance_metadata"]; assert p["records_touched"]>=1 and p["dependency_depth"]>=1 and "coverage_calculation_time_ms" in p

def test_snapshot_reproducibility():
    q="What evidence do you have about Atiku's economic record?"; a=present(q,ROOT); b=present(q,ROOT)
    assert a["database_snapshot"]==b["database_snapshot"] and a["interpreted_query"]==b["interpreted_query"] and a["coverage"]==b["coverage"]

def test_coverage_query_interpretation_is_deterministic():
    q=interpret_and_validate("What periods of Tinubu's record are poorly documented?")
    assert q["operation"]=="COVERAGE" and q["candidate_scope"]==["bola-ahmed-tinubu"] and q["causal_request"] is False

def test_no_candidate4_data():
    assert not (ROOT/"candidates"/"candidate-4").exists()
    for r in coverage_report(ROOT).values(): assert r["candidate_id"] in VALID_CANDIDATES

def test_causal_discipline_is_explicit_in_research_data():
    for cid in VALID_CANDIDATES:
        d=json.loads((ROOT/"candidates"/cid/"data/phase4-depth.json").read_text())
        assert "causal" in json.dumps(d).lower()
