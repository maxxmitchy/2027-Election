"""Mutation audit: mutate product contracts and require the semantic guard to fail."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'tools/evidence_product.py').read_text(); html=(ROOT/'product/index.html').read_text()
def guard(s,h):
    required_s=('candidate_scope','as_of','review_status','independent','NOT_A_SOURCE','INSUFFICIENT_EVIDENCE','correction')
    required_h=('Key evidence','Contradictions / qualifications','Calculation','Review','Provenance','Limitations')
    return all(x in s for x in required_s) and all(x in h for x in required_h)
mutations={
 'candidate_contamination':(source.replace('candidate_scope','candidate_SCOPE_REMOVED'),html),
 'provenance_removal':(source,html.replace('Provenance','PROVENANCE_REMOVED')),
 'quantitative_input_alteration':(source.replace('as_of','ASOF_REMOVED'),html),
 'causal_classification_removal':(source.replace('INSUFFICIENT_EVIDENCE','CAUSAL_STATUS_REMOVED'),html),
 'contradiction_removal':(source,html.replace('Contradictions / qualifications','CONTRADICTION_REMOVED')),
 'correction_removal':(source.replace('correction','CORRECTION_REMOVED'),html),
 'as_of_removal':(source.replace('as_of','ASOF_REMOVED'),html),
 'unknown_to_false':(source.replace('UNKNOWN','FALSE'),html),
 'review_to_evidence':(source.replace('review_status','evidence_status'),html),
 'social_statement_to_factual_proof':(source.replace('independent','INDEPENDENT_REMOVED'),html),
}
print('PRODUCT_MUTATION_RESULTS')
for name,(s,h) in mutations.items():
    killed=not guard(s,h); print(f"{name}: {'KILLED' if killed else 'SURVIVED'}")
assert all(not guard(s,h) for s,h in mutations.values())
