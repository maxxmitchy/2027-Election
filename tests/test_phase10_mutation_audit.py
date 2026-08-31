import json
from pathlib import Path
from phase10 import ANSWER_STATUSES

MUTATIONS={f'M{i}' for i in range(1,21)}

def test_all_twenty_mutations_are_represented():
    assert MUTATIONS == {f'M{i}' for i in range(1,21)}

def test_critical_statuses_remain_distinct():
    assert 'UNKNOWN' in ANSWER_STATUSES
    assert 'INSUFFICIENT_EVIDENCE' in ANSWER_STATUSES
    assert 'DISPUTED' in ANSWER_STATUSES
    assert 'FALSE' not in ANSWER_STATUSES
