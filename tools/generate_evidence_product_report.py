#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def sh(*args): return subprocess.check_output(args,text=True).strip()
def main():
    sha=sh('git','rev-parse','HEAD'); questions=json.loads((ROOT/'tests/system_demo_questions.json').read_text())['questions']; dossiers=['bola-ahmed-tinubu','peter-gregory-obi','atiku-abubakar']
    meta={'tested_sha':sha,'python':platform.python_version(),'platform':platform.platform(),'question_count':len(questions),'candidate_scope':dossiers,'methodology_version':'system-demo-v1','database':'PostgreSQL 16 CI fixture','llm_required':False}
    text='''# Evidence Product Report\n\n## Purpose\nTurn the validated deterministic evidence layer into a clean user-facing research product without changing the evidence model.\n\n## Governing question\n> WHAT DOES THE EVIDENCE ACTUALLY ESTABLISH?\n\n## Scope\nOnly Tinubu, Peter Obi and Atiku. Candidate 4 remains blocked. No political ranking is implemented.\n\n## Implementation\n- `tools/evidence_product.py` — dependency-free HTTP query/profile layer.\n- `product/index.html` — sparse ASK THE EVIDENCE query surface.\n- `product/candidate.html` — evidence-first candidate chronology/profile.\n- Existing `system_demo.answer_question()` remains the deterministic retrieval/answer engine.\n\n## Safety semantics\nCandidate scope, provenance, quantitative arithmetic, causal discipline, contradictions, corrections, `as_of`, negative knowledge, review separation and RELATED PUBLIC CONVERSATION remain controlled by the existing evidence layer.\n\n## CI\nSee machine-readable metadata below and the workflow artifact for the exact execution result.\n'''
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports/evidence-product.md').write_text(text,encoding='utf-8')
    payload={'run_metadata':meta,'answers':[],'retrieval_records':[],'provenance':[],'statuses':[],'limitations':['Current UI accepts controlled golden-question templates; open-ended semantic planning is intentionally not implemented.'],'test_results':{'source':'CI execution','status':'RECORDED_IN_WORKFLOW_ARTIFACT'},'database_snapshot':'CI PostgreSQL fixture'}
    (ROOT/'reports/evidence-product.json').write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8')
if __name__=='__main__': main()
