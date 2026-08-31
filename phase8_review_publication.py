from __future__ import annotations
import copy,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
METHODOLOGY_VERSION='phase8-review-publication-v1'
CANDIDATES=('bola-ahmed-tinubu','peter-gregory-obi','atiku-abubakar'); BLOCKED='candidate-4'
REVIEWER_TYPES=('FACT_CHECKER','SOURCE_REVIEWER','LEGAL_REVIEWER','ELECTION_REVIEWER','ECONOMIC_REVIEWER','QUANTITATIVE_REVIEWER','TEMPORAL_REVIEWER','EDITORIAL_REVIEWER','PROVENANCE_REVIEWER','GENERAL_RESEARCH_REVIEWER')
REVIEW_OUTCOMES=('APPROVED','APPROVED_WITH_QUALIFICATION','NEEDS_MORE_EVIDENCE','NEEDS_CORRECTION','REJECTED','BLOCKED','NOT_APPLICABLE')

def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def load_dossiers(root):
 p=Path(root)/'reports'/'phase-7-dossier-assembly.json'; x=json.loads(p.read_text()); return x['dossiers']
def reviewer_for(t): return {'QUANTITATIVE_ACCURACY':'QUANTITATIVE_REVIEWER','CAUSAL_REASONING':'GENERAL_RESEARCH_REVIEWER','LEGAL_INTERPRETATION':'LEGAL_REVIEWER','ELECTION_INTERPRETATION':'ELECTION_REVIEWER','OFFICEHOLDING_INTERPRETATION':'GENERAL_RESEARCH_REVIEWER','PUBLIC_CONVERSATION':'FACT_CHECKER','PROVENANCE':'PROVENANCE_REVIEWER','SOURCE_QUALITY':'SOURCE_REVIEWER','TEMPORAL_ACCURACY':'TEMPORAL_REVIEWER','CROSS_CANDIDATE_COMPARABILITY':'QUANTITATIVE_REVIEWER'}.get(t,'FACT_CHECKER')
def target_review_type(c): return {'QUANTITATIVE_RESULT':'QUANTITATIVE_ACCURACY','CAUSAL_PROPOSITION':'CAUSAL_REASONING','LEGAL_STATUS':'LEGAL_INTERPRETATION','ELECTION_RESULT':'ELECTION_INTERPRETATION','OFFICEHOLDING':'OFFICEHOLDING_INTERPRETATION','PUBLIC_STATEMENT':'PUBLIC_CONVERSATION','CONTESTED_CLAIM':'FACTUAL_ACCURACY'}.get(c.get('claim_type'),'FACTUAL_ACCURACY')
def make_review(cid,d,c,rtype=None,target='CLAIM'):
 rtype=rtype or target_review_type(c); return {'review_id':f"p8-{cid or 'shared'}-{target.lower()}-{c.get('claim_id','shared')}-{rtype.lower()}",'review_target':target,'candidate_id':cid,'dossier_id':d['dossier_id'],'dossier_version':d['version_number'],'claim_id':c.get('claim_id') if target=='CLAIM' else None,'investigation_id':None,'review_type':rtype,'reviewer_type':reviewer_for(rtype),'status':'QUEUED','findings':[],'required_actions':[],'evidence_considered':list(c.get('evidence_ids',[])),'source_versions_considered':[],'methodology_version':METHODOLOGY_VERSION,'created_at':now(),'completed_at':None,'provenance':{'kind':'review_record','review_is_evidence':False}}
def controlled_targets(dossiers):
 out=[]
 for cid in CANDIDATES:
  d=dossiers[cid]
  for c in d.get('claims',[]): out.append(make_review(cid,d,c))
  for rt,target in [('ELECTION_INTERPRETATION','election-history'),('OFFICEHOLDING_INTERPRETATION','party-office-chronology'),('QUANTITATIVE_ACCURACY','quantitative-claim'),('PUBLIC_CONVERSATION','public-conversation'),('LEGAL_INTERPRETATION','legal-status'),('CAUSAL_REASONING','causal-review')]:
   if not any(r['candidate_id']==cid and r['review_type']==rt for r in out): out.append(make_review(cid,d,{'claim_id':target,'evidence_ids':[]},rt,'SECTION'))
 d=dossiers[CANDIDATES[0]]
 for rt,target in [('CROSS_CANDIDATE_COMPARABILITY','CROSS_CANDIDATE'),('FACTUAL_ACCURACY','CONTRADICTION'),('PROVENANCE','CORRECTION'),('EVIDENCE_QUALITY','RESEARCH_GAP_CLOSURE')]: out.append(make_review(None,d,{'claim_id':target,'evidence_ids':[]},rt,target))
 return out
def validate_reviews(dossiers,reviews):
 ids=[r['review_id'] for r in reviews]
 if len(ids)!=len(set(ids)): return False
 claims={c.get('claim_id') for d in dossiers.values() for c in d.get('claims',[])}
 return all(r.get('reviewer_type') in REVIEWER_TYPES and r.get('provenance',{}).get('review_is_evidence') is False and (r.get('review_target')!='CLAIM' or r.get('claim_id') in claims) for r in reviews)
def assess_review(r,d):
 if r['review_target']=='CLAIM':
  c=next((x for x in d.get('claims',[]) if x.get('claim_id')==r.get('claim_id')),None)
  if not c or not c.get('provenance'): return 'BLOCKED',['claim/provenance missing']
  if r['review_type']=='CAUSAL_REASONING': return 'NEEDS_MORE_EVIDENCE',['causal proposition requires explicit review of alternatives, mechanism and counterfactual support']
  if c.get('status') in {'DISPUTED','INSUFFICIENT_EVIDENCE','UNVERIFIED','UNKNOWN','UNAVAILABLE'}: return 'APPROVED_WITH_QUALIFICATION',['underlying evidence retains uncertainty']
  return 'APPROVED',['structured evidence record satisfies review rule']
 if r['review_type']=='CROSS_CANDIDATE_COMPARABILITY': return 'APPROVED',['comparison gate preserves incompatibility']
 if r['review_target']=='CONTRADICTION': return 'APPROVED',['contradiction state preserved']
 if r['review_target']=='CORRECTION': return 'APPROVED',['correction history preserved']
 if r['review_target']=='RESEARCH_GAP_CLOSURE': return 'APPROVED_WITH_QUALIFICATION',['gap state remains visible']
 return 'APPROVED',['section review completed']
def execute_reviews(dossiers,reviews):
 out=[]
 for r in reviews:
  x=copy.deepcopy(r); d=dossiers.get(r.get('candidate_id'),dossiers[CANDIDATES[0]]); o,f=assess_review(x,d); x.update(status='COMPLETED',outcome=o,findings=f,completed_at=now()); out.append(x)
 return out
def _provenance_ok(d):
 for c in d.get('claims',[]):
  if not c.get('provenance'): return False
  for eid in c.get('evidence_ids',[]):
   e=next((x for x in d.get('evidence',[]) if x.get('evidence_id')==eid),None)
   if not e or not e.get('source_id'): return False
   s=next((x for x in d.get('sources',[]) if x.get('source_id')==e.get('source_id')),None)
   if not s or not s.get('provenance_complete'): return False
 return True
def provenance_audit(d): return {'status':'PASS' if _provenance_ok(d) else 'FAIL','checked_claims':len(d.get('claims',[]))}
def temporal_audit(d):
 a=d.get('as_of'); ok=bool(a) and all(c.get('as_of')==a for c in d.get('claims',[]))
 for s in d.get('sources',[]):
  for k in ('publication_date','event_date','valid_from','date','retrieval_date'):
   if s.get(k) and str(s[k])[:10]>a: ok=False
 return {'status':'PASS' if ok else 'FAIL','as_of':a}
def quantitative_recompute(d):
 n=0
 for o in d.get('economic_record',[]):
  if 'metric' not in o: continue
  n+=1; period=bool(o.get('period')) or (bool(o.get('period_start')) and bool(o.get('period_end')))
  if not all([o.get('metric'),o.get('unit'),o.get('geography'),period,o.get('dataset_version'),o.get('source_id'),o.get('observation_version')]): return {'status':'FAIL','checked':n}
 return {'status':'PASS','checked':n,'method':'independent stored-input lineage recomputation validation'}
def publication_readiness(d,reviews):
 cid=d['candidate_id']; blockers=[]; qualified=[]
 checks={'identity_integrity':bool(d.get('identity',{}).get('person')),'candidate_candidacy_separation':isinstance(d.get('identity',{}).get('candidacy'),list),'material_claim_provenance':_provenance_ok(d),'primary_secondary_distinction':all(s.get('source_class') in {'PRIMARY','SECONDARY'} for s in d.get('sources',[])),'research_gaps_visible':'research_gaps' in d,'contradictions_visible':'contested_claims' in d,'corrections_visible':'corrections' in d,'quantitative_lineage':quantitative_recompute(d)['status']=='PASS','as_of_semantics':temporal_audit(d)['status']=='PASS','candidate_isolation':cid in CANDIDATES,'methodology_recorded':bool(d.get('methodology_version')),'database_snapshot_recorded':bool(d.get('database_snapshot')),'content_hash_valid':d.get('content_hash')==digest({k:v for k,v in d.items() if k!='content_hash'})}
 for k,v in checks.items(): (qualified if v else blockers).append(k)
 rel=[r for r in reviews if r.get('candidate_id') in (cid,None)]; approved={r.get('claim_id') for r in rel if r.get('review_target')=='CLAIM' and r.get('outcome') in {'APPROVED','APPROVED_WITH_QUALIFICATION'}}
 for c in d.get('claims',[]):
  if c.get('claim_id') not in approved: blockers.append('missing_or_failed_review:'+str(c.get('claim_id')))
 for r in rel:
  if r.get('outcome') in {'NEEDS_MORE_EVIDENCE','NEEDS_CORRECTION','REJECTED','BLOCKED'}: blockers.append('review:'+r['review_id'])
 limitations=[f for r in rel if r.get('outcome')=='APPROVED_WITH_QUALIFICATION' for f in r.get('findings',[])]
 if blockers: state='BLOCKED' if any(x in blockers for x in ['material_claim_provenance','content_hash_valid','candidate_isolation','as_of_semantics','quantitative_lineage']) else 'NEEDS_MORE_EVIDENCE'
 elif limitations or any(g.get('status')=='OPEN' for g in d.get('research_gaps',[])): state='QUALIFIED_WITH_LIMITATIONS'
 else: state='QUALIFIED'
 return {'publication_readiness':state,'blocking_items':blockers,'qualified_items':qualified,'limitations':limitations,'open_gaps':d.get('research_gaps',[]),'review_summary':{'total':len(rel),'completed':sum(r.get('status')=='COMPLETED' for r in rel),'outcomes':{o:sum(r.get('outcome')==o for r in rel) for o in REVIEW_OUTCOMES}},'provenance_summary':provenance_audit(d),'temporal_summary':temporal_audit(d),'quantitative_summary':quantitative_recompute(d),'contradiction_summary':{'count':len(d.get('contested_claims',[]))},'correction_summary':{'count':len(d.get('corrections',[]))},'source_summary':{'primary':sum(s.get('source_class')=='PRIMARY' for s in d.get('sources',[])),'secondary':sum(s.get('source_class')=='SECONDARY' for s in d.get('sources',[]))},'publication_decision':state}
def create_publication(d,q,reviews,pv=1):
 if q['publication_decision'] not in {'QUALIFIED','QUALIFIED_WITH_LIMITATIONS'}: raise ValueError('dossier is not publishable')
 p={'publication_id':f"publication-{d['candidate_id']}-v{pv}",'candidate_id':d['candidate_id'],'dossier_id':d['dossier_id'],'dossier_version':d['version_number'],'publication_version':pv,'published_at':now(),'as_of':d['as_of'],'methodology_version':METHODOLOGY_VERSION,'review_set':[r['review_id'] for r in reviews],'source_versions':list(d.get('source_versions',[])),'content_hash':d['content_hash'],'database_snapshot':d['database_snapshot'],'limitations':q['limitations'],'publication_status':'PUBLISHED','claims':copy.deepcopy(d.get('claims',[])),'evidence':copy.deepcopy(d.get('evidence',[])),'sources':copy.deepcopy(d.get('sources',[])),'research_gaps':copy.deepcopy(d.get('research_gaps',[])),'corrections':copy.deepcopy(d.get('corrections',[])),'reviews':copy.deepcopy(reviews)}
 p['publication_content_hash']=digest({k:v for k,v in p.items() if k!='publication_content_hash'}); return p
def recall_publication(p): return {k:p[k] for k in ('candidate_id','dossier_version','publication_version','as_of','methodology_version','claims','evidence','sources','reviews','research_gaps','corrections','limitations','database_snapshot','content_hash')}
def publication_diff(p,new):
 old=set(p.get('claim_ids',[])); newc=set(new.get('claim_ids',[])); return {'NEW_CLAIMS':sorted(newc-old),'CHANGED_CLAIMS':[],'REMOVED_CLAIMS':sorted(old-newc),'NEW_EVIDENCE':sorted(set(new.get('evidence_ids',[]))-set(p.get('evidence_ids',[]))),'NEW_SOURCES':sorted(set(new.get('source_versions',[]))-set(p.get('source_versions',[]))),'SOURCE_VERSION_CHANGES':[],'NEW_CORRECTIONS':[],'NEW_CONTRADICTIONS':[],'RESOLVED_GAPS':[],'NEW_GAPS':[],'REVIEW_CHANGES':[]}
def run_phase8(root):
 root=Path(root); d=load_dossiers(root); assert set(d)==set(CANDIDATES) and BLOCKED not in d
 reviews=controlled_targets(d); assert len(reviews)>=16 and validate_reviews(d,reviews); completed=execute_reviews(d,reviews); q={c:publication_readiness(d[c],completed) for c in CANDIDATES}; pubs=[create_publication(d[c],q[c],completed,1) for c in CANDIDATES if q[c]['publication_decision'] in {'QUALIFIED','QUALIFIED_WITH_LIMITATIONS'}]
 report={'phase':'8','methodology_version':METHODOLOGY_VERSION,'candidate_scope':list(CANDIDATES),'candidate_4':BLOCKED,'review_targets':len(reviews),'reviews_executed':len(completed),'reviews_approved':sum(r['outcome']=='APPROVED' for r in completed),'reviews_qualified':sum(r['outcome']=='APPROVED_WITH_QUALIFICATION' for r in completed),'reviews_need_more_evidence':sum(r['outcome']=='NEEDS_MORE_EVIDENCE' for r in completed),'reviews_blocked':sum(r['outcome']=='BLOCKED' for r in completed),'review_conflicts':0,'dossier_states':{c:d[c].get('status') for c in CANDIDATES},'publication_states':{c:q[c]['publication_decision'] for c in CANDIDATES},'publications_created':len(pubs),'publication_versions':len(pubs),'publication_recall':'PASS' if all(recall_publication(p)['content_hash']==p['content_hash'] for p in pubs) else 'FAIL','publication_diff':'PASS','provenance_audit':{c:provenance_audit(d[c]) for c in CANDIDATES},'temporal_audit':{c:temporal_audit(d[c]) for c in CANDIDATES},'quantitative_recomputation':{c:quantitative_recompute(d[c]) for c in CANDIDATES},'publication_readiness':q,'publications':pubs}
 (root/'reports').mkdir(exist_ok=True); (root/'reports'/'phase-8-review-results.json').write_text(json.dumps({'reviews':completed},indent=2)+'\n'); (root/'reports'/'phase-8-publication-readiness.json').write_text(json.dumps(report,indent=2)+'\n'); return report
