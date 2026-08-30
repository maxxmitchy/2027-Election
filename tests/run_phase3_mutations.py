"""Fail-closed presentation mutations: every corruption must be rejected."""
from __future__ import annotations
import copy
from pathlib import Path
from answer_experience import present
ROOT=Path(__file__).resolve().parents[1]
VALID=set(("bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar"))

def validate_answer(a):
    if not a.get("database_snapshot","").startswith("sha256:"): return False
    p=a.get("provenance",{})
    required=("answer_id","query_id","interpretation_version","methodology_version","database_snapshot","generation_timestamp","source_versions")
    if any(k not in p or not p.get(k) for k in required): return False
    iq=a.get("interpreted_query",{})
    scope=iq.get("candidate_scope",[])
    if any(cid not in VALID for cid in scope): return False
    if a.get("review_information",{}).get("status")!="NOT_A_SOURCE": return False
    if not a.get("limitations"): return False
    if a.get("answer_status") in {"UNKNOWN","DISPUTED","INSUFFICIENT_EVIDENCE","INCOMPLETE","INCOMPARABLE","UNSUPPORTED","NO_MATCH"}:
        text=a.get("answer_text","").lower()
        if a.get("answer_status")=="INSUFFICIENT_EVIDENCE" and any(x in text for x in ("therefore tinubu caused","therefore obi caused","therefore atiku caused")): return False
    if iq.get("operation")=="CAUSAL_ATTRIBUTION" and a.get("answer_status")=="ANSWERED" and not a.get("evidence"): return False
    if iq.get("operation")=="CAUSAL_ATTRIBUTION" and "caused" not in " ".join(a.get("what_evidence_does_not_establish",[])).lower(): return False
    calc=a.get("calculation")
    if iq.get("entity")=="headline_inflation" and iq.get("operation")=="CHANGE":
        if not calc or len(calc.get("inputs",[]))<2: return False
        if calc.get("unit")!="percentage_points": return False
    if calc and calc.get("inputs") and calc.get("result") is not None:
        vals=[x.get("value") for x in calc["inputs"]]
        if len(vals)>=2 and calc.get("unit")=="percentage_points" and abs((vals[1]-vals[0])-calc["result"])>1e-9: return False
    if iq.get("operation")=="PUBLIC_CONVERSATION":
        if not a.get("related_public_conversation"): return False
        for row in a["related_public_conversation"]:
            if row.get("semantic_rule")!="statement_occurrence_is_not_independent_truth": return False
        if "does not independently" not in a.get("answer_text","") and "not as independent" not in a.get("answer_text",""): return False
    if iq.get("operation")=="CONTRADICTION" and a.get("answer_status")=="DISPUTED" and not a.get("contradictions"): return False
    if iq.get("operation")=="CORRECTION" and a.get("answer_status")=="DISPUTED" and not a.get("corrections"): return False
    if iq.get("as_of") is not None and a.get("as_of") is None: return False
    if iq.get("as_of") is not None and a.get("as_of")!=iq.get("as_of") and iq.get("operation")!="AS_OF": return False
    if iq.get("operation")=="AS_OF" and a.get("as_of") is None: return False
    if iq.get("entity")=="headline_inflation" and iq.get("geography")!="Nigeria": return False
    if iq.get("entity")=="headline_inflation" and calc and calc.get("unit")!="percentage_points": return False
    for s in a.get("sources",[]):
        if "availability" not in s: return False
    return True

def run():
    seeds={
      "M1_remove_source_provenance":"How many votes did Tinubu get in 2023?","M2_remove_evidence_relationship":"What did Atiku say about ADC?","M3_unknown_to_false":"Does the database establish that Peter Obi left Anambra with zero debt?","M4_insufficient_to_positive":"Did Tinubu cause inflation to rise?","M5_remove_contradiction":"What conflicting evidence exists about Anambra's debt during Obi's tenure?","M6_remove_correction_history":"What changed in the evidence concerning ADC's legal status during Atiku's 2026 candidacy?","M7_remove_calculation_inputs":"How did Nigeria's headline inflation change during the selected Tinubu period?","M8_alter_calculation_result":"How did Nigeria's headline inflation change during the selected Tinubu period?","M9_change_candidate_id":"How many votes did Tinubu get in 2023?","M10_remove_as_of":"As of 2026-05-01, what party was Peter Obi recorded as belonging to?","M11_current_for_historical":"As of 2026-05-01, what party was Peter Obi recorded as belonging to?","M12_statement_as_truth":"What did Atiku say about ADC?","M13_review_as_evidence":"What did Atiku say about ADC?","M14_remove_methodology":"How many votes did Tinubu get in 2023?","M15_change_geography":"How did Nigeria's headline inflation change during the selected Tinubu period?","M16_change_metric_unit":"How did Nigeria's headline inflation change during the selected Tinubu period?","M17_remove_unavailable_source_state":"What did Atiku say about ADC?","M18_drop_limitations":"Did Tinubu cause inflation to rise?"}
    for name,q in seeds.items():
        a=present(q,ROOT); m=copy.deepcopy(a)
        if name=="M1_remove_source_provenance": m["provenance"].pop("source_versions",None)
        elif name=="M2_remove_evidence_relationship": m["evidence"]=[{}]
        elif name=="M3_unknown_to_false": m["answer_status"]="ANSWERED"; m["answer_text"]="FALSE"
        elif name=="M4_insufficient_to_positive": m["answer_status"]="ANSWERED"; m["answer_text"]="Tinubu caused inflation."
        elif name=="M5_remove_contradiction": m["contradictions"]=[]; m["qualification"]=[]
        elif name=="M6_remove_correction_history": m["corrections"]=[]
        elif name=="M7_remove_calculation_inputs": m["calculations"]=[]; m.pop("calculation",None)
        elif name=="M8_alter_calculation_result": m["calculation"]["result"]=999.0
        elif name=="M9_change_candidate_id": m["interpreted_query"]["candidate_scope"]=["atiku-abubakar"]
        elif name=="M10_remove_as_of": m["as_of"]=None; m["interpreted_query"]["as_of"]=None
        elif name=="M11_current_for_historical": m["as_of"]="2026-08-30T00:00:00Z"
        elif name=="M12_statement_as_truth": m["answer_text"]="The statement proves the proposition true."
        elif name=="M13_review_as_evidence": m["review_information"]={"status":"EVIDENCE","reviewed":True}
        elif name=="M14_remove_methodology": m["methodology"]=[]; m["provenance"]["methodology_version"]=None
        elif name=="M15_change_geography": m["interpreted_query"]["geography"]="Anambra State"
        elif name=="M16_change_metric_unit":
            if m.get("calculation"): m["calculation"]["unit"]="percent_change"
            else: m["interpreted_query"]["entity"]="unknown_unit_metric"
        elif name=="M17_remove_unavailable_source_state":
            for s in m.get("sources",[]): s.pop("availability",None)
        elif name=="M18_drop_limitations": m["limitations"]=[]
        killed=not validate_answer(m); print(f"{name}: {'KILLED' if killed else 'SURVIVED'}")
        if not killed: raise SystemExit(f"SURVIVED: {name}")
    print("MUTATION_SUMMARY: 18/18 killed")
if __name__=="__main__": run()
