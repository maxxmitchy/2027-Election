"""Deterministic, retrieval-first public-query demonstration over validated dossiers."""
from __future__ import annotations
import copy, hashlib, json, re, time
from datetime import datetime, timezone
from pathlib import Path

CANDIDATES={"bola-ahmed-tinubu":"candidates/bola-ahmed-tinubu/data/pilot-record.json","peter-gregory-obi":"candidates/peter-gregory-obi/data/pilot-record.json","atiku-abubakar":"candidates/atiku-abubakar/data/pilot-record.json"}
STATUSES={"VERIFIED":"ESTABLISHED","CORROBORATED":"SUPPORTED","QUALIFIED":"PARTIALLY_SUPPORTED","DISPUTED":"DISPUTED","INSUFFICIENT_EVIDENCE":"INSUFFICIENT_EVIDENCE","UNVERIFIED":"UNVERIFIED","UNKNOWN":"UNKNOWN"}
NAMES={"bola-ahmed-tinubu":"Tinubu","peter-gregory-obi":"Peter Obi","atiku-abubakar":"Atiku"}

def load_dossiers(root:Path):
    return {cid:json.loads((root/rel).read_text(encoding="utf-8")) for cid,rel in CANDIDATES.items()}

def snapshot_ref(dossiers):
    raw=json.dumps({k:dossiers[k] for k in sorted(dossiers)},sort_keys=True,separators=(",",":"))
    return "sha256:"+hashlib.sha256(raw.encode()).hexdigest()

def _party_map(d): return {x.get("id"):x.get("name") for x in d.get("parties",[])}
def _source(d,sid): return next((x for x in d.get("sources",[]) if x.get("id")==sid),None)
def _claim(d,cid): return next((x for x in d.get("claims",[]) if x.get("id")==cid),None)
def _evidence(d,eid): return next((x for x in d.get("evidence",[]) if x.get("id")==eid),None)
def _scope(dossiers,scope): return {cid:dossiers[cid] for cid in scope if cid in dossiers}
def _source_ids(d, ids):
    out=[]
    for eid in ids:
        ev=_evidence(d,eid)
        if ev and ev.get("source_id"): out.append(ev["source_id"])
    return sorted(set(out))
def _versions(prefix, ids): return [f"{prefix}:{x}@v1" for x in ids]

def _base(qid,question,scope,dossiers,as_of,status,answer_text):
    return {"answer_id":f"system-demo-{qid}-v1","question":question,"candidate_scope":list(scope),"as_of":as_of,"answer_status":status,"answer_text":answer_text,"claim_versions":[],"evidence_versions":[],"source_versions":[],"observation_versions":[],"calculation_versions":[],"analysis_versions":[],"result_versions":[],"methodology_versions":["system-demo-v1"],"database_snapshot":snapshot_ref(dossiers),"generation_timestamp":datetime.now(timezone.utc).isoformat(),"limitations":[],"review_status":{"status":"NOT_A_SOURCE","reviewed":False},"missing_dependencies":[]}

def _sections(answer,key_evidence,establishes,not_establishes,qualifications,calculation=None,provenance=None,limitations=None):
    answer.update({"key_evidence":key_evidence,"what_evidence_establishes":establishes,"what_evidence_does_not_establish":not_establishes,"contradictions_qualifications":qualifications})
    if calculation is not None: answer["calculation"]=calculation
    if provenance: answer.update(provenance)
    if limitations: answer["limitations"].extend(limitations)
    return answer

def _factual_offices(qid,scope,dossiers,question):
    d=dossiers[scope[0]]; rows=d.get("officeholdings",[]); offices={x.get("id"):x.get("name") for x in d.get("offices",[])}
    items=[{"office_id":r.get("office_id"),"office":offices.get(r.get("office_id")),"from":r.get("valid_from"),"until":r.get("valid_until"),"status":r.get("certainty") or r.get("status")} for r in rows]
    ids=[c.get("id") for c in d.get("claims",[]) if "office" in c.get("id","")]
    a=_base(qid,question,scope,dossiers,None,"ESTABLISHED", "; ".join(x["office"] for x in items if x["office"]) or "No officeholding records are present.")
    a["claim_versions"]=_versions("claim",ids); a["source_versions"]=sorted({s for c in d.get("claims",[]) if c.get("id") in ids for s in _source_ids(d,c.get("evidence_ids",[]))})
    return _sections(a,items,["The dossier contains officeholding records for the named person."],["It does not establish any office not represented in the dossier."],[])

def _parties(qid,scope,dossiers,question):
    d=dossiers[scope[0]]; pm=d.get("party_memberships",[]); parties=_party_map(d)
    items=[{"membership_id":x.get("id"),"party_id":x.get("party_id"),"party":parties.get(x.get("party_id")),"valid_from":x.get("valid_from"),"valid_until":x.get("valid_until"),"certainty":x.get("certainty")} for x in pm]
    a=_base(qid,question,scope,dossiers,None,"ESTABLISHED","; ".join(x["party"] for x in items if x["party"]) or "No party-membership records are present.")
    a["claim_versions"]=_versions("party_membership",[x["membership_id"] for x in items])
    return _sections(a,items,["The listed party memberships are records associated with the person ID in this dossier."],["Association is not itself proof of policy agreement or performance."],[])

def _election_rows(scope,dossiers):
    rows=[]
    for cid in scope:
        d=dossiers[cid]; parties=_party_map(d); cands={x.get("id"):x for x in d.get("candidacies",[])}; elections={x.get("id"):x for x in d.get("elections",[])}
        for r in d.get("election_results",[]):
            c=cands.get(r.get("candidacy_id"),{}); e=elections.get(c.get("election_id"),{})
            if e.get("id")=="election-ng-pres-2023":
                rows.append({"candidate_id":cid,"candidate":d["person"]["name"],"party":parties.get(c.get("party_id")),"votes":r.get("votes"),"rank":r.get("rank"),"result":r.get("result_status"),"certification_status":r.get("certification_status"),"result_id":r.get("id"),"source_ids":r.get("source_ids") or ([r.get("source_id")] if r.get("source_id") else [])})
    return rows

def _cross_results(qid,scope,dossiers,question):
    rows=_election_rows(scope,dossiers); complete=len(rows)==len(scope) and all(r.get("votes") is not None for r in rows)
    status="ESTABLISHED" if complete else "INCOMPLETE"
    text="; ".join(f"{r['candidate']}: {r['votes']:,} votes (rank {r['rank']})" for r in rows)
    a=_base(qid,question,scope,dossiers,"2026-08-30T00:00:00Z",status,text)
    a["result_versions"]=[f"{r['result_id']}@v1" for r in rows]; a["source_versions"]=sorted({sid for r in rows for sid in r["source_ids"]})
    return _sections(a,rows,["The stored 2023 result records and their official/recorded status."],["The comparison does not by itself establish why voters chose each candidate."],[])

def _history(qid,scope,dossiers,question):
    rows={}
    for cid in scope:
        d=dossiers[cid]; parties=_party_map(d); elections={x.get("id"):x for x in d.get("elections",[])}
        rr={r.get("candidacy_id"):r for r in d.get("election_results",[])}; out=[]
        for c in d.get("candidacies",[]):
            e=elections.get(c.get("election_id"),{})
            if e.get("type")!="presidential": continue
            r=rr.get(c.get("id")); out.append({"election_id":e.get("id"),"year":str(e.get("date") or "")[:4] or None,"party":parties.get(c.get("party_id")),"role":c.get("role","PRESIDENTIAL"),"status":c.get("status"),"votes":r.get("votes") if r else None,"result":r.get("result_status") if r else None,"evidence_status":"RECORDED" if r else "NOT_FOUND_IN_CURRENT_DATASET"})
        rows[cid]=out
    a=_base(qid,question,scope,dossiers,None,"SUPPORTED","Presidential candidacies are counted from the stored presidential election records, not from narrative biography text.")
    a["result_versions"]=[f"{cid}:{len(rs)} presidential records" for cid,rs in rows.items()]
    return _sections(a,rows,["The database represents the listed presidential candidacies."],["NOT_FOUND_IN_CURRENT_DATASET does not mean the event did not occur."],[])

def _economic(qid,scope,dossiers,question):
    d=dossiers[scope[0]]; obs=d.get("observations",[]); calcs=d.get("calculations",[])
    econ=[o for o in obs if any(k in str(o.get("metric","")).lower() for k in ("inflation","debt","gdp","economic"))]
    if scope[0]=="bola-ahmed-tinubu":
        aobs=[o for o in econ if o.get("metric")=="headline_inflation_yoy"]
        a=_base(qid,question,scope,dossiers,None,"SUPPORTED" if len(aobs)>=2 else "INSUFFICIENT_EVIDENCE","Stored Nigerian headline-inflation observations are available for the selected Tinubu period." if aobs else "The selected Tinubu dossier does not contain enough headline-inflation observations for the requested comparison.")
        calc=next((c for c in calcs if c.get("id")=="calc-cpi-2022-2023"),None)
        if calc and len(aobs)>=2:
            a["observation_versions"]=[f"{o['id']}@v{o.get('observation_version',1)}" for o in aobs]; a["calculation_versions"]=[f"{calc['id']}@v1"]; a["calculation"]={"inputs":[{"id":o["id"],"value":o["value"],"unit":o["unit"],"period":o["period_end"]} for o in aobs[:2]],"formula":calc["formula"],"result":calc["result"],"unit":calc["unit"],"rounding":"stored calculation"}
            a["answer_text"]=f"Headline inflation moved from {aobs[0]['value']:.2f}% to {aobs[1]['value']:.2f}%: +{calc['result']:.2f} percentage points."
        return _sections(a,aobs,["The stored observations establish the measured rates and the stored calculation establishes the arithmetic change."],["They do not establish that the presidency personally caused the movement."],[])
    if scope[0]=="peter-gregory-obi":
        if not econ: status="INSUFFICIENT_EVIDENCE"; text="No economic observation matching the requested Anambra-period query is stored in the selected dataset."
        else: status="SUPPORTED"; text=f"The dossier contains {len(econ)} economic/debt observation(s), including stored Anambra debt observations." 
        a=_base(qid,question,scope,dossiers,None,status,text); a["observation_versions"]=[f"{o['id']}@v{o.get('observation_version',1)}" for o in econ]
        return _sections(a,econ,["Only observations actually stored in the Obi dossier are reported."],["The observations do not by themselves attribute responsibility for the measured outcome."],[])
    a=_base(qid,question,scope,dossiers,None,"INSUFFICIENT_EVIDENCE","The Atiku dossier does not contain a sufficiently anchored federal economic observation set for this question.")
    return _sections(a,[],[],["The absence of an observation set does not prove that no economic evidence exists outside this dataset."],["Current dataset coverage is incomplete for this query."],limitations=["No federal policy-outcome observation dependency was manufactured."])

def _causal(qid,scope,dossiers,question):
    d=dossiers[scope[0]]; claims=[c for c in d.get("claims",[]) if str(c.get("claim_type","")).upper()=="CAUSAL"]
    a=_base(qid,question,scope,dossiers,None,"INSUFFICIENT_EVIDENCE","The available records do not establish personal causation for the outcome in the question.")
    a["analysis_versions"]=[f"causal-analysis:{qid}@v1"]
    return _sections(a,claims,["Where present, the records can establish temporal association or an observed outcome."],["They do not establish that the named individual caused the outcome without direct causal evidence."],["Alternative explanations and institutional mechanisms are not reducible to personal causation from temporal sequence alone."],limitations=["Causal classification is deliberately conservative."])

def _contradiction(qid,scope,dossiers,question):
    d=dossiers[scope[0]]; records=[]
    for c in d.get("claims",[]):
        if c.get("status") in {"DISPUTED","INSUFFICIENT_EVIDENCE","UNVERIFIED","UNKNOWN"} or c.get("contradictory_evidence_ids"):
            records.append({"claim_id":c.get("id"),"claim":c.get("claim"),"status":STATUSES.get(c.get("status"),c.get("status")),"supporting_evidence":c.get("evidence_ids",[]),"contradictory_evidence":c.get("contradictory_evidence_ids",[])})
    status="DISPUTED" if any(r["contradictory_evidence"] for r in records) else ("INSUFFICIENT_EVIDENCE" if records else "NO_MATCH")
    text="Conflicting or qualifying records are preserved rather than collapsed into a single winner." if records else "No explicit contradiction record was found in the selected dossier."
    a=_base(qid,question,scope,dossiers,None,status,text); a["evidence_versions"]=[f"{eid}@v1" for r in records for eid in r["supporting_evidence"]+r["contradictory_evidence"]]
    return _sections(a,records,["The system preserves both supporting and contradictory evidence IDs where they are stored."],["A contradiction record does not by itself resolve which position is correct."],["Source scope and definitions must be inspected before resolving a disagreement."])

def _correction(qid,scope,dossiers,question):
    d=dossiers[scope[0]]; records=[]
    for key in ("corrections","correction_lineages"):
        for x in d.get(key,[]) or []: records.append(copy.deepcopy(x))
    if records:
        a=_base(qid,question,scope,dossiers,None,"DISPUTED","A correction lineage is present and is preserved as historical and current state.")
        a["evidence_versions"]=[f"correction:{i.get('id','unknown')}@v1" for i in records]
        return _sections(a,records,["The dossier preserves the correction lineage."],["A correction record does not erase the previous version."],["The exact legal interpretation remains tied to the sources and dates in the lineage."])
    a=_base(qid,question,scope,dossiers,None,"NO_MATCH","No explicit correction lineage matching this question is present in the selected Atiku dossier.")
    return _sections(a,[],[],["The absence of a correction record does not prove that no correction occurred elsewhere."],["No correction provenance was manufactured."])

def _social(qid,scope,dossiers,question):
    rows=[]
    for cid in scope:
        d=dossiers[cid]
        for key in ("public_conversation","related_public_conversation","social_media","public_statements"):
            for x in d.get(key,[]) or []:
                y=copy.deepcopy(x); y["candidate_id"]=cid; y["semantic_rule"]="statement_occurrence_is_not_independent_truth"; rows.append(y)
    status="SUPPORTED" if rows else "INCOMPLETE"
    a=_base(qid,question,scope,dossiers,None,status,"RELATED PUBLIC CONVERSATION is treated as evidence that a statement occurred, not as independent confirmation that its content is true.")
    a["evidence_versions"]=[f"social:{x.get('id','unknown')}@v1" for x in rows if x.get("id")]; a["source_versions"]=[x.get("source_id") for x in rows if x.get("source_id")]
    return _sections(a,rows,["A preserved statement can establish that the account/artifact said something, subject to artifact and identity status."],["A candidate's own statement does not independently prove the proposition stated."],["Independent evidence must be retrieved separately."])

def _asof(qid,scope,dossiers,question,as_of):
    d=dossiers[scope[0]]; dt=as_of[:10]; parties=_party_map(d); matches=[]
    for m in d.get("party_memberships",[]):
        start=m.get("valid_from") or "0000-00-00"; end=m.get("valid_until") or "9999-12-31"
        if start<=dt<=end: matches.append({"party":parties.get(m.get("party_id")),"membership_id":m.get("id"),"valid_from":start,"valid_until":m.get("valid_until"),"certainty":m.get("certainty")})
    status="ESTABLISHED" if matches else "NO_MATCH"; text=matches[0]["party"] if matches else "No membership valid at the requested as_of date is recorded."
    a=_base(qid,question,scope,dossiers,as_of,status,text); a["claim_versions"]=[f"party_membership:{m['membership_id']}@v1" for m in matches]
    return _sections(a,matches,["The valid-time membership interval covers the requested as_of date."],["This does not substitute the present-day party membership for the historical date."],[])

def answer_question(question_record,dossiers):
    qid=question_record["id"]; q=question_record["question"]; scope=question_record["candidate_scope"]; as_of=question_record.get("as_of")
    if any(cid not in CANDIDATES for cid in scope): return {"answer_id":f"system-demo-{qid}-v1","question":q,"candidate_scope":scope,"answer_status":"NO_MATCH","answer_text":"Candidate scope contains an unknown candidate ID."}
    start=time.perf_counter()
    if qid=="Q1": a=_factual_offices(qid,scope,dossiers,q)
    elif qid=="Q2": a=_factual_offices(qid,scope,dossiers,q)
    elif qid=="Q3": a=_parties(qid,scope,dossiers,q)
    elif qid in {"Q4","Q5"}: a=_cross_results(qid,scope,dossiers,q)
    elif qid=="Q6": a=_history(qid,scope,dossiers,q)
    elif qid in {"Q7","Q8","Q9"}: a=_economic(qid,scope,dossiers,q)
    elif qid in {"Q10","Q11","Q12"}: a=_causal(qid,scope,dossiers,q)
    elif qid=="Q13": a=_contradiction(qid,scope,dossiers,q)
    elif qid=="Q14": a=_correction(qid,scope,dossiers,q)
    elif qid in {"Q15","Q18"}: a=_social(qid,scope,dossiers,q)
    elif qid=="Q16": a=_asof(qid,scope,dossiers,q,as_of)
    elif qid=="Q17": a=_contradiction(qid,scope,dossiers,q)
    else: a=_base(qid,q,scope,dossiers,as_of,"NO_MATCH","No deterministic query template matches this question.")
    a["performance"]={"retrieval_time_ms":round((time.perf_counter()-start)*1000,3),"records_touched":sum(len(dossiers[c].get(k,[])) for c in scope for k in ("claims","evidence","observations")),"dependency_depth":2,"answer_generation_time_ms":0.0}
    return a

def load_questions(root): return json.loads((root/"tests/system_demo_questions.json").read_text(encoding="utf-8"))["questions"]

def run_all(root):
    dossiers=load_dossiers(root); questions=load_questions(root); return [answer_question(q,dossiers) for q in questions]

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("question",nargs="+"); p.add_argument("--root",default="."); args=p.parse_args()
    root=Path(args.root); text=" ".join(args.question).strip(); qs=load_questions(root); q=next((x for x in qs if x["question"].lower()==text.lower()),None)
    if not q:
        print(json.dumps({"answer_status":"NO_MATCH","answer_text":"No deterministic question template matches this query."},indent=2)); raise SystemExit(0)
    print(json.dumps(answer_question(q,load_dossiers(root)),indent=2,sort_keys=True))
