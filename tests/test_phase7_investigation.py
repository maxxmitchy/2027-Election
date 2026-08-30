from pathlib import Path
from phase7_investigation import CANDIDATES, controlled_investigations, assemble_investigation_records
ROOT=Path(__file__).resolve().parents[1]
def test_ten_controlled_investigations():
    invs=controlled_investigations()
    assert len(invs)==10
    assert sum(i['candidate_id'] is None for i in invs)==4
    assert sum(i['candidate_id'] is not None for i in invs)==6
    assert {i['candidate_id'] for i in invs if i['candidate_id'] is not None}==set(CANDIDATES)
def test_shared_investigations_have_shared_scope():
    shared=[i for i in controlled_investigations() if i['candidate_id'] is None]
    assert {i['title'] for i in shared}=={'Cross-candidate quantitative comparison','Contradiction investigation','Public-conversation investigation','Research-gap investigation'}
    assert all(set(i['scope']['candidate_ids'])==set(CANDIDATES) for i in shared)
def test_all_investigations_have_tasks_and_provenance():
    invs=assemble_investigation_records(ROOT)
    assert len(invs)==10
    assert all(i['research_tasks'] and i['provenance']['methodology_version'] for i in invs)
    assert all(i['status'] in {'COMPLETE','PARTIALLY_COMPLETE'} for i in invs)
