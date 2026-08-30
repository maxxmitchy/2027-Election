"""Deterministic presentation layer over the existing interpreter and retrieval demo."""
from __future__ import annotations
import hashlib, json, time
from datetime import datetime, timezone
from pathlib import Path
from query_interpreter import interpret_and_validate
from system_demo import CANDIDATES, load_dossiers, load_questions, answer_question, snapshot_ref
from evidence_coverage import coverage_for_candidate, coverage_report, VALID_CANDIDATES
ANSWER_STATUSES={"ANSWERED","PARTIALLY_ANSWERED","UNKNOWN","UNVERIFIED","DISPUTED","INSUFFICIENT_EVIDENCE","INCOMPLETE","INCOMPARABLE","NO_MATCH","UNSUPPORTED"}
SUPPORTED_PARTIAL_ENTITIES={"party_membership","presidential_election"}

def _question_record(root, interpreted):
    qs=load_questions(root); scope=interpreted["candidate_scope"]; op=interpreted["operation"]; entity=interpreted.get("entity")
    if op=="COUNT" and entity=="presidential_vote_count": return next((q for q in qs if q["id"]=="Q4"),None)
    if op=="COMPARISON" and entity in {"presidential_vote_count","presidential_election"}: return next((q for q in qs if q["id"]=="Q4"),None)
    if op=="CHANGE" and entity=="headline_inflation" and scope==["bola-ahmed-tinubu"]: return next((q for q in qs if q["id"]=="Q7"),None)
    if op=="CAUSAL_ATTRIBUTION" and entity=="headline_inflation" and scope==["bola-ahmed-tinubu"]: return next((q for q in qs if q["id"]=="Q10"),None)
    if op=="CAUSAL_ATTRIBUTION" and entity=="debt" and scope==["peter-gregory-obi"]: return next((q for q in qs if q["id"]=="Q11"),None)
    if op=="CAUSAL_ATTRIBUTION" and entity=="ncp_role" and scope==["atiku-abubakar"]: return next((q for q in qs if q["id"]=="Q12"),None)
    if op=="PUBLIC_CONVERSATION" and scope==["atiku-abubakar"]: return next((q for q in qs if q["id"]=="Q15"),None)
    if op=="CONTRADICTION" and scope==["peter-gregory-obi"]: return next((q for q in qs if q["id"]=="Q13"),None)
    if op=="CORRECTION" and scope==["atiku-abubakar"]: return next((q for q in qs if q["id"]=="Q14"),None)
    if op=="AS_OF" and scope==["peter-gregory-obi"]: return next((q for q in qs if q["id"]=="Q16"),None)
    if op=="FACTUAL_LOOKUP" and scope==["peter-gregory-obi"] and entity=="party_membership": return next((q for q in qs if q["id"]=="Q3"),None)
    if op=="FACTUAL_LOOKUP" and len(scope)==1 and entity=="office_holding": return next((q for q in qs if q["id"]==("Q1" if scope[0]=="bola-ahmed-tinubu" else "Q2")),None)
    return None

def _status_from_retrieval(a):
    raw=a.get("answer_status") or a.get("status") or "NO_MATCH"
    if raw in {"ESTABLISHED","SUPPORTED","CORROBORATED"}: return "ANSWERED"
    if raw in ANSWER_STATUSES: return raw
    if raw in {"QUALIFIED","PARTIALLY_SUPPORTED"}: return "PARTIALLY_ANSWERED"
    return "NO_MATCH"

def _source_details(dossiers, source_ids):
    out=[]
    for sid in sorted(set(source_ids or [])):
        found=None
        for cid,d in dossiers.items():
            for s in d.get("sources",[]):
                if s.get("id")==sid:
                    found={"source_id":sid,"candidate_id":cid,"title":s.get("title"),"publisher":s.get("publisher"),"tier":s.get("tier"),"source_type":s.get("source_type") or s.get("type"),"publication_date":s.get("publication_date") or s.get("date"),"canonical_url":s.get("url") or s.get("canonical_url"),"archive_url":s.get("archive_url"),"content_hash":s.get("content_hash"),"availability":s.get("availability") or "RECORDED","reliability_assessment":s.get("reliability_assessment") or s.get("reliability"),"limitations":s.get("limitations",[])}; break
            if found: break
        out.append(found or {"source_id":sid,"availability":"UNKNOWN","limitations":["Source metadata is not present in the selected dossier."]})
    return out

def _collect_sources(dossiers, answer):
    ids=list(answer.get("source_versions",[])); ids += [x.split("@")[0] for x in answer.get("evidence_versions",[]) if not x.startswith("social:") and not x.startswith("correction:")]
    for r in answer.get("key_evidence",[]) if isinstance(answer.get("key_evidence"),list) else []:
        if isinstance(r,dict):
            ids += r.get("source_ids",[]) or []
            if r.get("source_id"): ids += r["source_id"] if isinstance(r["source_id"],list) else [r["source_id"]]
    return _source_details(dossiers,[x for x in ids if x])

def _why(interpreted, retrieved):
    return {"question_interpreted_as":interpreted,"candidate_scope":interpreted.get("candidate_scope",[]),"entity":interpreted.get("entity"),"domain":interpreted.get("domain"),"time_range":interpreted.get("time_range"),"geography":interpreted.get("geography"),"operation":interpreted.get("operation"),"retrieved_record_count":len(retrieved.get("key_evidence",[])) if isinstance(retrieved.get("key_evidence"),list) else None,"calculation":retrieved.get("calculation"),"evidence_supports":retrieved.get("what_evidence_establishes",[]),"evidence_does_not_establish":retrieved.get("what_evidence_does_not_establish",[]),"qualifications":retrieved.get("contradictions_qualifications",[]),"methodology_version":retrieved.get("methodology_versions",[]),"limitations":retrieved.get("limitations",[])}

def _coverage_answer(question, interpreted, root):
    scope=interpreted.get("candidate_scope") or sorted(VALID_CANDIDATES)
    report={cid:coverage_for_candidate(root,cid) for cid in scope if cid in VALID_CANDIDATES}
    partial=any(any(x.get("coverage") in {"PARTIAL","SPARSE","UNKNOWN","UNAVAILABLE"} for x in r.get("domains",[])) or r.get("research_gaps") for r in report.values())
    status="PARTIALLY_ANSWERED" if partial else "ANSWERED"
    strongest={cid:[x for x in r.get("domains",[]) if x.get("coverage")=="HIGH"] for cid,r in report.items()}
    gaps={cid:r.get("research_gaps",[]) for cid,r in report.items()}
    text="Coverage describes the documentary record, not truth probability or candidate quality. " + "; ".join(f"{cid}: {r.get('source_coverage')} source coverage, {r.get('quantitative_coverage')} quantitative coverage" for cid,r in report.items())
    a=_contract(question,interpreted,None,root,status,text)
    a["coverage"]={"model":"multidimensional-documentary-coverage-v1","is_truth_probability":False,"candidates":report,"strongest_documented_domains":strongest,"known_gaps":gaps}
    a["evidence"]=[{"candidate_id":cid,"domains":r["domains"],"source_composition":r["source_composition"],"economic_metrics":r["economic_metrics"]} for cid,r in report.items()]
    a["sources"]=[]
    for cid in scope:
        if cid in report:
            candidate_path=Path(CANDIDATES[cid]); data_dir=(root/candidate_path).parent if candidate_path.suffix else root/candidate_path/"data"
            p4=json.loads((data_dir/"phase4-depth.json").read_text(encoding="utf-8"))
            a["sources"].extend(p4.get("source_upgrades",[]))
    a["research_gaps"]=gaps
    a["limitations"] += ["Coverage categories measure breadth/depth of the stored documentary record; they are not truth scores.","A gap means the repository has identified missing or incomplete coverage. It does not mean the underlying fact is false."]
    a["why_this_answer"]={"operation":"COVERAGE","candidate_scope":scope,"coverage_dimensions":["source_coverage","primary_source_coverage","provenance_coverage","temporal_coverage","quantitative_coverage","review_coverage","contradiction_coverage","correction_coverage"],"research_gaps":gaps,"limitations":a["limitations"]}
    a["performance_metadata"]={"coverage_calculation_time_ms":sum(r.get("performance",{}).get("coverage_calculation_time_ms",0) for r in report.values()),"records_touched":sum(r.get("performance",{}).get("records_touched",0) for r in report.values()),"dependency_depth":max([r.get("performance",{}).get("dependency_depth",0) for r in report.values()] or [0]),"total_time_ms":0.0}
    return a

def present(question: str, root: Path|str="."):
    root=Path(root); started=time.perf_counter(); interpreted=interpret_and_validate(question)
    if interpreted["interpretation_status"]=="UNSUPPORTED": return _contract(question,interpreted,None,root,"UNSUPPORTED","This question is not defined by the validated methodology.")
    if interpreted["operation"]=="COVERAGE": return _coverage_answer(question,interpreted,root)
    partial_supported=interpreted["interpretation_status"]=="PARTIALLY_INTERPRETED" and interpreted.get("entity") in SUPPORTED_PARTIAL_ENTITIES
    if interpreted["interpretation_status"] in {"AMBIGUOUS","PARTIALLY_INTERPRETED","NO_MATCH"} and not partial_supported and not (interpreted["operation"]=="COUNT" and interpreted.get("entity")=="presidential_vote_count"):
        status="PARTIALLY_ANSWERED" if interpreted["interpretation_status"]=="PARTIALLY_INTERPRETED" else "NO_MATCH"; text="The system cannot safely execute this question without resolving the stated ambiguity." if interpreted["ambiguities"] else "No supported deterministic retrieval route matches this question."; return _contract(question,interpreted,None,root,status,text)
    dossiers=load_dossiers(root); qr=_question_record(root,interpreted)
    if qr is None: return _contract(question,interpreted,None,root,"NO_MATCH","The interpreted query has no existing deterministic retrieval route.")
    qrec=dict(qr); qrec["candidate_scope"]=interpreted["candidate_scope"] or qr.get("candidate_scope",[])
    if interpreted.get("as_of"): qrec["as_of"]=qr.get("as_of") if "T" not in str(interpreted["as_of"]) else interpreted["as_of"]
    retrieved=answer_question(qrec,dossiers); status=_status_from_retrieval(retrieved); contract=_contract(question,interpreted,retrieved,root,status,retrieved.get("answer_text","")); contract["sources"]=_collect_sources(dossiers,retrieved); contract["why_this_answer"]=_why(interpreted,retrieved); contract["retrieval_plan"]={"engine":"existing deterministic system_demo retrieval","question_id":qr["id"],"candidate_scope":qrec["candidate_scope"],"raw_question_reinterpreted_by_retrieval":False}; contract["evidence_status"]=retrieved.get("answer_status",retrieved.get("status")); contract["contradictions"]=retrieved.get("contradictions_qualifications",[]); contract["corrections"]=retrieved.get("key_evidence",[]) if qr["id"]=="Q14" else []; contract["related_public_conversation"]=retrieved.get("key_evidence",[]) if qr["id"]=="Q15" else []; contract["review_information"]=retrieved.get("review_status",{"status":"NOT_A_SOURCE","reviewed":False}); p=retrieved.get("performance",{}); contract["performance_metadata"]={"query_interpretation_time_ms":round((time.perf_counter()-started)*1000,3),"retrieval_time_ms":p.get("retrieval_time_ms"),"answer_assembly_time_ms":0.0,"total_time_ms":round((time.perf_counter()-started)*1000,3),"records_touched":p.get("records_touched"),"dependency_depth":p.get("dependency_depth")}; return contract

def _contract(question,interpreted,retrieved,root,status,text):
    dossiers=load_dossiers(root); snap=snapshot_ref(dossiers); answer_id="answer-"+hashlib.sha256((question+json.dumps(interpreted,sort_keys=True)).encode()).hexdigest()[:16]
    return {"question":question,"interpreted_query":interpreted,"answer_status":status,"answer_text":text,"evidence_status":retrieved.get("answer_status") if retrieved else status,"qualification":(retrieved or {}).get("contradictions_qualifications",[]),"claims":(retrieved or {}).get("claim_versions",[]),"evidence":(retrieved or {}).get("key_evidence",[]),"sources":[],"observations":(retrieved or {}).get("observation_versions",[]),"calculations":(retrieved or {}).get("calculation_versions",[]),"calculation":(retrieved or {}).get("calculation"),"analyses":(retrieved or {}).get("analysis_versions",[]),"results":(retrieved or {}).get("result_versions",[]),"methodology":(retrieved or {}).get("methodology_versions",[]),"as_of":interpreted.get("as_of"),"database_snapshot":snap,"limitations":list((retrieved or {}).get("limitations",[]))+list(interpreted.get("ambiguities",[])),"contradictions":[],"corrections":[],"related_public_conversation":[],"review_information":{"status":"NOT_A_SOURCE","reviewed":False},"provenance":{"answer_id":answer_id,"query_id":interpreted.get("query_id"),"interpretation_version":interpreted.get("methodology_version"),"retrieval_plan":None,"claim_versions":(retrieved or {}).get("claim_versions",[]),"evidence_versions":(retrieved or {}).get("evidence_versions",[]),"source_versions":(retrieved or {}).get("source_versions",[]),"observation_versions":(retrieved or {}).get("observation_versions",[]),"calculation_versions":(retrieved or {}).get("calculation_versions",[]),"analysis_versions":(retrieved or {}).get("analysis_versions",[]),"result_versions":(retrieved or {}).get("result_versions",[]),"methodology_version":interpreted.get("methodology_version"),"database_snapshot":snap,"as_of":interpreted.get("as_of"),"generation_timestamp":datetime.now(timezone.utc).isoformat(),"limitations":list((retrieved or {}).get("limitations",[]))},"performance_metadata":{},"generation_version":"answer-experience-v2-coverage"}

def why_this_answer(question,root="."): return present(question,root).get("why_this_answer")
def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("question",nargs="+"); p.add_argument("--root",default="."); args=p.parse_args(); print(json.dumps(present(" ".join(args.question),args.root),indent=2,sort_keys=True))
if __name__=="__main__": main()
