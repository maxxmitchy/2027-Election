import copy, json
from pathlib import Path
from phase8_review_publication import *

ROOT=Path(__file__).resolve().parents[1]

def prepared():
    d=load_dossiers(ROOT); r=controlled_targets(d); e=execute_reviews(d,r); return d,r,e

def test_controlled_scope_and_review_count():
    d,r,e=prepared()
    assert set(d)==set(CANDIDATES) and BLOCKED not in d
    assert len(r)>=16 and len(e)==len(r)
    assert validate_reviews(d,r)

def test_review_is_not_evidence_and_has_reviewer_capability():
    d,r,e=prepared()
    assert all(x["provenance"]["review_is_evidence"] is False for x in e)
    assert all(x["reviewer_type"] in REVIEWER_TYPES for x in e)

def test_every_material_claim_has_review_state():
    d,r,e=prepared()
    for cid,x in d.items():
        reviewed={z.get("claim_id") for z in e if z.get("candidate_id")==cid and z.get("review_target")=="CLAIM"}
        assert all(c["claim_id"] in reviewed for c in x["claims"])

def test_causal_claim_is_not_upgraded():
    d,r,e=prepared(); causal=[x for x in e if x.get("review_type")=="CAUSAL_REASONING"]
    assert causal and causal[0]["outcome"]=="NEEDS_MORE_EVIDENCE"

def test_publication_readiness_is_deterministic_and_non_numeric():
    d,r,e=prepared(); a={c:publication_readiness(d[c],e) for c in CANDIDATES}; b={c:publication_readiness(d[c],e) for c in CANDIDATES}
    assert a==b
    raw=json.dumps(a)
    assert "confidence_percentage" not in raw and "electability" not in raw and "ranking" not in raw

def test_unqualified_dossier_cannot_publish():
    d,r,e=prepared(); x=copy.deepcopy(d[CANDIDATES[0]]); x["content_hash"]="bad"
    q=publication_readiness(x,e)
    assert q["publication_decision"]=="BLOCKED"
    import pytest
    with pytest.raises(ValueError): create_publication(x,q,e)

def test_publication_recall_and_immutability_shape():
    d,r,e=prepared();
    for cid in CANDIDATES:
        q=publication_readiness(d[cid],e)
        if q["publication_decision"] in {"QUALIFIED","QUALIFIED_WITH_LIMITATIONS"}:
            p=create_publication(d[cid],q,e)
            before=copy.deepcopy(p); recalled=recall_publication(p)
            assert recalled["candidate_id"]==p["candidate_id"]
            assert recalled["dossier_version"]==p["dossier_version"]
            assert recalled["content_hash"]==p["content_hash"]
            assert p==before

def test_temporal_and_quantitative_audits():
    d,r,e=prepared()
    assert all(temporal_audit(d[c])["status"]=="PASS" for c in CANDIDATES)
    assert all(quantitative_recompute(d[c])["status"]=="PASS" for c in CANDIDATES)

def test_candidate4_blocked():
    d,_,_=prepared(); assert BLOCKED not in d
