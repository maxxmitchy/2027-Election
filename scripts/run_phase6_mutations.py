from __future__ import annotations
# Phase 6 implementation point: mutation audit is a fail-closed gate.
import copy, json
from datetime import datetime, timezone
from pathlib import Path
from tests.test_phase6_evidence_acquisition import baseline_bundle, valid_bundle

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"reports"

def main():
    seed=baseline_bundle()
    muts={
      "M1_discovery_as_verification":lambda b:b["sources"][0].update({"verification_status":"DISCOVERED"}),
      "M2_secondary_as_primary":lambda b:b["sources"][0].update({"source_class":"SECONDARY"}),
      "M3_remove_primary_gap":lambda b:b.update({"research_gaps":[]}),
      "M4_retrieval_failure_as_false":lambda b:b["retrieval_events"][0].update({"retrieval_status":"FALSE"}),
      "M5_source_disappearance_as_false":lambda b:b["sources"][0].update({"verification_status":"FALSE"}),
      "M6_remove_content_hash":lambda b:b["evidence"][0].update({"content_hash":None}),
      "M7_change_source_version":lambda b:b["versions"][0].update({"source_version_id":"v2"}),
      "M8_duplicate_evidence":lambda b:b["evidence"].append(copy.deepcopy(b["evidence"][0])),
      "M9_duplicate_task_execution":lambda b:b["tasks"].append(copy.deepcopy(b["tasks"][0])),
      "M10_remove_provenance":lambda b:b["evidence"][0].pop("retrieval_event_id"),
      "M11_evidence_as_review":lambda b:b["review"].update({"review_is_not_source":False}),
      "M12_review_as_evidence":lambda b:b["evidence"][0].update({"verification_status":"REVIEW_COMPLETED"}),
      "M13_statement_as_truth":lambda b:b.update({"truth_probability":True}),
      "M14_remove_legal_chronology":lambda b:b.update({"legal_chronology":[]}),
      "M15_remove_election_result_semantics":lambda b:b.update({"election_semantics":["nomination"]}),
      "M16_corrupt_metric_unit":lambda b:b["economic_metadata"].update({"unit":"percent"}),
      "M17_corrupt_geography":lambda b:b["economic_metadata"].update({"geography":"Lagos State"}),
      "M18_corrupt_period":lambda b:b["economic_metadata"].update({"period":"monthly"}),
      "M19_remove_dataset_version":lambda b:b["economic_metadata"].update({"dataset_version":None}),
      "M20_remove_methodology":lambda b:b["economic_metadata"].update({"methodology":None}),
      "M21_cross_candidate_contamination":lambda b:b["tasks"][0].update({"candidate_id":"bola-ahmed-tinubu"}),
      "M22_candidate_scope_removal":lambda b:b["tasks"][0].update({"candidate_id":None}),
      "M23_remove_research_gap":lambda b:b.update({"research_gaps":[]}),
      "M24_force_gap_closed":lambda b:b["research_gaps"][0].update({"status":"RESOLVED"}),
      "M25_remove_as_of":lambda b:b.update({"as_of":None}),
      "M26_source_text_instruction_injection":lambda b:b["sources"][0].update({"verification_status":"INJECTED_INSTRUCTION"}),
      "M27_source_version_overwrite":lambda b:b["versions"][0].update({"content_hash":"b"*64}),
      "M28_retrieval_event_identity_corruption":lambda b:b["retrieval_events"][0].update({"retrieval_event_id":"r2"}),
      "M29_evidence_source_substitution":lambda b:b["evidence"][0].update({"source_version_id":"v2"}),
      "M30_verification_status_inflation":lambda b:b["evidence"][0].update({"verification_status":"VERIFIED_BY_REVIEW"})}
    results=[]
    for name,mutate in muts.items():
        m=copy.deepcopy(seed); mutate(m); killed=not valid_bundle(m)
        results.append({"mutation":name,"defect":"critical invariant mutation","expected_failure":"baseline validation must reject corrupted bundle","actual_result":"KILLED" if killed else "SURVIVED","status":"KILLED" if killed else "SURVIVED"})
        if not killed: raise SystemExit(f"SURVIVED: {name}")
    bundle={"phase":"6","methodology_version":"phase6-evidence-acquisition-v1","generated_at":datetime.now(timezone.utc).isoformat(),"mutation_count":len(results),"killed":sum(r["status"]=="KILLED" for r in results),"survived":sum(r["status"]=="SURVIVED" for r in results),"results":results}
    REPORT.mkdir(exist_ok=True); (REPORT/"phase-6-mutation-results.json").write_text(json.dumps(bundle,indent=2)+"\n"); (REPORT/"phase-6-mutation-results.md").write_text("# Phase 6 — Mutation Results\n\n**Result:** 30/30 killed\n\n| Mutation | Result |\n|---|---|\n"+"\n".join(f"| {r['mutation']} | {r['status']} |" for r in results)+"\n")
    print(f"MUTATION_SUMMARY: {bundle['killed']}/{bundle['mutation_count']} killed")
if __name__=="__main__": main()
