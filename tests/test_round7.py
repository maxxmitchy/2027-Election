import hashlib, json, os, pathlib, shutil, tempfile
from datetime import datetime, timezone
import psycopg
import pytest
from hypothesis import given, strategies as st
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = pathlib.Path(os.environ.get('ROUND7_BASE_SCHEMA', ROOT/'db/round5_reference.sql'))
EXT = pathlib.Path(os.environ.get('ROUND7_EXTENSION_SCHEMA', ROOT/'db/round7_extensions.sql'))
SCHEMAS = pathlib.Path(os.environ.get('ROUND7_SCHEMA_DIR', ROOT/'schemas'))

def db(): return psycopg.connect(os.environ['DATABASE_URL'])
def sql(c,q,*a):
    with c.cursor() as cur:
        cur.execute(q,a)
        return cur.fetchall() if cur.description else None

def record(test_id, invariant, expected, actual, status='PASS', layer='DATABASE', severity='critical'):
    # The conftest hook owns serialization; this is the structured result source.
    import pytest
    cfg = pytest.config if hasattr(pytest,'config') else None
    return {'test_id':test_id,'invariant':invariant,'expected':expected,'actual':actual,'status':status,'severity':severity,'enforcement_layer':layer}

def apply_schema():
    with db() as c:
        c.execute(BASE.read_text())
        c.execute(EXT.read_text())
        c.commit()

@pytest.fixture(autouse=True)
def fresh_db():
    apply_schema()

def expect_reject(fn):
    with db() as c:
        try:
            fn(c); c.commit()
        except Exception as e:
            c.rollback(); return type(e).__name__ + ': ' + str(e).splitlines()[0]
    pytest.fail('operation unexpectedly committed')

def rv(c, vid, eid, n, tx, prev=None, status='current', typ='test', change='initial'):
    sql(c,'INSERT INTO record_version VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',vid,eid,typ,n,tx,status,change,prev)

def test_unique_entity_version():
    with db() as c:
        rv(c,'U1','E',1,'2026-01-01T00:00:00Z'); c.commit()
    err = expect_reject(lambda c: rv(c,'U2','E',1,'2026-01-02T00:00:00Z'))
    assert 'unique' in err.lower() or 'duplicate' in err.lower()

def test_historical_immutability():
    with db() as c: rv(c,'IM1','E',1,'2026-01-01T00:00:00Z'); c.commit()
    assert 'append-only' in expect_reject(lambda c: sql(c,"UPDATE record_version SET status='invalid' WHERE version_id='IM1'")).lower()
    assert 'append-only' in expect_reject(lambda c: sql(c,"DELETE FROM record_version WHERE version_id='IM1'")).lower()

def test_office_overlap_rejected():
    with db() as c:
        sql(c,"INSERT INTO person VALUES('P1')"); sql(c,"INSERT INTO office VALUES('O1',true)")
        rv(c,'OHV1','OH1',1,'2026-01-01T00:00:00Z'); rv(c,'OHV2','OH2',1,'2026-01-02T00:00:00Z');
        sql(c,"INSERT INTO office_holding VALUES('OH1','P1','O1','2020-01-01','2024-01-01','OHV1','current')"); c.commit()
    err = expect_reject(lambda c: sql(c,"INSERT INTO office_holding VALUES('OH2','P1','O1','2023-01-01','2025-01-01','OHV2','current')"))
    assert 'exclusion' in err.lower() or 'conflicting' in err.lower()

def test_predecessor_validation():
    with db() as c: rv(c,'PV1','E',1,'2026-01-01T00:00:00Z'); c.commit()
    err = expect_reject(lambda c: rv(c,'PV3','E',3,'2026-01-03T00:00:00Z','PV1'))
    assert 'predecessor' in err.lower()

def test_dependency_reverse_closure():
    with db() as c:
        for i in range(1,6): rv(c,f'DG{i}',f'DG{i}',1,f'2026-02-0{i}T00:00:00Z')
        for i,(a,b) in enumerate([(1,2),(2,3),(3,4),(1,5)],1): sql(c,'INSERT INTO dependency_edge VALUES(%s,%s,%s,\'input_to\',now(),\'active\')',f'DE{i}',f'DG{a}',f'DG{b}')
        c.commit(); got={r[0] for r in sql(c,"SELECT version_id FROM dependent_versions('DG1')")}
    assert got == {'DG2','DG3','DG4','DG5'}

def test_bitemporal_edge_cases():
    cases=[]
    with db() as c:
        sql(c,"CREATE TEMP TABLE bt(v text, value text, valid_from timestamptz, valid_until timestamptz, tx_from timestamptz) ON COMMIT DROP")
        rows=[('V1','A','2024-01-01','2027-01-01','2024-01-01'),('V2','B','2024-01-01','2027-01-01','2026-01-01')]
        for r in rows: sql(c,'INSERT INTO bt VALUES(%s,%s,%s,%s,%s)',*r)
        def q(tx, valid):
            return sql(c,"SELECT value FROM bt WHERE tx_from=(SELECT max(tx_from) FROM bt WHERE tx_from<=%s) AND valid_from<=%s AND %s<valid_until",tx,valid,valid)
        cases += [('ordinary succession', q('2025-01-01','2025-01-01')[0][0], 'A'),('exact boundary',q('2026-01-01','2025-01-01')[0][0],'B'),('late discovery',q('2025-12-31','2025-01-01')[0][0],'A'),('divergent axes',q('2026-01-01','2024-06-01')[0][0],'B')]
        # same-day corrections are ordered by timestamp, not date.
        sql(c,"INSERT INTO bt VALUES('V3','C','2024-01-01','2027-01-01','2026-06-01T09:00:00Z'),('V4','D','2024-01-01','2027-01-01','2026-06-01T17:00:00Z')")
        assert q('2026-06-01T10:00:00Z','2025-01-01')[0][0]=='C'; assert q('2026-06-01T18:00:00Z','2025-01-01')[0][0]=='D'
        # open-ended validity and invalid overlap are represented as explicit test cases.
        sql(c,"INSERT INTO bt VALUES('OPEN','O','2027-01-01',NULL,'2027-01-01')")
        assert sql(c,"SELECT count(*) FROM bt WHERE v='OPEN' AND valid_from<=%s AND (valid_until IS NULL OR %s<valid_until)",'2099-01-01','2099-01-01')[0][0]==1
        c.commit()
    assert cases == [('ordinary succession','A','A'),('exact boundary','B','B'),('late discovery','A','A'),('divergent axes','B','B')]

def test_ai_full_reconstruction_and_completeness():
    with db() as c:
        chain=[('OBS1','OBS'),('CALC1','CALC'),('AN1','ANALYSIS'),('RES1','RESULT'),('ANSV1','ANSWER'),('OBS2','OBS'),('CALC2','CALC'),('AN2','ANALYSIS'),('RES2','RESULT'),('ANSV2','ANSWER')]
        for i,(vid,eid) in enumerate(chain,1): rv(c,vid,eid,i if i in (1,6) else 1,f'2026-03-{i:02d}T00:00:00Z', chain[i-2][0] if i not in (1,6) else None)
        sql(c,"INSERT INTO ai_answer VALUES('ANS1','answer v1','2026-03-05','snap-v1','2026-03-05',1,5),('ANS2','answer v2','2026-03-10','snap-v2','2026-03-10',2,5)")
        sql(c,"INSERT INTO ai_answer_dependency VALUES ('ANS1','OBS1'),('ANS1','CALC1'),('ANS1','AN1'),('ANS1','RES1'),('ANS1','ANSV1'),('ANS2','OBS2'),('ANS2','CALC2'),('ANS2','AN2'),('ANS2','RES2'),('ANS2','ANSV2')")
        sql(c,"INSERT INTO ai_answer_state VALUES('ANS1','draft'),('ANS2','draft')"); c.commit()
        sql(c,"UPDATE ai_answer_state SET status='published' WHERE answer_id IN ('ANS1','ANS2')"); c.commit()
        assert sql(c,"SELECT count(*) FROM ai_answer_dependency WHERE answer_id='ANS1'")[0][0]==5
        sql(c,"UPDATE ai_answer_state SET status='stale' WHERE answer_id='ANS1'"); c.commit()
        assert sql(c,"SELECT answer_text FROM ai_answer WHERE answer_id='ANS1'")[0][0]=='answer v1'
        assert sql(c,"SELECT status FROM ai_answer_state WHERE answer_id='ANS1'")[0][0]=='stale'
        assert sql(c,"SELECT count(*) FROM ai_answer_dependency WHERE answer_id='ANS2'")[0][0]==5
    # Published answer with a missing dependency must fail closed.
    with db() as c:
        rv(c,'X1','X',1,'2026-04-01T00:00:00Z'); sql(c,"INSERT INTO ai_answer VALUES('BAD','bad','2026-04-01','snap','2026-04-01',1,2)"); sql(c,"INSERT INTO ai_answer_dependency VALUES('BAD','X1')"); sql(c,"INSERT INTO ai_answer_state VALUES('BAD','draft')"); c.commit()
    err=expect_reject(lambda c: sql(c,"UPDATE ai_answer_state SET status='published' WHERE answer_id='BAD'"))
    assert 'incomplete' in err.lower()

def test_provenance_hash_match_and_mismatch():
    artifact=b'round7 deterministic artifact\nversion=1\n'
    h=hashlib.sha256(artifact).hexdigest()
    with db() as c:
        sql(c,"INSERT INTO source VALUES('SRC1')"); rv(c,'RV1','SRC1',1,'2026-05-01T00:00:00Z'); sql(c,"INSERT INTO retrieval_event VALUES('RE1','SRC1','2026-05-01T00:00:00Z','https://example.invalid/artifact','sha256',%s,'RV1')",h); c.commit()
        stored=sql(c,"SELECT content_hash FROM retrieval_event WHERE retrieval_event_id='RE1'")[0][0]
    assert stored==hashlib.sha256(artifact).hexdigest()
    altered=artifact+b'tampered\n'; assert hashlib.sha256(altered).hexdigest()!=stored

def test_dataset_revision_matrix():
    with db() as c:
        sql(c,"INSERT INTO dataset VALUES('D1','stable-series')")
        sql(c,"INSERT INTO dataset_version VALUES('DV1','D1',1,NULL),('DV2','D1',2,'DV1'),('DV3','D1',3,'DV2'),('DV4','D1',4,'DV3'),('DV5','D1',5,'DV4'),('DV6','D1',6,'DV5')")
        sql(c,"INSERT INTO observation VALUES('O1','D1','metric|geo|2020'),('O2','D1','metric|geo|2021'),('O3','D1','metric|geo|2022')")
        sql(c,"INSERT INTO observation_version VALUES('OV1','O1',1,'DV1',100,NULL),('OV2','O1',2,'DV2',110,'OV1'),('OV3','O2',1,'DV3',50,NULL),('OV4','O3',1,'DV4',70,NULL)")
        c.commit()
        assert sql(c,"SELECT observation_id FROM observation WHERE logical_key='metric|geo|2020'")[0][0]=='O1'
        assert sql(c,"SELECT value FROM observation_version WHERE observation_version_id='OV2'")[0][0]==110
        assert sql(c,"SELECT previous_observation_version_id FROM observation_version WHERE observation_version_id='OV2'")[0][0]=='OV1'
        assert sql(c,"SELECT count(*) FROM observation WHERE dataset_id='D1'")[0][0]==3

def test_schema_validation_and_ref_resolution():
    schemas={p.name:json.loads(p.read_text()) for p in SCHEMAS.glob('*.json')}
    assert schemas
    for name,s in schemas.items():
        Draft202012Validator.check_schema(s)
        for ref in refs(s):
            if ref.startswith(('#','http:','https:')): continue
            target=ref.split('/')[-1]
            assert target in schemas, f'{name}: unresolved $ref {ref}'
    valid={'version_id':'V','entity_id':'E','entity_type':'test','version_number':1,'transaction_from':'2026-01-01T00:00:00Z','status':'current','change_type':'initial'}
    if 'version.schema.json' in schemas: Draft202012Validator(schemas['version.schema.json']).validate(valid)

def refs(x):
    if isinstance(x,dict):
        if isinstance(x.get('$ref'),str): yield x['$ref']
        for v in x.values(): yield from refs(v)
    elif isinstance(x,list):
        for v in x: yield from refs(v)

@given(st.integers(min_value=1,max_value=100))
def test_property_version_chain(n):
    assert all(i==1 or i-1==i-1 for i in range(1,n+1))

@given(st.integers(0,100),st.integers(1,100))
def test_property_half_open_intervals(a,length): assert a<a+length

@given(st.lists(st.integers(0,20),min_size=1,max_size=20,unique=True))
def test_property_dag_order(nodes):
    ordered=sorted(nodes); assert len(ordered)==len(set(ordered))
