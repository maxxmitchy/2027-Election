import json
from pathlib import Path
import phase9
ROOT=Path(__file__).resolve().parents[1]

def test_phase8_blockers_explicit():
    x=phase9.blocker_reviews(ROOT)
    assert {r['claim_id'] for r in x}=={'claim-inflation-causation','claim-obi-debt-causation','claim-causal-ncp'}

def test_closure_register_complete():
    d=json.loads((ROOT/'reports/phase-9-closure-register.json').read_text())
    assert len(d['closures'])==3
    for c in d['closures']:
        assert c['closure_status']=='RESOLVED'
        assert c['review_required'] is True
        assert c['resolution_evidence'] and c['resolution_source']

def test_versioning_preserved():
    d=json.loads((ROOT/'reports/phase-9-dossier-v2.json').read_text())['dossiers']
    for cid in phase9.CANDIDATES:
        hist=d[cid]['claim_history']
        assert len(hist)==1
        entry=next(iter(hist.values()))
        assert entry['v1']['status'] in {'INSUFFICIENT_EVIDENCE','UNVERIFIED'}
        assert entry['v2']['version_number']==2
        assert entry['v2']['provenance']['historical_claim_preserved'] is True
        assert d[cid]['version_number']==2

def test_re_review_and_readiness():
    r=json.loads((ROOT/'reports/phase-9-publication-readiness.json').read_text())
    assert set(r['matrix'])==set(phase9.CANDIDATES)
    assert all(v['publication_state']=='READY_WITH_LIMITATIONS' for v in r['matrix'].values())

def test_historical_reconstruction_and_future_leak():
    r=json.loads((ROOT/'reports/phase-9-publication-readiness.json').read_text())['historical_reconstruction']
    assert r['2023-12-31'] is True and r['2025-06-30'] is True and r['2026-08-30'] is True
    assert r['future-leak-control'] is True

def test_candidate_isolation_and_no_candidate4():
    r=json.loads((ROOT/'reports/phase-9-publication-readiness.json').read_text())
    assert set(r['matrix'])==set(phase9.CANDIDATES)
    assert r['candidate_4']=='BLOCKED'

def test_mutations_all_killed():
    r=json.loads((ROOT/'reports/phase-9-mutation-results.json').read_text())
    assert r['mutation_count']==20 and r['killed']==20 and r['survived']==0
