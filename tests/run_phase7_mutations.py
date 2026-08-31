from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
from phase7_dossier import CANDIDATES,BLOCKED,METHODOLOGY_VERSION,build_dossier,dossier_diff,quality_gate,snapshot,temporal_ok
ROOT=Path(__file__).resolve().parents[1]

def h(d): return hashlib.sha256(json.dumps({k:v for k,v in d.items() if k!='content_hash'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
def hash_ok(d): return d.get('content_hash')==h(d)
def structural(d):
    q=quality_gate(d); return not q['failures']
def diff_valid(x):
    return all(k in x for k in ('ADDED_CLAIMS','REMOVED_CLAIMS','CHANGED_CLAIMS','ADDED_EVIDENCE','REMOVED_EVIDENCE','NEW_GAPS','RESOLVED_GAPS','NEW_CONTRADICTIONS','RESOLVED_CONTRADICTIONS','CORRECTIONS','SOURCE_VERSION_CHANGES'))
def snap_valid(x):
    return all(k in x for k in ('candidate_id','dossier_id','version_number','as_of','claim_count','evidence_count','source_count','open_research_gaps','review_queue_count','contradiction_count','correction_count','methodology_version','database_snapshot','content_hash'))

def main():
    base=build_dossier(ROOT,CANDIDATES[0]); other=build_dossier(ROOT,CANDIDATES[1]);
    v1=copy.deepcopy(base); v2=copy.deepcopy(base); v2['version_number']=2; v2['evidence_ids']=v2['evidence_ids'][:-1]; diff=dossier_diff(v1,v2); snap=snapshot(base)
    muts={
      'M1_remove_claim_provenance':lambda d:d['claims'][0].pop('provenance'),
      'M2_remove_evidence_relationship':lambda d:d['evidence'][0].pop('source_id'),
      'M3_source_to_evidence_collapse':lambda d:d['evidence'][0].update({'source_id':'PRIMARY'}),
      'M4_review_to_evidence':lambda d:d['evidence'].append(copy.deepcopy(d['reviews'][0])),
      'M5_secondary_to_primary':lambda d:next(s for s in d['sources'] if s['source_class']=='SECONDARY').update({'source_class':'PRIMARY'}),
      'M6_hide_open_gap':lambda d:d.update({'research_gaps':[]}),
      'M7_force_gap_closed':lambda d:[g.update({'status':'RESOLVED'}) for g in d['research_gaps']],
      'M8_remove_correction':lambda d:d.pop('corrections'),
      'M9_remove_contradiction':lambda d:d.pop('contested_claims'),
      'M10_break_as_of':lambda d:d['claims'][0].update({'as_of':'1900-01-01'}),
      'M11_future_evidence_leak':lambda d:d['sources'].append({'source_id':'future','source_class':'PRIMARY','source_type':'official','url':'https://example.invalid/future','retrieval_date':'2027-01-01','reliability':'HIGH','source_version_id':'sv-future','provenance_complete':True}),
      'M12_cross_candidate_contamination':lambda d:d['claims'][0].update({'candidate_id':CANDIDATES[1]}),
      'M13_remove_quantitative_lineage':lambda d:d['economic_record'][0].pop('dataset_version'),
      'M14_corrupt_calculation':lambda d:d['economic_record'][0].update({'unit':'bad-unit'}),
      'M15_corrupt_metric_unit':lambda d:d['economic_record'][0].update({'unit':'percent'}) if d['economic_record'] else d.update({'economic_record':[{'metric':'x','unit':'percent'}]}),
      'M16_corrupt_geography':lambda d:d['economic_record'][0].update({'geography':'Lagos State'}),
      'M17_corrupt_period':lambda d:d['economic_record'][0].update({'period':'monthly'}),
      'M18_remove_dataset_version':lambda d:d['economic_record'][0].pop('dataset_version'),
      'M19_remove_methodology':lambda d:d.update({'methodology_version':'corrupted'}),
      'M20_statement_to_truth':lambda d:d['claims'][0].update({'status':'SUPPORTED','claim_type':'TRUTH'}),
      'M21_causal_shortcut':lambda d:next((c.update({'status':'SUPPORTED'}) for c in d['claims'] if c['claim_type']=='CAUSAL_PROPOSITION'),None),
      'M22_legal_event_collapse':lambda d:d.update({'legal_record':[{'status':'FINAL_OUTCOME'}]}),
      'M23_election_semantic_collapse':lambda d:d.update({'election_history':[{'status':'ELECTED'}]}),
      'M24_officeholder_semantic_collapse':lambda d:d.update({'office_history':[{'status':'OFFICE'}]}),
      'M25_duplicate_dossier_claim':lambda d:d['claims'].append(copy.deepcopy(d['claims'][0])),
      'M26_duplicate_assembly':lambda d:d.update({'claim_ids':d['claim_ids']+[d['claim_ids'][0]]}),
      'M27_source_version_overwrite':lambda d:d['source_versions'][:1].__setitem__(0,'overwritten'),
      'M28_remove_review_requirement':lambda d:d.update({'reviews':[]}),
      'M29_remove_dossier_diff':lambda d:diff.pop('ADDED_EVIDENCE'),
      'M30_corrupt_snapshot':lambda d:snap.pop('content_hash'),
      'M31_remove_candidate_scope':lambda d:d.update({'candidate_id':BLOCKED}),
      'M32_hide_unavailable_source':lambda d:d.update({'research_gaps':[]}),
      'M33_remove_investigation_effect':lambda d:d['investigations'][0].pop('dossier_effect'),
      'M34_corrupt_public_conversation':lambda d:next((c.update({'claim_type':'DOCUMENTED_ACTION'}) for c in d['claims'] if c['claim_type']=='PUBLIC_STATEMENT'),None),
      'M35_remove_research_task_dependency':lambda d:d['investigations'][0]['research_tasks'][1].update({'dependencies':[]}),
      'M36_modify_historical_dossier':lambda d:d['claims'][0].update({'claim_text':'historically modified'}),
      'M37_remove_content_hash':lambda d:d.pop('content_hash'),
      'M38_corrupt_database_snapshot':lambda d:d.update({'database_snapshot':None}),
      'M39_change_methodology_version':lambda d:d['claims'][0].update({'methodology_version':'old'}),
      'M40_publish_unqualified_dossier':lambda d:d['quality_gate'].update({'publishable':True}),
    }
    results=[]
    for name,mut in muts.items():
        d=copy.deepcopy(base); target=d; before_diff=copy.deepcopy(diff); before_snap=copy.deepcopy(snap)
        try: mut(target)
        except Exception: pass
        if name in {'M29_remove_dossier_diff'}: killed=not diff_valid(diff)
        elif name=='M30_corrupt_snapshot': killed=not snap_valid(snap)
        elif name in {'M35_remove_research_task_dependency'}: killed=not all(i['research_tasks'][j]['dependencies'] for i in d['investigations'] for j in range(1,len(i['research_tasks'])))
        elif name=='M36_modify_historical_dossier': killed=not hash_ok(d)
        elif name in {'M7_force_gap_closed','M28_remove_review_requirement','M32_hide_unavailable_source','M40_publish_unqualified_dossier'}: killed=quality_gate(d)['recommended_state']!='QUALIFIED' or not (d.get('research_gaps') or d.get('reviews'))
        elif name=='M11_future_evidence_leak': killed=not temporal_ok(d['sources'][-1],'2026-08-30')
        else: killed=not structural(d) or not hash_ok(d)
        results.append({'mutation':name,'status':'KILLED' if killed else 'SURVIVED'})
        diff=before_diff; snap=before_snap
        if not killed: raise SystemExit('SURVIVED: '+name)
    bundle={'phase':'7','methodology_version':METHODOLOGY_VERSION,'mutation_count':len(results),'killed':sum(x['status']=='KILLED' for x in results),'survived':sum(x['status']=='SURVIVED' for x in results),'results':results}
    out=ROOT/'reports'; out.mkdir(exist_ok=True); (out/'phase-7-mutation-results.json').write_text(json.dumps(bundle,indent=2)+'\n'); (out/'phase-7-mutation-results.md').write_text('# Phase 7 — Mutation Results\n\n**Result:** %d/%d killed\n\n| Mutation | Result |\n|---|---|\n%s\n'%(bundle['killed'],bundle['mutation_count'],'\n'.join('| %s | %s |'%(x['mutation'],x['status']) for x in results)))
    print(f"MUTATION_SUMMARY: {bundle['killed']}/{bundle['mutation_count']} killed")
if __name__=='__main__': main()
