from __future__ import annotations
import hashlib
from phase7_dossier import METHODOLOGY_VERSION, CANDIDATES, controlled_investigations as candidate_investigations, investigation_tasks, load_candidate, build_gaps, make_investigation

def make_shared(title, question, as_of="2026-08-30"):
    iid="inv-shared-"+hashlib.sha256(title.encode()).hexdigest()[:20]
    return make_investigation.__wrapped__(None,title,question,as_of=as_of) if hasattr(make_investigation,"__wrapped__") else {
      "investigation_id":iid,"candidate_id":None,"title":title,"research_question":question,
      "scope":{"candidate_ids":list(CANDIDATES),"shared":True},"as_of":as_of,"status":"PLANNED","priority":100,
      "created_at":as_of+"T00:00:00+00:00","methodology_version":METHODOLOGY_VERSION,
      "research_tasks":[],"required_evidence":[],"claims_under_investigation":[],"known_unknowns":[],
      "research_gaps":[],"contradictions":[],"corrections":[],"reviews":[],"dependencies":[],"provenance":{},
      "answerability":{"status":"INSUFFICIENT_EVIDENCE","reason":"Shared investigation does not establish truth."},
      "dossier_effect":[],"completion_state":"INCOMPLETE"
    }

def controlled_investigations(as_of="2026-08-30"):
    shared=[
      make_shared("Cross-candidate quantitative comparison","Which quantitative observations are comparable across the three validated candidates?",as_of),
      make_shared("Contradiction investigation","Which candidate claims or evidence relationships contain unresolved contradictions?",as_of),
      make_shared("Public-conversation investigation","Which public-conversation records require verification or contextual review?",as_of),
      make_shared("Research-gap investigation","Which Phase 5/6 research gaps remain unresolved and what evidence is required?",as_of),
    ]
    return candidate_investigations(as_of)+shared

def assemble_investigation_records(root,as_of="2026-08-30"):
    records=[]
    for inv in controlled_investigations(as_of):
        if inv["candidate_id"] is None:
            inv["research_tasks"]=[{
              "task_id":f"{inv['investigation_id']}-task-{i+1:02d}","investigation_id":inv["investigation_id"],"candidate_id":None,
              "task_type":typ,"question_kind":kind,"status":"QUEUED","priority":100,"blocking":True,
              "dependencies":[] if i==0 else [f"{inv['investigation_id']}-task-{i:02d}"],"methodology_version":METHODOLOGY_VERSION
            } for i,(kind,typ) in enumerate([("scope","ESTABLISH_SCOPE"),("comparison","ASSESS_COMPARABILITY"),("contradictions","ASSESS_CONTRADICTIONS"),("gaps","RESOLVE_RESEARCH_GAPS")])]
            inv["required_evidence"]=[t["task_id"] for t in inv["research_tasks"]]
            inv["provenance"]={"methodology_version":METHODOLOGY_VERSION,"database_snapshot":"runtime-reference","as_of":as_of}
            inv["status"]="PARTIALLY_COMPLETE"; inv["completion_state"]="INCOMPLETE"; inv["dossier_effect"]=["GAP_REMAINING_OPEN"] if inv["title"].startswith("Research-gap") else ["NEW_EVIDENCE"]
            records.append(inv); continue
        data=load_candidate(root,inv["candidate_id"]); inv["research_tasks"]=investigation_tasks(inv); inv["claims_under_investigation"]=[c.get("id") for c in data.get("claims",[])]; inv["required_evidence"]=[t["task_id"] for t in inv["research_tasks"]]; inv["research_gaps"]=[g["gap_id"] for g in build_gaps(data,inv["candidate_id"])]; inv["provenance"]={"methodology_version":METHODOLOGY_VERSION,"database_snapshot":"runtime-reference","as_of":as_of}; inv["status"]="PARTIALLY_COMPLETE" if inv["research_gaps"] else "COMPLETE"; inv["completion_state"]="INCOMPLETE" if inv["research_gaps"] else "COMPLETE"; inv["answerability"]={"status":"PARTIALLY_ANSWERABLE" if inv["research_gaps"] else "ANSWERABLE","reason":"Documentary coverage, not truth probability."}; inv["dossier_effect"]=["GAP_REMAINING_OPEN"] if inv["research_gaps"] else ["NEW_EVIDENCE"]; records.append(inv)
    return records
