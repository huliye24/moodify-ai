"""Data plane behavior tests — MFY_PRODUCTION_DATA_PLANE_001.

Connection/retry/idempotency/fail-closed/request-id propagation across the
BFF → Data API chain, plus concurrent-write safety (timeout/retry must never
duplicate authoritative rows).
"""

from __future__ import annotations

import os
import threading
from unittest.mock import patch

os.environ["MOODIFY_INTERNAL_API_KEY"] = "test-service-key"

import httpx
import pytest
from fastapi.testclient import TestClient

from conftest import ENGINE
from moodify_music import models as M
from moodify_music.api.main import app as internal_app
from moodify_music.bff import main as bff_main
from moodify_music.bff.main import app as bff_app
from moodify_music.config import MusicConfig
from moodify_music.db import make_engine

internal_client = TestClient(internal_app)
bff_client = TestClient(bff_app)
AUTH = {"X-Moodify-Service-Key": "test-service-key"}


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with ENGINE.begin() as conn:
        for table in reversed(M.Base.metadata.sorted_tables):
            conn.execute(table.delete())
    bff_main._session_cache.clear()
    bff_main._cache.clear()  # catalogue etc. have 30s TTL decorators
    # concurrency tests swap the DB override; always restore the shared one
    from conftest import _override_db
    from moodify_music.api.deps import get_db

    internal_app.dependency_overrides[get_db] = _override_db


# catalogue is cached; use uncached forwarded routes for chain tests
UNCACHED = "/api/v1/music/tracks/nonexistent-chain-test"


def _seed() -> tuple[str, str]:
    internal_client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={"user_id": "u1", "display_name": "U"})
    creator = internal_client.post("/internal/v1/music/creators", headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-c"},
                                   json={"user_id": "u1", "handle": "h1", "display_name": "h1"}).json()
    track = internal_client.post("/internal/v1/music/tracks", headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-t"},
                                 json={"creator_id": creator["id"], "title": "S"}).json()
    internal_client.post(f"/internal/v1/music/tracks/{track['id']}/versions",
                         headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-v"},
                         json={"audio_asset_key": "a.wav", "mime_type": "audio/wav", "metadata_json": {"sha256": "abc"}})
    internal_client.put(f"/internal/v1/music/tracks/{track['id']}/passport",
                        headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-p"},
                        json={"origin_type": "human"})
    return track["id"], "u1"


# ---------------------------------------------------------- request-id chain

def test_request_id_propagates_through_bff():
    seen = {}
    def fake(method, url, **kwargs):
        seen["rid"] = kwargs["headers"].get("X-Request-Id")
        return httpx.Response(200, json={"id": "t1"})
    with patch("moodify_music.bff.main.httpx.request", side_effect=fake):
        r = bff_client.get(UNCACHED, headers={"X-Request-Id": "req-abc-123"})
    assert r.status_code == 200
    assert seen["rid"] == "req-abc-123"  # caller request id carried end-to-end


def test_bff_generates_request_id_when_absent():
    seen = {}
    def fake(method, url, **kwargs):
        seen["rid"] = kwargs["headers"].get("X-Request-Id")
        return httpx.Response(200, json={"items": []})
    with patch("moodify_music.bff.main.httpx.request", side_effect=fake):
        bff_client.get(UNCACHED)
    assert seen["rid"] and len(seen["rid"]) >= 8  # generated uuid prefix


# ---------------------------------------------------------- timeout/retry

def test_timeout_retry_replays_same_idempotency_key():
    """Retry after timeout must forward the identical Idempotency-Key so the
    upstream can replay safely (no duplicate authoritative rows)."""
    keys = []
    def flaky(method, url, **kwargs):
        keys.append(kwargs["headers"].get("Idempotency-Key"))
        if len(keys) == 1:
            raise httpx.TimeoutException("first attempt timed out")
        return httpx.Response(200, json={"id": "t1"})
    with patch("moodify_music.bff.main.httpx.request", side_effect=flaky):
        r = bff_client.get(UNCACHED, headers={"Idempotency-Key": "idem-retry-1"})
    assert r.status_code == 200
    assert keys == ["idem-retry-1", "idem-retry-1"]  # same key both attempts


def test_request_error_fails_closed_with_request_id():
    def down(method, url, **kwargs):
        raise httpx.RequestError("upstream down")
    with patch("moodify_music.bff.main.httpx.request", side_effect=down):
        r = bff_client.get(UNCACHED, headers={"X-Request-Id": "req-fail-1"})
    assert r.status_code == 502
    assert r.json()["error"]["code"] == "UPSTREAM_UNAVAILABLE"
    assert r.json()["error"]["request_id"] == "req-fail-1"


# ---------------------------------------------------------- concurrency

def _multi_connection_client(tmp_path):
    """File-backed SQLite with a per-request connection (NullPool) so threads
    exercise real concurrent transactions like the MySQL pool would."""
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import Session
    from sqlalchemy.pool import NullPool

    engine = create_engine(f"sqlite:///{tmp_path}/conc.sqlite3", poolclass=NullPool, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _busy_timeout(dbapi_connection, _record):
        dbapi_connection.execute("PRAGMA busy_timeout=5000")

    M.Base.metadata.create_all(engine)
    internal_app.dependency_overrides.clear()
    from moodify_music.api.deps import get_db

    def _override():
        with Session(engine) as session:
            yield session

    internal_app.dependency_overrides[get_db] = _override
    return TestClient(internal_app), engine


def test_concurrent_same_key_publish_never_duplicates(tmp_path):
    client, engine = _multi_connection_client(tmp_path)
    client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={"user_id": "u1", "display_name": "U"})
    creator = client.post("/internal/v1/music/creators", headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-c"},
                          json={"user_id": "u1", "handle": "h1", "display_name": "h1"}).json()
    track = client.post("/internal/v1/music/tracks", headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-t"},
                        json={"creator_id": creator["id"], "title": "S"}).json()
    client.post(f"/internal/v1/music/tracks/{track['id']}/versions",
                headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-v"},
                json={"audio_asset_key": "a.wav", "mime_type": "audio/wav", "metadata_json": {"sha256": "abc"}})
    client.put(f"/internal/v1/music/tracks/{track['id']}/passport",
               headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-p"},
               json={"origin_type": "human"})

    results = []
    barrier = threading.Barrier(8)

    def publish():
        barrier.wait()
        r = client.post(f"/internal/v1/music/tracks/{track['id']}/publish",
                        headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "idem-pub-1"},
                        json={})
        results.append(r.status_code)

    threads = [threading.Thread(target=publish) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(code == 200 for code in results), results
    from sqlalchemy import text as sql_text

    with engine.connect() as conn:
        rows = conn.execute(sql_text("SELECT COUNT(*) FROM idempotency_keys WHERE idempotency_key='idem-pub-1' AND scope='publish'")).scalar()
        audit = conn.execute(sql_text("SELECT COUNT(*) FROM audit_events WHERE action='track.published'")).scalar()
    assert rows == 1, f"concurrent same-key publish duplicated idempotency rows: {rows}"
    assert audit == 1, f"concurrent same-key publish duplicated audit rows: {audit}"
    state = client.get(f"/internal/v1/music/tracks/{track['id']}", headers={**AUTH, "X-Moodify-Actor-User-Id": "u1"}).json()
    assert state["status"] == "published"
    engine.dispose()


def test_concurrent_distinct_keys_create_distinct_tracks(tmp_path):
    client, engine = _multi_connection_client(tmp_path)
    client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={"user_id": "u2", "display_name": "U2"})
    creator = client.post("/internal/v1/music/creators", headers={**AUTH, "X-Moodify-Actor-User-Id": "u2", "Idempotency-Key": "k-c2"},
                          json={"user_id": "u2", "handle": "h2", "display_name": "h2"}).json()
    results = []
    barrier = threading.Barrier(5)

    def create(i):
        barrier.wait()
        r = client.post("/internal/v1/music/tracks",
                        headers={**AUTH, "X-Moodify-Actor-User-Id": "u2", "Idempotency-Key": f"idem-tr-{i}"},
                        json={"creator_id": creator["id"], "title": f"T{i}"})
        results.append(r.status_code)

    threads = [threading.Thread(target=create, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(code == 201 for code in results), results
    from sqlalchemy import text as sql_text

    with engine.connect() as conn:
        count = conn.execute(sql_text("SELECT COUNT(*) FROM tracks WHERE creator_id=:c"), {"c": creator["id"]}).scalar()
    assert count == 5
    engine.dispose()


# ---------------------------------------------------------- pool config

def test_engine_pool_configuration_is_applied():
    config = MusicConfig.from_env()  # test env defaults
    engine = make_engine(config)
    assert engine.pool.size() == config.db_pool_size
    assert engine.pool._max_overflow == config.db_max_overflow
    engine.dispose()


def test_music_config_defaults_match_documented_budget():
    config = MusicConfig.from_env()
    assert config.db_pool_size <= 4, "1.6GB host pool budget"
    assert config.db_max_overflow <= 4
