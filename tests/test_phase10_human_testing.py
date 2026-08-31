import json
from pathlib import Path
from phase10 import TASKS, ANSWER_STATUSES, COHORTS, CANDIDATE_4, validate_session, aggregate, CANDIDATES


def test_task_set_has_at_least_15_and_required_categories():
    assert len(TASKS) >= 15
    cats={x[2] for x in TASKS}
    assert {'QUANTITATIVE','HISTORICAL_AS_OF','CROSS_CANDIDATE','INCOMPARABLE','CAUSAL','PUBLIC_CONVERSATION','CONTRADICTION','CORRECTION','RESEARCH_GAP','UNAVAILABLE_SOURCE','EVIDENCE_INSPECTION','QUANTITATIVE_LINEAGE','LIMITATIONS','OPEN_ENDED'} <= cats


def test_no_candidate_four():
    assert CANDIDATE_4 == 'BLOCKED'
    assert 'Candidate 4' not in CANDIDATES


def test_session_validation_and_status_vocabulary():
    s={'session_id':'S-001','tester_id':'T-001','cohort':'GENERAL_USER','timestamp':'2026-08-31T20:00:00Z','human_test_executed':True,'tasks':[{'task_id':'T01','answer_status':'ANSWERED','success':True,'completion_time':12,'error_count':0}]}
    validate_session(s)
    assert ANSWER_STATUSES[2]=='INSUFFICIENT_EVIDENCE'


def test_no_fabricated_human_data_in_empty_fixture():
    sessions=[]
    assert aggregate(sessions)['sessions']==0
    assert aggregate(sessions)['tasks']==0


def test_aggregation_is_reproducible():
    s={'session_id':'S-1','tester_id':'T-1','cohort':'GENERAL_USER','human_test_executed':True,'tasks':[{'task_id':'T1','answer_status':'ANSWERED','success':True,'completion_time':10,'error_count':0}]}
    assert aggregate([s])==aggregate([s])
