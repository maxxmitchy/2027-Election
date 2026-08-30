#!/usr/bin/env python3
"""Small dependency-free HTTP product over the validated deterministic evidence layer."""
from __future__ import annotations
import argparse, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from system_demo import load_dossiers, load_questions, answer_question, CANDIDATES, NAMES

PRODUCT = ROOT / "product"


def question_catalog():
    return load_questions(ROOT)


def execute(question: str, candidate: str = "all", as_of: str | None = None):
    q = next((x for x in question_catalog() if x["question"].casefold() == question.strip().casefold()), None)
    if q is None:
        return {"answer_status": "NO_MATCH", "answer_text": "No deterministic question template matches this query."}
    record = dict(q)
    if candidate != "all":
        cid = next((k for k, v in NAMES.items() if v.casefold() == candidate.casefold() or k == candidate), None)
        if cid:
            record["candidate_scope"] = [cid]
    if as_of:
        record["as_of"] = as_of
    return answer_question(record, load_dossiers(ROOT))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/questions":
            self._send(200, json.dumps({"questions": question_catalog()}, indent=2))
            return
        if parsed.path == "/api/query":
            p = parse_qs(parsed.query)
            q = p.get("question", [""])[0]
            candidate = p.get("candidate", ["all"])[0]
            as_of = p.get("as_of", [""])[0] or None
            self._send(200, json.dumps(execute(q, candidate, as_of), indent=2, sort_keys=True))
            return
        if parsed.path in ("/", "/index.html"):
            self._send(200, (PRODUCT / "index.html").read_bytes(), "text/html; charset=utf-8")
            return
        self._send(404, json.dumps({"error": "not_found"}))

    def log_message(self, fmt, *args):
        return


def main():
    p = argparse.ArgumentParser(description="Run the ASK THE EVIDENCE product")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    args = p.parse_args()
    print(f"ASK THE EVIDENCE: http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
