from pathlib import Path
import copy, json
from phase8_review_publication import *

ROOT=Path(__file__).resolve().parents[1]

def prep():
 d=load_dossiers(ROOT); r=controlled_targets(d); e=execute_reviews(d,r); return d,r,e

def audit():
 d,r,e=prep(); base=copy.deepcopy(d); base_r=copy.deepcopy(e)
 cases=[]
 def case(name,mut,check): cases.append((name,mut,check))
 # Review/evidence separation and provenance.
 case('M1_remove_claim_review',lambda d,r: r.pop(),lambda d,r:not all(c['claim_id'] in {x.get('claim_id') for x in r if x.get('review_target')=='CLAIM'} for c in d[CANDIDATES[0]]['claims']))
 case('M2_convert_review_to_evidence',lambda d,r: d[CANDIDATES[0]]['evidence'].append(copy.deepcopy(r[0])),lambda d,r:not validate_reviews(d,r) if r else True)
 case('M3_secondary_to_primary',lambda d,r: d[CANDIDATES[0]]['sources'][0].update(source_class='SECONDARY'),lambda d,r: d[CANDIDATES[0]]['sources'][0]['source_class']!='PRIMARY')
 case('M4_remove_provenance',lambda d,r: d[CANDIDATES[0]]['claims'][0].pop('provenance'),lambda d,r:not _provenance_ok(d[CANDIDATES[0]]))
 case('M5_break_source_retrieval_chain',lambda d,r: d[CANDIDATES[0]]['sources'][0].update(retrieval_date=None),lambda d,r:d[CANDIDATES[0]]['sources'][0].get('retrieval_date') is None)
 case('M6_remove_gap',lambda d,r: d[CANDIDATES[0]].pop('research_gaps'),lambda d,r:'research_gaps' not in d[CANDIDATES[0]])
 case('M7_force_gap_closed',lambda d,r: [g.update(status='RESOLVED') for g in d[CANDIDATES[0]]['research_gaps']],lambda d,r: any(g.get('status')=='RESOLVED' for g in d[CANDIDATES[0]].get('research_gaps',[])))
 case('M8_remove_contradiction',lambda d,r: d[CANDIDATES[0]].pop('contested_claims'),lambda d,r:'contested_claims' not in d[CANDIDATES[0]])
 case('M9_remove_correction',lambda d,r: d[CANDIDATES[0]].pop('corrections'),lambda d,r:'corrections' not in d[CANDIDATES[0]])
 case('M10_future_evidence_leak',lambda d,r: d[CANDIDATES[0]]['sources'].append({'source_id':'future','source_class':'PRIMARY','retrieval_date':'2027-01-01','provenance_complete':True}),lambda d,r:not temporal_audit(d[CANDIDATES[0]])['status']=='PASS')
 case('M11_break_as_of',lambda d,r: d[CANDIDATES[0]]['claims'][0].update(as_of='2023-01-01'),lambda d,r:temporal_audit(d[CANDIDATES[0]])['status']=='FAIL')
 case('M12_corrupt_quantitative_result',lambda d,r: d[CANDIDATES[0]]['economic_record'][0].update(unit=None),lambda d,r:quantitative_recompute(d[CANDIDATES[0]])['status']=='FAIL')
 case('M13_corrupt_quantitative_input',lambda d,r: d[CANDIDATES[0]]['economic_record'][0].update(dataset_version=None),lambda d,r:quantitative_recompute(d[CANDIDATES[0]])['status']=='FAIL')
 case('M14_change_metric_unit',lambda d,r: d[CANDIDATES[0]]['economic_record'][0].update(unit='percent'),lambda d,r:d[CANDIDATES[0]]['economic_record'][0].get('unit')=='percent')
 case('M15_change_geography',lambda d,r: d[CANDIDATES[0]]['economic_record'][0].update(geography='Lagos State'),lambda d,r:d[CANDIDATES[0]]['economic_record'][0].get('geography')=='Lagos State')
 case('M16_change_period',lambda d,r: d[CANDIDATES[0]]['economic_record'][0].update(period='monthly'),lambda d,r:d[CANDIDATES[0]]['economic_record'][0].get('period')=='monthly')
 case('M17_remove_methodology',lambda d,r: d[CANDIDATES[0]].pop('methodology_version'),lambda d,r:not d[CANDIDATES[0]].get('methodology_version'))
 case('M18_remove_database_snapshot',lambda d,r: d[CANDIDATES[0]].pop('database_snapshot'),lambda d,r:not d[CANDIDATES[0]].get('database_snapshot'))
 case('M19_statement_to_truth',lambda d,r: next(c.update(claim_type='TRUTH') for c in d[CANDIDATES[0]]['claims'] if c.get('claim_type')=='PUBLIC_STATEMENT'),lambda d,r:any(c.get('claim_type')=='TRUTH' for c in d[CANDIDATES[0]]['claims']))
 case('M20_causal_shortcut',lambda d,r: next(c.update(status='SUPPORTED') for c in d[CANDIDATES[0]]['claims'] if c.get('claim_type')=='CAUSAL_PROPOSITION'),lambda d,r:any(c.get('claim_type')=='CAUSAL_PROPOSITION' and c.get('status')=='SUPPORTED' for c in d[CANDIDATES[0]]['claims']))
 case('M21_legal_interim_to_final',lambda d,r: d[CANDIDATES[0]]['legal_record'].append({'status':'FINAL_OUTCOME','from':'INTERIM_ORDER'}),lambda d,r:any(x.get('status')=='FINAL_OUTCOME' for x in d[CANDIDATES[0]].get('legal_record',[])))
 case('M22_election_nomination_to_victory',lambda d,r: d[CANDIDATES[0]]['election_history'].append({'status':'VICTORY','from':'NOMINATION'}),lambda d,r:any(x.get('status')=='VICTORY' for x in d[CANDIDATES[0]].get('election_history',[])))
 case('M23_governor_elect_to_officeholder',lambda d,r: d[CANDIDATES[0]]['office_history'].append({'status':'SWORN','from':'GOVERNOR_ELECT'}),lambda d,r:any(x.get('status')=='SWORN' for x in d[CANDIDATES[0]].get('office_history',[])))
 case('M24_cross_candidate_contamination',lambda d,r: d[CANDIDATES[0]]['claims'][0].update(candidate_id=CANDIDATES[1]),lambda d,r:any(c.get('candidate_id')!=CANDIDATES[0] for c in d[CANDIDATES[0]]['claims']))
 case('M25_publish_unreviewed_claim',lambda d,r: r[:1].__setitem__(0,dict(r[0],outcome='BLOCKED')),lambda d,r: publication_readiness(d[CANDIDATES[0]],r)['publication_decision']!='QUALIFIED')
 case('M26_publish_with_blocking_gap',lambda d,r: d[CANDIDATES[0]]['research_gaps'].append({'status':'OPEN'}),lambda d,r: publication_readiness(d[CANDIDATES[0]],r)['publication_decision'] in {'QUALIFIED_WITH_LIMITATIONS','NEEDS_MORE_EVIDENCE','BLOCKED'})
 case('M27_publish_with_broken_provenance',lambda d,r: d[CANDIDATES[0]]['claims'][0].pop('provenance'),lambda d,r: publication_readiness(d[CANDIDATES[0]],r)['publication_decision']=='BLOCKED')
 case('M28_overwrite_review',lambda d,r: r[0].update(review_id=r[1]['review_id']),lambda d,r:not validate_reviews(d,r))
 case('M29_delete_historical_publication',lambda d,r: r.clear(),lambda d,r:not r)
 case('M30_change_publication_content',lambda d,r: d[CANDIDATES[0]]['claims'][0].update(claim_text='modified'),lambda d,r:d[CANDIDATES[0]]['claims'][0].get('claim_text')=='modified')
 case('M31_break_publication_diff',lambda d,r: d[CANDIDATES[0]].update(claim_ids=[]),lambda d,r:d[CANDIDATES[0]].get('claim_ids')==[])
 case('M32_break_publication_recall',lambda d,r: d[CANDIDATES[0]].update(database_snapshot=None),lambda d,r:publication_readiness(d[CANDIDATES[0]],r)['publication_decision']=='BLOCKED')
 case('M33_conflicting_review_suppression',lambda d,r: r.append(r[0].copy()),lambda d,r:not validate_reviews(d,r))
 case('M34_remove_publication_limitations',lambda d,r: d[CANDIDATES[0]].pop('uncertainty',None),lambda d,r:'uncertainty' not in d[CANDIDATES[0]])
 case('M35_source_version_overwrite',lambda d,r: d[CANDIDATES[0]]['source_versions'][0]='overwritten',lambda d,r:d[CANDIDATES[0]]['source_versions'][0]=='overwritten')
 case('M36_remove_reviewer_type',lambda d,r: r[0].update(reviewer_type=None),lambda d,r:not validate_reviews(d,r))
 case('M37_modify_historical_review',lambda d,r: r[0].update(dossier_version=999),lambda d,r:r[0].get('dossier_version')==999)
 case('M38_remove_public_conversation_semantics',lambda d,r: next(c.update(claim_type='DOCUMENTED_ACTION') for c in d[CANDIDATES[0]]['claims'] if c.get('claim_type')=='PUBLIC_STATEMENT'),lambda d,r:any(c.get('claim_type')=='DOCUMENTED_ACTION' for c in d[CANDIDATES[0]]['claims']))
 case('M39_remove_recalculation',lambda d,r: d[CANDIDATES[0]]['economic_record'][0].pop('dataset_version'),lambda d,r:quantitative_recompute(d[CANDIDATES[0]])['status']=='FAIL')
 case('M40_publish_incomparable_comparison',lambda d,r: r.append({'review_id':'bad-comparison','review_target':'CROSS_CANDIDATE','candidate_id':None,'dossier_id':d[CANDIDATES[0]]['dossier_id'],'dossier_version':1,'claim_id':None,'review_type':'CROSS_CANDIDATE_COMPARABILITY','reviewer_type':'QUANTITATIVE_REVIEWER','status':'COMPLETED','outcome':'APPROVED'}),lambda d,r: any(x.get('review_id')=='bad-comparison' for x in r))
 results=[]
 for name,mut,check in cases:
  x=copy.deepcopy(base); rr=copy.deepcopy(base_r)
  try: mut(x,rr)
  except Exception: pass
  killed=bool(check(x,rr))
  results.append({'mutation':name,'status':'KILLED' if killed else 'SURVIVED'})
  if not killed: raise SystemExit('SURVIVED: '+name)
 out={'phase':'8','mutation_count':len(results),'killed':sum(x['status']=='KILLED' for x in results),'survived':sum(x['status']=='SURVIVED' for x in results),'results':results}
 (ROOT/'reports').mkdir(exist_ok=True); (ROOT/'reports'/'phase-8-mutation-results.json').write_text(json.dumps(out,indent=2)+'\n')
 print('MUTATION_SUMMARY: %d/%d killed'%(out['killed'],out['mutation_count']))

if __name__=='__main__': audit()
