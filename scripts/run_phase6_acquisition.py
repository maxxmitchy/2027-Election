from __future__ import annotations
import json, os
from dataclasses import asdict
from pathlib import Path
from phase6_acquisition import METHODOLOGY_VERSION, ResearchTask, capture, verify, extract_evidence, make_task, now, sha256

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"evidence"/"phase-6"/"artifacts"
REPORT=ROOT/"reports"

def main():
    manifest=json.loads((ROOT/"phase6_controlled_sources.json").read_text())
    tasks=[]; discoveries=[]; retrievals=[]; verifications=[]; evidence=[]; gaps=[]; versions=[]
    for item in manifest:
        tid=f"phase6-{item['id']}"
        task=make_task(f"phase6-investigation-{item['kind']}",item.get("candidate_id"),item["title"],item["title"],item["id"],"PRIMARY_REQUIRED" if item["primary_required"] else "PRIMARY_NOT_REQUIRED",priority=100,gap=f"gap-{item['id']}",effect="RESOLVE_GAP")
        d={"discovery_id":"disc-"+sha256(item["id"].encode())[:16],"task_id":task.task_id,"candidate_id":item.get("candidate_id"),"discovery_url":item["url"],"canonical_url":item["url"],"source_title":item["title"],"publisher":item["publisher"],"publication_date":None,"discovery_timestamp":now(),"discovery_method":"controlled_public_corpus","source_type":item["source_type"],"candidate_relevance":True,"claim_relevance":True,"primary_secondary":"PRIMARY" if item["primary_required"] else "SECONDARY","verification_status":"UNVERIFIED","capture_status":"NOT_CAPTURED"}
        task.status="DISCOVERED"; task.result={"discovered":[d]}; discoveries.append(d)
        r=capture(task,d,OUT)
        retrievals.append(r)
        if r.get("retrieval_status")=="SUCCESS":
            v=verify(task,d,r)
            verifications.append({"task_id":task.task_id,**v})
            if v.get("verification_status") in {"VERIFIED","PARTIALLY_VERIFIED"}:
                ev=extract_evidence(task,d,r,v,item["title"])
                evidence.append(ev)
                task.status="COMPLETE" if v.get("verification_status")=="VERIFIED" else "REQUIRES_REVIEW"
                versions.append({"source_id":d["canonical_url"],"source_version_id":r["artifact_id"],"content_hash":r["content_hash"],"retrieval_event_id":r["retrieval_event_id"],"version_policy":"immutable"})
            else: task.status="REQUIRES_REVIEW"
        else:
            verifications.append({"task_id":task.task_id,"verification_status":"UNAVAILABLE","primary_state":"PRIMARY_UNAVAILABLE" if item["primary_required"] else "SECONDARY_ONLY"})
        gaps.append({"gap_id":f"gap-{item['id']}","candidate":item.get("candidate_id"),"status":"RESOLVED" if task.status=="COMPLETE" else ("UNAVAILABLE" if task.status=="UNAVAILABLE" else "PARTIALLY_RESOLVED" if task.status=="REQUIRES_REVIEW" else "OPEN"),"last_task_id":task.task_id})
        tasks.append(asdict(task))
    # Add explicit controlled contradiction and revision records without pretending they are source truth.
    contradictions=[{"contradiction_id":"phase6-contradiction-01","status":"OPEN","source_a":"controlled-source-A","source_b":"controlled-source-B","resolution":"REQUIRES_REVIEW","basis":"definition_or_period_must_be_checked"}]
    corrections=[{"correction_id":"phase6-revision-01","source_id":"revision-fixture","old_version":"v1","new_version":"v2","old_preserved":True,"reason":"new captured content"}]
    bundle={"phase":"6","name":"Evidence Acquisition & Research Execution","methodology_version":METHODOLOGY_VERSION,"generated_at":now(),"tasks":tasks,"discoveries":discoveries,"retrieval_events":retrievals,"source_versions":versions,"evidence":evidence,"verifications":verifications,"research_gaps":gaps,"contradictions":contradictions,"corrections":corrections,"candidate_4":"BLOCKED","candidate_scope":["bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar"],"summary":{"tasks_executed":len(tasks),"sources_discovered":len(discoveries),"sources_captured":sum(r.get("retrieval_status")=="SUCCESS" for r in retrievals),"sources_verified":sum(v.get("verification_status")=="VERIFIED" for v in verifications),"retrieval_failures":sum(r.get("retrieval_status")=="RETRIEVAL_FAILED" for r in retrievals),"evidence_records":len(evidence),"gaps_resolved":sum(g["status"]=="RESOLVED" for g in gaps),"gaps_remaining_open":sum(g["status"]=="OPEN" for g in gaps)}}
    REPORT.mkdir(exist_ok=True); (REPORT/"phase-6-evidence-acquisition.json").write_text(json.dumps(bundle,indent=2)+"\n")
    (REPORT/"phase-6-evidence-acquisition.md").write_text("# Phase 6 — Evidence Acquisition & Research Execution\n\n```json\n"+json.dumps(bundle,indent=2)+"\n```\n")
    (REPORT/"phase-6-source-acquisition.json").write_text(json.dumps({"sources":discoveries,"retrieval_events":retrievals,"source_versions":versions},indent=2)+"\n")
    (REPORT/"phase-6-source-acquisition.md").write_text("# Phase 6 — Source Acquisition\n\n"+json.dumps({"sources":discoveries,"retrieval_events":retrievals,"source_versions":versions},indent=2)+"\n")
    (REPORT/"phase-6-research-execution.json").write_text(json.dumps({"tasks":tasks,"verifications":verifications,"evidence":evidence,"gaps":gaps},indent=2)+"\n")
    (REPORT/"phase-6-research-execution.md").write_text("# Phase 6 — Research Execution\n\n"+json.dumps({"tasks":tasks,"verifications":verifications,"evidence":evidence,"gaps":gaps},indent=2)+"\n")
    (REPORT/"phase-6-coverage.json").write_text(json.dumps({"model":"acquisition-integrity-v1","discovery_is_not_verification":True,"source_is_not_evidence":True,"evidence_is_not_review":True,"statement_is_not_truth":True,"retrieval_failure_is_not_falsity":True,"gaps":gaps},indent=2)+"\n")
    (REPORT/"phase-6-coverage.md").write_text("# Phase 6 — Coverage\n\n"+json.dumps({"model":"acquisition-integrity-v1","gaps":gaps},indent=2)+"\n")
    return bundle

if __name__=="__main__":
    b=main(); print(json.dumps(b["summary"],indent=2))
