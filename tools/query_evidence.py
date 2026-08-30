#!/usr/bin/env python3
"""Public-query demo entry point. It performs deterministic retrieval before answer assembly."""
from pathlib import Path
import sys
from system_demo import load_dossiers, load_questions, answer_question

ROOT=Path(__file__).resolve().parents[1]
query=" ".join(sys.argv[1:]).strip()
if not query:
    raise SystemExit('Usage: python tools/query_evidence.py "question"')
questions=load_questions(ROOT)
record=next((x for x in questions if x["question"].casefold()==query.casefold()),None)
if record is None:
    print('{"answer_status":"NO_MATCH","answer_text":"No deterministic question template matches this query."}')
    raise SystemExit(0)
import json
print(json.dumps(answer_question(record,load_dossiers(ROOT)),indent=2,sort_keys=True))
