import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text())


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def test_sources_have_retrieval_and_hashes():
    sources = load('sources/gate3/source-records.json') + load('sources/gate3/source-records-additional.json')
    retrievals = {x['retrieval_event_id']: x for x in load('sources/gate3/retrieval-events.json') + load('sources/gate3/retrieval-events-additional.json')}
    for source in sources:
        assert source['retrieval_event_refs']
        for ref in source['retrieval_event_refs']:
            assert ref in retrievals
            assert retrievals[ref]['source_id'] == source['source_id']
            assert retrievals[ref]['hash_algorithm'] == source['content_hash_algorithm']
            assert retrievals[ref]['content_hash'] == source['content_hash']


def test_social_statement_is_separate_from_truth_claim():
    claims = {x['version_id']: x for x in load('evidence/gate3/claims.json')}
    evidence = {x['evidence_id']: x for x in load('evidence/gate3/evidence.json')}
    statement = claims['CLM-G3-X-STATEMENT-V1']
    proposition = claims['CLM-G3-X-PROPOSITION-V1']
    assert statement['claim_type'] == 'statement'
    assert proposition['claim_type'] == 'fact'
    assert evidence['EVD-G3-X-STATEMENT']['relationship'] == 'is_subject_statement'
    assert statement['claim_id'] != proposition['claim_id']


def test_contradictory_evidence_is_preserved():
    claims = {x['version_id']: x for x in load('evidence/gate3/claims.json')}
    evidence = {x['evidence_id']: x for x in load('evidence/gate3/evidence.json')}
    disputed = claims['CLM-G3-CBN-CURRENT-INFLATION-V1']
    assert disputed['verification_status'] == 'disputed'
    assert disputed['contradictory_evidence_ids']
    for evidence_id in disputed['contradictory_evidence_ids']:
        assert evidence_id in evidence
        assert evidence[evidence_id]['relationship'] == 'contradicts_claim'


def test_correction_preserves_predecessor_and_stales_downstream():
    claims = {x['version_id']: x for x in load('evidence/gate3/claims.json')}
    derived = {x['derived_record_id']: x for x in load('evidence/gate3/derived-records.json')}
    v1 = claims['CLM-G3-CORRECTION-V1']
    v2 = claims['CLM-G3-CORRECTION-V2']
    assert v1['verification_status'] == 'superseded'
    assert v2['previous_version_id'] == v1['version_id']
    assert derived['DER-G3-CORRECTION-V1']['status'] == 'superseded'
    assert derived['DER-G3-CORRECTION-V1']['superseded_by'] == 'DER-G3-CORRECTION-V2'
    assert derived['DER-G3-CORRECTION-V2']['status'] == 'valid'


def test_source_revision_preserves_v1():
    versions = load('sources/gate3/source-version-fixtures.json')
    by_version = {x['version_id']: x for x in versions}
    assert by_version['SRC-G3-NBS-CPI-2026-07-V2']['previous_version_id'] == 'SRC-G3-NBS-CPI-2026-07-V1'
    assert by_version['SRC-G3-NBS-CPI-2026-07-V1']['availability_status'] == 'available'
    assert by_version['SRC-G3-NBS-CPI-2026-07-V2']['version_kind'] == 'simulated_revision'


def test_retrieval_failure_is_not_falsehood():
    failure = load('sources/gate3/source-version-fixtures.json')[-1]
    assert failure['version_kind'] == 'retrieval_failure'
    assert failure['availability_status'] == 'unknown'
    assert 'not as evidence' in failure['notes']


def test_canonical_capture_hashes_are_deterministic():
    canonical = {
        'SRC-G3-NBS-CPI-2026-07': 'National Bureau of Statistics | July 2026 CPI Report | Published 2026-08-17 | Headline inflation 15.43% y/y; food inflation 20.31% y/y; CPI 145.3.',
        'SRC-G3-NBS-CPI-DATASET': 'NGA-NBS-CPI | Consumer Price Index and Inflation | National Bureau of Statistics, Nigeria | July 2026 CPI report available; catalog metadata.',
        'SRC-G3-REUTERS-COL-2026-08-10': "Reuters | Nigerians' cost of living pain deepens as election looms | 2026-08-10 | Reuters reports national petrol prices averaging roughly 1,600 naira/litre and describes inflation as near 16%.",
        'SRC-G3-PROSHARE-X-2026-03-24': "Proshare | X post | 2026-03-24 05:37 AM | Nigeria February 2026 headline inflation held at 15.06%; post comments on policy variables and cites NBS.",
        'SRC-G3-CBN-HOMEPAGE-SNAPSHOT': 'Central Bank of Nigeria | homepage snapshot | crawled 2026-08-30 | Inflation Rate 15.93%; Monetary Policy Rate 26.5%.',
        'SRC-G3-PREMIUMTIMES-JULY-2026': "Premium Times | Nigeria's inflation falls to 15.43% in July as food prices rise | Published 2026-08-18 | NBS says headline inflation 15.43% in July 2026; food inflation 20.31% y/y.",
    }
    sources = load('sources/gate3/source-records.json') + load('sources/gate3/source-records-additional.json')
    for source in sources:
        assert sha(canonical[source['source_id']]) == source['content_hash']
