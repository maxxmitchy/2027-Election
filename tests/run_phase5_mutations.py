"""Controlled Phase 5 mutations. Any critical invariant mutation must be observable."""
from __future__ import annotations
import copy, json
from pathlib import Path
from research_workbench import BLOCKED, CANDIDATES, METHODOLOGY_VERSION, investigate
ROOT=Path(__file__).resolve().parents[1]


def baseline():
    return investigate(ROOT,"What evidence exists for Peter Obi's economic record?",as_of="2026-08-30")


def valid(m):
    q=m["investigation"]["question"]
    if not q.get("candidate_scope") or BLOCKED in q["candidate_scope"]: return False
    if q.get("methodology_version")!=METHODOLOGY_VERSION: return False
    if not m["investigation"]["sub_questions"]: return False
    if not m["investigation"]["evidence_requirements"]: return False
    if any(r.get("required_provenance") is not True for r in m["investigation"]["evidence_requirements"]): return False
    if m["review"]["status"]!="NOT_REVIEWED" or m["review"]["review_is_not_source"] is not True: return False
    if "truth probability" not in m["answerability"]["reason"].lower(): return False
    if not m["provenance"].get("database_snapshot") or not m["provenance"].get("generation_timestamp"): return False
    if any(s.get("verification_state")=="VERIFIED" for s in m["sources"]): return False
    return True


def run():
    seed=baseline()
    muts={
      "M1_remove_claim_decomposition":lambda m:m["investigation"].update({"sub_questions":[]}),
      "M2_remove_evidence_requirement":lambda m:m["investigation"].update({"evidence_requirements":[]}),
      "M3_secondary_as_primary":lambda m:m["investigation"]["evidence_requirements"][0].update({"required_source_class":"PRIMARY"}),
      "M4_remove_primary_gap":lambda m:m["research_gaps"].clear(),
      "M5_remove_research_gap":lambda m:m["research_gaps"].clear(),
      "M6_corrupt_gap_status":lambda m:m["research_gaps"].__getitem__(0).update({"status":"RESOLVED"}) if m["research_gaps"] else m["investigation"].update({"status":"ANSWERABLE"}),
      "M7_remove_contradiction":lambda m:m.update({"contradictions":[]}),
      "M8_remove_correction":lambda m:m.update({"corrections":[]}),
      "M9_temporal_to_causal":lambda m:m["investigation"]["question"].update({"question_type":"CAUSAL"}),
      "M10_proposed_to_implemented":lambda m:m["investigation"]["question"].update({"domain":"policy"}),
      "M11_allegation_to_finding":lambda m:m["investigation"]["question"].update({"domain":"legal"}),
      "M12_nomination_to_result":lambda m:m["investigation"]["question"].update({"domain":"electoral"}),
      "M13_statement_to_truth":lambda m:m["investigation"]["question"].update({"question_type":"PUBLIC_CONVERSATION"}),
      "M14_corrupt_metric_unit":lambda m:m["investigation"]["evidence_requirements"][0].update({"required_unit":"percent"}),
      "M15_corrupt_geography":lambda m:m["investigation"]["question"].update({"geographic_scope":"Mars"}),
      "M16_corrupt_period":lambda m:m["investigation"]["question"].update({"temporal_scope":{"as_of":"1999"}}),
      "M17_remove_as_of":lambda m:m["provenance"].update({"as_of":None}),
      "M18_current_state_substitution":lambda m:m["provenance"].update({"database_snapshot":"current"}),
      "M19_review_to_evidence":lambda m:m["review"].update({"review_is_not_source":False}),
      "M20_answerability_inflation":lambda m:m["answerability"].update({"status":"ANSWERABLE"}),
      "M21_candidate_contamination":lambda m:m["investigation"]["question"]["candidate_scope"].append("candidate-4"),
      "M22_remove_candidate_scope":lambda m:m["investigation"]["question"].update({"candidate_scope":[]}),
      "M23_remove_provenance":lambda m:m["provenance"].pop("methodology_version",None),
      "M24_remove_methodology":lambda m:m["investigation"]["question"].update({"methodology_version":None}),
      "M25_remove_dependency":lambda m:m["performance_metadata"].update({"dependency_depth":0}),
      "M26_hide_stale_result":lambda m:m["investigation"].update({"status":"ANSWERABLE"}),
    }
    for name,mutate in muts.items():
        m=copy.deepcopy(seed); mutate(m); killed=not valid(m); print(f"{name}: {'KILLED' if killed else 'SURVIVED'}")
        if not killed: raise SystemExit(f"SURVIVED: {name}")
    print("MUTATION_SUMMARY: 26/26 killed")

if __name__=="__main__": run()
