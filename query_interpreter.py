"""Deterministic natural-language -> structured-query interpreter.

Language interpretation only. This module never decides factual truth, source
correctness, causation, candidate quality, or allegation status.
"""
from __future__ import annotations
import hashlib, re
from datetime import datetime, timezone

CANDIDATE_ALIASES = {
    "bola-ahmed-tinubu": ("tinubu", "bola tinubu", "bola ahmed tinubu"),
    "peter-gregory-obi": ("obi", "peter obi", "peter gregory obi"),
    "atiku-abubakar": ("atiku", "atiku abubakar"),
}
CAUSAL_RE = re.compile(r"\b(caused?|causes?|causing|because of|responsible for|led to|resulted in|made|created|due to|as a result of|why .* because)\b", re.I)
SUBJECTIVE_RE = re.compile(r"\b(best|worst|most competent|least competent|performed better|most successful|better candidate|worse candidate|who performed best)\b", re.I)
SECURITY_RE = re.compile(r"\b(ignore|assume|don't mention|do not mention|everyone knows|give me the most favorable)\b[^.?!]*", re.I)

def _scope(q: str):
    ql=q.lower(); found=[]
    for cid, aliases in CANDIDATE_ALIASES.items():
        if any(re.search(r"\b"+re.escape(a)+r"\b", ql) for a in aliases): found.append(cid)
    if ("three candidates" in ql or ("tinubu" in ql and "obi" in ql and "atiku" in ql)):
        return list(CANDIDATE_ALIASES)
    return found

def _time(q: str):
    ql=q.lower()
    m=re.search(r"between\s+(19\d{2}|20\d{2})\s+(?:and|to|-)\s+(19\d{2}|20\d{2})", ql)
    if m: return {"start":m.group(1),"end":m.group(2),"expression":m.group(0)}
    years=re.findall(r"\b(19\d{2}|20\d{2})\b", ql)
    if len(years)>=2: return {"start":years[0],"end":years[1],"expression":years[0]+" to "+years[1]}
    if years: return {"year":years[0],"expression":years[0]}
    m=re.search(r"as of\s+([A-Za-z]+\s+\d{4}|\d{4}-\d{2}-\d{2})", q, re.I)
    if m: return {"as_of_expression":m.group(1)}
    if re.search(r"during\s+tinubu(?:'s)?\s+presidency", q, re.I): return {"expression":"during Tinubu's presidency","administrative_scope":"tinubu_presidency"}
    return None

def _domain_entity(ql):
    if "inflation" in ql: return "economy","headline_inflation","Nigeria"
    if "anambra" in ql and "debt" in ql: return "economy","debt","Anambra State"
    if "debt" in ql: return "economy","debt",None
    if "vote" in ql: return "election","presidential_vote_count","Nigeria"
    if "adc" in ql: return "legal","adc_legal_status","Nigeria"
    if "ncp" in ql: return "politics","ncp_role","Nigeria"
    if "office" in ql: return "political_history","office_holding",None
    if "party" in ql: return "political_history","party_membership",None
    if "election" in ql: return "election","presidential_election",None
    if "economy" in ql: return "economy",None,"Nigeria"
    return None,None,None

def interpret(raw_question: str) -> dict:
    raw=raw_question.strip(); ql=raw.lower(); scope=_scope(raw)
    substantive=SECURITY_RE.sub("", raw).strip() or raw
    causal=bool(CAUSAL_RE.search(substantive))
    domain,entity,geography=_domain_entity(ql)
    t=_time(raw)
    ambiguities=[]; unsupported=[]
    if SUBJECTIVE_RE.search(raw): status="UNSUPPORTED"; operation="FACTUAL_LOOKUP"; unsupported.append("Subjective ranking or evaluation is not defined by the validated methodology.")
    elif causal: status="INTERPRETED"; operation="CAUSAL_ATTRIBUTION"
    elif re.search(r"\bwhat did\b|\bwhat has .* said\b|\bwhat .* say\b|\bstatement", ql) and ("adc" in ql or "ncp" in ql or "said" in ql): status="INTERPRETED"; operation="PUBLIC_CONVERSATION"
    elif re.search(r"\bhow many\b|\bhow much\b|\bcount\b|\bnumber of", ql): status="INTERPRETED"; operation="COUNT"
    elif re.search(r"\b(increase|decrease|change|moved from|rose|fell)\b", ql): status="INTERPRETED"; operation="CHANGE"
    elif re.search(r"\bcompare\b|\bversus\b|\bvs\.?\b", ql): status="INTERPRETED"; operation="COMPARISON"
    elif re.search(r"\bconflicting evidence\b|\bcontradict", ql): status="INTERPRETED"; operation="CONTRADICTION"
    elif re.search(r"\bcorrection\b|\bcorrected\b|\bwhat changed in the evidence", ql): status="INTERPRETED"; operation="CORRECTION"
    elif re.search(r"\bprovenance\b|\blineage\b", ql): status="INTERPRETED"; operation="PROVENANCE"
    elif re.search(r"\breview\b|\bassessment by reviewer", ql): status="INTERPRETED"; operation="REVIEW"
    elif re.search(r"\bas of\b", ql): status="INTERPRETED"; operation="AS_OF"
    elif re.search(r"\bwhat offices?\b|\boffices? has\b|\bparty history\b|\belection history\b", ql): status="INTERPRETED"; operation="FACTUAL_LOOKUP"
    elif "what happened" in ql or "timeline" in ql or "chronology" in ql: status="INTERPRETED"; operation="TIMELINE"
    elif domain or scope: status="PARTIALLY_INTERPRETED"; operation="FACTUAL_LOOKUP"; ambiguities.append("The question is broader than a currently defined deterministic metric or operation.")
    else: status="NO_MATCH"; operation="UNKNOWN_LOOKUP"; unsupported.append("No supported deterministic topic or operation was identified.")
    if not domain and operation in {"COUNT","CHANGE","CAUSAL_ATTRIBUTION","COMPARISON"}:
        ambiguities.append("The requested metric/topic could not be resolved to a validated entity.")
        if status=="INTERPRETED": status="PARTIALLY_INTERPRETED"
    if operation=="COMPARISON" and len(scope)<2: ambiguities.append("Comparison requires at least two compatible subjects."); status="PARTIALLY_INTERPRETED"
    if len(scope)>1 and operation not in {"COMPARISON","COUNT"}: status="PARTIALLY_INTERPRETED"; ambiguities.append("Multiple candidate subjects require an explicit comparison or aggregate operation.")
    if "during tinubu" in ql and causal: ambiguities.append("Administrative period and personal causation are distinct concepts.")
    if re.search(r"under tinubu|during tinubu", ql) and not causal and operation=="FACTUAL_LOOKUP" and domain=="economy": operation="CHANGE"
    as_of=t.get("as_of_expression") if t and "as_of_expression" in t else None
    return {
        "query_id":"query-"+hashlib.sha256(raw.encode()).hexdigest()[:16], "raw_question":raw,
        "candidate_scope":scope, "person_scope":scope, "domain":domain, "entity":entity, "operation":operation,
        "geography":geography, "time_range":t, "as_of":as_of,
        "comparison_scope":scope if operation in {"COMPARISON","COUNT"} and len(scope)>1 else [],
        "evidence_type":["PUBLIC_STATEMENT"] if operation=="PUBLIC_CONVERSATION" else ["PRIMARY_OR_VALIDATED_RECORD"],
        "causal_request":causal, "requested_output":"answer_with_evidence_status_and_provenance",
        "interpretation_status":status, "ambiguities":ambiguities, "unsupported_elements":unsupported,
        "methodology_version":"query-interpreter-v1"
    }

def interpret_and_validate(raw_question):
    q=interpret(raw_question)
    q["validation"]={"deterministic_retrieval_only":True,"llm_dependency":False,"raw_question_is_evidence":False,"security_instructions_ignored":True}
    return q
