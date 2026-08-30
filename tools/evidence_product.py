#!/usr/bin/env python3
"""Small dependency-free HTTP product over the validated deterministic evidence layer."""
from __future__ import annotations
import argparse, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from system_demo import load_dossiers, load_questions, answer_question, CANDIDATES, NAMES
from query_interpreter import interpret_and_validate
PRODUCT=ROOT/'product'

def question_catalog(): return load_questions(ROOT)

def _canonical_query(i):
    """Map an interpreted query to an existing deterministic golden question.
    This is deliberately a finite routing table: interpretation never invents facts.
    """
    q=i["raw_question"].casefold(); op=i["operation"]; scope=i["candidate_scope"]
    if op=="FACTUAL_LOOKUP" and "office" in q and scope==["bola-ahmed-tinubu"]: return "What offices has Tinubu held?"
    if op=="COUNT" and "vote" in q:
        if len(scope)==3: return "Compare the presidential election results of Tinubu, Obi and Atiku in 2023."
        if scope==["bola-ahmed-tinubu"]: return "How many votes did Tinubu receive in the 2023 presidential election?"
        if scope==["peter-gregory-obi"]: return "How many votes did Peter Obi receive in the 2023 presidential election?"
        if scope==["atiku-abubakar"]: return "How many votes did Atiku Abubakar receive in the 2023 presidential election?"
    if op=="CHANGE" and i["entity"]=="headline_inflation": return "How did Nigeria's headline inflation change during the selected Tinubu period?"
    if op=="CAUSAL_ATTRIBUTION" and scope==["bola-ahmed-tinubu"] and "inflation" in q: return "Did Tinubu cause inflation to rise?"
    if op=="CONTRADICTION" and scope==["peter-gregory-obi"] and "anambra" in q: return "What conflicting evidence exists about Anambra's debt during Obi's tenure?"
    if op=="CORRECTION" and scope==["atiku-abubakar"] and "adc" in q: return "What changed in the evidence concerning ADC's legal status during Atiku's 2026 candidacy?"
    if op=="PUBLIC_CONVERSATION" and scope==["atiku-abubakar"] and "adc" in q: return "What did Atiku say about ADC?"
    if op=="AS_OF" and scope==["peter-gregory-obi"] and "party" in q: return "As of 2026-05-01, what party was Peter Obi recorded as belonging to?"
    if op=="COMPARISON" and len(scope)>=2 and "vote" in q: return "Compare the presidential election results of Tinubu, Obi and Atiku in 2023."
    return None

def execute(question,candidate='all',as_of=None):
    interpretation=interpret_and_validate(question)
    if interpretation["interpretation_status"] in {"UNSUPPORTED","NO_MATCH","AMBIGUOUS","PARTIALLY_INTERPRETED"}:
        return {"answer_status":interpretation["interpretation_status"],"answer_text":"The question needs clarification before deterministic evidence retrieval can run.","interpretation":interpretation,"limitations":interpretation["ambiguities"]+interpretation["unsupported_elements"]}
    canonical=_canonical_query(interpretation)
    if not canonical:
        return {"answer_status":"NO_MATCH","answer_text":"I can interpret part of this question, but no validated deterministic retrieval pathway currently matches it.","interpretation":interpretation,"limitations":["Natural-language interpretation is not allowed to manufacture a new factual retrieval pathway."]}
    q=next((x for x in question_catalog() if x['question'].casefold()==canonical.casefold()),None)
    if q is None: return {"answer_status":"NO_MATCH","answer_text":"The interpreted query has no validated retrieval fixture.","interpretation":interpretation}
    record=dict(q); record["interpreted_query"]=interpretation
    if candidate!='all':
        cid=next((k for k,v in NAMES.items() if v.casefold()==candidate.casefold() or k==candidate),None)
        if cid:
            if len(record.get('candidate_scope',[]))>1: return {'answer_status':'INCOMPARABLE','answer_text':'This is a cross-candidate question. Candidate scope must remain explicit.','candidate_scope':record['candidate_scope'],'interpretation':interpretation,'limitations':['A single-candidate filter cannot silently narrow a cross-candidate comparison.']}
            record['candidate_scope']=[cid]
    if as_of: record['as_of']=as_of
    result=answer_question(record,load_dossiers(ROOT)); result["interpretation"]=interpretation; result["canonical_retrieval_question"]=canonical
    return result

def profile(cid):
    d=load_dossiers(ROOT)[cid]; person=d.get('person',{}); offices={x.get('id'):x.get('name') for x in d.get('offices',[])}; parties={x.get('id'):x.get('name') for x in d.get('parties',[])}; timeline=[]
    for x in d.get('officeholdings',[]): timeline.append({'date':x.get('valid_from'),'type':'Officeholding','label':offices.get(x.get('office_id')),'id':x.get('id')})
    elections={x.get('id'):x for x in d.get('elections',[])}
    for x in d.get('candidacies',[]):
        e=elections.get(x.get('election_id'),{}); timeline.append({'date':e.get('date'),'type':'Election','label':e.get('name') or e.get('id'),'id':x.get('id')})
    for x in d.get('party_memberships',[]): timeline.append({'date':x.get('valid_from'),'type':'Party membership','label':parties.get(x.get('party_id')),'id':x.get('id')})
    return {'candidate_id':cid,'name':person.get('name'),'overview':person,'office_history':[x for x in timeline if x['type']=='Officeholding'],'party_history':[x for x in timeline if x['type']=='Party membership'],'election_history':[x for x in timeline if x['type']=='Election'],'timeline':sorted(timeline,key=lambda x:str(x.get('date') or '')),'counts':{'claims':len(d.get('claims',[])),'evidence':len(d.get('evidence',[])),'sources':len(d.get('sources',[])),'observations':len(d.get('observations',[]))}}
class Handler(BaseHTTPRequestHandler):
    def _send(self,code,body,content_type='application/json; charset=utf-8'):
        data=body if isinstance(body,bytes) else body.encode('utf-8'); self.send_response(code); self.send_header('Content-Type',content_type); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        p=urlparse(self.path)
        if p.path=='/api/questions': self._send(200,json.dumps({'questions':question_catalog()},indent=2)); return
        if p.path=='/api/query':
            q=parse_qs(p.query); self._send(200,json.dumps(execute(q.get('question',[''])[0],q.get('candidate',['all'])[0],q.get('as_of',[''])[0] or None),indent=2,sort_keys=True)); return
        if p.path=='/api/candidate':
            cid=parse_qs(p.query).get('id',[''])[0]
            if cid not in CANDIDATES: self._send(404,json.dumps({'error':'unknown_candidate'})); return
            self._send(200,json.dumps(profile(cid),indent=2,sort_keys=True)); return
        if p.path in ('/','/index.html'): self._send(200,(PRODUCT/'index.html').read_bytes(),'text/html; charset=utf-8'); return
        if p.path=='/candidate.html': self._send(200,(PRODUCT/'candidate.html').read_bytes(),'text/html; charset=utf-8'); return
        self._send(404,json.dumps({'error':'not_found'}))
    def log_message(self,fmt,*args): return
def main():
    p=argparse.ArgumentParser(description='Run the ASK THE EVIDENCE product'); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=8080); a=p.parse_args(); print(f'ASK THE EVIDENCE: http://{a.host}:{a.port}'); ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
if __name__=='__main__': main()
