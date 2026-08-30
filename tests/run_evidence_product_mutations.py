"""Mutation audit: mutate product presentation contracts and require the guard to fail."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'tools/evidence_product.py').read_text(); html=(ROOT/'product/index.html').read_text()
def guard(s,h):
    required_s=('candidate_scope','as_of','review_status','independent','NOT_A_SOURCE','INSUFFICIENT_EVIDENCE')
    required_h=('Key evidence','Contradictions / qualifications','Calculation','Review','Provenance','Limitations')
    return all(x in s for x in required_s) and all(x in h for x in required_h)
mutations={
 'candidate_contamination':(source.replace("record['candidate_scope']=[cid]","record['candidate_scope']=[]",1),html),
 'provenance_removal':(source,html.replace('Provenance','',1)),
 'quantitative_input_alteration':(source,html.replace('Calculation','Arithmetic',1)),
 'causal_classification_removal':(source.replace("'INSUFFICIENT_EVIDENCE'","'ESTABLISHED'",1),html),
 'contradiction_removal':(source,html.replace('Contradictions / qualifications','',1)),
 'correction_removal':(source.replace('correction','correction_removed',1),html),
 'as_of_removal':(source.replace("if as_of: record['as_of']=as_of","if False: record['as_of']=as_of",1),html),
 'unknown_to_false':(source.replace('NOT_A_SOURCE','FALSE',1),html),
 'review_to_evidence':(source.replace('review_status','evidence_status',1),html),
 'social_statement_to_factual_proof':(source.replace('statement_occurrence_is_not_independent_truth','statement_is_fact',1),html),
}
print('PRODUCT_MUTATION_RESULTS')
for name,(s,h) in mutations.items():
    killed=not guard(s,h); print(f"{name}: {'KILLED' if killed else 'SURVIVED'}")
assert all(not guard(s,h) for s,h in mutations.values())
