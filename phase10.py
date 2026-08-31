from __future__ import annotations

CANDIDATES = ("Bola Ahmed Tinubu", "Peter Gregory Obi", "Atiku Abubakar")
CANDIDATE_4 = "BLOCKED"
ANSWER_STATUSES = ("ANSWERED","PARTIALLY_ANSWERED","INSUFFICIENT_EVIDENCE","UNKNOWN","UNVERIFIED","DISPUTED","INCOMPARABLE","UNSUPPORTED","RESEARCH_GAP","SYSTEM_ERROR")
COHORTS = ("GENERAL_USER","POLITICAL_RESEARCH","TECHNICAL_ANALYTICAL")

TASKS = [
("T01","How many votes did Tinubu receive in the 2023 presidential election?","SIMPLE_FACTUAL"),
("T02","How much did Nigeria's headline inflation change between December 2022 and December 2023?","QUANTITATIVE"),
("T03","What did the system know about Tinubu as of December 31, 2023?","HISTORICAL_AS_OF"),
("T04","What documented economic evidence is available for Tinubu and Atiku?","CROSS_CANDIDATE"),
("T05","Can the system compare two figures that use different periods and units? Why or why not?","INCOMPARABLE"),
("T06","Did Tinubu cause inflation to rise?","CAUSAL"),
("T07","What did Atiku say about ADC, and does that statement establish a legal fact?","PUBLIC_CONVERSATION"),
("T08","What does the evidence show when sources disagree or qualify one another?","CONTRADICTION"),
("T09","Show me how a corrected claim changed from V1 to V2.","CORRECTION"),
("T10","What is known about a claim for which the system identifies a research gap?","RESEARCH_GAP"),
("T11","What can you conclude when the required historical source is unavailable?","UNAVAILABLE_SOURCE"),
("T12","Trace the answer back to its claim, evidence, and source.","EVIDENCE_INSPECTION"),
("T13","Where did the number in this answer come from? Trace its quantitative lineage.","QUANTITATIVE_LINEAGE"),
("T14","What does this answer NOT establish?","LIMITATIONS"),
("T15","Ask one real political-research question of your own and investigate it.","OPEN_ENDED")
]

def protocol_status(human_sessions):
    return "HUMAN_TESTING_PENDING" if not human_sessions else "HUMAN_TEST_EXECUTED"

def validate_session(session):
    assert session["tester_id"].startswith("T-")
    assert session["cohort"] in COHORTS
    assert session.get("human_test_executed") is True
    assert all(t.get("task_id") for t in session.get("tasks", []))
    assert not any(t.get("candidate") == "Candidate 4" for t in session.get("tasks", []))
    for t in session.get("tasks", []):
        assert t["answer_status"] in ANSWER_STATUSES

def aggregate(sessions):
    tasks=[t for s in sessions for t in s.get("tasks", [])]
    n=len(tasks)
    return {"sessions":len(sessions),"tasks":n,"task_success_rate":sum(t.get("success",False) for t in tasks)/n if n else None,
            "avg_completion_time":sum(t.get("completion_time",0) or 0 for t in tasks)/n if n else None,
            "avg_error_count":sum(t.get("error_count",0) for t in tasks)/n if n else None}
