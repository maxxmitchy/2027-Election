import os, pathlib, psycopg, pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=pathlib.Path(os.environ.get('ROUND7_BASE_SCHEMA',ROOT/'db/round5_reference.sql'))
EXT=pathlib.Path(os.environ.get('ROUND7_EXTENSION_SCHEMA',ROOT/'db/round7_extensions.sql'))

def apply():
    with psycopg.connect(os.environ['DATABASE_URL']) as c: c.execute(BASE.read_text()); c.execute(EXT.read_text()); c.commit()
@pytest.fixture(autouse=True)
def fresh(): apply()
def test_bitemporal_view_snapshot():
    with psycopg.connect(os.environ['DATABASE_URL']) as c:
        c.execute("INSERT INTO record_version VALUES('BT1','BT', 'fact',1,'2024-01-01','current','initial',NULL)")
        c.execute("INSERT INTO record_version VALUES('BT2','BT', 'fact',2,'2026-01-01','current','correction','BT1')")
        for cutoff,expected in [('2025-01-01','BT1'),('2026-01-01','BT2'),('2026-12-31','BT2')]:
            rows=c.execute("SELECT version_id FROM version_bitemporal WHERE entity_id='BT' AND transaction_from<=%s AND (transaction_to IS NULL OR %s<transaction_to) ORDER BY version_number",(cutoff,cutoff)).fetchall()
            assert [r[0] for r in rows]==[expected]
        c.commit()
