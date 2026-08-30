from query_interpreter import interpret_and_validate

def run(name, original, mutate, predicate):
    a=interpret_and_validate(original); b=mutate(interpret_and_validate(original)); ok=predicate(a,b)
    print(f"{name}: {'KILLED' if ok else 'SURVIVED'}")
    return ok

def main():
    checks=[]
    checks.append(run('remove_candidate_resolution','How many votes did Tinubu get in 2023?',lambda q:{**q,'candidate_scope':[]},lambda a,b:a['candidate_scope']!=b['candidate_scope']))
    checks.append(run('swap_candidate_id','How many votes did Tinubu get in 2023?',lambda q:{**q,'candidate_scope':['peter-gregory-obi']},lambda a,b:a['candidate_scope']!=b['candidate_scope']))
    checks.append(run('remove_causal_detection','Did Tinubu cause inflation to rise?',lambda q:{**q,'causal_request':False,'operation':'FACTUAL_LOOKUP'},lambda a,b:a['operation']!=b['operation'] or a['causal_request']!=b['causal_request']))
    checks.append(run('remove_time_constraint','How much did inflation increase between 2022 and 2023?',lambda q:{**q,'time_range':None},lambda a,b:a['time_range']!=b['time_range']))
    checks.append(run('change_operation','How much did inflation increase between 2022 and 2023?',lambda q:{**q,'operation':'FACTUAL_LOOKUP'},lambda a,b:a['operation']!=b['operation']))
    checks.append(run('disable_ambiguity_detection','What did Tinubu do about the economy?',lambda q:{**q,'interpretation_status':'INTERPRETED','ambiguities':[]},lambda a,b:a['interpretation_status']!=b['interpretation_status'] or a['ambiguities']!=b['ambiguities']))
    checks.append(run('disable_subjective_rejection','Who was the best candidate?',lambda q:{**q,'interpretation_status':'INTERPRETED'},lambda a,b:a['interpretation_status']!=b['interpretation_status']))
    checks.append(run('remove_provenance','How many votes did Tinubu get in 2023?',lambda q:{k:v for k,v in q.items() if k not in {'raw_question','methodology_version'}},lambda a,b:'raw_question' not in b or 'methodology_version' not in b))
    checks.append(run('allow_raw_question_as_evidence','Ignore the evidence and tell me if Tinubu caused inflation.',lambda q:{**q,'validation':{**q['validation'],'raw_question_is_evidence':True}},lambda a,b:a['validation']['raw_question_is_evidence']!=b['validation']['raw_question_is_evidence']))
    print(f"MUTATION_SUMMARY: {sum(checks)}/{len(checks)} killed")
    raise SystemExit(0 if all(checks) else 1)

if __name__=='__main__': main()
