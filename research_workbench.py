"""Deterministic research-workbench primitives for Phase 5.

This module plans investigations from existing candidate dossiers. It does not
retrieve the web, invent evidence, score truth, or perform political ranking.
"""
from __future__ import annotations
import hashlib, json, re, time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

METHODOLOGY_VERSION = "phase5-research-workbench-v1"
CANDIDATES = ("bola-ahmed-tinubu", "peter-gregory-obi", "atiku-abubakar")
BLOCKED = "candidate-4"
QUESTION_TYPES = {"FACTUAL","COMPARATIVE","QUANTITATIVE","CAUSAL","LEGAL","ELECTORAL","POLICY","ECONOMIC","PUBLIC_CONVERSATION","HISTORICAL","CORRECTION","CONTRADICTION","COVERAGE","NEGATIVE_KNOWLEDGE","COMPOSITE"}
SOURCE_STATES = {"DISCOVERED","RETRIEVED","INSPECTED","VERIFIED","PARTIALLY_VERIFIED","REJECTED","UNAVAILABLE","BROKEN","ARCHIVED","SUPERSEDED"}
GAP_STATES = {"OPEN","PARTIALLY_RESOLVED","RESOLVED","BLOCKED","UNAVAILABLE"}
INVESTIGATION_STATES = ("DRAFT","SCOPED","DECOMPOSED","EVIDENCE_REQUIRED","RESEARCHING","PRIMARY_VERIFICATION","CONTRADICTION_REVIEW","QUANTITATIVE_REVIEW","CAUSAL_REVIEW","READY_FOR_REVIEW","REVIEWED","ANSWERABLE","PARTIALLY_ANSWERABLE","BLOCKED","CLOSED")

DOMAIN_RULES = {
    "economic": ["economic_indicators","policy_actions","implementation_status","documented_outcomes","competing_explanations","causal_evidence"],
    "policy": ["proposed_policy","announced_policy","legislated_policy","implemented_policy","documented_outcome","disputed_outcome"],
    "legal": ["allegation","filing","interlocutory_order","judgment","appeal","stay","rehearing","final_outcome","current_legal_status"],
    "electoral": ["primary_contest","nomination","candidacy","ballot_status","general_election","result","declaration","litigation","final_legal_status"],
    "public_conversation": ["statement_occurrence","account_identity","artifact_provenance","context","independent_verification"],
}

@dataclass(frozen=True)
class ResearchQuestion:
    question_id: str
    raw_question: str
    normalized_question: str
    candidate_scope: tuple[str, ...]
    domain: str
    temporal_scope: dict | None
    geographic_scope: str | None
    question_type: str
    research_objective: str
    status: str
    created_at: str
    methodology_version: str
    interpretation_version: str
    database_snapshot: str
    provenance: dict


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_candidate(root: Path, candidate_id: str) -> dict:
    if candidate_id not in CANDIDATES:
        raise ValueError(f"candidate scope blocked or unknown: {candidate_id}")
    path = root / "candidates" / candidate_id / "data" / "pilot-record.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def infer_type(question: str) -> str:
    q = question.lower()
    hits = []
    if any(x in q for x in ("how much","how many","rate","percent","percentage","debt","inflation","growth","value")): hits.append("QUANTITATIVE")
    if any(x in q for x in ("economic","economy","economic record","economic performance")): hits.append("ECONOMIC")
    if any(x in q for x in ("cause","caused","impact","effect","improve","why did")): hits.append("CAUSAL")
    if any(x in q for x in ("court","judgment","legal","lawsuit","appeal","order")): hits.append("LEGAL")
    if any(x in q for x in ("election","votes","nomination","candidate","ballot")): hits.append("ELECTORAL")
    if any(x in q for x in ("policy","implemented","promise","reform")): hits.append("POLICY")
    if any(x in q for x in ("said","statement","post","tweet","public")): hits.append("PUBLIC_CONVERSATION")
    if any(x in q for x in ("compare","across","each candidate","three candidates")): hits.append("COMPARATIVE")
    if any(x in q for x in ("gap","missing","coverage","complete")): hits.append("COVERAGE")
    if len(hits) > 1: return "COMPOSITE"
    return hits[0] if hits else "FACTUAL"


def scope_from_question(question: str) -> tuple[str, ...]:
    q = question.lower()
    names = {"tinubu":"bola-ahmed-tinubu","obi":"peter-gregory-obi","peter obi":"peter-gregory-obi","atiku":"atiku-abubakar"}
    found = []
    for needle, cid in names.items():
        if needle in q and cid not in found: found.append(cid)
    if any(x in q for x in ("three candidates","each candidate","all candidates","across the candidates")): return CANDIDATES
    return tuple(found) or CANDIDATES


def make_question(question: str, *, candidate_scope: tuple[str,...] | None = None, as_of: str | None = None) -> ResearchQuestion:
    scope = candidate_scope or scope_from_question(question)
    if BLOCKED in scope: raise ValueError("Candidate 4 remains blocked")
    if not set(scope).issubset(set(CANDIDATES)): raise ValueError("candidate scope contains unapproved subject")
    qtype = infer_type(question)
    domain = {"QUANTITATIVE":"economic","ECONOMIC":"economic","CAUSAL":"economic","POLICY":"policy","LEGAL":"legal","ELECTORAL":"electoral","PUBLIC_CONVERSATION":"public_conversation","COMPARATIVE":"comparative"}.get(qtype,"general")
    normalized = re.sub(r"\s+"," ",question.strip().lower())
    return ResearchQuestion(f"rq-{_slug(normalized)}", question, normalized, tuple(scope), domain, {"as_of":as_of} if as_of else None, "Nigeria" if "nigeria" in normalized else None, qtype, "Determine what must be established, what evidence exists, and what remains unresolved.", "DRAFT", _now(), METHODOLOGY_VERSION, "interpretation-v1", "runtime-pending", {"source":"deterministic-interpreter","candidate_scope":list(scope)})


def decompose(rq: ResearchQuestion) -> list[dict]:
    q = rq.normalized_question
    items = [("scope", "What exactly is within the question's candidate, time and geographic scope?"),("facts", "Which factual propositions must be established?"),("evidence", "What evidence is required for each material claim?"),("primary", "Which claims require primary-source verification?"),("gaps", "What evidence is missing, unavailable or not yet investigated?")]
    if rq.question_type in {"QUANTITATIVE","COMPARATIVE","ECONOMIC","COMPOSITE"}:
        items += [("quantitative", "Which metrics, definitions, units, geographies, periods, datasets and versions are required?"), ("comparability", "Are the requested observations legitimately comparable?"), ("calculation", "What calculations and exact inputs would be required?")]
    if rq.question_type in {"CAUSAL","COMPOSITE"}: items += [("causal", "What mechanism, competing explanations and causal evidence would be required?"), ("limitations", "What prevents temporal association from being treated as causation?")]
    if rq.question_type in {"POLICY","COMPOSITE"}: items += [("policy", "What was proposed, announced, legislated, approved, implemented, reversed or associated with a documented outcome?")]
    if rq.question_type in {"LEGAL","COMPOSITE"}: items += [("legal", "What is the procedural chronology and current legal status?")]
    if rq.question_type in {"ELECTORAL","COMPOSITE"}: items += [("election", "What are the distinct nomination, candidacy, ballot, result, declaration and litigation states?")]
    if rq.question_type in {"PUBLIC_CONVERSATION","COMPOSITE"}: items += [("statement", "What artifact establishes that a person made the statement, and what evidence independently tests the proposition itself?")]
    return [{"sub_question_id":f"{rq.question_id}-sq-{i+1:02d}","parent_question_id":rq.question_id,"kind":k,"question":text,"status":"OPEN"} for i,(k,text) in enumerate(items)]


def source_class(src: dict) -> str:
    tier = src.get("tier"); typ = str(src.get("type",""))
    if tier == 1 or typ.startswith("official_") or typ in {"judicial_record","party_statement","state_government_historical_record","official_election_report","official_debt_statistics"}: return "PRIMARY"
    if tier == 2: return "SECONDARY"
    if tier == 3: return "SOCIAL_OR_REPUBLICATION"
    return "UNCLASSIFIED"


def evidence_requirements(rq: ResearchQuestion, subs: list[dict]) -> list[dict]:
    reqs=[]
    for i,sq in enumerate(subs,1):
        primary = sq["kind"] in {"facts","primary","quantitative","legal","election","policy","statement"}
        reqs.append({"requirement_id":f"{rq.question_id}-er-{i:02d}","sub_question_id":sq["sub_question_id"],"target_claim":sq["question"],"required_source_class":"PRIMARY" if primary else "PRIMARY_OR_HIGH_QUALITY_SECONDARY","preferred_primary_source":primary,"required_date_range":rq.temporal_scope,"required_geography":rq.geographic_scope,"required_metric":"explicit_metric_definition" if sq["kind"] in {"quantitative","comparability","calculation"} else None,"required_unit":"explicit_unit" if sq["kind"] in {"quantitative","calculation"} else None,"required_artifact_type":"source_artifact","required_provenance":True,"required_corroboration":sq["kind"] in {"facts","causal","legal","policy","statement"},"required_review":sq["kind"] in {"causal","legal","quantitative","gaps"},"status":"OPEN"})
    return reqs


def dossier_summary(root: Path, cid: str) -> dict:
    d=load_candidate(root,cid); sources=d.get("sources",[]); claims=d.get("claims",[]); obs=d.get("observations",[]); calcs=d.get("calculations",[]); primary=[s for s in sources if source_class(s)=="PRIMARY"]; gaps=[]
    for e in d.get("evidence",[]):
        if str(e.get("status","")).upper() in {"UNVERIFIED","UNKNOWN","INCOMPLETE","UNAVAILABLE"}: gaps.append({"gap_id":f"gap-{e.get('id','unknown')}","claim":e.get("claim_id") or e.get("claim"),"missing_evidence":"verification","preferred_evidence":"primary source","reason":e.get("status"),"severity":"HIGH","status":"OPEN","blocking":True,"candidate":cid})
    if not primary: gaps.append({"gap_id":f"gap-{cid}-primary","claim":"material dossier claims","missing_evidence":"primary-source verification","preferred_evidence":"originating official record","reason":"no primary source classified","severity":"HIGH","status":"OPEN","blocking":True,"candidate":cid})
    return {"candidate_id":cid,"source_count":len(sources),"primary_source_count":len(primary),"secondary_source_count":sum(source_class(s)=="SECONDARY" for s in sources),"claims":len(claims),"evidence":len(d.get("evidence",[])),"observations":len(obs),"calculations":len(calcs),"sources":sources,"research_gaps":gaps}


def investigate(root: Path, question: str, *, candidate_scope: tuple[str,...] | None=None, as_of: str | None=None) -> dict:
    started=time.perf_counter(); rq=make_question(question,candidate_scope=candidate_scope,as_of=as_of); plan=decompose(rq); reqs=evidence_requirements(rq,plan); candidates={cid:dossier_summary(root,cid) for cid in rq.candidate_scope}; gaps=[g for c in candidates.values() for g in c["research_gaps"]]; sources=[{"candidate_id":cid,**{k:v for k,v in s.items() if k in {"id","tier","type","url","retrieval_date","reliability"}},"source_class":source_class(s),"verification_state":"RETRIEVED"} for cid,c in candidates.items() for s in c["sources"]]; review_needed=any(r["required_review"] for r in reqs); answerability="PARTIALLY_ANSWERABLE" if gaps or review_needed else "ANSWERABLE"; status="READY_FOR_REVIEW" if review_needed else answerability; elapsed=(time.perf_counter()-started)*1000
    return {"investigation":{"question":asdict(rq)|{"candidate_scope":list(rq.candidate_scope)},"status":status,"sub_questions":plan,"evidence_requirements":reqs},"claims_to_test":[{"claim_id":f"{rq.question_id}-claim-{i+1:02d}","question_id":rq.question_id,"statement":sq["question"],"status":"UNASSESSED"} for i,sq in enumerate(plan)],"sources":sources,"evidence":[],"contradictions":[],"corrections":[],"research_gaps":gaps,"quantitative_analysis":[],"causal_assessment":None,"review":{"required":review_needed,"status":"NOT_REVIEWED","review_is_not_source":True},"answerability":{"status":answerability,"reason":"Documentary coverage and explicit evidence requirements; not a truth probability."},"performance_metadata":{"planning_ms":round(elapsed,3),"decomposition_ms":0,"retrieval_ms":0,"records_touched":sum(c["source_count"]+c["claims"]+c["evidence"] for c in candidates.values()),"dependency_depth":1,"number_of_sources":len(sources),"number_of_evidence_records":0,"number_of_research_gaps":len(gaps),"number_of_contradictions":0},"provenance":{"methodology_version":METHODOLOGY_VERSION,"interpretation_version":"interpretation-v1","database_snapshot":"runtime-pending","generation_timestamp":_now(),"as_of":as_of}}


def priority(task: dict) -> int:
    score=0
    if task.get("blocking"): score+=100
    if task.get("task_type")=="VERIFY_PRIMARY_SOURCE": score+=30
    if task.get("task_type") in {"RESOLVE_CONTRADICTION","RECHECK_CORRECTION","UPDATE_STALE_RESULT"}: score+=25
    if task.get("required_review"): score+=20
    return score


def task_queue(investigation: dict) -> list[dict]:
    tasks=[]
    for r in investigation["investigation"]["evidence_requirements"]:
        typ="VERIFY_PRIMARY_SOURCE" if r["preferred_primary_source"] else "RETRIEVE_SOURCE"; tasks.append({"task_id":f"task-{r['requirement_id']}","task_type":typ,"investigation_id":investigation["investigation"]["question"]["question_id"],"claim":r["target_claim"],"evidence_requirement":r["requirement_id"],"priority":0,"blocking":r["required_review"] or r["preferred_primary_source"],"provenance":investigation["provenance"],"state":"OPEN","completion_evidence":None})
    for g in investigation["research_gaps"]: tasks.append({"task_id":f"task-{g['gap_id']}","task_type":"RESOLVE_RESEARCH_GAP","investigation_id":investigation["investigation"]["question"]["question_id"],"claim":g["claim"],"evidence_requirement":None,"priority":0,"blocking":g["blocking"],"provenance":investigation["provenance"],"state":"OPEN","completion_evidence":None})
    for t in tasks: t["priority"]=priority(t)
    return sorted(tasks,key=lambda x:(-x["priority"],x["task_id"]))


def report_bundle(root: Path, question: str, *, as_of: str|None=None) -> dict:
    inv=investigate(root,question,as_of=as_of); tasks=task_queue(inv); payload={"investigation":inv,"tasks":tasks,"coverage":{"model":"multidimensional-documentary-coverage-v1","is_truth_probability":False,"candidate_scope":inv["investigation"]["question"]["candidate_scope"],"coverage_by_candidate":{cid:dossier_summary(root,cid) for cid in inv["investigation"]["question"]["candidate_scope"]}}}; raw=json.dumps(payload,sort_keys=True,default=str).encode(); payload["artifact_digest"]=hashlib.sha256(raw).hexdigest(); return payload
