from pathlib import Path
import json
from research_workbench import report_bundle
from tests.phase5_golden_investigations import GOLDEN

ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/"reports"

def main():
    investigations=[]
    for i,q in enumerate(GOLDEN,1):
        b=report_bundle(ROOT,q,as_of="2026-08-30")
        investigations.append({"id":f"G{i}","question":q,"answerability":b["investigation"]["answerability"],"status":b["investigation"]["investigation"]["status"],"sub_questions":b["investigation"]["investigation"]["sub_questions"],"evidence_requirements":b["investigation"]["investigation"]["evidence_requirements"],"gaps":b["investigation"]["research_gaps"],"sources":b["investigation"]["sources"],"provenance":b["investigation"]["provenance"]})
    tasks=[]
    for x in investigations: tasks.extend(report_bundle(ROOT,x["question"],as_of="2026-08-30")["tasks"])
    coverage={"model":"multidimensional-documentary-coverage-v1","is_truth_probability":False,"candidates":{cid:report_bundle(ROOT,f"What evidence exists for {cid}?")["coverage"]["coverage_by_candidate"][cid] for cid in ("bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar")}}
    mutation={"phase":"5","status":"NOT_EXECUTED","mutations":[],"note":"Mutation execution requires GitHub Actions; implementation existence is not PASS."}
    phase={"phase":"5","name":"Research Workbench & Evidence Investigation","implemented":True,"executed":False,"status":"UNTESTED","candidate_scope":["bola-ahmed-tinubu","peter-gregory-obi","atiku-abubakar"],"candidate_4":"BLOCKED","methodology_version":"phase5-research-workbench-v1","golden_count":len(investigations)}
    (REPORTS/"research-investigations.json").write_text(json.dumps(investigations,indent=2,sort_keys=True)+"\n")
    (REPORTS/"research-tasks.json").write_text(json.dumps(tasks,indent=2,sort_keys=True)+"\n")
    (REPORTS/"research-coverage.json").write_text(json.dumps(coverage,indent=2,sort_keys=True)+"\n")
    (REPORTS/"phase-5-mutation-results.json").write_text(json.dumps(mutation,indent=2)+"\n")
    (REPORTS/"phase-5-research-workbench.json").write_text(json.dumps(phase,indent=2)+"\n")
    md=["# Phase 5 — Research Workbench","","## Status","","IMPLEMENTED: YES  ","EXECUTED: NO  ","PASS: NO  ","UNTESTED: YES","","The workbench is deterministic and scoped to the three validated candidates. CI execution is required before PASS.",""]
    md += ["## Golden investigations",""]+[f"- **G{i}** — {q}" for i,q in enumerate(GOLDEN,1)]
    (REPORTS/"phase-5-research-workbench.md").write_text("\n".join(md)+"\n")
    (REPORTS/"research-investigations.md").write_text("# Research Investigations\n\n"+"\n".join(f"- G{i}: {q}" for i,q in enumerate(GOLDEN,1))+"\n")
    (REPORTS/"research-tasks.md").write_text("# Research Tasks\n\nGenerated deterministically from evidence requirements.\n")
    (REPORTS/"research-coverage.md").write_text("# Research Coverage\n\nCoverage is documentary coverage, not truth probability.\n")
    (REPORTS/"phase-5-mutation-results.md").write_text("# Phase 5 Mutation Results\n\nNOT_EXECUTED until CI runs the mutation suite.\n")

if __name__=="__main__": main()
