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
PRODUCT=ROOT/'product'
def question_catalog(): return load_questions(ROOT)
def execute(question,candidate='all',as_of=None):
    q=next((x for x in question_catalog() if x['question'].casefold()==question.strip().casefold()),None)
    if q is None: return {'answer_status':'NO_MATCH','answer_text':'No deterministic question template matches this query.'}
    record=dict(q)
    if candidate!='all':
        cid=next((k for k,v in NAMES.items() if v.casefold()==candidate.casefold() or k==candidate),None)
        if cid: record['candidate_scope']=[cid]
    if as_of: record['as_of']=as_of
    return answer_question(record,load_dossiers(ROOT))
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
