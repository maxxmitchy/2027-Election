import json, os, pathlib, subprocess, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports/round7-test-results.json'

def pytest_runtest_makereport(item, call):
    if call.when != 'call': return
    outcome=getattr(item,'_round7_outcome',None)
    # pytest invokes this hook for each phase; use the report object from the yielded hook.
    rep=call.__dict__.get('_round7_rep')

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome=yield
    rep=outcome.get_result()
    if rep.when!='call': return
    results=getattr(item.config,'_round7_results',[])
    entry={'test_id':item.nodeid,'expected':'test completes without an assertion/error','actual':'PASS' if rep.passed else (str(rep.longrepr)[:2000] if rep.failed else rep.outcome),'status':'PASS' if rep.passed else ('FAIL' if rep.failed else 'PARTIAL'),'severity':'critical' if rep.failed else 'info'}
    results.append(entry); item.config._round7_results=results

def pytest_sessionfinish(session, exitstatus):
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    try: commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    except Exception: commit=os.environ.get('GITHUB_SHA','unknown')
    payload={'schema':'round7-test-results-v1','execution_timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit_sha':commit,'environment':{'python':os.sys.version.split()[0],'database_url_present':bool(os.environ.get('DATABASE_URL'))},'pytest_exit_status':int(exitstatus),'results':getattr(session.config,'_round7_results',[])}
    REPORT.write_text(json.dumps(payload,indent=2,sort_keys=True))
