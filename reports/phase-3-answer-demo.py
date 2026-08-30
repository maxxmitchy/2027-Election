from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from answer_experience import present
QUESTIONS=["What offices has Tinubu held?","What offices has Atiku held?","What parties has Peter Obi been associated with?","Compare the presidential election results of Tinubu, Obi and Atiku in 2023.","Who received the most votes among the three in 2023?","How did Nigeria's headline inflation change during the selected Tinubu period?","Did Tinubu cause inflation to rise?","Did Peter Obi's administration cause Anambra's debt position?","Did Atiku personally cause the outcomes associated with NCP activity?","What conflicting evidence exists about Anambra's debt during Obi's tenure?","What changed in the evidence concerning ADC's legal status during Atiku's 2026 candidacy?","What did Atiku say about ADC?","As of 2026-05-01, what party was Peter Obi recorded as belonging to?","Does the database establish that Peter Obi left Anambra with zero debt?","Who was the best candidate?","Compare Anambra debt with Nigeria inflation.","How many votes did Tinubu get in 2023?","How did inflation change during Tinubu's presidency?"]
def json_dump(x):
    import json
    return "```json\n"+json.dumps(x,indent=2,sort_keys=True)+"\n```"
def render(a):
    iq=a["interpreted_query"]; lines=[f"## {a['question']}","","### SYSTEM INTERPRETATION",f"- Candidate: {', '.join(iq.get('candidate_scope',[])) or 'none'}",f"- Domain/entity: {iq.get('domain')} / {iq.get('entity')}",f"- Operation: {iq.get('operation')}",f"- Time: {iq.get('time_range')}",f"- Geography: {iq.get('geography')}","","### ANSWER",a["answer_text"],"","### EVIDENCE STATUS",a["answer_status"],"","### WHY THIS ANSWER",json_dump(a.get("why_this_answer",{})),"","### PROVENANCE",json_dump(a["provenance"]),"","### LIMITATIONS"]
    lines += [f"- {x}" for x in a["limitations"]] or ["- None recorded."]
    return "\n".join(lines)
if __name__=="__main__":
    out=["# Phase 3 Evidence Answer Experience — Demonstration","","Generated from deterministic retrieval and presentation; no factual content is authored by this script.",""]
    for q in QUESTIONS: out.append(render(present(q,ROOT))+"\n")
    (ROOT/"reports/phase-3-evidence-answer-demo.md").write_text("\n".join(out),encoding="utf-8")
