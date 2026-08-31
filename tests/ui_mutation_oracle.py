import os, sys
from pathlib import Path
sys.path.insert(0, os.environ["MUTANT_MODULE_DIR"])
import evidence_product_api as api

checks = {
 "M1_candidate_filter": lambda: _raises(lambda: api._candidate_ids(["candidate-4"])),
 "M2_candidate_substitution": lambda: _raises(lambda: api._candidate_ids(["candidate-4"])),
 "M3_provenance": lambda: api.ask("What offices has Tinubu held")["database_snapshot"].startswith("sha256:"),
 "M4_incompatible_scope": lambda: api.ask("What offices has Tinubu held?", ["bola-ahmed-tinubu","peter-gregory-obi"])["answer_status"] == "INCOMPARABLE",
 "M5_quantitative_change": lambda: api.ask("How did Nigeria's headline inflation change during the selected Tinubu period?")["answer_status"] == "SUPPORTED",
 "M6_causal": lambda: api.ask("Did Tinubu cause inflation to rise?")["answer_status"] == "INSUFFICIENT_EVIDENCE",
 "M7_public_conversation": lambda: api.ask("Did a candidate's X statement prove the statement true?")["answer_id"].endswith("Q18-v1"),
 "M8_contradiction": lambda: api.ask("What conflicting evidence exists about Anambra's debt during Obi's tenure?")["answer_id"].endswith("Q13-v1"),
 "M9_correction": lambda: api.ask("What changed in the evidence concerning ADC's legal status during Atiku's 2026 candidacy?")["answer_id"].endswith("Q14-v1"),
 "M10_as_of": lambda: api.ask("As of 2026-05-01, what party was Peter Obi recorded as belonging to?")["as_of"].startswith("2026-05-01"),
 "M11_office_routing": lambda: api.ask("What offices has Tinubu held?")["answer_id"].endswith("Q1-v1"),
 "M12_party_routing": lambda: api.ask("What parties has Peter Obi been associated with?")["answer_id"].endswith("Q3-v1"),
 "M13_subjective": lambda: api.ask("Who is the best candidate?")["answer_status"] == "UNSUPPORTED",
 "M14_no_llm_fallback": lambda: api.ask("Who is the best candidate?")["interpreted_query"]["validation"]["llm_dependency"] is False,
 "M15_unknown_question": lambda: api.ask("Give me an answer to an unsupported invented question") ["answer_status"] in {"NO_MATCH","UNSUPPORTED"},
}

def _raises(fn):
    try: fn()
    except ValueError: return True
    return False

if __name__ == "__main__":
    failed=[]
    for name, check in checks.items():
        try: ok=bool(check())
        except Exception: ok=False
        if not ok: failed.append(name)
    print(f"MUTANT_ORACLE checks={len(checks)} failed={failed}")
    raise SystemExit(1 if failed else 0)
