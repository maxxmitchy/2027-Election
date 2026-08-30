"""Phase 6 auditable evidence acquisition primitives.

Discovery, capture, verification and evidence extraction are deliberately
separate. The executor never treats source text as instructions and never
promotes discovery or review into factual verification.
"""
# Phase 6 implementation validation point: acquisition integrity is CI-gated.

from __future__ import annotations
import hashlib, json, re, time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

METHODOLOGY_VERSION = "phase6-evidence-acquisition-v1"
CANDIDATES = ("bola-ahmed-tinubu", "peter-gregory-obi", "atiku-abubakar")
BLOCKED = "candidate-4"
TASK_STATES = ("QUEUED","DISCOVERING","DISCOVERED","CAPTURE_PENDING","CAPTURED","VERIFICATION_PENDING","VERIFIED","PARTIALLY_VERIFIED","REJECTED","BLOCKED","UNAVAILABLE","FAILED","REQUIRES_REVIEW","COMPLETE")
PRIMARY_STATES = ("PRIMARY_FOUND","PRIMARY_CAPTURED","PRIMARY_VERIFIED","PRIMARY_UNAVAILABLE","PRIMARY_NOT_FOUND","PRIMARY_INACCESSIBLE","SECONDARY_ONLY","PRIMARY_NOT_REQUIRED")
SOURCE_TYPES = ("OFFICIAL_PRIMARY","COURT_RECORD","ELECTION_RECORD","GOVERNMENT_DATA","OFFICIAL_STATEMENT","OFFICIAL_SOCIAL_ACCOUNT","ARCHIVAL_RECORD","SECONDARY_NEWS","SECONDARY_ANALYSIS","ACADEMIC","THINK_TANK","DATABASE","USER_SUPPLIED","UNKNOWN")

def now(): return datetime.now(timezone.utc).isoformat()
def sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def canonical_url(url: str) -> str: return url.split("#",1)[0].rstrip("/")
def norm(s: str) -> str: return re.sub(r"\s+", " ", s or "").strip()

@dataclass
class ResearchTask:
    task_id: str
    investigation_id: str
    candidate_id: str | None
    question: str
    claim_target: str
    evidence_requirement: str
    source_requirement: str
    priority: int
    status: str = "QUEUED"
    created_at: str = field(default_factory=now)
    methodology_version: str = METHODOLOGY_VERSION
    dependencies: list[str] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)
    attempts: int = 0
    last_attempt: str | None = None
    result: dict | None = None
    research_gap_reference: str | None = None
    review_requirement: bool = False
    answerability_effect: str = "NONE"

def make_task(investigation_id, candidate_id, question, claim_target, evidence_requirement, source_requirement, *, priority=100, gap=None, review=False, effect="NONE", task_id=None):
    if candidate_id == BLOCKED: raise ValueError("Candidate 4 remains blocked")
    if candidate_id is not None and candidate_id not in CANDIDATES: raise ValueError("candidate scope contains unapproved subject")
    tid = task_id or "task-" + hashlib.sha256(f"{investigation_id}|{candidate_id}|{claim_target}|{evidence_requirement}".encode()).hexdigest()[:16]
    return ResearchTask(tid, investigation_id, candidate_id, question, claim_target, evidence_requirement, source_requirement, priority, research_gap_reference=gap, review_requirement=review, answerability_effect=effect)

def discover(task: ResearchTask, candidates: list[dict]) -> list[dict]:
    task.status = "DISCOVERING"; task.attempts += 1; task.last_attempt = now(); matches=[]
    terms = set(re.findall(r"[a-z0-9]{4,}", task.claim_target.lower()))
    for c in candidates:
        if task.candidate_id and c.get("candidate_id") != task.candidate_id: continue
        for s in c.get("sources", []):
            text = norm(" ".join(str(s.get(k,"")) for k in ("title","url","type"))).lower(); score=sum(1 for t in terms if t in text)
            if score or task.evidence_requirement in text: matches.append({"discovery_id":f"disc-{sha256((task.task_id+s.get('url','')).encode())[:16]}","task_id":task.task_id,"candidate_id":c.get("candidate_id"),"discovery_url":s.get("url"),"canonical_url":canonical_url(s.get("url","")),"source_title":s.get("title"),"publisher":s.get("publisher"),"publication_date":s.get("publication_date"),"discovery_timestamp":now(),"discovery_method":"dossier_index","source_type":classify_source(s),"candidate_relevance":score>0,"claim_relevance":score>0,"primary_secondary":source_class(s),"verification_status":"UNVERIFIED","capture_status":"NOT_CAPTURED"})
    task.status = "DISCOVERED" if matches else "UNAVAILABLE"; task.result={"discovered":matches}; return matches

def classify_source(s):
    typ=str(s.get("type","")).lower()
    if typ in {"official_election_report","official_debt_statistics"}: return "ELECTION_RECORD" if "election" in typ else "GOVERNMENT_DATA"
    if typ.startswith("official_"): return "OFFICIAL_PRIMARY"
    if typ == "judicial_record": return "COURT_RECORD"
    if typ in {"party_statement","official_statement"}: return "OFFICIAL_STATEMENT"
    if s.get("tier") == 1: return "OFFICIAL_PRIMARY"
    if s.get("tier") == 2: return "SECONDARY_NEWS"
    if s.get("tier") == 3: return "SECONDARY_ANALYSIS"
    return "UNKNOWN"

def source_class(s): return "PRIMARY" if s.get("tier") == 1 or classify_source(s) in {"OFFICIAL_PRIMARY","COURT_RECORD","ELECTION_RECORD","GOVERNMENT_DATA","OFFICIAL_STATEMENT","OFFICIAL_SOCIAL_ACCOUNT"} else "SECONDARY"

def capture(task: ResearchTask, discovery: dict, outdir: Path, *, timeout=20) -> dict:
    task.status="CAPTURE_PENDING"; task.attempts += 1; task.last_attempt=now(); url=discovery["canonical_url"]
    if not url: task.status="FAILED"; return {"status":"FAILED","reason":"missing URL"}
    req=Request(url,headers={"User-Agent":"2027-Election-Phase6/1.0 evidence-acquisition"}); started=time.time()
    try:
        with urlopen(req,timeout=timeout) as r:
            body=r.read(2_000_000); ctype=r.headers.get("Content-Type",""); final_url=r.geturl(); status=getattr(r,"status",200); headers={k:v for k,v in r.headers.items() if k.lower() in {"content-type","etag","last-modified","content-length","date"}}
        content_hash=sha256(body); artifact_id=f"artifact-{content_hash[:20]}"; folder=outdir/artifact_id; folder.mkdir(parents=True,exist_ok=True); (folder/"content.bin").write_bytes(body)
        event={"retrieval_event_id":"retrieval-"+sha256(f"{task.task_id}|{final_url}|{content_hash}".encode())[:20],"task_id":task.task_id,"retrieval_timestamp":now(),"original_url":discovery["discovery_url"],"canonical_url":url,"final_url":final_url,"content_type":ctype,"artifact_id":artifact_id,"capture_method":"http_get","hash_algorithm":"SHA-256","content_hash":content_hash,"hash_type":"RAW_ARTIFACT_HASH","http_status":status,"http_metadata":headers,"retrieval_status":"SUCCESS","capture_status":"CAPTURED","elapsed_ms":round((time.time()-started)*1000,2)}
        (folder/"retrieval-event.json").write_text(json.dumps(event,indent=2)+"\n",encoding="utf-8"); task.status="CAPTURED"; task.result={"capture":event}; return event
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        reason=norm(str(e)); task.status="UNAVAILABLE" if isinstance(e,HTTPError) and e.code in (404,410) else "FAILED"; event={"retrieval_event_id":"retrieval-"+sha256(f"{task.task_id}|{url}|failure".encode())[:20],"task_id":task.task_id,"retrieval_timestamp":now(),"original_url":discovery["discovery_url"],"canonical_url":url,"retrieval_status":"RETRIEVAL_FAILED","capture_status":"NOT_CAPTURED","error_class":type(e).__name__,"error":reason,"elapsed_ms":round((time.time()-started)*1000,2)}; task.result={"capture":event}; return event

def verify(task: ResearchTask, discovery: dict, retrieval: dict, *, source_text=None) -> dict:
    if retrieval.get("retrieval_status") != "SUCCESS": task.status="UNAVAILABLE"; return {"verification_status":"UNAVAILABLE","primary_state":"PRIMARY_UNAVAILABLE" if task.source_requirement=="PRIMARY_REQUIRED" else "SECONDARY_ONLY"}
    primary=discovery.get("primary_secondary")=="PRIMARY"; text=(source_text or "").lower(); hostile=any(x in text for x in ("ignore previous instructions","system prompt","ai generated summary","this document proves"))
    if hostile: task.status="REQUIRES_REVIEW"; return {"verification_status":"PARTIALLY_VERIFIED","primary_state":"PRIMARY_CAPTURED" if primary else "SECONDARY_ONLY","requires_review":True,"reason":"hostile source content treated as data"}
    if task.review_requirement: task.status="REQUIRES_REVIEW"; return {"verification_status":"PARTIALLY_VERIFIED","primary_state":"PRIMARY_CAPTURED" if primary else "SECONDARY_ONLY","requires_review":True}
    task.status="VERIFIED" if primary or task.source_requirement != "PRIMARY_REQUIRED" else "PARTIALLY_VERIFIED"; return {"verification_status":"VERIFIED" if task.status=="VERIFIED" else "PARTIALLY_VERIFIED","primary_state":"PRIMARY_VERIFIED" if primary else "SECONDARY_ONLY"}

def extract_evidence(task: ResearchTask, source: dict, retrieval: dict, verification: dict, proposition: str, *, location="captured_artifact") -> dict:
    if task.status not in {"VERIFIED","PARTIALLY_VERIFIED","REQUIRES_REVIEW"}: raise ValueError("evidence requires capture/verification boundary")
    ev_id="evidence-"+sha256(f"{source.get('canonical_url')}|{retrieval.get('artifact_id')}|{task.claim_target}|{proposition}".encode())[:20]
    return {"evidence_id":ev_id,"source_id":source.get("canonical_url"),"source_version_id":retrieval.get("artifact_id"),"retrieval_event_id":retrieval.get("retrieval_event_id"),"artifact_id":retrieval.get("artifact_id"),"content_hash":retrieval.get("content_hash"),"retrieval_timestamp":retrieval.get("retrieval_timestamp"),"methodology_version":METHODOLOGY_VERSION,"claim_id":task.claim_target,"evidence_type":"EXTRACTED_PROPOSITION","location":location,"extracted_proposition":proposition,"support_relationship":"SUPPORTS_OR_REQUIRES_REVIEW","verification_status":verification.get("verification_status"),"review_requirement":task.review_requirement,"provenance_complete":all(retrieval.get(k) for k in ("artifact_id","retrieval_event_id","content_hash","retrieval_timestamp"))}

def run_task(task: ResearchTask, dossier_sources: list[dict], outdir: Path) -> dict:
    discoveries=discover(task,[{"candidate_id":task.candidate_id,"sources":dossier_sources}])
    if not discoveries: return {"task":asdict(task),"discoveries":[],"evidence":[]}
    d=discoveries[0]; retrieval=capture(task,d,outdir)
    if retrieval.get("retrieval_status") != "SUCCESS": return {"task":asdict(task),"discoveries":discoveries,"retrieval":retrieval,"evidence":[]}
    artifact=outdir/retrieval["artifact_id"]/"content.bin"; text=artifact.read_bytes().decode("utf-8","replace")[:10000] if artifact.exists() else ""; verification=verify(task,d,retrieval,source_text=text); evidence=[]
    if verification.get("verification_status") in {"VERIFIED","PARTIALLY_VERIFIED"}: evidence.append(extract_evidence(task,d,retrieval,verification,task.claim_target))
    task.result={"discoveries":discoveries,"retrieval":retrieval,"verification":verification,"evidence":evidence}
    if task.status in {"VERIFIED","PARTIALLY_VERIFIED"}: task.status="COMPLETE"
    return {"task":asdict(task),"discoveries":discoveries,"retrieval":retrieval,"verification":verification,"evidence":evidence}

def idempotency_key(task: ResearchTask, source_version_id: str): return sha256(f"{task.task_id}|{source_version_id}|{METHODOLOGY_VERSION}".encode())
def apply_gap_result(gap: dict, task: ResearchTask, verification: dict) -> dict:
    out=dict(gap)
    if verification.get("primary_state") == "PRIMARY_VERIFIED": out["status"]="RESOLVED"
    elif verification.get("primary_state") in {"PRIMARY_UNAVAILABLE","PRIMARY_NOT_FOUND","PRIMARY_INACCESSIBLE"}: out["status"]="UNAVAILABLE"
    elif verification.get("verification_status") == "PARTIALLY_VERIFIED": out["status"]="PARTIALLY_RESOLVED"
    else: out["status"]="OPEN"
    out["last_task_id"]=task.task_id; return out
