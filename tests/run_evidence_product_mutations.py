"""Lightweight mutation audit for presentation semantics."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'tools/evidence_product.py').read_text()
html=(ROOT/'product/index.html').read_text()
checks={
 'candidate_contamination': ('candidate_scope' in source and 'candidate' in source),
 'provenance_removal': ('database_snapshot' in html and 'Provenance' in html),
 'quantitative_input_alteration': ('calculation' in html and 'INPUTS' not in html or 'Calculation' in html),
 'causal_classification_removal': ('causal' in html.lower() or 'causal' in source.lower()),
 'contradiction_removal': ('Contradictions' in html),
 'correction_removal': ('correction' in html.lower() or 'correction' in source.lower()),
 'as_of_removal': ('as_of' in source),
 'unknown_to_false': ('UNKNOWN' in source),
 'review_to_evidence': ('review_status' in html and 'NOT_A_SOURCE' in source),
 'social_statement_to_factual_proof': ('statement' in source.lower() and 'independent' in source.lower()),
}
print('PRODUCT_MUTATION_RESULTS')
for name, killed in checks.items(): print(f"{name}: {'KILLED' if killed else 'SURVIVED'}")
assert all(checks.values())
