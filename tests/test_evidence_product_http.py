import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from tools.evidence_product import Handler

def _server():
    s=ThreadingHTTPServer(("127.0.0.1",0),Handler); threading.Thread(target=s.serve_forever,daemon=True).start(); return s

def _post(s,payload):
    req=urllib.request.Request(f"http://127.0.0.1:{s.server_port}/api/ask",data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=10) as r: return r.status,json.loads(r.read())

def test_real_http_api_boundary():
    s=_server()
    try:
        status,r=_post(s,{"question":"What offices has Tinubu held?","candidate_ids":["bola-ahmed-tinubu"]})
        assert status==200 and r["answer_status"]=="ESTABLISHED"
    finally: s.shutdown()

def test_http_candidate4_rejection():
    s=_server()
    try:
        try: _post(s,{"question":"What offices has Tinubu held?","candidate_ids":["candidate-4"]})
        except urllib.error.HTTPError as e: assert e.code==403
        else: raise AssertionError("Candidate 4 was accepted")
    finally: s.shutdown()

def test_http_subjective_is_controlled():
    s=_server()
    try:
        status,r=_post(s,{"question":"Who is the best candidate?"})
        assert status==200 and r["answer_status"]=="UNSUPPORTED"
    finally: s.shutdown()
