import json, os, pathlib, subprocess, datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports' / 'round7-test-results.json'

def pytest_sessionfinish(session, exitstatus):
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    try:
        commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    except Exception:
        commit = os.environ.get('GITHUB_SHA','unknown')
    payload = {
        'schema': 'round7-test-results-v1',
        'execution_timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'commit_sha': commit,
        'environment': {
            'python': os.sys.version.split()[0],
            'database_url_present': bool(os.environ.get('DATABASE_URL')),
        },
        'pytest_exit_status': int(exitstatus),
        'results': getattr(session.config, '_round7_results', []),
    }
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True))
