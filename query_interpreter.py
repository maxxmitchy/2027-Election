"""Deterministic natural-language -> structured-query interpreter.

This module only interprets language. It never decides factual truth or evidence quality.
"""
from __future__ import annotations
import hashlib, re
from datetime import datetime, timezone

CANDIDATE_ALIASES={
 "bola-ahmed-tinubu":["tinubu","bola tinubu","bola ahmed tinubu"],
 "peter-gregory-obi":["obi","peter obi","peter gregory obi"],
 "atiku-abubakar":["atiku","atiku abubakar"],
}
CAUSAL_RE=re.compile(r"\b(caus(?:e|ed|es|ing)|because of|responsible for|led to|resulted in|made|created|due to|as a result of)\b",re.I)
SUBJECTIVE_RE=re.compile(r"\b(best|worst|most competent|least competent|performed better|most successful|better candidate|worse candidate)\b",re.I)
PUBLIC_RE=re.compile(r"\b(what did|said|say|statement|tweet|post|according to)\b.*\b(adc|litigation|ncp)\b",re.I)

def _scope(q):
    ql=q.lower(); found=[]
    for cid,aliases in CANDIDATE_ALIASES.items():
        if any(re.search(r"\b"+re.escape(a)+r"\b",ql) for a in aliases): found.append(cid)
    if "three candidates" in ql or ("tinubu" in ql and "obi" in ql and "atiku" in ql):
        found=[x for x in CANDIDATE_ALIASES]
    return found

def _time(q):
    ql=q.lower(); years=re.findall(r"\b(19\d{2}|20\d{2})\b",ql)
    if len(years)>=2: return {"start":years[0],"end":years[1],"expression":years[0]+" to "+years[1]}
    if years: return {"year":years[0],"expression":years[0]}
    m=re.search(r"as of\s+([A-Za-z]+\s+\d{4})",q,re.I)
    if m: return {"as_of_expression":m.group(1)}
    return None

def interpret(raw_question:str)->dict:
    q=raw_question.strip(); ql=q.lower(); scope=_scope(q); causal=bool(CAUSAL_RE.search(q))
    if SUBJECTIVE_RE.search(q): status="UNSUPPORTED"; operation="FACTUAL_LOOKUP"
    elif causal: status="INTERPRETED"; operation="CAUSAL_ATTRIBUTION"
    elif PUBLIC_RE.search(q): status="INTERPRETED"; operation="PUBLIC_CONVERSATION"
    elif "how many" in ql or "how much" in ql or "count" in ql: status="INTERPRETED"; operation="COUNT" if "how many" in ql or "count" in ql else "CHANGE"
    elif "increase" in ql or "decrease" in ql or "change" in ql: status="INTERPRETED"; operation="CHANGE"
    elif "timeline" in ql or "chronology" in ql or "what happened" in ql: status="INTERPRETED"; operation="TIMELINE"
    elif "compare" in ql: status="INTERPRETED"; operation="COMPARISON"
    elif "office" in ql or "party" in ql or "vote" in ql or "election" in ql: status="INTERPRETED"; operation="FACTUAL_LOOKUP"
    elif "provenance" in ql or "lineage" in ql: status="INTERPRETED"; operation="PROVENANCE"
    else: status="PARTIALLY_INTERPRETED"; operation="FACTUAL_LOOKUP"
    if not scope and any(x in ql for x in ["best candidate","most competent"]): status="UNSUPPORTED"
    if len(scope)>1 and operation not in {"COMPARISON","COUNT"}: status="PARTIALLY_INTERPRETED"
    domain=None; entity=None; geography=None
    if "inflation" in ql: domain="economy"; entity="headline_inflation"; geography="Nigeria"
    elif "debt" in ql: domain="economy"; entity="debt"; geography="Anambra State" if "anambra" in ql else None
    elif "vote" in ql: domain="election"; entity="presidential_vote_count"; geography="Nigeria"
    elif "adc" in ql: domain="legal"; entity="adc_legal_status"; geography="Nigeria"
    elif "ncp" in ql: domain="politics"; entity="ncp_role"; geography="Nigeria"
    time_range=_time(q)
    ambiguities=[]; unsupported=[]
    if status=="PARTIALLY_INTERPRETED": ambiguities.append("The question is broader than a currently defined deterministic metric or operation.")
    if status=="UNSUPPORTED": unsupported.append("Subjective ranking or evaluation is not defined by the validated methodology.")
    if "during tinubu" in ql and causal: ambiguities.append("Administrative period and personal causation are distinct concepts.")
    return {
      "query_id":"query-"+hashlib.sha256(q.encode()).hexdigest()[:16],"raw_question":q,
      "candidate_scope":scope,"person_scope":scope,"domain":domain,"entity":entity,"operation":operation,
      "geography":geography,"time_range":time_range,"as_of":time_range.get("as_of_expression") if time_range and "as_of_expression" in time_range else None,
      "comparison_scope":scope if operation=="COMPARISON" else [],"evidence_type":["PUBLIC_STATEMENT"] if operation=="PUBLIC_CONVERSATION" else ["PRIMARY_OR_VALIDATED_RECORD"],
      "causal_request":causal,"requested_output":"answer_with_evidence_status_and_provenance",
      "interpretation_status":status,"ambiguities":ambiguities,"unsupported_elements":unsupported,"methodology_version":"query-interpreter-v1"
    }

def interpret_and_validate(raw_question):
    q=interpret(raw_question)
    if q["interpretation_status"]=="INTERPRETED" and q["operation"]=="COMPARISON" and len(q["candidate_scope"])<2:
        q["interpretation_status"]="PARTIALLY_INTERPRETED"; q["ambiguities"].append("Comparison requires at least two subjects.")
    q["validation"]={"deterministic_retrieval_only":True,"llm_dependency":False,"raw_question_is_evidence":False}
    return q
