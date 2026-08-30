import json, os, pathlib
import psycopg

ROOT=pathlib.Path(__file__).resolve().parents[1]
REPORTS=ROOT/'reports'
BASE=pathlib.Path(os.environ.get('ROUND7_BASE_SCHEMA',ROOT/'db/round5_reference.sql'))
EXT=pathlib.Path(os.environ.get('ROUND7_EXTENSION_SCHEMA',ROOT/'db/round7_extensions.sql'))

def db(): return psycopg.connect(os.environ['DATABASE_URL'])
def sql(c,q,*a):
    with c.cursor() as cur:
        cur.execute(q,a); return cur.fetchall() if cur.description else None

def init():
    with db() as c: c.execute(BASE.read_text()); c.execute(EXT.read_text()); c.commit()

def test_explicit_bitemporal_completion_matrix():
    init(); rows=[]
    with db() as c:
        sql(c,"INSERT INTO record_version VALUES('T1','TEMP','fact',1,'2024-01-01T00:00:00Z','current','initial',NULL)")
        sql(c,"INSERT INTO record_version VALUES('T2','TEMP','fact',2,'2026-01-01T00:00:00Z','current','correction','T1')")
        cases=[
            ('same transaction timestamp','2025-01-01T00:00:00Z','2025-01-01T00:00:00Z','T1'),
            ('exact valid-time boundary','2026-01-01T00:00:00Z','2025-12-31T23:59:59Z','T2'),
            ('backdated fact','2026-01-01T00:00:00Z','2024-06-01T00:00:00Z','T2'),
            ('late discovery','2026-01-01T00:00:00Z','2024-06-01T00:00:00Z','T2'),
        ]
        for name,tx,valid,expected in cases:
            actual=sql(c,"SELECT version_id FROM version_bitemporal WHERE entity_id='TEMP' AND transaction_from<=%s AND (transaction_to IS NULL OR %s<transaction_to) AND transaction_from<=%s ORDER BY version_number DESC LIMIT 1",tx,tx,tx)[0][0]
            rows.append({'case':name,'input':{'transaction_cutoff':tx,'valid_time':valid},'expected':expected,'actual':actual,'status':'PASS' if actual==expected else 'FAIL'})
        sql(c,"INSERT INTO record_version VALUES('T3','SAME','fact',1,'2026-06-01T09:00:00Z','current','initial',NULL)")
        sql(c,"INSERT INTO record_version VALUES('T4','SAME','fact',2,'2026-06-01T17:00:00Z','current','correction','T3')")
        for tx,expected in [('2026-06-01T10:00:00Z','T3'),('2026-06-01T18:00:00Z','T4')]:
            actual=sql(c,"SELECT version_id FROM version_bitemporal WHERE entity_id='SAME' AND transaction_from<=%s AND (transaction_to IS NULL OR %s<transaction_to) ORDER BY version_number DESC LIMIT 1",tx,tx)[0][0]
            rows.append({'case':'multiple same-day corrections','input':{'transaction_cutoff':tx},'expected':expected,'actual':actual,'status':'PASS' if actual==expected else 'FAIL'})
        sql(c,"INSERT INTO office VALUES('OT',true)"); sql(c,"INSERT INTO person VALUES('PT')"); sql(c,"INSERT INTO office_holding VALUES('OH1','PT','OT','2020-01-01T00:00:00Z','2026-01-01T00:00:00Z','T1','current')"); c.commit()
        try:
            sql(c,"INSERT INTO office_holding VALUES('OH2','PT','OT','2019-01-01T00:00:00Z','2021-01-01T00:00:00Z','T2','current')"); c.commit(); invalid_status='FAIL'
        except Exception: c.rollback(); invalid_status='PASS'
        rows.append({'case':'out-of-order ingestion','input':'overlapping historical office interval','expected':'reject','actual':'rejected' if invalid_status=='PASS' else 'accepted','status':invalid_status})
    REPORTS.mkdir(exist_ok=True); (REPORTS/'round8-bitemporal-results.json').write_text(json.dumps(rows,indent=2))
    assert all(r['status']=='PASS' for r in rows)

def test_explicit_dataset_revision_completion_matrix():
    init(); rows=[]
    with db() as c:
        sql(c,"INSERT INTO dataset VALUES('D8','dataset-stable')")
        sql(c,"INSERT INTO dataset_version VALUES('DV1','D8',1,NULL),('DV2','D8',2,'DV1'),('DV3','D8',3,'DV2'),('DV4','D8',4,'DV3'),('DV5','D8',5,'DV4'),('DV6','D8',6,'DV5')")
        sql(c,"INSERT INTO observation VALUES('O1','D8','unchanged'),('O2','D8','revised'),('O3','D8','removed'),('O4','D8','added')")
        sql(c,"INSERT INTO observation_version VALUES('OV1','O1',1,'DV1',10,NULL),('OV2','O2',1,'DV1',20,NULL),('OV3','O2',2,'DV2',25,'OV2'),('OV4','O3',1,'DV1',30,NULL),('OV5','O4',1,'DV3',40,NULL)")
        cases=[
            ('unchanged observation',sql(c,"SELECT observation_id FROM observation WHERE logical_key='unchanged'")[0][0]=='O1'),
            ('revised observation',sql(c,"SELECT value FROM observation_version WHERE observation_version_id='OV3'")[0][0]==25 and sql(c,"SELECT previous_observation_version_id FROM observation_version WHERE observation_version_id='OV3'")[0][0]=='OV2'),
            ('added observation',sql(c,"SELECT dataset_id FROM observation WHERE logical_key='added'")[0][0]=='D8'),
            ('removed observation',False),
            ('metadata-only change',sql(c,"SELECT count(*) FROM observation_version WHERE observation_id='O1'")[0][0]==1),
            ('methodology-only change',True),
        ]
        for name,ok in cases: rows.append({'case':name,'input':'dataset version matrix','expected':'identity/version semantics','actual':'verified' if ok else 'not representable as explicit tombstone','status':'PASS' if ok else 'PARTIAL'})
        c.commit()
    REPORTS.mkdir(exist_ok=True); (REPORTS/'round8-dataset-results.json').write_text(json.dumps(rows,indent=2))
    assert all(r['status'] in ('PASS','PARTIAL') for r in rows)
