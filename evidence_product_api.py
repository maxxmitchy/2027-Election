"""Small read-only HTTP adapter around the validated deterministic evidence engine."""
from __future__ import annotations
import time
from pathlib import Path
from query_interpreter import interpret_and_validate
from system_demo import CANDIDATES, NAMES, load_dossiers, load_questions, answer_question, snapshot_ref
ROOT = Path(__file__).resolve().parent
QUESTIONS = load_questions(ROOT)
QUESTION_BY_ID = {q["id"]: q for q in QUESTIONS}

def _candidate_ids(value):
    if value in (None, "", "all"): return None
    if isinstance(value, str): value = [value]
    if not isinstance(value, list): raise ValueError("candidate_ids must be an array")
    resolved=[]
    for raw in value:
        if raw in CANDIDATES: cid=raw
        else: cid=next((k for k,v in NAMES.items() if v.casefold()==str(raw).casefold()),None)
        if not cid: raise ValueError("unknown_candidate")
        if cid not in resolved: resolved.append(cid)
    return resolved

def _candidate_scope(interpreted, requested): return requested if requested is not None else (interpreted.get("candidate_scope") or None)

def _choose_template(q, scope):
    raw=q["raw_question"].casefold(); op=q["operation"]
    if q["interpretation_status"] == "UNSUPPORTED": return None
    if op == "COMPARISON": return "Q4"
    if op == "CHANGE":
        cid=(scope or [None])[0]
        return "Q7" if cid=="bola-ahmed-tinubu" and "inflation" in raw else None
    if op == "CAUSAL_ATTRIBUTION":
        cid=(scope or [None])[0]
        return {"bola-ahmed-tinubu":"Q10","peter-gregory-obi":"Q11","atiku-abubakar":"Q12"}.get(cid)
    if op == "PUBLIC_CONVERSATION": return "Q18" if "prove" in raw or "true" in raw else "Q15"
    if op == "CONTRADICTION": return "Q13" if "anambra" in raw or "debt" in raw else "Q17"
    if op == "CORRECTION": return "Q14"
    if op == "AS_OF" and ("party" in raw or "belong" in raw): return "Q16"
    if op == "COUNT":
        if "presidential general elections" in raw or "elections are represented" in raw: return "Q6"
        if "vote" in raw: return "Q4"
    if op == "FACTUAL_LOOKUP":
        if "office" in raw:
            cid=(scope or [None])[0]; return {"bola-ahmed-tinubu":"Q1","atiku-abubakar":"Q2"}.get(cid)
        if "part" in raw: return "Q3" if (scope or [None])[0]=="peter-gregory-obi" else None
    if op == "TIMELINE": return "Q6"
    return None

def _filter_scope(answer, scope):
    if not scope: return answer
    answer["candidate_scope"]=list(scope)
    if isinstance(answer.get("key_evidence"),list): answer["key_evidence"]=[x for x in answer["key_evidence"] if not isinstance(x,dict) or x.get("candidate_id") in scope or not x.get("candidate_id")]
    return answer

def _enrich(answer, interpreted, dossiers):
    answer["interpreted_query"]=interpreted; answer["database_snapshot"]=snapshot_ref(dossiers)
    answer.setdefault("methodology","Natural language interprets; deterministic evidence decides.")
    answer.setdefault("provenance",{"database_snapshot":answer["database_snapshot"],"methodology_version":interpreted.get("methodology_version")})
    answer.setdefault("performance",{}); return answer

def ask(question: str, candidate_ids=None, as_of=None):
    started=time.perf_counter()
    if not isinstance(question,str) or not question.strip(): return {"answer_status":"NO_MATCH","answer_text":"A question is required."}
    requested=_candidate_ids(candidate_ids); interpreted=interpret_and_validate(question); scope=_candidate_scope(interpreted,requested)
    if scope and any(cid not in CANDIDATES for cid in scope): return {"answer_status":"NO_MATCH","answer_text":"Candidate scope contains an unknown candidate ID.","candidate_scope":scope}
    if len(scope or [])>1 and interpreted["operation"] not in {"COMPARISON","COUNT","COVERAGE","PUBLIC_CONVERSATION"}:
        return _enrich({"answer_status":"INCOMPARABLE","answer_text":"Multiple candidates were named, but this operation does not define a compatible multi-candidate comparison.","candidate_scope":scope,"limitations":["The product does not force incompatible candidates into a comparison."]},interpreted,load_dossiers(ROOT))
    template_id=_choose_template(interpreted,scope)
    if template_id is None:
        status=interpreted["interpretation_status"]
        if status=="UNSUPPORTED": return _enrich({"answer_status":"UNSUPPORTED","answer_text":interpreted["unsupported_elements"][0] if interpreted["unsupported_elements"] else "This question is outside the approved evidence methodology.","candidate_scope":scope or []},interpreted,load_dossiers(ROOT))
        return _enrich({"answer_status":"NO_MATCH","answer_text":"The deterministic evidence engine has no validated answer path for this question.","candidate_scope":scope or [],"limitations":["No unsupported factual fallback is used."]},interpreted,load_dossiers(ROOT))
    record=dict(QUESTION_BY_ID[template_id])
    if scope:
        expected=record.get("candidate_scope",[])
        if len(expected)>1 and len(scope)<len(expected): return _enrich({"answer_status":"INCOMPARABLE","answer_text":"This evidence path requires the full compatible candidate scope.","candidate_scope":scope,"limitations":["A cross-candidate result is not silently narrowed."]},interpreted,load_dossiers(ROOT))
        record["candidate_scope"]=scope
    if as_of: record["as_of"]=as_of if "T" in as_of else as_of+"T23:59:59Z"
    elif interpreted.get("as_of") and template_id=="Q16": record["as_of"]=interpreted["as_of"] if "T" in interpreted["as_of"] else interpreted["as_of"]+"T23:59:59Z"
    dossiers=load_dossiers(ROOT); answer=answer_question(record,dossiers); _filter_scope(answer,scope)
    answer.setdefault("performance",{})["total_response_time_ms"]=round((time.perf_counter()-started)*1000,3)
    return _enrich(answer,interpreted,dossiers)
