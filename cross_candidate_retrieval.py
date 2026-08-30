"""Deterministic cross-candidate retrieval over the three validated dossiers."""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
CANDIDATES={"bola-ahmed-tinubu":"candidates/bola-ahmed-tinubu/data/pilot-record.json","peter-gregory-obi":"candidates/peter-gregory-obi/data/pilot-record.json","atiku-abubakar":"candidates/atiku-abubakar/data/pilot-record.json"}
def load_dossiers(root): return {cid:json.loads((root/rel).read_text(encoding="utf-8")) for cid,rel in CANDIDATES.items()}
def snapshot_ref(dossiers): return "sha256:"+hashlib.sha256(json.dumps({k:dossiers[k] for k in sorted(dossiers)},sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _party_map(d): return {p["id"]:p.get("name") for p in d.get("parties",[])}
def _candidacies(d): return {c["id"]:c for c in d.get("candidacies",[])}
def _elections(d): return {e["id"]:e for e in d.get("elections",[])}
def election_2023(dossiers):
 rows=[]
 for cid,d in dossiers.items():
  parties,cands,elections=_party_map(d),_candidacies(d),_elections(d)
  for r in d.get("election_results",[]):
   c=cands.get(r.get("candidacy_id"),{}); e=elections.get(c.get("election_id"),{})
   if e.get("id")=="election-ng-pres-2023":
    sid=r.get("source_id") or (r.get("source_ids") or [None])[0]
    rows.append({"candidate_id":cid,"candidate":d["person"]["name"],"party":parties.get(c.get("party_id")),"votes":r.get("votes"),"rank":r.get("rank"),"result":r.get("result_status"),"election_id":e.get("id"),"source_id":sid,"source_tier":next((s.get("tier") for s in d.get("sources",[]) if s.get("id")==sid),None),"evidence_relationship":"DIRECT_RESULT_RECORD" if sid else "UNVERIFIED","assessment":"VERIFIED" if r.get("certification_status")=="OFFICIAL" else "UNVERIFIED","missing_fields":[k for k in ("source_id","votes","rank") if r.get(k) is None and not(k=="source_id" and sid)],"claim_ids":[x["id"] for x in d.get("claims",[]) if "2023" in x.get("id","") and "result" in x.get("id","")]})
 return {"question":"Compare Tinubu, Obi and Atiku in the 2023 presidential election.","rows":rows,"status":"SUPPORTED" if len(rows)==3 else "INCOMPLETE"}
def presidential_history(dossiers):
 out={}
 for cid,d in dossiers.items():
  parties,cands,elections=_party_map(d),_candidacies(d),_elections(d); rows=[]
  for c in d.get("candidacies",[]):
   e=elections.get(c.get("election_id"),{})
   if e.get("type")!="presidential": continue
   r=next((r for r in d.get("election_results",[]) if r.get("candidacy_id")==c.get("id")),None)
   rows.append({"election_id":e.get("id"),"year":(e.get("date") or "")[:4] or None,"party":parties.get(c.get("party_id")),"candidacy_type":c.get("role","PRESIDENTIAL"),"status":c.get("status"),"votes":r.get("votes") if r else None,"rank":r.get("rank") if r else None,"result":r.get("result_status") if r else None,"source_ids":(r.get("source_ids") if r else None) or ([r.get("source_id")] if r and r.get("source_id") else []),"evidence_status":"RECORDED" if r else "NOT_FOUND_IN_CURRENT_DATASET"})
  out[cid]=rows
 return {"question":"Show the documented presidential election history currently represented for each candidate.","candidates":out}
def economic_claims(dossiers):
 out={}
 for cid,d in dossiers.items():
  rows=[]
  for cl in d.get("claims",[]):
   ct=str(cl.get("claim_type","")).upper()
   if any(x in ct for x in ("ECONOMIC","CALCULATED","CAUSAL","ASSESSMENT")) or any(x in cl.get("id","") for x in ("inflation","debt","economic")):
    calc=cl.get("calculation_id"); calculation=next((x for x in d.get("calculations",[]) if x.get("id")==calc),None)
    rows.append({"claim_id":cl.get("id"),"claim":cl.get("claim"),"claim_type":cl.get("claim_type"),"status":cl.get("status"),"causal_classification":cl.get("causal_classification"),"calculation":calculation,"evidence_ids":cl.get("evidence_ids",[]),"uncertainty":cl.get("uncertainty")})
  out[cid]=rows
 return {"question":"Show selected economic claims associated with each candidate and the evidence status.","candidates":out}
def contradictions(dossiers):
 out=[]
 for cid,d in dossiers.items():
  for cl in d.get("claims",[]):
   if cl.get("status") in {"DISPUTED","INSUFFICIENT_EVIDENCE","UNVERIFIED","UNKNOWN"}: out.append({"candidate_id":cid,"claim_id":cl.get("id"),"claim":cl.get("claim"),"status":cl.get("status"),"supporting_evidence":cl.get("evidence_ids",[]),"contradictory_evidence":cl.get("contradictory_evidence_ids",[]),"correction_status":cl.get("correction_status")})
 return {"question":"Which claims in the three dossiers are disputed or insufficiently evidenced?","records":out}
def corrections(dossiers):
 records=[]
 for cid,d in dossiers.items():
  for key in ("corrections","correction_lineages"):
   for x in d.get(key,[]) or []: y=copy.deepcopy(x); y["candidate_id"]=cid; records.append(y)
 return {"question":"Show all correction lineages currently represented for the three candidates.","records":records,"status":"SUPPORTED" if records else "NO_MATCH"}
def public_conversation(dossiers):
 out={}
 for cid,d in dossiers.items():
  rows=[]
  for key in ("public_conversation","related_public_conversation","social_media","public_statements"):
   for x in d.get(key,[]) or []: y=copy.deepcopy(x); y["candidate_id"]=cid; rows.append(y)
  out[cid]=rows
 return {"question":"Show examples of RELATED PUBLIC CONVERSATION and distinguish statements from facts.","candidates":out}
def make_answer(qid,dossiers,as_of=None):
 builders={"Q1":election_2023,"Q2":presidential_history,"Q3":economic_claims,"Q4":contradictions,"Q5":corrections,"Q6":public_conversation}
 if qid not in builders:return {"question_id":qid,"status":"NO_MATCH"}
 body=builders[qid](dossiers)
 return {"answer_id":f"system-{qid}-v1","question_id":qid,"answer_version":1,"answer_state":"DERIVED","database_snapshot":snapshot_ref(dossiers),"as_of":as_of,"methodology_version":"system-retrieval-v1","generation_version":"deterministic-python-v1","generation_timestamp":"TEST_TIME","dependencies":body,"uncertainties":[],"limitations":["Only validated candidate dossier data is used; missing fields remain missing."],"status":body.get("status","SUPPORTED")}
def compatible(a,b):
 fields=("geography","period_start","period_end","metric","unit","dataset_version"); mismatches=[f for f in fields if a.get(f) is not None and b.get(f) is not None and a.get(f)!=b.get(f)]
 return ((not mismatches),"INCOMPARABLE: "+", ".join(mismatches)) if mismatches else (True,"COMPATIBLE")
def validate_dependency(answer,dossiers):
 text=json.dumps(answer,sort_keys=True)
 for cid,d in dossiers.items():
  for cl in d.get("claims",[]):
   if cl.get("id") in text:
    valid_ev={e.get("id") for e in d.get("evidence",[])}
    if any(eid not in valid_ev for eid in cl.get("evidence_ids",[])): return False,f"missing evidence dependency for {cid}:{cl.get('id')}"
 return True,"OK"
def validate_candidate_identity(answer,dossiers):
 rows=answer.get("dependencies",{}).get("rows",[])
 for row in rows:
  cid=row.get("candidate_id")
  if cid not in dossiers:return False,"UNKNOWN_CANDIDATE"
  d=dossiers[cid]; cands=_candidacies(d); result=None
  for r in d.get("election_results",[]):
   if r.get("id")==row.get("result_id") or (r.get("votes")==row.get("votes") and r.get("rank")==row.get("rank")): result=r; break
  if result is None:return False,f"result not owned by {cid}"
  c=cands.get(result.get("candidacy_id"),{})
  if c.get("person_id")!=d["person"]["id"]:return False,f"candidate ownership mismatch for {cid}"
  for claim_id in row.get("claim_ids",[]):
   if not any(cl.get("id")==claim_id for cl in d.get("claims",[])):return False,f"claim {claim_id} not owned by {cid}"
 return True,"OK"
