#!/usr/bin/env python3
"""Read-only web server for the Evidence Product."""
from __future__ import annotations
import argparse, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evidence_product_api import ask
from system_demo import CANDIDATES, NAMES, load_dossiers, load_questions
PRODUCT = ROOT / "product"

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)
    def _json(self, code, obj): self._send(code, json.dumps(obj, indent=2, sort_keys=True))
    def do_OPTIONS(self):
        self.send_response(204); self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("Access-Control-Allow-Headers", "Content-Type"); self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS"); self.end_headers()
    def do_GET(self):
        p = urlparse(self.path)
        if p.path == "/api/health": return self._json(200, {"status":"ok","read_only":True,"candidate_4":"BLOCKED"})
        if p.path == "/api/questions": return self._json(200, {"questions":load_questions(ROOT)})
        if p.path == "/api/query":
            q=parse_qs(p.query); question=q.get("question",[""])[0]; candidate=q.get("candidate",["all"])[0]; as_of=q.get("as_of",[None])[0]
            if candidate not in ("all", "", *CANDIDATES.keys(), *NAMES.values()): return self._json(400,{"error":"unknown_candidate"})
            return self._json(200, ask(question, None if candidate in ("all","") else [candidate], as_of))
        if p.path in ("/", "/index.html"): return self._send(200, (PRODUCT/"index.html").read_bytes(), "text/html; charset=utf-8")
        if p.path == "/candidate.html": return self._send(200, (PRODUCT/"candidate.html").read_bytes(), "text/html; charset=utf-8")
        return self._json(404,{"error":"not_found"})
    def do_POST(self):
        p=urlparse(self.path)
        if p.path != "/api/ask": return self._json(404,{"error":"not_found"})
        try:
            length=int(self.headers.get("Content-Length","0")); raw=self.rfile.read(length); payload=json.loads(raw or b"{}")
            if not isinstance(payload,dict): raise ValueError("request body must be an object")
            candidate_ids=payload.get("candidate_ids")
            if candidate_ids is not None:
                if not isinstance(candidate_ids,list): raise ValueError("candidate_ids must be an array")
                if "candidate-4" in candidate_ids or "candidate4" in candidate_ids: return self._json(403,{"error":"candidate_4_blocked"})
            result=ask(payload.get("question",""), candidate_ids, payload.get("as_of"))
            return self._json(200,result)
        except ValueError as e: return self._json(400,{"error":str(e)})
        except json.JSONDecodeError: return self._json(400,{"error":"malformed_json"})
        except Exception: return self._json(500,{"error":"backend_error","answer_status":"RETRIEVAL_FAILURE"})
    def log_message(self, fmt, *args): return

def main():
    p=argparse.ArgumentParser(); p.add_argument("--host",default="0.0.0.0"); p.add_argument("--port",type=int,default=8080); a=p.parse_args(); ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
if __name__ == "__main__": main()
