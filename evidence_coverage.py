"""Deterministic evidence-coverage measurement over the three validated dossiers."""
from __future__ import annotations
import hashlib, json, time
from pathlib import Path

CANDIDATES={
    "bola-ahmed-tinubu":"candidates/bola-ahmed-tinubu",
    "peter-gregory-obi":"candidates/peter-gregory-obi",
    "atiku-abubakar":"candidates/atiku-abubakar",
}
DOMAINS=("IDENTITY","POLITICAL_HISTORY","PARTY_HISTORY","OFFICE_HISTORY","ELECTION_HISTORY","PUBLIC_STATEMENTS","RELATED_PUBLIC_CONVERSATION","DOCUMENTED_ACTIONS_POLICIES","ECONOMIC_RECORD","LEGAL_RECORD","CONTESTED_CLAIMS","CORRECTIONS","UNCERTAINTY","SOURCES","REVIEWS")
ECONOMIC_METRICS=("inflation","exchange_rate","debt","revenue","expenditure","gdp_growth","unemployment","poverty","selected_consumer_prices")
VALID_CANDIDATES=frozenset(CANDIDATES)


def _load(root,cid):
    base=root/CANDIDATES[cid]/"data"
    pilot=json.loads((base/"pilot-record.json").read_text(encoding="utf-8"))
    p4=json.loads((base/"phase4-depth.json").read_text(encoding="utf-8")) if (base/"phase4-depth.json").exists() else {}
    return pilot,p4


def snapshot(root):
    payload={}
    for cid in sorted(CANDIDATES): payload[cid]=_load(root,cid)
    return "sha256:"+hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _cat(primary, secondary, total):
    if total==0:return "UNKNOWN"
    if primary and primary>=max(1,total//2): return "HIGH"
    if primary or secondary: return "MODERATE" if total>=3 else "PARTIAL"
    return "SPARSE"


def _source_composition(pilot,p4):
    sources=list(pilot.get("sources",[]))+list(p4.get("source_upgrades",[]))
    counts={"PRIMARY":0,"SECONDARY":0,"ARCHIVAL":0,"SOCIAL":0,"TERTIARY":0,"UNAVAILABLE":0}
    for s in sources:
        tier=s.get("tier")
        typ=str(s.get("type","")).lower()
        if s.get("primary_source_status")=="UNAVAILABLE": counts["UNAVAILABLE"]+=1
        elif "social" in typ: counts["SOCIAL"]+=1
        elif tier==1 or "official" in typ or "judicial" in typ or "central_bank" in typ: counts["PRIMARY"]+=1
        elif "archive" in typ: counts["ARCHIVAL"]+=1
        elif tier in (2,3): counts["SECONDARY"]+=1
        else: counts["TERTIARY"]+=1
    return counts


def _domain_status(pilot,p4,domain):
    maps={
      "IDENTITY":len(pilot.get("person",{}))>0,
      "POLITICAL_HISTORY":bool(pilot.get("officeholdings") or pilot.get("candidacies")),
      "PARTY_HISTORY":bool(pilot.get("party_memberships")),
      "OFFICE_HISTORY":bool(pilot.get("officeholdings")),
      "ELECTION_HISTORY":bool(pilot.get("elections") or pilot.get("election_results")),
      "PUBLIC_STATEMENTS":bool(pilot.get("public_statements") or pilot.get("claims") or pilot.get("evidence")),
      "RELATED_PUBLIC_CONVERSATION":bool(pilot.get("public_conversation") or pilot.get("related_public_conversation") or pilot.get("social_media")),
      "DOCUMENTED_ACTIONS_POLICIES":bool(pilot.get("policies") or pilot.get("actions") or any("policy" in str(x.get("claim_type","")).lower() for x in pilot.get("claims",[]))),
      "ECONOMIC_RECORD":bool(pilot.get("observations") or p4.get("observations")),
      "LEGAL_RECORD":bool(pilot.get("legal_records") or any("court" in str(x.get("type","")).lower() or "legal" in str(x.get("claim_type","")).lower() for x in pilot.get("claims",[])) or any("judicial" in str(x.get("type","")).lower() for x in p4.get("source_upgrades",[]))),
      "CONTESTED_CLAIMS":bool(any(x.get("status") in {"DISPUTED","INSUFFICIENT_EVIDENCE","UNVERIFIED","UNKNOWN"} for x in pilot.get("claims",[]))),
      "CORRECTIONS":bool(pilot.get("corrections") or pilot.get("correction_lineages")),
      "UNCERTAINTY":bool(pilot.get("uncertainty") or any(x.get("date_precision") or x.get("date_status") for x in pilot.get("party_memberships",[]))),
      "SOURCES":bool(pilot.get("sources") or p4.get("source_upgrades")),
      "REVIEWS":bool(pilot.get("reviews") or pilot.get("review_status") or pilot.get("review")),
    }
    if not maps.get(domain): return "UNKNOWN"
    if domain=="ECONOMIC_RECORD":
        n=len(pilot.get("observations",[]))+len(p4.get("observations",[])); primary=sum(1 for s in p4.get("source_upgrades",[]) if s.get("tier")==1)
        return "HIGH" if n>=6 and primary>=3 else ("MODERATE" if n>=3 else "PARTIAL")
    if domain in {"SOURCES","ELECTION_HISTORY","LEGAL_RECORD"}: return "HIGH" if len(pilot.get("sources",[]))+len(p4.get("source_upgrades",[]))>=10 else "MODERATE"
    return "MODERATE" if domain in {"IDENTITY","OFFICE_HISTORY","PARTY_HISTORY","POLITICAL_HISTORY","CONTESTED_CLAIMS","UNCERTAINTY"} else "PARTIAL"


def coverage_for_candidate(root,cid):
    if cid not in VALID_CANDIDATES: raise ValueError("UNKNOWN_CANDIDATE")
    started=time.perf_counter(); pilot,p4=_load(root,cid)
    sources=_source_composition(pilot,p4)
    primary_total=sources["PRIMARY"]; secondary_total=sources["SECONDARY"]
    domain_rows=[]
    for d in DOMAINS:
        domain_rows.append({"domain":d,"coverage":_domain_status(pilot,p4,d),"primary_evidence":primary_total>0,"provenance":"MODERATE" if sources["PRIMARY"] else "SPARSE","gaps":[]})
    econ_metrics={m:{"status":"UNKNOWN","observation_count":0} for m in ECONOMIC_METRICS}
    for o in list(pilot.get("observations",[]))+list(p4.get("observations",[])):
        metric=str(o.get("metric","")).lower()
        key=("inflation" if "inflation" in metric else "exchange_rate" if "exchange" in metric or "fx" in metric else "debt" if "debt" in metric else "revenue" if "revenue" in metric or "igr" in metric else "gdp_growth" if "gdp" in metric else "unemployment" if "unemployment" in metric else "poverty" if "poverty" in metric else "selected_consumer_prices" if "price" in metric else None)
        if key: econ_metrics[key]["observation_count"]+=1; econ_metrics[key]["status"]="MODERATE" if econ_metrics[key]["observation_count"]>=2 else "PARTIAL"
    gaps=[]
    for g in p4.get("coverage_notes",{}).get("primary_source_gaps",[]): gaps.append({"status":"OPEN","type":"PRIMARY_SOURCE","description":g})
    for g in p4.get("coverage_notes",{}).get("partial_areas",[]): gaps.append({"status":"OPEN","type":"DOMAIN","description":g})
    return {"candidate_id":cid,"coverage_model":"multidimensional-documentary-coverage-v1","coverage_is_not_truth_probability":True,"domains":domain_rows,"source_composition":sources,"source_coverage":"HIGH" if primary_total>=5 else "MODERATE","primary_source_coverage":"HIGH" if primary_total>=5 else ("MODERATE" if primary_total else "SPARSE"),"provenance_coverage":"MODERATE" if primary_total else "SPARSE","temporal_coverage":"MODERATE" if pilot.get("elections") and (pilot.get("officeholdings") or pilot.get("party_memberships")) else "PARTIAL","quantitative_coverage":"HIGH" if len(pilot.get("observations",[]))+len(p4.get("observations",[]))>=6 else ("MODERATE" if pilot.get("observations") else "SPARSE"),"review_coverage":"UNKNOWN" if not (pilot.get("reviews") or pilot.get("review_status")) else "MODERATE","contradiction_coverage":"MODERATE" if any(x.get("contradictory_evidence_ids") for x in pilot.get("claims",[])) else "PARTIAL","correction_coverage":"MODERATE" if pilot.get("corrections") or pilot.get("correction_lineages") else "UNKNOWN","economic_metrics":econ_metrics,"research_gaps":gaps,"performance":{"coverage_calculation_time_ms":round((time.perf_counter()-started)*1000,3),"records_touched":len(pilot.get("claims",[]))+len(pilot.get("evidence",[]))+len(pilot.get("sources",[]))+len(p4.get("observations",[])),"dependency_depth":3},"database_snapshot":snapshot(root)}


def coverage_report(root): return {cid:coverage_for_candidate(root,cid) for cid in CANDIDATES}


def validate_coverage(report):
    if set(report)!=VALID_CANDIDATES:return False,"candidate_scope"
    for cid,r in report.items():
        if r.get("coverage_is_not_truth_probability") is not True:return False,f"truth_probability:{cid}"
        if cid not in VALID_CANDIDATES:return False,f"candidate:{cid}"
        for row in r.get("domains",[]):
            if row.get("coverage") not in {"HIGH","MODERATE","PARTIAL","SPARSE","UNKNOWN","UNAVAILABLE"}:return False,f"domain_state:{cid}"
        for g in r.get("research_gaps",[]):
            if g.get("status") not in {"OPEN","PARTIALLY_RESOLVED","RESOLVED","BLOCKED","UNAVAILABLE"}:return False,f"gap_state:{cid}"
    return True,"OK"
