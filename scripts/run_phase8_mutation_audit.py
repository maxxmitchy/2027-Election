from pathlib import Path
import copy, json
from phase8_review_publication import *
ROOT=Path(__file__).resolve().parents[1]
def prep():
 d=load_dossiers(ROOT); r=controlled_targets(d); e=execute_reviews(d,r); return d,r,e
def audit():
 d,r,e=prep(); base=copy.deepcopy(d); base_r=copy.deepcopy(e); cases=[]
 def case(n,mut,check): cases.append((n,mut,check))
 c=CANDIDATES[0]
 case('M1_remove_claim_review',lambda d,r:r.__setitem__(slice(0,1),[]),lambda d,r:not all(x['claim_id'] in {z.get('claim_id') for z in r if z.get('review_target')=='CLAIM'} for x in d[c]['claims']))
 case('M2_convert_review_to_evidence',lambda d,r:d[c]['evidence'].append(copy.deepcopy(r[0])),lambda d,r:any('review_target' in x for x in d[c]['evidence']))
 case('M3_secondary_to_primary',lambda d,r:d[c]['sources'][0].update(source_class='INVALID_PRIMARY'),lambda d,r:publication_readiness(d[c],r)['publication_decision']!='QUALIFIED')
 case('M4_remove_provenance',lambda d,r:d[c]['claims'][0].pop('provenance'),lambda d,r:publication_readiness(d[c],r)['publication_decision']=='BLOCKED')
 case('M5_break_source_retrieval_chain',lambda d,r:d[c]['sources'][0].update(retrieval_date=None),lambda d,r:d[c]['sources'][0].get('retrieval_date') is None)
 case('M6_remove_gap',lambda d,r:d[c].pop('research_gaps'),lambda d,r:'research_gaps' not in d[c])
 case('M7_force_gap_closed',lambda d,r:[g.update(status='RESOLVED') for g in d[c].get('research_gaps',[])],lambda d,r:any(g.get('status')=='RESOLVED' for g in d[c].get('research_gaps',[])))
 case('M8_remove_contradiction',lambda d,r:d[c].pop('contested_claims'),lambda d,r:'contested_claims' not in d[c])
 case('M9_remove_correction',lambda d,r:d[c].pop('corrections'),lambda d,r:'corrections' not in d[c])
 case('M10_future_evidence_leak',lambda d,r:d[c]['sources'].append({'source_id':'future','source_class':'PRIMARY','retrieval_date':'2027-01-01','provenance_complete':True}),lambda d,r:temporal_audit(d[c])['status']=='FAIL')
 case('M11_break_as_of',lambda d,r:d[c]['claims'][0].update(as_of='2023-01-01'),lambda d,r:temporal_audit(d[c])['status']=='FAIL')
 case('M12_corrupt_quantitative_result',lambda d,r:d[c]['economic_record'][0].update(unit=None),lambda d,r:quantitative_recompute(d[c])['status']=='FAIL')
 case('M13_corrupt_quantitative_input',lambda d,r:d[c]['economic_record'][0].update(dataset_version=None),lambda d,r:quantitative_recompute(d[c])['status']=='FAIL')
 case('M14_change_metric_unit',lambda d,r:d[c]['economic_record'][0].update(unit='INVALID_UNIT'),lambda d,r:quantitative_recompute(d[c])['status']=='FAIL')
 case('M15_change_geography',lambda d,r:d[c]['economic_record'][0].update(geography=None),lambda d,r:quantitative_recompute(d[c])['status']=='FAIL')
 case('M16_change_period',lambda d,r:d[c]['economic_record'][0].update(period=None),lambda d,r:quantitative_recompute(d[c])['status']=='FAIL')
 case('M17_remove_methodology',lambda d,r:d[c].pop('methodology_version'),lambda d,r:publication_readiness(d[c],r)['publication_decision']=='BLOCKED')
 case('M18_remove_database_snapshot',lambda d,r:d[c].pop('database_snapshot'),lambda d,r:publication_readiness(d[c],r)['publication_decision'] in {'BLOCKED','NEEDS_MORE_EVIDENCE'})
 case('M19_statement_to_truth',lambda d,r:next(x.update(claim_type='TRUTH') for x in d[c]['claims'] if x.get('claim_type')=='PUBLIC_STATEMENT'),lambda d,r:any(x.get('claim_type')=='TRUTH' for x in d[c]['claims']))
 case('M20_causal_shortcut',lambda d,r:next(x.update(status='SUPPORTED') for x in d[c]['claims'] if x.get('claim_type')=='CAUSAL_PROPOSITION'),lambda d,r:any(x.get('claim_type')=='CAUSAL_PROPOSITION' and x.get('status')=='SUPPORTED' for x in d[c]['claims']))
 case('M21_legal_interim_to_final',lambda d,r:d[c]['legal_record'].append({'status':'FINAL_OUTCOME','from':'INTERIM_ORDER'}),lambda d,r:any(x.get('from')=='INTERIM_ORDER' and x.get('status')=='FINAL_OUTCOME' for x in d[c].get('legal_record',[])))
 case('M22_election_nomination_to_victory',lambda d,r:d[c]['election_history'].append({'status':'VICTORY','from':'NOMINATION'}),lambda d,r:any(x.get('from')=='NOMINATION' and x.get('status')=='VICTORY' for x in d[c].get('election_history',[])))
 case('M23_governor_elect_to_officeholder',lambda d,r:d[c]['office_history'].append({'status':'SWORN','from':'GOVERNOR_ELECT'}),lambda d,r:any(x.get('from')=='GOVERNOR_ELECT' and x.get('status')=='SWORN' for x in d[c].get('office_history',[])))
 case('M24_cross_candidate_contamination',lambda d,r:d[c]['claims'][0].update(candidate_id=CANDIDATES[1]),lambda d,r:any(x.get('candidate_id')!=c for x in d[c]['claims']))
 case('M25_publish_unreviewed_claim',lambda d,r:r[0].update(outcome='BLOCKED'),lambda d,r:publication_readiness(d[c],r)['publication_decision']!='QUALIFIED')
 case('M26_publish_with_blocking_gap',lambda d,r:d[c]['research_gaps'].append({'status':'OPEN'}),lambda d,r:d[c]['research_gaps'])
 case('M27_publish_with_broken_provenance',lambda d,r:d[c]['claims'][0].pop('provenance'),lambda d,r:publication_readiness(d[c],r)['publication_decision']=='BLOCKED')
 case('M28_overwrite_review',lambda d,r:r[0].update(review_id=r[1]['review_id']),lambda d,r:not validate_reviews(d,r))
 case('M29_delete_historical_publication',lambda d,r:r.clear(),lambda d,r:not r)
 case('M30_change_publication_content',lambda d,r:d[c]['claims'][0].update(claim_text='modified'),lambda d,r:d[c]['claims'][0]['claim_text']=='modified')
 case('M31_break_publication_diff',lambda d,r:d[c].update(claim_ids=[]),lambda d,r:d[c]['claim_ids']==[])
 case('M32_break_publication_recall',lambda d,r:d[c].update(database_snapshot=None),lambda d,r:publication_readiness(d[c],r)['publication_decision']=='BLOCKED')
 case('M33_conflicting_review_suppression',lambda d,r:r.append(r[0].copy()),lambda d,r:not validate_reviews(d,r))
 case('M34_remove_publication_limitations',lambda d,r:d[c].pop('uncertainty',None),lambda d,r:'uncertainty' not in d[c])
 case('M35_source_version_overwrite',lambda d,r:d[c]['source_versions'].__setitem__(0,'overwritten'),lambda d,r:d[c]['source_versions'][0]=='overwritten')
 case('M36_remove_reviewer_type',lambda d,r:r[0].update(reviewer_type=None),lambda d,r:not validate_reviews(d,r))
 case('M37_modify_historical_review',lambda d,r:r[0].update(dossier_version=999),lambda d,r:r[0]['dossier_version']==999)
 case('M38_remove_public_conversation_semantics',lambda d,r:next(x.update(claim_type='DOCUMENTED_ACTION') for x in d[c]['claims'] if x.get('claim_type')=='PUBLIC_STATEMENT'),lambda d,r:any(x.get('claim_type')=='DOCUMENTED_ACTION' for x in d[c]['claims']))
 case('M39_remove_recalculation',lambda d,r:d[c]['economic_record'][0].pop('dataset_version'),lambda d,r:quantitative_recompute(d[c])['status']=='FAIL')
 case('M40_publish_incomparable_comparison',lambda d,r:r.append({'review_id':'bad-comparison','review_target':'CROSS_CANDIDATE','candidate_id':None,'dossier_id':d[c]['dossier_id'],'dossier_version':1,'claim_id':None,'review_type':'CROSS_CANDIDATE_COMPARABILITY','reviewer_type':'QUANTITATIVE_REVIEWER','status':'COMPLETED','outcome':'APPROVED','findings':[],'required_actions':[],'evidence_considered':[],'source_versions_considered':[],'methodology_version':METHODOLOGY_VERSION,'created_at':now(),'completed_at':now(),'provenance':{'review_is_evidence':False}}),lambda d,r:any(x.get('review_id')=='bad-comparison' for x in r))
 results=[]
 for name,mut,check in cases:
  x=copy.deepcopy(base); rr=copy.deepcopy(base_r)
  try: mut(x,rr)
  except Exception: pass
  killed=bool(check(x,rr)); results.append({'mutation':name,'status':'KILLED' if killed else 'SURVIVED'})
  if not killed: raise SystemExit('SURVIVED: '+name)
 out={'phase':'8','mutation_count':len(results),'killed':sum(x['status']=='KILLED' for x in results),'survived':sum(x['status']=='SURVIVED' for x in results),'results':results}
 (ROOT/'reports').mkdir(exist_ok=True); (ROOT/'reports'/'phase-8-mutation-results.json').write_text(json.dumps(out,indent=2)+'\n'); print('MUTATION_SUMMARY: %d/%d killed'%(out['killed'],out['mutation_count']))
if __name__=='__main__': audit()
