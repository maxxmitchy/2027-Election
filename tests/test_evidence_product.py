from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from tools.evidence_product import execute, question_catalog
from system_demo import load_dossiers

def q(text): return next(x for x in question_catalog() if x['question']==text)
def test_product_has_three_validated_candidates_only():
    assert set(load_dossiers(ROOT)) == {'bola-ahmed-tinubu','peter-gregory-obi','atiku-abubakar'}
    assert not (ROOT/'candidates'/'candidate-4').exists()
def test_answer_render_contract_fields():
    a=execute('What offices has Tinubu held?','Tinubu'); assert a['answer_status']=='ESTABLISHED'; assert a['candidate_scope']==['bola-ahmed-tinubu']
    for key in ('answer_text','key_evidence','what_evidence_establishes','what_evidence_does_not_establish','review_status','database_snapshot','limitations'): assert key in a
def test_candidate_isolation():
    a=execute('What offices has Tinubu held?','Tinubu'); b=execute('What offices has Tinubu held?','Peter Obi'); assert a['candidate_scope']!=b['candidate_scope']; assert a['answer_text']!=b['answer_text']
def test_cross_candidate_scope_cannot_be_silently_narrowed():
    a=execute('How many votes did Tinubu, Obi and Atiku receive in the 2023 presidential election?','Tinubu'); assert a['answer_status']=='INCOMPARABLE'; assert len(a['candidate_scope'])==3
def test_quantitative_view_preserves_percentage_points():
    a=execute("How did Nigeria's headline inflation change during the selected Tinubu period?",'Tinubu'); assert 'percentage points' in a['answer_text']; assert a.get('calculation',{}).get('formula'); assert a.get('observation_versions')
def test_causal_view_is_conservative():
    a=execute('Did Tinubu cause inflation to rise?','Tinubu'); assert a['answer_status']=='INSUFFICIENT_EVIDENCE'; assert 'causation' in a['answer_text'].lower(); assert a['review_status']['reviewed'] is False
def test_contradiction_view_preserves_conflict():
    a=execute("What conflicting evidence exists about Anambra's debt during Obi's tenure?",'Peter Obi'); assert a['answer_status'] in {'DISPUTED','INSUFFICIENT_EVIDENCE','NO_MATCH'}; assert 'what_evidence_does_not_establish' in a
def test_correction_view_does_not_erase_history():
    a=execute("What happened to ADC's legal status in 2026?",'Atiku'); assert 'correction' in (a['answer_text']+json.dumps(a.get('key_evidence',[]))).lower() or a['answer_status'] in {'NO_MATCH','DISPUTED'}
def test_social_statement_is_not_proof():
    a=execute('What did Atiku say about the ADC litigation?','Atiku'); assert a['answer_status'] in {'SUPPORTED','INCOMPLETE'}; assert 'independent' in json.dumps(a).lower()
def test_as_of_does_not_fall_back_to_present_state():
    record=dict(q('What parties has Peter Obi been associated with?')); record['as_of']='2010-01-01'; from system_demo import answer_question; a=answer_question(record,load_dossiers(ROOT)); assert a['as_of']=='2010-01-01'; assert a['answer_status'] in {'ESTABLISHED','NO_MATCH'}
def test_review_is_not_evidence():
    a=execute('What offices has Tinubu held?','Tinubu'); assert a['review_status']['status']=='NOT_A_SOURCE'; assert 'review' not in ' '.join(a.get('source_versions',[])).lower()
def test_no_llm_dependency_in_product_module():
    text=(ROOT/'tools'/'evidence_product.py').read_text(); assert 'openai' not in text.lower(); assert 'anthropic' not in text.lower()
def test_no_match_is_explicit():
    a=execute('Tell me the best candidate in 2027','all'); assert a['answer_status']=='NO_MATCH'
