import os
import psycopg
import pytest


def test_gate4_postgres_schema_available():
    dsn = os.getenv("GATE4_POSTGRES_DSN")
    if not dsn:
        pytest.skip("GATE4_POSTGRES_DSN not configured outside Gate 4 CI")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_setting('server_version')")
            version = cur.fetchone()[0]
            assert version.startswith("16.")
            cur.execute("SELECT to_regclass('public.person'), to_regclass('public.candidacy'), to_regclass('public.election_result'), to_regclass('public.claim'), to_regclass('public.evidence')")
            tables = cur.fetchone()
            assert all(tables)
