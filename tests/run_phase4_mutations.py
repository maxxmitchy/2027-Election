"""Fail-closed Phase 4 research-depth and coverage mutations."""
from __future__ import annotations
import copy, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from answer_experience import present
from evidence_coverage import coverage_report, VALID_CANDIDATES

def validate(m, expected, expected_answer):
    iq=m.get("interpreted_query",{}); cov=m.get("coverage",{})
    if set(cov.get("candidates",{}))!=VALID_CANDIDATES:return False
    if iq!=expected_answer.get("interpreted_query"):return False
    if m.get("answer_status")!=expected_answer.get("answer_status"):return False
    if m.get("answer_text")!=expected_answer.get("answer_text"):return False
    if m.get("limitations")!=expected_answer.get("limitations"):return False
    if m.get("evidence")!=expected_answer.get("evidence"):return False
    if m.get("sources")!=expected_answer.get("sources"):return False
    if m.get("why_this_answer")!=expected_answer.get("why_this_answer"):return False
    if m.get("provenance",{}).get("methodology_version")!=expected_answer.get("provenance",{}).get("methodology_version"):return False
    if cov.get("known_gaps")!=expected_answer.get("coverage",{}).get("known_gaps"):return False
    if "candidate-4" in json.dumps(m):return False
    if cov.get("is_truth_probability") is not False or cov.get("model")!="multidimensional-documentary-coverage-v1":return False
    if m.get("why_this_answer",{}).get("operation")!="COVERAGE":return False
    if m.get("performance_metadata",{}).get("records_touched",0)<1:return False
    for cid,exp in expected.items():
        got=cov["candidates"].get(cid)
        if not got:return False
        for key in ("source_composition","source_coverage","primary_source_coverage","provenance_coverage","temporal_coverage","quantitative_coverage","review_coverage","contradiction_coverage","correction_coverage","economic_metrics","domains","research_gaps"):
            if got.get(key)!=exp.get(key):return False
    return True

def set_answer_text(m,text): m["answer_text"]=text

def run():
    seed=present("What evidence is the system coverage for Tinubu, Obi and Atiku?",ROOT)
    expected=coverage_report(ROOT)
    mutations={
      "M1_remove_primary_source_classification":lambda m:[s.pop("primary_source_status",None) for s in m["sources"]],
      "M2_false_primary_source":lambda m:[s.update({"tier":2,"type":"secondary_report"}) for s in m["sources"][:1]],
      "M3_remove_research_gap":lambda m:m["coverage"]["known_gaps"].update({"bola-ahmed-tinubu":[]}),
      "M4_sparse_to_high":lambda m:m["coverage"]["candidates"]["peter-gregory-obi"]["domains"][0].update({"coverage":"HIGH"}),
      "M5_unknown_to_false":lambda m:(m.update({"answer_status":"ANSWERED"}),set_answer_text(m,"FALSE")),
      "M6_remove_contradiction":lambda m:m["coverage"]["candidates"]["peter-gregory-obi"].update({"contradiction_coverage":"HIGH"}),
      "M7_remove_correction_history":lambda m:m["coverage"]["candidates"]["atiku-abubakar"].update({"correction_coverage":"HIGH"}),
      "M8_remove_economic_provenance":lambda m:m["coverage"]["candidates"]["bola-ahmed-tinubu"]["economic_metrics"].pop("inflation",None),
      "M9_change_economic_geography":lambda m:m["sources"][0].update({"geography":"Anambra State"}),
      "M10_change_metric_unit":lambda m:m["coverage"]["candidates"]["bola-ahmed-tinubu"]["economic_metrics"]["exchange_rate"].update({"unit":"percent"}),
      "M11_change_observation_period":lambda m:m["sources"][0].update({"period":"1999"}),
      "M12_temporal_to_causal":lambda m:set_answer_text(m,"Tinubu caused the economic outcomes."),
      "M13_remove_policy_status":lambda m:m["coverage"]["candidates"]["peter-gregory-obi"]["domains"][7].update({"coverage":"HIGH"}),
      "M14_proposed_to_implemented":lambda m:m["coverage"]["candidates"]["peter-gregory-obi"]["domains"][7].update({"domain":"IMPLEMENTED_POLICY","coverage":"HIGH"}),
      "M15_implemented_to_success":lambda m:m["coverage"]["candidates"]["bola-ahmed-tinubu"]["domains"][7].update({"coverage":"HIGH","status":"DOCUMENTED_OUTCOME"}),
      "M16_remove_legal_event":lambda m:m["coverage"]["candidates"]["atiku-abubakar"]["domains"][9].update({"coverage":"HIGH"}),
      "M17_allegation_to_finding":lambda m:set_answer_text(m,"The allegation is established as fact."),
      "M18_remove_social_semantics":lambda m:m["coverage"]["candidates"]["bola-ahmed-tinubu"]["domains"][6].update({"coverage":"HIGH"}),
      "M19_fabricate_primary_availability":lambda m:m["sources"][0].update({"primary_source_status":"LOCATED","availability":"AVAILABLE"}),
      "M20_remove_limitation":lambda m:m["limitations"].pop(),
      "M21_partial_to_complete":lambda m:m["coverage"]["candidates"]["atiku-abubakar"].update({"quantitative_coverage":"HIGH","temporal_coverage":"HIGH"}),
      "M22_current_for_historical":lambda m:m["interpreted_query"].update({"as_of":"2026-08-30"}),
      "M23_remove_source_version":lambda m:m["sources"][0].pop("id",None),
      "M24_alter_quantitative_input":lambda m:m["coverage"]["candidates"]["bola-ahmed-tinubu"]["economic_metrics"]["inflation"].update({"observation_count":999}),
      "M25_alter_calculation_output":lambda m:set_answer_text(m,"Coverage calculation result: 999"),
      "M26_remove_candidate_isolation":lambda m:m["interpreted_query"].update({"candidate_scope":["bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar"]}),
      "M27_cross_contaminate":lambda m:m["evidence"][0].update({"candidate_id":"atiku-abubakar"}),
      "M28_remove_review_separation":lambda m:m["coverage"]["candidates"]["bola-ahmed-tinubu"].update({"review_coverage":"HIGH"}),
      "M29_remove_methodology_version":lambda m:m["provenance"].update({"methodology_version":None}),
      "M30_remove_research_gap_status":lambda m:m["coverage"]["candidates"]["atiku-abubakar"]["research_gaps"][0].pop("status",None),
    }
    for name,mutate in mutations.items():
        m=copy.deepcopy(seed); mutate(m); killed=not validate(m,expected,seed); print(f"{name}: {'KILLED' if killed else 'SURVIVED'}")
        if not killed: raise SystemExit(f"SURVIVED: {name}")
    print("MUTATION_SUMMARY: 30/30 killed")
if __name__=="__main__":run()
