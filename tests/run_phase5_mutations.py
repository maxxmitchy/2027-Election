"""Controlled Phase 5 mutations. Any critical invariant mutation must be observable."""
from __future__ import annotations
import copy, json
from pathlib import Path
from research_workbench import BLOCKED, CANDIDATES, GAP_STATES, METHODOLOGY_VERSION, investigate
ROOT=Path(__file__).resolve().parents[1]


def baseline():
    m=investigate(ROOT,"What evidence exists for Peter Obi's economic record?",as_of="2026-08-30")
    m["contradictions"]=[{"id":"mutation-fixture-contradiction","status":"OPEN","material_conflict":True}]
    m["corrections"]=[{"id":"mutation-fixture-correction","status":"OPEN","supersedes":"mutation-fixture-v1"}]
    return m


def valid(m, expected):
    q=m["investigation"]["question"]; eq=expected["investigation"]["question"]
    if q.get("candidate_scope")!=eq.get("candidate_scope") or BLOCKED in q.get("candidate_scope",[]): return False
    for key in ("methodology_version","question_type","domain","temporal_scope","geographic_scope"):
        if q.get(key)!=eq.get(key): return False
    if not m["investigation"]["sub_questions"]: return False
    er=m["investigation"]["evidence_requirements"]; eer=expected["investigation"]["evidence_requirements"]
    if er!=eer: return False
    if any(r.get("required_provenance") is not True for r in er): return False
    if not m["research_gaps"] or any(g.get("status") not in GAP_STATES for g in m["research_gaps"]): return False
    if m["research_gaps"]!=expected["research_gaps"]: return False
    if m["contradictions"]!=expected["contradictions"] or m["corrections"]!=expected["corrections"]: return False
    if m["review"]!=expected["review"]: return False
    if m["answerability"]["status"]!=expected["answerability"]["status"]: return False
    if "truth probability" not in m["answerability"]["reason"].lower(): return False
    if m["provenance"].get("as_of")!=expected["provenance"].get("as_of"): return False
    if m["provenance"].get("database_snapshot")!=expected["provenance"].get("database_snapshot"): return False
    if m["provenance"].get("methodology_version")!=expected["provenance"].get("methodology_version"): return False
    if m["performance_metadata"].get("dependency_depth")!=expected["performance_metadata"].get("dependency_depth"): return False
    if m["investigation"].get("status")!=expected["investigation"].get("status"): return False
    if any(s.get("verification_state")=="VERIFIED" for s in m["sources"]): return False
    if m["sources"]!=expected["sources"]: return False
    return True


def run():
    seed=baseline()
    muts={
      "M1_remove_claim_decomposition":lambda m:m["investigation"].update({"sub_questions":[]}),
      "M2_remove_evidence_requirement":lambda m:m["investigation"].update({"evidence_requirements":[]}),
      "M3_secondary_as_primary":lambda m:m["sources"][0].update({"source_class":"PRIMARY","verification_state":"VERIFIED"}),
      "M4_remove_primary_gap":lambda m:m["research_gaps"].clear(),
      "M5_remove_research_gap":lambda m:m["research_gaps"].clear(),
      "M6_corrupt_gap_status":lambda m:m["research_gaps"].__getitem__(0).update({"status":"ANSWERED"}) if m["research_gaps"] else m["investigation"].update({"status":"ANSWERABLE"}),
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
        m=copy.deepcopy(seed); mutate(m); killed=not valid(m,seed); print(f"{name}: {'KILLED' if killed else 'SURVIVED'}")
        if not killed: raise SystemExit(f"SURVIVED: {name}")
    print("MUTATION_SUMMARY: 26/26 killed")

if __name__=="__main__": run()
