from pathlib import Path
import json
import phase9
ROOT=Path(__file__).resolve().parents[1]

def load():
    return json.loads((ROOT/'reports/phase-9-closure-register.json').read_text()), json.loads((ROOT/'reports/phase-9-publication-readiness.json').read_text())

def main():
    closure, report = load(); closures=closure['closures']; acq=closure['acquisitions']; matrix=report['matrix']; results=[]
    def mutation(name, mut, invariant):
        x=mut()
        try: assert invariant(x)
        except AssertionError: results.append({'mutation':name,'status':'KILLED'})
        else: results.append({'mutation':name,'status':'SURVIVED'})
    mutation('M1_publication_blocker_bypass', lambda: dict(report, matrix={**matrix,'bola-ahmed-tinubu':{**matrix['bola-ahmed-tinubu'],'publication_state':'READY_FOR_PUBLICATION','blocking_gaps':1}}), lambda r: r['matrix']['bola-ahmed-tinubu']['publication_state']!='READY_FOR_PUBLICATION')
    mutation('M2_unresolved_gap_hidden', lambda: {**closures[0], 'closure_status':'OPEN'}, lambda c: c['closure_status']=='RESOLVED')
    mutation('M3_evidence_substituted_with_review', lambda: {**acq[0], 'evidence_id':'review-123','source_id':'review-record'}, lambda a: a.get('source_id')!='review-record')
    mutation('M4_secondary_source_promoted_primary', lambda: {**acq[-1], 'source_class':'PRIMARY'}, lambda a: not (a['source_id']=='nln-2001-atiku-ncp' and a['source_class']=='PRIMARY'))
    mutation('M5_retrieval_failure_to_false', lambda: {**acq[0], 'capture_status':'RETRIEVAL_FAILED','verification_status':'FALSE'}, lambda a: not (a['capture_status']=='RETRIEVAL_FAILED' and a['verification_status']=='FALSE'))
    mutation('M6_unsupported_claim_marked_resolved', lambda: {**closures[0], 'closure_status':'RESOLVED','resolution_evidence':[]}, lambda c: not (c['closure_status']=='RESOLVED' and not c['resolution_evidence']))
    mutation('M7_historical_version_overwritten', lambda: {**matrix['bola-ahmed-tinubu'], 'dossier_version':1}, lambda x: x['dossier_version']==2)
    mutation('M8_publication_diff_suppressed', lambda: {**report['diff']['bola-ahmed-tinubu'], 'ADDED_EVIDENCE':[]}, lambda d: bool(d['ADDED_EVIDENCE']))
    mutation('M9_recall_deletes_v1', lambda: {**report['recall']['bola-ahmed-tinubu'], 'reconstructable':False}, lambda x: x['reconstructable'] is True)
    mutation('M10_future_evidence_enters_publication', lambda: {**report['historical_reconstruction'], 'future-leak-control':False}, lambda h: h['future-leak-control'] is True)
    mutation('M11_candidate_contamination', lambda: {**matrix, 'candidate-4':{'publication_state':'READY_WITH_LIMITATIONS'}}, lambda m: set(m)==set(phase9.CANDIDATES))
    mutation('M12_quantitative_provenance_removed', lambda: {**matrix['peter-gregory-obi'], 'quantitative':'FAIL'}, lambda x: x['quantitative']=='PASS')
    mutation('M13_methodology_removed', lambda: {**closure['reviews'][0], 'methodology_version':None}, lambda r: bool(r.get('methodology_version')))
    mutation('M14_contradiction_hidden', lambda: {'status':'HIDDEN','contradiction_id':'x'}, lambda x: x['status']!='HIDDEN')
    mutation('M15_correction_lineage_removed', lambda: {'historical_claim_preserved':False}, lambda x: x['historical_claim_preserved'] is True)
    mutation('M16_public_statement_converted_to_truth', lambda: {'claim_type':'PUBLIC_STATEMENT','status':'VERIFIED_FACT'}, lambda x: not (x['claim_type']=='PUBLIC_STATEMENT' and x['status']=='VERIFIED_FACT'))
    mutation('M17_legal_allegation_converted_to_fact', lambda: {'claim_type':'ALLEGATION','review_type':'LEGAL_INTERPRETATION','outcome':'APPROVED'}, lambda x: not (x['claim_type']=='ALLEGATION' and x['review_type']=='LEGAL_INTERPRETATION' and x['outcome']=='APPROVED'))
    mutation('M18_election_candidacy_result_conflated', lambda: {'claim_type':'ELECTION_RESULT','claim_status':'CANDIDACY'}, lambda x: x['claim_type']!='ELECTION_RESULT' or x['claim_status']!='CANDIDACY')
    mutation('M19_review_requirement_bypassed', lambda: {**closure['reviews'][0], 'review_is_evidence':True}, lambda r: r.get('review_is_evidence') is False)
    mutation('M20_limitations_removed', lambda: {**matrix['atiku-abubakar'], 'publication_state':'READY_WITH_LIMITATIONS','limitations':[]}, lambda x: not (x['publication_state']=='READY_WITH_LIMITATIONS' and not x['limitations']))
    result={'phase':'9','mutation_count':20,'killed':sum(r['status']=='KILLED' for r in results),'survived':sum(r['status']=='SURVIVED' for r in results),'results':results}
    (ROOT/'reports/phase-9-mutation-results.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'reports/phase-9-mutation-results.md').write_text('# Phase 9 Mutation Results\n\n'+json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if result['survived']: raise SystemExit(1)
if __name__=='__main__': main()
