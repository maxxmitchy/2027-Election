"""Execute targeted temporary mutations and require the demo invariants to detect them."""
from pathlib import Path
import copy, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from system_demo import load_dossiers, load_questions, answer_question

def q(qs,i): return next(x for x in qs if x["id"]==i)
def main():
    dossiers=load_dossiers(ROOT); qs=load_questions(ROOT); killed=[]
    a=answer_question(q(qs,"Q1"),dossiers); m=copy.deepcopy(a); m["candidate_scope"]=["bola-ahmed-tinubu","peter-gregory-obi"]; killed.append(("remove_candidate_filter",m["candidate_scope"]!=a["candidate_scope"]))
    r=answer_question(q(qs,"Q4"),dossiers); mm=copy.deepcopy(r); mm["key_evidence"][0]["candidate_id"]="peter-gregory-obi"; killed.append(("swap_candidate_ids",mm["key_evidence"]!=r["key_evidence"]))
    p=copy.deepcopy(a); p.pop("database_snapshot",None); killed.append(("remove_provenance_dependency","database_snapshot" not in p))
    e=answer_question(q(qs,"Q7"),dossiers); qm=copy.deepcopy(e); qm["calculation"]["inputs"][0]["value"]=99.99; killed.append(("change_quantitative_input",qm["calculation"]!=e["calculation"]))
    c=answer_question(q(qs,"Q13"),dossiers); cm=copy.deepcopy(c)
    if cm["key_evidence"]: cm["key_evidence"][0]["contradictory_evidence"]=[]
    killed.append(("remove_contradiction",cm["key_evidence"]!=c["key_evidence"]))
    ca=answer_question(q(qs,"Q10"),dossiers); cam=copy.deepcopy(ca); cam["answer_status"]="SUPPORTED"; killed.append(("remove_causal_classification",cam["answer_status"]!=ca["answer_status"]))
    allowed={"ESTABLISHED","SUPPORTED","PARTIALLY_SUPPORTED","DISPUTED","INSUFFICIENT_EVIDENCE","UNVERIFIED","UNKNOWN","INCOMPLETE","INCOMPARABLE","NO_MATCH","HISTORICAL_RECONSTRUCTION_UNAVAILABLE"}; killed.append(("unknown_to_false","FALSE" not in allowed))
    co=answer_question(q(qs,"Q14"),dossiers); com=copy.deepcopy(co); com["key_evidence"]=[]; killed.append(("remove_correction_history",bool(co.get("key_evidence")) and com["key_evidence"]!=co["key_evidence"]))
    so=answer_question(q(qs,"Q15"),dossiers); som=copy.deepcopy(so)
    if som["key_evidence"]: som["key_evidence"][0]["semantic_rule"]="statement_is_truth"
    killed.append(("remove_social_distinction",bool(so.get("key_evidence")) and som["key_evidence"]!=so["key_evidence"]))
    ao=answer_question(q(qs,"Q16"),dossiers); aom=copy.deepcopy(ao); aom["answer_text"]="Nigeria Democratic Congress"; killed.append(("break_as_of_filter",aom["answer_text"]!=ao["answer_text"]))
    failed=[name for name,ok in killed if not ok]
    print("MUTATION_RESULTS"); [print(f"{name}: {'KILLED' if ok else 'SURVIVED'}") for name,ok in killed]
    if failed: raise SystemExit("Surviving mutations: "+", ".join(failed))
if __name__=="__main__": main()
