from __future__ import annotations
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from phase7_dossier import CANDIDATES,BLOCKED,METHODOLOGY_VERSION,build_dossier,dossier_diff,snapshot,quality_gate
from phase7_investigation import assemble_investigation_records
ROOT=Path(__file__).resolve().parents[1]; REPORT=ROOT/"reports"; AS_OF="2026-08-30"
def write(n,x): (REPORT/n).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
def md(n,t,x): (REPORT/n).write_text("# "+t+"\n\n```json\n"+json.dumps(x,indent=2,sort_keys=True)+"\n```\n")
def main():
 REPORT.mkdir(exist_ok=True); invs=assemble_investigation_records(ROOT,AS_OF); ds={c:build_dossier(ROOT,c,as_of=AS_OF,database_snapshot="round5-reference") for c in CANDIDATES}
 v1=copy.deepcopy(ds["bola-ahmed-tinubu"]); removed=v1["evidence_ids"][-1] if v1["evidence_ids"] else None
 if removed:
  v1["evidence_ids"].remove(removed); v1["evidence"]=[e for e in v1["evidence"] if e["evidence_id"]!=removed]
  for c in v1["claims"]: c["evidence_ids"]=[x for x in c["evidence_ids"] if x!=removed]
  v1["research_gap_ids"].append("gap-v1-"+removed); v1["quality_gate"]=quality_gate(v1); v1["status"]=v1["quality_gate"]["recommended_state"]
 v2=copy.deepcopy(v1); v2["version_number"]=2
 if removed:
  original=next(e for e in ds["bola-ahmed-tinubu"]["evidence"] if e["evidence_id"]==removed); v2["evidence"].append(original); v2["evidence_ids"].append(removed)
  for c in v2["claims"]:
   oc=next((x for x in ds["bola-ahmed-tinubu"]["claims"] if x["claim_id"]==c["claim_id"]),None)
   if oc and removed in oc["evidence_ids"]: c["evidence_ids"].append(removed)
  v2["research_gap_ids"]=[x for x in v2["research_gap_ids"] if x!="gap-v1-"+removed]; v2["quality_gate"]=quality_gate(v2); v2["status"]=v2["quality_gate"]["recommended_state"]
 diff=dossier_diff(v1,v2); snaps={c:snapshot(d) for c,d in ds.items()}
 historical={"as_of_2023":build_dossier(ROOT,"bola-ahmed-tinubu",as_of="2023-12-31",database_snapshot="round5-reference"),"as_of_2026":ds["bola-ahmed-tinubu"]}
 write("phase-7-research-investigation.json",{"phase":"7","methodology_version":METHODOLOGY_VERSION,"as_of":AS_OF,"investigations":invs}); md("phase-7-research-investigation.md","Phase 7 — Research Investigation",{"investigations":invs})
 write("phase-7-dossier-assembly.json",{"phase":"7","candidate_scope":list(CANDIDATES),"candidate_4":BLOCKED,"dossiers":ds}); md("phase-7-dossier-assembly.md","Phase 7 — Dossier Assembly",{"dossiers":ds})
 write("phase-7-dossier-diff.json",diff); md("phase-7-dossier-diff.md","Phase 7 — Dossier Diff",diff)
 queue=[r for d in ds.values() for r in d["reviews"]]; write("phase-7-review-queue.json",{"status":"QUEUED","items":queue}); md("phase-7-review-queue.md","Phase 7 — Review Queue",{"status":"QUEUED","items":queue})
 coverage={"investigations":len(invs),"candidate_investigations":sum(i["candidate_id"] is not None for i in invs),"shared_investigations":sum(i["candidate_id"] is None for i in invs),"tasks":sum(len(i["research_tasks"]) for i in invs),"dossier_versions":4,"v1_v2_added_evidence":diff["ADDED_EVIDENCE"],"historical_rebuilds":2,"candidates":list(CANDIDATES),"candidate_4":BLOCKED,"reviews_queued":len(queue),"open_gaps":sum(len(d["research_gaps"]) for d in ds.values()),"methodology_version":METHODOLOGY_VERSION}
 write("phase-7-coverage.json",coverage); md("phase-7-coverage.md","Phase 7 — Coverage",coverage); write("phase-7-snapshots.json",snaps); write("phase-7-v1-v2.json",{"v1":v1,"v2":v2}); write("phase-7-historical-rebuild.json",historical)
 print("PHASE7_ASSEMBLY_OK",json.dumps({"investigations":len(invs),"tasks":coverage["tasks"]}))
if __name__=="__main__": main()
