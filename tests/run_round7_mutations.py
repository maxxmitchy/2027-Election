import hashlib,json,os,pathlib,shutil,subprocess,tempfile,datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]; BASE=ROOT/'db/round5_reference.sql'; EXT=ROOT/'db/round7_extensions.sql'; SCHEMA_DIR=ROOT/'schemas'; OUT=ROOT/'reports/round7-mutation-results.json'
MUTATIONS={
'M1':('remove entity/version UNIQUE constraint','tests/test_round7.py::test_unique_entity_version',lambda s:s.replace(', UNIQUE(entity_id, version_number)','',1)),
'M2':('disable historical immutability trigger','tests/test_round7.py::test_historical_immutability',lambda s:s.replace('CREATE TRIGGER version_immutable BEFORE UPDATE OR DELETE ON record_version FOR EACH ROW EXECUTE FUNCTION deny_version_mutation();','-- MUTATION M2: trigger disabled',1)),
'M3':('remove office single-occupancy exclusion constraint','tests/test_round7.py::test_office_overlap_rejected',lambda s:s.replace("ALTER TABLE office_holding ADD CONSTRAINT office_single_occupancy_excl EXCLUDE USING gist(office_id WITH =,tstzrange(valid_from,coalesce(valid_until,'infinity'),'[)') WITH &&) WHERE(state NOT IN ('invalid','superseded'));","-- MUTATION M3: exclusion disabled",1)),
'M4':('break predecessor validation','tests/test_round7.py::test_predecessor_validation',lambda s:s.replace('p.version_number<>NEW.version_number-1','p.version_number<>NEW.version_number-2',1)),
'M5':('break reverse dependency traversal','tests/test_round7.py::test_dependency_reverse_closure',lambda s:s.replace('SELECT v FROM walk WHERE v<>seed','SELECT seed FROM walk WHERE v<>seed',1)),
'M6':('leak transaction-future information through bitemporal view','tests/test_round7_bitemporal.py::test_bitemporal_view_snapshot',lambda s:s.replace('CREATE VIEW version_bitemporal AS SELECT v.*,lead(transaction_from) OVER(PARTITION BY entity_id ORDER BY version_number) AS transaction_to FROM record_version v;','CREATE VIEW version_bitemporal AS SELECT v.*,NULL::timestamptz AS transaction_to FROM record_version v;',1)),
'M7':('disable published AI dependency completeness trigger','tests/test_round7.py::test_ai_full_reconstruction_and_completeness',None),
'M8':('break JSON Schema external $ref resolution','tests/test_round7.py::test_schema_validation_and_ref_resolution',None)}

def mutate_file(text,mid):
    if mid=='M7': return text.replace('CREATE TRIGGER ai_answer_completeness_guard BEFORE UPDATE OF status ON ai_answer_state FOR EACH ROW EXECUTE FUNCTION enforce_published_ai_completeness();','-- MUTATION M7: completeness trigger disabled',1)
    return MUTATIONS[mid][2](text) if MUTATIONS[mid][2] else text

def run_test(testid,base,ext,sd):
    env=os.environ.copy(); env.update(ROUND7_BASE_SCHEMA=str(base),ROUND7_EXTENSION_SCHEMA=str(ext),ROUND7_SCHEMA_DIR=str(sd))
    return subprocess.run(['pytest','-q',testid],cwd=ROOT,env=env,text=True,capture_output=True)

def mutate_schema_dir(src,dst):
    shutil.copytree(src,dst); target=next(dst.glob('*.json')); obj=json.loads(target.read_text()); obj.setdefault('properties',{})['round7_ref_probe']={'$ref':'missing-round7.schema.json'}; target.write_text(json.dumps(obj,indent=2))

def main():
    OUT.parent.mkdir(exist_ok=True); results=[]
    with tempfile.TemporaryDirectory(prefix='round7-mut-') as td:
        td=pathlib.Path(td)
        for mid,(defect,testid,_) in MUTATIONS.items():
            mb=td/f'{mid}-base.sql'; me=td/f'{mid}-ext.sql'; mb.write_text(mutate_file(BASE.read_text(),mid)); me.write_text(mutate_file(EXT.read_text(),mid)); sd=td/f'{mid}-schemas'; (mutate_schema_dir(SCHEMA_DIR,sd) if mid=='M8' else shutil.copytree(SCHEMA_DIR,sd)); r=run_test(testid,mb,me,sd); sensitive=r.returncode!=0
            results.append({'mutation_id':mid,'defect_introduced':defect,'expected_test':testid,'actual_exit_code':r.returncode,'sensitivity':'YES' if sensitive else 'NO','evidence':(r.stdout+r.stderr)[-4000:]})
    results.append({'baseline_restoration':'PASS','base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'extension_sha256':hashlib.sha256(EXT.read_bytes()).hexdigest()}); OUT.write_text(json.dumps({'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results},indent=2)); print(json.dumps(results,indent=2)); raise SystemExit(0 if all(x.get('sensitivity')=='YES' for x in results if 'mutation_id' in x) else 1)
if __name__=='__main__': main()
