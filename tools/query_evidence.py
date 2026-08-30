#!/usr/bin/env python3
"""Public-query demo entry point. Retrieval precedes answer assembly."""
from pathlib import Path
import sys, json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from system_demo import load_dossiers, load_questions, answer_question
query=" ".join(sys.argv[1:]).strip()
if not query: raise SystemExit('Usage: python tools/query_evidence.py "question"')
record=next((x for x in load_questions(ROOT) if x["question"].casefold()==query.casefold()),None)
if record is None: print(json.dumps({"answer_status":"NO_MATCH","answer_text":"No deterministic question template matches this query."})); raise SystemExit(0)
print(json.dumps(answer_question(record,load_dossiers(ROOT)),indent=2,sort_keys=True))
