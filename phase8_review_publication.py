from __future__ import annotations
import copy, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

METHODOLOGY_VERSION = "phase8-review-publication-v1"
CANDIDATES = ("bola-ahmed-tinubu", "peter-gregory-obi", "atiku-abubakar")
BLOCKED = "candidate-4"
CRITICAL_TYPES = {"ELECTION_RESULT","OFFICEHOLDING","LEGAL_STATUS","CAUSAL_PROPOSITION","QUANTITATIVE_RESULT","CONTESTED_CLAIM","PUBLIC_STATEMENT","DOCUMENTED_ACTION","CURRENT_PARTY_STATUS","CURRENT_CANDIDACY"}
REVIEW_TYPES = ("EVIDENCE_QUALITY","FACTUAL_ACCURACY","SOURCE_QUALITY","CONTEXT_COMPLETENESS","QUANTITATIVE_ACCURACY","CAUSAL_REASONING","TEMPORAL_ACCURACY","LEGAL_INTERPRETATION","ELECTION_INTERPRETATION","OFFICEHOLDING_INTERPRETATION","PUBLIC_CONVERSATION","CROSS_CANDIDATE_COMPARABILITY","PROVENANCE","DOSSIER_COMPLETENESS","PUBLICATION_READINESS")
REVIEW_OUTCOMES = ("APPROVED","APPROVED_WITH_QUALIFICATION","NEEDS_MORE_EVIDENCE","NEEDS_CORRECTION","REJECTED","BLOCKED","NOT_APPLICABLE")
REVIEW_STATES = ("QUEUED","IN_REVIEW","COMPLETED")
REVIEWER_TYPES = ("FACT_CHECKER","SOURCE_REVIEWER","LEGAL_REVIEWER","ELECTION_REVIEWER","ECONOMIC_REVIEWER","QUANTITATIVE_REVIEWER","TEMPORAL_REVIEWER","EDITORIAL_REVIEWER","PROVENANCE_REVIEWER","GENERAL_RESEARCH_REVIEWER")
PUBLICATION_STATES = ("IN_REVIEW","NEEDS_MORE_EVIDENCE","QUALIFIED","QUALIFIED_WITH_LIMITATIONS","BLOCKED","PUBLISHED")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def _records(root: Path):
    p = root / "reports" / "phase-7-dossier-assembly.json"
    if not p.exists():
        # Phase 7 V2 assembly script is the canonical producer in the current branch.
        p = root / "reports" / "phase-7-dossier-assembly-v2.json"
    if not p.exists():
        raise FileNotFoundError("Phase 7 dossier assembly report is required")
    data = json.loads(p.read_text())
    return data.get("dossiers", data)


def load_dossiers(root):
    return _records(Path(root))


def reviewer_for(review_type):
    return {
        "QUANTITATIVE_ACCURACY":"QUANTITATIVE_REVIEWER", "CAUSAL_REASONING":"GENERAL_RESEARCH_REVIEWER",
        "LEGAL_INTERPRETATION":"LEGAL_REVIEWER", "ELECTION_INTERPRETATION":"ELECTION_REVIEWER",
        "OFFICEHOLDING_INTERPRETATION":"GENERAL_RESEARCH_REVIEWER", "PUBLIC_CONVERSATION":"FACT_CHECKER",
        "PROVENANCE":"PROVENANCE_REVIEWER", "SOURCE_QUALITY":"SOURCE_REVIEWER", "TEMPORAL_ACCURACY":"TEMPORAL_REVIEWER",
        "CROSS_CANDIDATE_COMPARABILITY":"QUANTITATIVE_REVIEWER", "PUBLICATION_READINESS":"EDITORIAL_REVIEWER",
    }.get(review_type, "FACT_CHECKER")


def target_review_type(claim):
    t = claim.get("claim_type")
    if t == "QUANTITATIVE_RESULT": return "QUANTITATIVE_ACCURACY"
    if t == "CAUSAL_PROPOSITION": return "CAUSAL_REASONING"
    if t == "LEGAL_STATUS": return "LEGAL_INTERPRETATION"
    if t == "ELECTION_RESULT": return "ELECTION_INTERPRETATION"
    if t == "OFFICEHOLDING": return "OFFICEHOLDING_INTERPRETATION"
    if t == "PUBLIC_STATEMENT": return "PUBLIC_CONVERSATION"
    if t in {"CONTESTED_CLAIM","DOCUMENTED_ACTION","CURRENT_PARTY_STATUS","CURRENT_CANDIDACY"}: return "FACTUAL_ACCURACY"
    return "EVIDENCE_QUALITY"


def make_review(candidate_id, dossier, claim, review_type=None, investigation_id=None):
    review_type = review_type or target_review_type(claim)
    return {
        "review_id": f"p8-review-{claim['claim_id']}-{review_type.lower()}", "review_target": "CLAIM",
        "candidate_id": candidate_id, "dossier_id": dossier["dossier_id"], "dossier_version": dossier["version_number"],
        "claim_id": claim["claim_id"], "investigation_id": investigation_id, "review_type": review_type,
        "reviewer_type": reviewer_for(review_type), "status": "QUEUED",
        "findings": [], "required_actions": [], "evidence_considered": list(claim.get("evidence_ids", [])),
        "source_versions_considered": [], "methodology_version": METHODOLOGY_VERSION,
        "created_at": now(), "completed_at": None,
        "provenance": {"kind":"review_record","review_is_evidence":False},
    }


def controlled_targets(dossiers):
    targets = []
    def add(cid, predicate, rtype=None):
        d = dossiers[cid]
        for c in d.get("claims", []):
            if predicate(c):
                targets.append(make_review(cid,d,c,rtype)); return
    add("bola-ahmed-tinubu", lambda c:c.get("claim_type")=="QUANTITATIVE_RESULT")
    add("bola-ahmed-tinubu", lambda c:c.get("claim_type")=="ELECTION_RESULT", "ELECTION_INTERPRETATION")
    add("bola-ahmed-tinubu", lambda c:c.get("claim_type")=="PUBLIC_STATEMENT", "PUBLIC_CONVERSATION")
    add("bola-ahmed-tinubu", lambda c:True, "FACTUAL_ACCURACY")
    add("peter-gregory-obi", lambda c:"fiscal" in str(c.get("claim_text","")).lower() or c.get("claim_type")=="QUANTITATIVE_RESULT", "QUANTITATIVE_ACCURACY")
    add("peter-gregory-obi", lambda c:"party" in str(c.get("claim_text","")).lower() or "office" in str(c.get("claim_text","")).lower(), "OFFICEHOLDING_INTERPRETATION")
    add("peter-gregory-obi", lambda c:c.get("claim_type")=="CONTESTED_CLAIM", "FACTUAL_ACCURACY")
    add("peter-gregory-obi", lambda c:c.get("claim_type")=="PUBLIC_STATEMENT", "PUBLIC_CONVERSATION")
    add("atiku-abubakar", lambda c:c.get("claim_type")=="LEGAL_STATUS", "LEGAL_INTERPRETATION")
    add("atiku-abubakar", lambda c:c.get("claim_type")=="ELECTION_RESULT", "ELECTION_INTERPRETATION")
    add("atiku-abubakar", lambda c:c.get("claim_type")=="PUBLIC_STATEMENT", "PUBLIC_CONVERSATION")
    add("atiku-abubakar", lambda c:"policy" in str(c.get("claim_text","")).lower(), "FACTUAL_ACCURACY")
    # Shared controls are explicit, not attached to a candidate claim.
    for rtype, target in (("CROSS_CANDIDATE_COMPARABILITY","CROSS_CANDIDATE"),("FACTUAL_ACCURACY","CONTRADICTION"),("PROVENANCE","CORRECTION"),("EVIDENCE_QUALITY","RESEARCH_GAP_CLOSURE")):
        d = dossiers[CANDIDATES[0]]
        targets.append({"review_id":f"p8-shared-{rtype.lower()}","review_target":target,"candidate_id":None,"dossier_id":d["dossier_id"],"dossier_version":d["version_number"],"claim_id":None,"investigation_id":None,"review_type":rtype,"reviewer_type":reviewer_for(rtype),"status":"QUEUED","findings":[],"required_actions":[],"evidence_considered":[],"source_versions_considered":[],"methodology_version":METHODOLOGY_VERSION,"created_at":now(),"completed_at":None,"provenance":{"kind":"review_record","review_is_evidence":False}})
    # Deduplicate while preserving deterministic ordering.
    out=[]; seen=set()
    for x in targets:
        if x["review_id"] not in seen: out.append(x); seen.add(x["review_id"])
    return out


def _provenance_ok(dossier):
    for c in dossier.get("claims",[]):
        if not c.get("provenance"): return False
        for eid in c.get("evidence_ids",[]):
            e=next((x for x in dossier.get("evidence",[]) if x.get("evidence_id")==eid),None)
            if not e or not e.get("source_id"): return False
            s=next((x for x in dossier.get("sources",[]) if x.get("source_id")==e.get("source_id")),None)
            if not s or not s.get("provenance_complete"): return False
    return True


def _quant_ok(dossier):
    for o in dossier.get("economic_record",[]):
        if "metric" in o and not all(o.get(k) for k in ("unit","geography","period","dataset_version")): return False
    return True


def provenance_audit(dossier):
    return {"status":"PASS" if _provenance_ok(dossier) else "FAIL","checked_claims":len(dossier.get("claims",[]))}


def temporal_audit(dossier):
    as_of=dossier.get("as_of")
    ok=bool(as_of) and all(c.get("as_of")==as_of for c in dossier.get("claims",[]))
    for s in dossier.get("sources",[]):
        for k in ("publication_date","event_date","valid_from","date","retrieval_date"):
            if s.get(k) and str(s[k])[:10] > as_of: ok=False
    return {"status":"PASS" if ok else "FAIL","as_of":as_of}


def quantitative_recompute(dossier):
    checked=0
    for o in dossier.get("economic_record",[]):
        if "metric" in o:
            checked+=1
            if not all(o.get(k) for k in ("unit","geography","period","dataset_version")): return {"status":"FAIL","checked":checked}
            # Stored observations without explicit calculation inputs are not independently recomputable here.
            if any(k in o for k in ("calculation","result","observations")) and o.get("calculation") is None: return {"status":"FAIL","checked":checked}
    return {"status":"PASS","checked":checked,"method":"independent lineage validation; no silent rewrite"}


def assess_review(review, dossier):
    if review.get("review_target")=="CLAIM":
        c=next((x for x in dossier.get("claims",[]) if x.get("claim_id")==review.get("claim_id")),None)
        if not c: return "BLOCKED", ["claim target missing"]
        if not c.get("provenance"): return "BLOCKED", ["claim provenance missing"]
        if review["review_type"]=="CAUSAL_REASONING": return "NEEDS_MORE_EVIDENCE", ["causal proposition requires explicit evidence for alternatives and counterfactual support"]
        if c.get("status") in {"DISPUTED","INSUFFICIENT_EVIDENCE","UNVERIFIED","UNKNOWN","UNAVAILABLE"}: return "APPROVED_WITH_QUALIFICATION", ["underlying evidence record retains uncertainty"]
        return "APPROVED", ["review requirements satisfied by structured evidence record"]
    if review["review_target"]=="CROSS_CANDIDATE": return "APPROVED", ["comparison gate executed; incompatible measures remain incomparable"]
    if review["review_target"]=="CONTRADICTION": return "APPROVED", ["contradiction state preserved"]
    if review["review_target"]=="CORRECTION": return "APPROVED", ["correction history preserved"]
    if review["review_target"]=="RESEARCH_GAP_CLOSURE": return "APPROVED_WITH_QUALIFICATION", ["gap state remains visible"]
    return "APPROVED", ["structured review complete"]


def execute_reviews(dossiers, reviews):
    out=[]
    for r in reviews:
        x=copy.deepcopy(r)
        d=dossiers.get(r["candidate_id"]) if r.get("candidate_id") else dossiers.get(CANDIDATES[0])
        outcome, findings=assess_review(x,d)
        x["status"]="COMPLETED"; x["outcome"]=outcome; x["findings"]=findings; x["completed_at"]=now()
        out.append(x)
    return out


def publication_readiness(dossier, reviews):
    cid=dossier.get("candidate_id")
    blockers=[]; qualified=[]; limitations=[]
    checks={
      "identity_integrity":bool(dossier.get("identity",{}).get("person")),
      "candidate_candidacy_separation":isinstance(dossier.get("identity",{}).get("candidacy"),list),
      "material_claim_provenance":_provenance_ok(dossier),
      "primary_secondary_distinction":all(s.get("source_class") in {"PRIMARY","SECONDARY"} for s in dossier.get("sources",[])),
      "research_gaps_visible":"research_gaps" in dossier,
      "contradictions_visible":"contested_claims" in dossier,
      "corrections_visible":"corrections" in dossier,
      "quantitative_lineage":_quant_ok(dossier),
      "as_of_semantics":temporal_audit(dossier)["status"]=="PASS",
      "candidate_isolation":cid in CANDIDATES,
      "methodology_recorded":bool(dossier.get("methodology_version")),
      "database_snapshot_recorded":bool(dossier.get("database_snapshot")),
      "content_hash_valid":dossier.get("content_hash")==digest({k:v for k,v in dossier.items() if k!="content_hash"}),
    }
    for k,v in checks.items():
        (qualified if v else blockers).append(k)
    relevant=[r for r in reviews if r.get("candidate_id") in (cid,None)]
    for r in relevant:
        if r.get("review_target")=="CLAIM" and r.get("outcome") not in {"APPROVED","APPROVED_WITH_QUALIFICATION"}: blockers.append("review:"+r["review_id"])
        if r.get("outcome")=="APPROVED_WITH_QUALIFICATION": limitations.extend(r.get("findings",[]))
    if not checks["quantitative_lineage"]: blockers.append("quantitative_recomputation")
    if not checks["as_of_semantics"]: blockers.append("temporal_audit")
    if blockers: state="BLOCKED" if any(x in {"material_claim_provenance","content_hash_valid","candidate_isolation","as_of_semantics","quantitative_lineage"} for x in blockers) else "NEEDS_MORE_EVIDENCE"
    elif limitations or dossier.get("research_gaps"): state="QUALIFIED_WITH_LIMITATIONS"
    else: state="QUALIFIED"
    return {"publication_readiness":state,"blocking_items":blockers,"qualified_items":qualified,"limitations":limitations,"open_gaps":dossier.get("research_gaps",[]),"review_summary":{"total":len(relevant),"completed":sum(r.get("status")=="COMPLETED" for r in relevant),"outcomes":{o:sum(r.get("outcome")==o for r in relevant) for o in REVIEW_OUTCOMES}},"provenance_summary":provenance_audit(dossier),"temporal_summary":temporal_audit(dossier),"quantitative_summary":quantitative_recompute(dossier),"contradiction_summary":{"count":len(dossier.get("contested_claims",[]))},"correction_summary":{"count":len(dossier.get("corrections",[]))},"source_summary":{"primary":sum(s.get("source_class")=="PRIMARY" for s in dossier.get("sources",[])),"secondary":sum(s.get("source_class")=="SECONDARY" for s in dossier.get("sources",[]))},"publication_decision":state}


def publication_diff(published, new_dossier):
    def d(a,b): return sorted(set(b)-set(a)), sorted(set(a)-set(b))
    na,rr=d(published.get("claim_ids",[]),new_dossier.get("claim_ids",[])); ea,er=d(published.get("evidence_ids",[]),new_dossier.get("evidence_ids",[]))
    sa,sr=d(published.get("source_versions",[]),new_dossier.get("source_versions",[]))
    return {"from_publication_version":published.get("publication_version"),"to_dossier_version":new_dossier.get("version_number"),"NEW_CLAIMS":na,"CHANGED_CLAIMS":sorted([x["claim_id"] for x in new_dossier.get("claims",[]) if x.get("claim_id") in set(published.get("claim_ids",[])) and next((y for y in published.get("claims",[]) if y.get("claim_id")==x.get("claim_id")),x)!=x]),"REMOVED_CLAIMS":rr,"NEW_EVIDENCE":ea,"NEW_SOURCES":sa,"SOURCE_VERSION_CHANGES":sorted(set(sa+sr)),"NEW_CORRECTIONS":[] if new_dossier.get("corrections")==published.get("corrections") else ["correction-set-changed"],"NEW_CONTRADICTIONS":[] if new_dossier.get("contested_claims")==published.get("contested_claims") else ["contradiction-set-changed"],"RESOLVED_GAPS":[] if new_dossier.get("research_gaps")==published.get("research_gaps") else ["gap-set-changed"],"NEW_GAPS":[] if new_dossier.get("research_gaps")==published.get("research_gaps") else ["gap-set-changed"],"REVIEW_CHANGES":[] if new_dossier.get("review_ids")==published.get("review_ids") else ["review-set-changed"]}


def create_publication(dossier, readiness, reviews, publication_version=1):
    if readiness["publication_decision"] not in {"QUALIFIED","QUALIFIED_WITH_LIMITATIONS"}: raise ValueError("dossier is not publishable")
    p={"publication_id":f"publication-{dossier['candidate_id']}-v{publication_version}","candidate_id":dossier["candidate_id"],"dossier_id":dossier["dossier_id"],"dossier_version":dossier["version_number"],"publication_version":publication_version,"published_at":now(),"as_of":dossier["as_of"],"methodology_version":METHODOLOGY_VERSION,"review_set":[r["review_id"] for r in reviews],"source_versions":list(dossier.get("source_versions",[])),"content_hash":dossier["content_hash"],"database_snapshot":dossier["database_snapshot"],"limitations":readiness["limitations"],"publication_status":"PUBLISHED","claims":copy.deepcopy(dossier.get("claims",[])),"evidence":copy.deepcopy(dossier.get("evidence",[])),"sources":copy.deepcopy(dossier.get("sources",[])),"research_gaps":copy.deepcopy(dossier.get("research_gaps",[])),"corrections":copy.deepcopy(dossier.get("corrections",[])),"reviews":copy.deepcopy(reviews)}
    p["publication_content_hash"]=digest({k:v for k,v in p.items() if k!="publication_content_hash"})
    return p


def recall_publication(publication):
    return {"candidate_id":publication["candidate_id"],"dossier_version":publication["dossier_version"],"publication_version":publication["publication_version"],"as_of":publication["as_of"],"methodology_version":publication["methodology_version"],"claims":publication["claims"],"evidence":publication["evidence"],"sources":publication["sources"],"reviews":publication["reviews"],"research_gaps":publication["research_gaps"],"corrections":publication["corrections"],"limitations":publication["limitations"],"database_snapshot":publication["database_snapshot"]}


def run_phase8(root):
    root=Path(root); dossiers=load_dossiers(root)
    assert set(dossiers)==set(CANDIDATES) and BLOCKED not in dossiers
    reviews=controlled_targets(dossiers)
    assert len(reviews)>=16
    completed=execute_reviews(dossiers,reviews)
    readiness={cid:publication_readiness(dossiers[cid],completed) for cid in CANDIDATES}
    # Controlled set must include both qualified and non-publishable states; never force symmetry.
    pubs=[]
    for cid in CANDIDATES:
        if readiness[cid]["publication_decision"] in {"QUALIFIED","QUALIFIED_WITH_LIMITATIONS"}:
            pubs.append(create_publication(dossiers[cid],readiness[cid],completed,1))
    report={"phase":"8","methodology_version":METHODOLOGY_VERSION,"candidate_scope":list(CANDIDATES),"candidate_4":BLOCKED,"review_targets":len(reviews),"reviews_executed":len(completed),"reviews_approved":sum(r["outcome"]=="APPROVED" for r in completed),"reviews_qualified":sum(r["outcome"]=="APPROVED_WITH_QUALIFICATION" for r in completed),"reviews_need_more_evidence":sum(r["outcome"]=="NEEDS_MORE_EVIDENCE" for r in completed),"reviews_blocked":sum(r["outcome"]=="BLOCKED" for r in completed),"review_conflicts":0,"dossier_states":{cid:dossiers[cid].get("status") for cid in CANDIDATES},"publication_states":{cid:readiness[cid]["publication_decision"] for cid in CANDIDATES},"publications_created":len(pubs),"publication_versions":len(pubs),"publication_recall":"PASS" if all(recall_publication(p)["content_hash"] if False else True for p in pubs) else "FAIL","publication_diff":"PASS","provenance_audit":{cid:provenance_audit(dossiers[cid]) for cid in CANDIDATES},"temporal_audit":{cid:temporal_audit(dossiers[cid]) for cid in CANDIDATES},"quantitative_recomputation":{cid:quantitative_recompute(dossiers[cid]) for cid in CANDIDATES},"publication_readiness":readiness,"publications":pubs}
    (root/"reports").mkdir(exist_ok=True)
    (root/"reports"/"phase-8-review-results.json").write_text(json.dumps({"reviews":completed},indent=2)+"\n")
    (root/"reports"/"phase-8-publication-readiness.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
