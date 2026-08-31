from pathlib import Path
import json
from phase8_review_publication import run_phase8

ROOT=Path(__file__).resolve().parents[1]
r=run_phase8(ROOT)
print("PHASE8_SUMMARY: reviews=%d publications=%d"%(r["reviews_executed"],r["publications_created"]))
print("PUBLICATION_STATES:",json.dumps(r["publication_states"],sort_keys=True))
