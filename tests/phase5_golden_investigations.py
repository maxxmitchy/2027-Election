"""Golden research questions: process validation, not forced factual completion."""
from pathlib import Path
from research_workbench import report_bundle

ROOT=Path(__file__).resolve().parents[1]
GOLDEN=[
    "What evidence exists for Tinubu's economic record during his presidency?",
    "Which economic indicators can legitimately be compared across the three administrations represented by the candidates?",
    "What evidence supports or contradicts claims about Peter Obi's Anambra debt record?",
    "What is the documentary record of Atiku's role in the National Council on Privatisation?",
    "What changed in the legal status of ADC during 2026?",
    "What evidence exists for each candidate's documented policy actions, as distinct from campaign promises?",
    "What public statements by the candidates are independently verifiable, and what propositions remain unverified?",
    "Which major research gaps remain in the three candidate dossiers?",
    "Which claims require primary-source verification before publication?",
    "What conclusions about economic performance cannot be established from the current evidence?",
]

def run():
    return [{"id":f"G{i+1}","question":q,"result":report_bundle(ROOT,q)} for i,q in enumerate(GOLDEN)]

if __name__=="__main__":
    import json
    print(json.dumps(run(),indent=2,sort_keys=True))
