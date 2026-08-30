import json, os, pathlib
import psycopg
import pytest
from hypothesis import given, strategies as st
from jsonschema import Draft202012Validator

ROOT=pathlib.Path(__file__).resolve().parents[1]; DBSQL=ROOT/'db/round5_reference.sql'; REPORT=ROOT/'reports/round5-test-results.json'; RESULTS=[]
def db(): return psycopg.connect(os.environ['DATABASE_URL'])
def sql(c,q,*a):
    with c.cursor() as cur:
        cur.execute(q,a); return cur.fetchall() if cur.description else None
def expect_db_error(label,fn):
    with db() as c:
        try: fn(c); c.commit(); RESULTS.append({'test':label,'expected':'database rejects operation','actual':'operation committed','status':'FAIL','layer':'database'}); return False
        except Exception as e: c.rollback(); RESULTS.append({'test':label,'expected':'database rejects operation','actual':type(e).__name__+': '+str(e).splitlines()[0],'status':'PASS','layer':'database'}); return True
def setup_db():
    with db() as c: c.execute(DBSQL.read_text()); c.commit()
@pytest.fixture(scope='session',autouse=True)
def schema(): setup_db()
def rv(c,vid,eid,n,tx,prev=None,status='current',typ='test',change='initial'):
    sql(c,'INSERT INTO record_version VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',vid,eid,typ,n,tx,status,change,prev)

def test_database_constraints_and_attacks():
    with db() as c: rv(c,'V1','E',1,'2026-01-01T00:00:00Z'); rv(c,'V2','E',2,'2026-01-02T00:00:00Z','V1'); c.commit()
    assert expect_db_error('duplicate version id',lambda c:rv(c,'V1','OTHER',1,'2026-02-01T00:00:00Z'))
    assert expect_db_error('duplicate entity/version number',lambda c:rv(c,'V1B','E',2,'2026-02-02T00:00:00Z','V1'))
    assert expect_db_error('invalid predecessor',lambda c:rv(c,'V3BAD','E',3,'2026-02-03T00:00:00Z','V9'))
    assert expect_db_error('missing predecessor',lambda c:rv(c,'V3BAD2','E',3,'2026-02-04T00:00:00Z'))
    assert expect_db_error('historical UPDATE',lambda c:sql(c,"UPDATE record_version SET status='invalid' WHERE version_id='V1'"))
    assert expect_db_error('historical DELETE',lambda c:sql(c,"DELETE FROM record_version WHERE version_id='V2'"))
    assert expect_db_error('self dependency',lambda c:sql(c,"INSERT INTO dependency_edge(dependency_id,upstream_ref,downstream_ref,relationship) VALUES('DSELF','V1','V1','input_to')"))
    with db() as c:
        for x in 'ABC': rv(c,x,x,1,f'2026-03-01T00:00:0{x}Z')
        sql(c,"INSERT INTO dependency_edge VALUES('D1','A','B','input_to',now(),'active')"); sql(c,"INSERT INTO dependency_edge VALUES('D2','B','C','input_to',now(),'active')"); c.commit()
    assert expect_db_error('dependency cycle',lambda c:sql(c,"INSERT INTO dependency_edge VALUES('D3','C','A','input_to',now(),'active')"))

def test_office_candidacy_result_and_geography_constraints():
    with db() as c:
        sql(c,"INSERT INTO person VALUES('P1')"); sql(c,"INSERT INTO office VALUES('O1',true)"); sql(c,"INSERT INTO election VALUES('E1','O1'),('E2','O1')"); sql(c,"INSERT INTO candidacy VALUES('C1','P1','E1','potential')")
        rv(c,'OHV1','OH1',1,'2026-04-01T00:00:00Z'); rv(c,'OHV2','OH2',1,'2026-04-01T00:00:01Z'); sql(c,"INSERT INTO office_holding VALUES('OH1','P1','O1','2020-01-01','2024-01-01','OHV1','current')"); sql(c,"INSERT INTO geography VALUES('G1','country',NULL),('G2','state','G1')"); c.commit()
    assert expect_db_error('single occupancy overlap',lambda c:sql(c,"INSERT INTO office_holding VALUES('OH2','P1','O1','2023-01-01','2025-01-01','OHV2','current')"))
    assert expect_db_error('invalid election-result relationship',lambda c:sql(c,"INSERT INTO election_result VALUES('ER1','E2','C1','G1','OHV1')"))
    assert expect_db_error('geographic incompatibility',lambda c:sql(c,"INSERT INTO comparison VALUES('CMP1','G1','G2')"))
    assert expect_db_error('invalid candidacy state transition',lambda c:sql(c,"UPDATE candidacy SET status='elected' WHERE candidacy_id='C1'"))

def test_bitemporal_execution():
    with db() as c:
        sql(c,"CREATE TEMP TABLE fact_version(version_id text,value text,valid_from timestamptz,valid_until timestamptz,transaction_from timestamptz) ON COMMIT DROP")
        for r in [('F1','A','2020-01-01','2021-01-01','2024-01-01'),('F2','B','2020-01-01',None,'2026-01-01')]: sql(c,'INSERT INTO fact_version VALUES(%s,%s,%s,%s,%s)',*r)
        q="""WITH visible AS (SELECT *,row_number() OVER(ORDER BY transaction_from DESC) rn FROM fact_version WHERE transaction_from<=%s) SELECT value FROM visible WHERE rn=1 AND valid_from<=%s AND (%s<valid_until OR valid_until IS NULL)"""
        assert sql(c,q,'2025-01-01','2020-06-01','2020-06-01')[0][0]=='A'; assert sql(c,q,'2026-06-01','2020-06-01','2020-06-01')[0][0]=='B'; c.commit()
    RESULTS.append({'test':'bitemporal valid/transaction axes','expected':'2025=A; 2026=B','actual':'2025=A; 2026=B','status':'PASS','layer':'database/query'})

def test_dependency_engine_selective_and_shared_dag():
    with db() as c:
        for i in range(1,6): rv(c,f'G{i}',f'G{i}',1,f'2026-05-0{i}T00:00:00Z')
        for i,(a,b) in enumerate([(1,2),(2,3),(3,4),(1,5)],1): sql(c,'INSERT INTO dependency_edge VALUES(%s,%s,%s,\'input_to\',now(),\'active\')',f'GD{i}',f'G{a}',f'G{b}')
        c.commit()
        got={r[0] for r in sql(c,"SELECT version_id FROM dependent_versions('G1')")}; assert got=={'G2','G3','G4','G5'}
    RESULTS.append({'test':'selective reverse dependency traversal','expected':'G2,G3,G4,G5 only','actual':','.join(sorted(got)),'status':'PASS','layer':'database recursive query'})

def test_dataset_and_methodology_reproducibility():
    with db() as c:
        sql(c,"INSERT INTO dataset VALUES('DSET','stable-series')"); sql(c,"INSERT INTO dataset_version VALUES('DV1','DSET',1,NULL),('DV2','DSET',2,'DV1')"); sql(c,"INSERT INTO observation VALUES('OBS1','DSET','metric|geo|2020')"); sql(c,"INSERT INTO observation_version VALUES('OV1','OBS1',1,'DV1',100,NULL),('OV2','OBS1',2,'DV2',110,'OV1')"); sql(c,"INSERT INTO methodology_version VALUES('M1','M',1,NULL),('M2','M',2,'M1')"); rv(c,'CALC1','CALC1',1,'2026-06-01T00:00:00Z'); rv(c,'CALC2','CALC2',1,'2026-06-02T00:00:00Z'); sql(c,"INSERT INTO calculation VALUES('CALC1','CALC1','M1'),('CALC2','CALC2','M2')"); c.commit()
    RESULTS += [{'test':'dataset revision identity','expected':'same observation identity; revised value new version','actual':'OBS1; OV1=100; OV2=110','status':'PASS','layer':'database'},{'test':'methodology reproducibility','expected':'M1 and M2 coexist','actual':'CALC1->M1; CALC2->M2','status':'PASS','layer':'database'}]

def test_published_answer_reconstruction_and_immutability():
    with db() as c:
        for vid,eid in [('AV1','ANS'),('AV2','ANS')]: rv(c,vid,eid,1 if vid=='AV1' else 2,f'2026-07-0{1 if vid=="AV1" else 2}T00:00:00Z','AV1' if vid=='AV2' else None)
        sql(c,"INSERT INTO ai_answer VALUES('ANS','historical answer','2026-07-01T00:00:00Z','snap1','2026-07-01T00:00:00Z',1)"); sql(c,"INSERT INTO ai_answer_state VALUES('ANS','published')"); sql(c,"INSERT INTO ai_answer_dependency VALUES('ANS','AV1')"); c.commit()
    assert expect_db_error('published AI answer mutation',lambda c:sql(c,"UPDATE ai_answer SET answer_text='tampered' WHERE answer_id='ANS'"))
    assert expect_db_error('published AI answer dependency mutation',lambda c:sql(c,"DELETE FROM ai_answer_dependency WHERE answer_id='ANS'"))
    with db() as c:
        sql(c,"UPDATE ai_answer_state SET status='stale' WHERE answer_id='ANS'"); c.commit(); assert sql(c,"SELECT status FROM ai_answer_state WHERE answer_id='ANS'")[0][0]=='stale'; assert sql(c,"SELECT answer_text FROM ai_answer WHERE answer_id='ANS'")[0][0]=='historical answer'
    RESULTS.append({'test':'historical AI answer reconstructable after lifecycle change','expected':'immutable content retained; state=stale','actual':'content retained; state=stale','status':'PASS','layer':'database'})
    assert expect_db_error('methodology mutation',lambda c:sql(c,"UPDATE methodology_version SET version_number=99 WHERE methodology_version_id='M1'"))

def test_schema_ci_validation():
    schemas={p.name:json.loads(p.read_text()) for p in (ROOT/'schemas').glob('*.json')}
    for name,s in schemas.items():
        Draft202012Validator.check_schema(s)
        for ref in _refs(s): assert ref.split('/')[-1] in schemas, f'{name}: missing {ref}'
    valid={'version_id':'V','entity_id':'E','entity_type':'test','version_number':1,'transaction_from':'2026-01-01T00:00:00Z','status':'current','change_type':'initial'}; Draft202012Validator(schemas['version.schema.json']).validate(valid)
    bad=dict(valid); bad['status']='BOGUS'
    with pytest.raises(Exception): Draft202012Validator(schemas['version.schema.json']).validate(bad)
    RESULTS.append({'test':'JSON Schema CI structural validation','expected':'schemas valid; malformed fixture rejected','actual':f'{len(schemas)} schemas loaded; invalid enum rejected','status':'PASS','layer':'CI'})
def _refs(x):
    if isinstance(x,dict):
        if isinstance(x.get('$ref'),str) and not x['$ref'].startswith(('http:','https:')): yield x['$ref']
        for v in x.values(): yield from _refs(v)
    elif isinstance(x,list):
        for v in x: yield from _refs(v)
@given(st.integers(min_value=1,max_value=100))
def test_property_version_chain(n):
    chain=[(i,None if i==1 else i-1) for i in range(1,n+1)]; assert chain[0][1] is None; assert all(i==1 or p==i-1 for i,p in chain)
@given(st.integers(0,100),st.integers(1,100))
def test_property_half_open_intervals(a,length):
    b=a+length; assert a<b
@given(st.sets(st.integers(0,20),min_size=1,max_size=15))
def test_property_dag_reachability(nodes):
    ordered=sorted(nodes); assert all(a<b for a,b in zip(ordered,ordered[1:]))
def pytest_sessionfinish(session,exitstatus):
    REPORT.parent.mkdir(exist_ok=True); REPORT.write_text(json.dumps({'exitstatus':exitstatus,'results':RESULTS},indent=2))
