from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
METHODOLOGY_VERSION="phase7-research-investigation-dossier-v1"
CANDIDATES=("bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar")
BLOCKED="candidate-4"
INVESTIGATION_STATES=("PLANNED","ACTIVE","EVIDENCE_ACQUISITION","EVIDENCE_REVIEW","PARTIALLY_COMPLETE","COMPLETE","BLOCKED","CLOSED")
CLAIM_STATES=("SUPPORTED","PARTIALLY_SUPPORTED","DISPUTED","INSUFFICIENT_EVIDENCE","UNVERIFIED","UNKNOWN","UNAVAILABLE")
REVIEW_STATES=("QUEUED","IN_REVIEW","APPROVED","REJECTED","NEEDS_MORE_EVIDENCE","BLOCKED")
def now(): return datetime.now(timezone.utc).isoformat()
def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def assert_candidate(cid):
    if cid==BLOCKED or cid not in CANDIDATES: raise ValueError("candidate scope contains blocked or unapproved subject")
def load_candidate(root,cid):
    assert_candidate(cid); return json.loads((Path(root)/"candidates"/cid/"data"/"pilot-record.json").read_text(encoding="utf-8"))
def temporal_ok(record,as_of):
    if not as_of:return True
    vals=[record.get(k) for k in ("publication_date","event_date","valid_from","date","retrieved_at","retrieval_date") if record.get(k)]
    return not vals or min(str(v)[:10] for v in vals)<=as_of
def make_investigation(cid,title,question,*,as_of="2026-08-30",priority=100,dependencies=()):
    assert_candidate(cid); iid="inv-"+hashlib.sha256(f"{cid}|{title}".encode()).hexdigest()[:20]
    return {"investigation_id":iid,"candidate_id":cid,"title":title,"research_question":question,"scope":{"candidate_id":cid,"geography":"Nigeria"},"as_of":as_of,"status":"PLANNED","priority":priority,"created_at":now(),"methodology_version":METHODOLOGY_VERSION,"research_tasks":[],"required_evidence":[],"claims_under_investigation":[],"known_unknowns":[],"research_gaps":[],"contradictions":[],"corrections":[],"reviews":[],"dependencies":list(dependencies),"provenance":{},"answerability":{"status":"INSUFFICIENT_EVIDENCE","reason":"Investigation existence does not establish truth."},"dossier_effect":[],"completion_state":"INCOMPLETE"}
def controlled_investigations(as_of="2026-08-30"):
    s=[("bola-ahmed-tinubu","economic-record","What evidence documents the economic record during Tinubu's presidency?"),("bola-ahmed-tinubu","election-history","What documentary evidence establishes Tinubu's election history?"),("peter-gregory-obi","anambra-fiscal","What evidence documents Peter Obi's Anambra fiscal record?"),("peter-gregory-obi","party-office","What evidence establishes Peter Obi's party and office chronology?"),("atiku-abubakar","adc-legal","What evidence establishes the ADC legal status relevant to Atiku Abubakar?"),("atiku-abubakar","federal-policy-ncp","What evidence documents Atiku's role in the National Council on Privatisation and federal policy?")]
    return [make_investigation(cid,title,q,as_of=as_of) for cid,title,q in s]
def investigation_tasks(inv):
    kinds=[("scope","ESTABLISH_SCOPE"),("facts","ESTABLISH_FACTS"),("primary","VERIFY_PRIMARY_SOURCE"),("gaps","RESOLVE_RESEARCH_GAPS")]; t=inv["title"].lower()
    if "economic" in t or "fiscal" in t:kinds.append(("quantitative","VERIFY_QUANTITATIVE_LINEAGE"))
    if "legal" in t:kinds.append(("legal","RECONSTRUCT_LEGAL_CHRONOLOGY"))
    if "election" in t:kinds.append(("election","RECONSTRUCT_ELECTION_SEMANTICS"))
    return [{"task_id":f"{inv['investigation_id']}-task-{i+1:02d}","investigation_id":inv["investigation_id"],"candidate_id":inv["candidate_id"],"task_type":typ,"question_kind":kind,"status":"QUEUED","priority":100 if i<4 else 80,"blocking":True,"dependencies":[] if i==0 else [f"{inv['investigation_id']}-task-{i:02d}"],"methodology_version":METHODOLOGY_VERSION} for i,(kind,typ) in enumerate(kinds)]
def claim_type(c):
    t=str(c.get("claim_type","")).upper(); return {"FACT":"DOCUMENTED_ACTION","CALCULATED_FACT":"QUANTITATIVE_RESULT","CAUSAL":"CAUSAL_PROPOSITION","STATEMENT_OCCURRENCE":"PUBLIC_STATEMENT","ASSESSMENT":"CONTESTED_CLAIM"}.get(t,t or "UNKNOWN")
def source_class(s): return "PRIMARY" if s.get("tier")==1 else "SECONDARY"
def build_gaps(d,cid):
    return [{"gap_id":f"gap-{cid}-{e.get('id','unknown')}","description":"Verification remains incomplete for an evidence relationship.","reason":str(e.get("status")),"required_evidence":"verification","tasks":[],"status":"OPEN","attempts":[],"sources":[e.get("source_id")],"resolution":None,"remaining_limitation":"Not verified."} for e in d.get("evidence",[]) if str(e.get("status","")).upper() in {"UNVERIFIED","UNKNOWN","INCOMPLETE","UNAVAILABLE"}]
def build_dossier(root,cid,*,version=1,as_of="2026-08-30",database_snapshot="runtime-reference"):
    d=load_candidate(root,cid); sources={s.get("id"):s for s in d.get("sources",[])}; sr=[{"source_id":s.get("id"),"source_class":source_class(s),"source_type":s.get("type"),"url":s.get("url"),"retrieval_date":s.get("retrieval_date"),"reliability":s.get("reliability"),"source_version_id":f"sv-{s.get('id')}","provenance_complete":bool(s.get("id") and s.get("url"))} for s in d.get("sources",[]) if temporal_ok(s,as_of)]; sids={s["source_id"] for s in sr}
    er=[{"evidence_id":e.get("id"),"source_id":e.get("source_id"),"source_version_id":f"sv-{e.get('source_id')}","evidence_relationship":e.get("relationship"),"claim_ids":e.get("claim_ids",[]),"status":e.get("status","UNASSESSED"),"provenance_complete":bool(e.get("id") and e.get("source_id") in sids)} for e in d.get("evidence",[]) if e.get("source_id") in sids]; eids={e["evidence_id"] for e in er}
    cr=[]
    for c in d.get("claims",[]):
        st=str(c.get("status","UNKNOWN")).upper(); state={"VERIFIED":"SUPPORTED","QUALIFIED":"PARTIALLY_SUPPORTED","INSUFFICIENT_EVIDENCE":"INSUFFICIENT_EVIDENCE","DISPUTED":"DISPUTED"}.get(st,"UNVERIFIED"); ids=[x for x in c.get("evidence_ids",[]) if x in eids]
        cr.append({"claim_id":c.get("id"),"candidate_id":cid,"claim_text":c.get("claim"),"claim_type":claim_type(c),"status":state,"evidence_ids":ids,"source_ids":[e["source_id"] for e in er if c.get("id") in e.get("claim_ids",[])],"investigation_ids":[],"review_ids":[],"confidence_qualification":c.get("causal_classification"),"as_of":as_of,"methodology_version":METHODOLOGY_VERSION,"provenance":{"source":"pilot-record","source_claim_id":c.get("id")}})
    gaps=build_gaps(d,cid); reviews=[{"review_id":f"review-{c['claim_id']}","claim_id":c["claim_id"],"reason":"material uncertainty or high-impact interpretation","required_reviewer_type":"domain_reviewer","status":"QUEUED","evidence_dependencies":c["evidence_ids"],"created_at":now(),"methodology_version":METHODOLOGY_VERSION} for c in cr if c["claim_type"] in {"CAUSAL_PROPOSITION","CONTESTED_CLAIM","LEGAL_STATUS","QUANTITATIVE_RESULT"} or c["status"] in {"DISPUTED","INSUFFICIENT_EVIDENCE"}]
    inv=[i for i in controlled_investigations(as_of) if i["candidate_id"]==cid]; invids=[i["investigation_id"] for i in inv]; [c.update(investigation_ids=invids) for c in cr]
    out={"dossier_id":f"dossier-{cid}","candidate_id":cid,"version_number":version,"created_at":now(),"as_of":as_of,"methodology_version":METHODOLOGY_VERSION,"source_versions":[s["source_version_id"] for s in sr],"evidence_ids":[e["evidence_id"] for e in er],"claim_ids":[c["claim_id"] for c in cr],"investigation_ids":invids,"research_gap_ids":[g["gap_id"] for g in gaps],"review_ids":[r["review_id"] for r in reviews],"identity":{"person":d.get("person"),"candidacy":d.get("candidacies",[])},"party_history":d.get("party_memberships",[]),"office_history":d.get("officeholdings",[]),"election_history":d.get("election_results",[]),"public_statements":[c for c in cr if c["claim_type"]=="PUBLIC_STATEMENT"],"related_public_conversation":[c for c in cr if c["claim_type"]=="PUBLIC_STATEMENT],"documented_actions":[],"policies":[],"economic_record":d.get("observations",[]),"legal_record":d.get("legal_events",[]),"contested_claims":[c for c in cr if c["status"] in {"DISPUTED","INSUFFICIENT_EVIDENCE"}],"corrections":d.get("corrections",[]),"uncertainty":[c for c in cr if c["status"]!="SUPPORTED"],"research_gaps":gaps,"reviews":reviews,"sources":sr,"evidence":er,"claims":cr,"investigations":inv,"database_snapshot":database_snapshot,"generation_metadata":{"generator":"phase7_dossier_assembly","candidate_source":"pilot-record"}}
    out["quality_gate"]=quality_gate(out); out["status"]=out["quality_gate"]["recommended_state"]; out["content_hash"]=digest({k:v for k,v in out.items() if k!="content_hash"}); return out
def quality_gate(d):
    checks={"identity_integrity":bool(d.get("identity",{}).get("person")),"candidate_candidacy_separation":isinstance(d.get("identity",{}).get("candidacy"),list),"claim_provenance":all(c.get("provenance") for c in d.get("claims",[])),"source_provenance":all(s.get("provenance_complete") for s in d.get("sources",[])),"evidence_relationships":all(e.get("evidence_id") and e.get("source_id") for e in d.get("evidence",[])),"research_gap_visibility":"research_gaps" in d,"correction_visibility":"corrections" in d,"contradiction_visibility":"contested_claims" in d,"review_requirements":all(r.get("review_id") and r.get("status") in REVIEW_STATES for r in d.get("reviews",[])),"quantitative_lineage":all("source_id" in o and "dataset_version" in o for o in d.get("economic_record",[]) if "metric" in o),"temporal_correctness":all(c.get("as_of")==d.get("as_of") for c in d.get("claims",[])),"candidate_isolation":d.get("candidate_id") in CANDIDATES,"methodology_version":d.get("methodology_version")==METHODOLOGY_VERSION}
    failures=[k for k,v in checks.items() if not v]; state="BLOCKED" if failures else ("IN_REVIEW" if d.get("research_gaps") or any(r["status"]!="APPROVED" for r in d.get("reviews",[])) else "QUALIFIED"); return {"checks":checks,"failures":failures,"recommended_state":state,"publishable":state=="QUALIFIED"}
def assemble_investigation_records(root,as_of="2026-08-30"):
    out=[]
    for inv in controlled_investigations(as_of):
        d=load_candidate(root,inv["candidate_id"]); inv["research_tasks"]=investigation_tasks(inv); inv["claims_under_investigation"]=[c.get("id") for c in d.get("claims",[])]; inv["required_evidence"]= [t["task_id"] for t in inv["research_tasks"]]; inv["research_gaps"]= [g["gap_id"] for g in build_gaps(d,inv["candidate_id"])]; inv["provenance"]={"methodology_version":METHODOLOGY_VERSION,"database_snapshot":"runtime-reference","as_of":as_of}; inv["status"]="PARTIALLY_COMPLETE" if inv["research_gaps"] else "COMPLETE"; inv["completion_state"]="INCOMPLETE" if inv["research_gaps"] else "COMPLETE"; inv["answerability"]={"status":"PARTIALLY_ANSWERABLE" if inv["research_gaps"] else "ANSWERABLE","reason":"Documentary coverage, not truth probability."}; inv["dossier_effect"]=["GAP_REMAINING_OPEN"] if inv["research_gaps"] else ["NEW_EVIDENCE"]; out.append(inv)
    return out
def dossier_diff(v1,v2):
    def d(a,b): return {"added":sorted(set(b)-set(a)),"removed":sorted(set(a)-set(b))}
    c=d(v1.get("claim_ids",[]),v2.get("claim_ids",[])); e=d(v1.get("evidence_ids",[]),v2.get("evidence_ids",[])); g=d(v1.get("research_gap_ids",[]),v2.get("research_gap_ids",[])); a={x["claim_id"]:x for x in v1.get("claims",[])}; b={x["claim_id"]:x for x in v2.get("claims",[])}
    return {"dossier_id":v2["dossier_id"],"from_version":v1["version_number"],"to_version":v2["version_number"],"ADDED_CLAIMS":c["added"],"REMOVED_CLAIMS":c["removed"],"CHANGED_CLAIMS":sorted(k for k in set(a)&set(b) if a[k]!=b[k]),"ADDED_EVIDENCE":e["added"],"REMOVED_EVIDENCE":e["removed"],"NEW_GAPS":g["added"],"RESOLVED_GAPS":g["removed"],"NEW_CONTRADICTIONS":[],"RESOLVED_CONTRADICTIONS":[],"CORRECTIONS":v2.get("corrections",[]),"SOURCE_VERSION_CHANGES":d(v1.get("source_versions",[]),v2.get("source_versions",[]))}
def snapshot(d):
    s={"candidate_id":d["candidate_id"],"dossier_id":d["dossier_id"],"version_number":d["version_number"],"as_of":d["as_of"],"claim_count":len(d["claims"]),"evidence_count":len(d["evidence"]),"source_count":len(d["sources"]),"open_research_gaps":len(d["research_gaps"]),"review_queue_count":sum(r["status"]=="QUEUED" for r in d["reviews"]),"contradiction_count":len(d.get("contested_claims",[])),"correction_count":len(d.get("corrections",[])),"methodology_version":d["methodology_version"],"database_snapshot":d["database_snapshot"]}; s["content_hash"]=digest(s); return s
def valid_dossier(d): return not quality_gate(d)["failures"]
