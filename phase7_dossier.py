from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

METHODOLOGY_VERSION = "phase7-research-investigation-dossier-v1"
CANDIDATES = ("bola-ahmed-tinubu", "peter-gregory-obi", "atiku-abubakar")
BLOCKED = "candidate-4"
INVESTIGATION_STATES = ("PLANNED","ACTIVE","EVIDENCE_ACQUISITION","EVIDENCE_REVIEW","PARTIALLY_COMPLETE","COMPLETE","BLOCKED","CLOSED")
CLAIM_STATES = ("SUPPORTED","PARTIALLY_SUPPORTED","DISPUTED","INSUFFICIENT_EVIDENCE","UNVERIFIED","UNKNOWN","UNAVAILABLE")
REVIEW_STATES = ("QUEUED","IN_REVIEW","APPROVED","REJECTED","NEEDS_MORE_EVIDENCE","BLOCKED")

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def assert_candidate(candidate_id):
    if candidate_id == BLOCKED or candidate_id not in CANDIDATES:
        raise ValueError("candidate scope contains blocked or unapproved subject")

def load_candidate(root, candidate_id):
    assert_candidate(candidate_id)
    path = Path(root) / "candidates" / candidate_id / "data" / "pilot-record.json"
    return json.loads(path.read_text(encoding="utf-8"))

def temporal_ok(record, as_of):
    if not as_of:
        return True
    values = [record.get(k) for k in ("publication_date", "event_date", "valid_from", "date", "retrieved_at", "retrieval_date") if record.get(k)]
    return not values or min(str(v)[:10] for v in values) <= as_of

def make_investigation(candidate_id, title, question, *, as_of="2026-08-30", priority=100, dependencies=()):
    assert_candidate(candidate_id)
    iid = "inv-" + hashlib.sha256(f"{candidate_id}|{title}".encode()).hexdigest()[:20]
    return {
        "investigation_id": iid, "candidate_id": candidate_id, "title": title,
        "research_question": question, "scope": {"candidate_id": candidate_id, "geography": "Nigeria"},
        "as_of": as_of, "status": "PLANNED", "priority": priority,
        "created_at": now(), "methodology_version": METHODOLOGY_VERSION,
        "research_tasks": [], "required_evidence": [], "claims_under_investigation": [],
        "known_unknowns": [], "research_gaps": [], "contradictions": [], "corrections": [],
        "reviews": [], "dependencies": list(dependencies), "provenance": {},
        "answerability": {"status": "INSUFFICIENT_EVIDENCE", "reason": "Investigation existence does not establish truth."},
        "dossier_effect": [], "completion_state": "INCOMPLETE",
    }

def controlled_investigations(as_of="2026-08-30"):
    specs = [
        ("bola-ahmed-tinubu", "economic-record", "What evidence documents the economic record during Tinubu's presidency?"),
        ("bola-ahmed-tinubu", "election-history", "What documentary evidence establishes Tinubu's election history?"),
        ("peter-gregory-obi", "anambra-fiscal", "What evidence documents Peter Obi's Anambra fiscal record?"),
        ("peter-gregory-obi", "party-office", "What evidence establishes Peter Obi's party and office chronology?"),
        ("atiku-abubakar", "adc-legal", "What evidence establishes the ADC legal status relevant to Atiku Abubakar?"),
        ("atiku-abubakar", "federal-policy-ncp", "What evidence documents Atiku's role in the National Council on Privatisation and federal policy?"),
    ]
    return [make_investigation(cid, title, question, as_of=as_of) for cid, title, question in specs]

def investigation_tasks(inv):
    kinds = [("scope", "ESTABLISH_SCOPE"), ("facts", "ESTABLISH_FACTS"), ("primary", "VERIFY_PRIMARY_SOURCE"), ("gaps", "RESOLVE_RESEARCH_GAPS")]
    title = inv["title"].lower()
    if "economic" in title or "fiscal" in title:
        kinds.append(("quantitative", "VERIFY_QUANTITATIVE_LINEAGE"))
    if "legal" in title:
        kinds.append(("legal", "RECONSTRUCT_LEGAL_CHRONOLOGY"))
    if "election" in title:
        kinds.append(("election", "RECONSTRUCT_ELECTION_SEMANTICS"))
    return [{
        "task_id": f"{inv['investigation_id']}-task-{i+1:02d}",
        "investigation_id": inv["investigation_id"], "candidate_id": inv["candidate_id"],
        "task_type": typ, "question_kind": kind, "status": "QUEUED",
        "priority": 100 if i < 4 else 80, "blocking": True,
        "dependencies": [] if i == 0 else [f"{inv['investigation_id']}-task-{i:02d}"],
        "methodology_version": METHODOLOGY_VERSION,
    } for i, (kind, typ) in enumerate(kinds)]

def claim_type(claim):
    typ = str(claim.get("claim_type", "")).upper()
    return {"FACT":"DOCUMENTED_ACTION", "CALCULATED_FACT":"QUANTITATIVE_RESULT", "CAUSAL":"CAUSAL_PROPOSITION", "STATEMENT_OCCURRENCE":"PUBLIC_STATEMENT", "ASSESSMENT":"CONTESTED_CLAIM"}.get(typ, typ or "UNKNOWN")

def source_class(source):
    return "PRIMARY" if source.get("tier") == 1 else "SECONDARY"

def build_gaps(data, candidate_id):
    gaps = []
    for evidence in data.get("evidence", []):
        if str(evidence.get("status", "")).upper() in {"UNVERIFIED", "UNKNOWN", "INCOMPLETE", "UNAVAILABLE"}:
            gaps.append({
                "gap_id": f"gap-{candidate_id}-{evidence.get('id','unknown')}",
                "description": "Verification remains incomplete for an evidence relationship.",
                "reason": str(evidence.get("status")), "required_evidence": "verification",
                "tasks": [], "status": "OPEN", "attempts": [], "sources": [evidence.get("source_id")],
                "resolution": None, "remaining_limitation": "Not verified.",
            })
    return gaps

def build_dossier(root, candidate_id, *, version=1, as_of="2026-08-30", database_snapshot="runtime-reference"):
    data = load_candidate(root, candidate_id)
    source_map = {s.get("id"): s for s in data.get("sources", [])}
    sources = []
    for source in data.get("sources", []):
        if temporal_ok(source, as_of):
            sources.append({
                "source_id": source.get("id"), "source_class": source_class(source), "source_type": source.get("type"),
                "url": source.get("url"), "retrieval_date": source.get("retrieval_date"), "reliability": source.get("reliability"),
                "source_version_id": f"sv-{source.get('id')}", "provenance_complete": bool(source.get("id") and source.get("url")),
            })
    source_ids = {s["source_id"] for s in sources}
    evidence = []
    for item in data.get("evidence", []):
        sid = item.get("source_id")
        if sid in source_ids:
            evidence.append({
                "evidence_id": item.get("id"), "source_id": sid, "source_version_id": f"sv-{sid}",
                "evidence_relationship": item.get("relationship"), "claim_ids": item.get("claim_ids", []),
                "status": item.get("status", "UNASSESSED"),
                "provenance_complete": bool(item.get("id") and source_map.get(sid, {}).get("url")),
            })
    evidence_ids = {e["evidence_id"] for e in evidence}
    claims = []
    for claim in data.get("claims", []):
        raw_status = str(claim.get("status", "UNKNOWN")).upper()
        status = {"VERIFIED":"SUPPORTED", "QUALIFIED":"PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE":"INSUFFICIENT_EVIDENCE", "DISPUTED":"DISPUTED"}.get(raw_status, "UNVERIFIED")
        claims.append({
            "claim_id": claim.get("id"), "candidate_id": candidate_id, "claim_text": claim.get("claim"),
            "claim_type": claim_type(claim), "status": status,
            "evidence_ids": [x for x in claim.get("evidence_ids", []) if x in evidence_ids],
            "source_ids": [e["source_id"] for e in evidence if claim.get("id") in e.get("claim_ids", [])],
            "investigation_ids": [], "review_ids": [], "confidence_qualification": claim.get("causal_classification"),
            "as_of": as_of, "methodology_version": METHODOLOGY_VERSION,
            "provenance": {"source": "pilot-record", "source_claim_id": claim.get("id")},
        })
    gaps = build_gaps(data, candidate_id)
    reviews = []
    for claim in claims:
        if claim["claim_type"] in {"CAUSAL_PROPOSITION", "CONTESTED_CLAIM", "LEGAL_STATUS", "QUANTITATIVE_RESULT"} or claim["status"] in {"DISPUTED", "INSUFFICIENT_EVIDENCE"}:
            reviews.append({
                "review_id": f"review-{claim['claim_id']}", "claim_id": claim["claim_id"],
                "reason": "material uncertainty or high-impact interpretation", "required_reviewer_type": "domain_reviewer",
                "status": "QUEUED", "evidence_dependencies": claim["evidence_ids"], "created_at": now(),
                "methodology_version": METHODOLOGY_VERSION,
            })
    investigations = [i for i in controlled_investigations(as_of) if i["candidate_id"] == candidate_id]
    investigation_ids = [i["investigation_id"] for i in investigations]
    for claim in claims:
        claim["investigation_ids"] = investigation_ids
    out = {
        "dossier_id": f"dossier-{candidate_id}", "candidate_id": candidate_id, "version_number": version,
        "created_at": now(), "as_of": as_of, "methodology_version": METHODOLOGY_VERSION,
        "source_versions": [s["source_version_id"] for s in sources], "evidence_ids": [e["evidence_id"] for e in evidence],
        "claim_ids": [c["claim_id"] for c in claims], "investigation_ids": investigation_ids,
        "research_gap_ids": [g["gap_id"] for g in gaps], "review_ids": [r["review_id"] for r in reviews],
        "identity": {"person": data.get("person"), "candidacy": data.get("candidacies", [])},
        "party_history": data.get("party_memberships", []), "office_history": data.get("officeholdings", []),
        "election_history": data.get("election_results", []),
        "public_statements": [c for c in claims if c["claim_type"] == "PUBLIC_STATEMENT"],
        "related_public_conversation": [c for c in claims if c["claim_type"] == "PUBLIC_STATEMENT"],
        "documented_actions": [], "policies": [], "economic_record": data.get("observations", []),
        "legal_record": data.get("legal_events", []),
        "contested_claims": [c for c in claims if c["status"] in {"DISPUTED", "INSUFFICIENT_EVIDENCE"}],
        "corrections": data.get("corrections", []), "uncertainty": [c for c in claims if c["status"] != "SUPPORTED"],
        "research_gaps": gaps, "reviews": reviews, "sources": sources, "evidence": evidence,
        "claims": claims, "investigations": investigations, "database_snapshot": database_snapshot,
        "generation_metadata": {"generator": "phase7_dossier_assembly", "candidate_source": "pilot-record"},
    }
    out["quality_gate"] = quality_gate(out)
    out["status"] = out["quality_gate"]["recommended_state"]
    out["content_hash"] = digest({k:v for k,v in out.items() if k != "content_hash"})
    return out

def quality_gate(dossier):
    checks = {
        "identity_integrity": bool(dossier.get("identity", {}).get("person")),
        "candidate_candidacy_separation": isinstance(dossier.get("identity", {}).get("candidacy"), list),
        "claim_provenance": all(c.get("provenance") for c in dossier.get("claims", [])),
        "source_provenance": all(s.get("provenance_complete") for s in dossier.get("sources", [])),
        "evidence_relationships": all(e.get("evidence_id") and e.get("source_id") for e in dossier.get("evidence", [])),
        "research_gap_visibility": "research_gaps" in dossier,
        "correction_visibility": "corrections" in dossier,
        "contradiction_visibility": "contested_claims" in dossier,
        "review_requirements": all(r.get("review_id") and r.get("status") in REVIEW_STATES for r in dossier.get("reviews", [])),
        "quantitative_lineage": all("source_id" in o and "dataset_version" in o for o in dossier.get("economic_record", []) if "metric" in o),
        "temporal_correctness": all(c.get("as_of") == dossier.get("as_of") for c in dossier.get("claims", [])),
        "candidate_isolation": dossier.get("candidate_id") in CANDIDATES,
        "methodology_version": dossier.get("methodology_version") == METHODOLOGY_VERSION,
    }
    failures = [k for k,v in checks.items() if not v]
    state = "BLOCKED" if failures else ("IN_REVIEW" if dossier.get("research_gaps") or any(r["status"] != "APPROVED" for r in dossier.get("reviews", [])) else "QUALIFIED")
    return {"checks": checks, "failures": failures, "recommended_state": state, "publishable": state == "QUALIFIED"}

def assemble_investigation_records(root, as_of="2026-08-30"):
    records = []
    for inv in controlled_investigations(as_of):
        data = load_candidate(root, inv["candidate_id"])
        inv["research_tasks"] = investigation_tasks(inv)
        inv["claims_under_investigation"] = [c.get("id") for c in data.get("claims", [])]
        inv["required_evidence"] = [t["task_id"] for t in inv["research_tasks"]]
        inv["research_gaps"] = [g["gap_id"] for g in build_gaps(data, inv["candidate_id"])]
        inv["provenance"] = {"methodology_version": METHODOLOGY_VERSION, "database_snapshot": "runtime-reference", "as_of": as_of}
        inv["status"] = "PARTIALLY_COMPLETE" if inv["research_gaps"] else "COMPLETE"
        inv["completion_state"] = "INCOMPLETE" if inv["research_gaps"] else "COMPLETE"
        inv["answerability"] = {"status": "PARTIALLY_ANSWERABLE" if inv["research_gaps"] else "ANSWERABLE", "reason": "Documentary coverage, not truth probability."}
        inv["dossier_effect"] = ["GAP_REMAINING_OPEN"] if inv["research_gaps"] else ["NEW_EVIDENCE"]
        records.append(inv)
    return records

def dossier_diff(v1, v2):
    def delta(a,b): return {"added": sorted(set(b)-set(a)), "removed": sorted(set(a)-set(b))}
    claims = delta(v1.get("claim_ids", []), v2.get("claim_ids", []))
    evidence = delta(v1.get("evidence_ids", []), v2.get("evidence_ids", []))
    gaps = delta(v1.get("research_gap_ids", []), v2.get("research_gap_ids", []))
    old = {x["claim_id"]:x for x in v1.get("claims", [])}; new = {x["claim_id"]:x for x in v2.get("claims", [])}
    return {
        "dossier_id": v2["dossier_id"], "from_version": v1["version_number"], "to_version": v2["version_number"],
        "ADDED_CLAIMS": claims["added"], "REMOVED_CLAIMS": claims["removed"], "CHANGED_CLAIMS": sorted(k for k in set(old)&set(new) if old[k] != new[k]),
        "ADDED_EVIDENCE": evidence["added"], "REMOVED_EVIDENCE": evidence["removed"],
        "NEW_GAPS": gaps["added"], "RESOLVED_GAPS": gaps["removed"], "NEW_CONTRADICTIONS": [], "RESOLVED_CONTRADICTIONS": [],
        "CORRECTIONS": v2.get("corrections", []), "SOURCE_VERSION_CHANGES": delta(v1.get("source_versions", []), v2.get("source_versions", [])),
    }

def snapshot(dossier):
    result = {
        "candidate_id": dossier["candidate_id"], "dossier_id": dossier["dossier_id"], "version_number": dossier["version_number"],
        "as_of": dossier["as_of"], "claim_count": len(dossier["claims"]), "evidence_count": len(dossier["evidence"]),
        "source_count": len(dossier["sources"]), "open_research_gaps": len(dossier["research_gaps"]),
        "review_queue_count": sum(r["status"] == "QUEUED" for r in dossier["reviews"]),
        "contradiction_count": len(dossier.get("contested_claims", [])), "correction_count": len(dossier.get("corrections", [])),
        "methodology_version": dossier["methodology_version"], "database_snapshot": dossier["database_snapshot"],
    }
    result["content_hash"] = digest(result)
    return result

def valid_dossier(dossier):
    return not quality_gate(dossier)["failures"]
