from pathlib import Path
import json
from phase9 import run
ROOT=Path(__file__).resolve().parents[1]
r=run(ROOT)
print('PHASE9_SUMMARY:', json.dumps({'closure_attempts':r['closure_count'],'evidence_acquired':r['evidence_acquired'],'gaps_resolved':r['gaps_resolved'],'mutations':r['mutations']},sort_keys=True))
print('PUBLICATION_STATES:', json.dumps({k:v['publication_state'] for k,v in r['matrix'].items()},sort_keys=True))
