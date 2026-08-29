"""Data plane application-layer constraint tests — MFY_PRODUCTION_DATA_PLANE_001.

PolarDB XEngine has no foreign keys; every critical relationship must be
guarded at the application layer. These tests assert the guards exist and
fail closed, and that timeout/retry never duplicates authoritative rows.
"""

from __future__ import annotations

import os

os.environ["MOODIFY_INTERNAL_API_KEY"] = "test-service-key"

import pytest
from fastapi.testclient import TestClient

from conftest import ENGINE
from moodify_music import models as M
from moodify_music.api.main import app

client = TestClient(app)
AUTH = {"X-Moodify-Service-Key": "test-service-key"}


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with ENGINE.begin() as conn:
        for table in reversed(M.Base.metadata.sorted_tables):
            conn.execute(table.delete())


def test_key_relationships_have_application_guards():
    """Critical relations (no FK in XEngine) must be guarded in code."""
    import ast
    from pathlib import Path

    api_dir = Path("src/moodify_music/api")
    guards = {
        "require_actor_matches": "identity ownership",
        "_require_owner": "creator ownership",
    }
    sources = "\n".join(p.read_text(encoding="utf-8") for p in api_dir.glob("*.py"))
    for guard, meaning in guards.items():
        assert guard in sources, f"missing application guard {guard} ({meaning})"
    # bridge + passport + tracks routes must call an ownership guard
    for route_file in ["routes_tracks.py", "routes_bridge.py"]:
        src = (api_dir / route_file).read_text(encoding="utf-8")
        assert "require_actor_matches" in src or "_require_owner" in src, f"{route_file} lacks ownership guard"


def test_retry_never_duplicates_track_or_version():
    client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={"user_id": "u1", "display_name": "U"})
    creator = client.post("/internal/v1/music/creators", headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-c"},
                          json={"user_id": "u1", "handle": "h1", "display_name": "h1"}).json()
    track = client.post("/internal/v1/music/tracks", headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-t"},
                        json={"creator_id": creator["id"], "title": "S"}).json()

    for _ in range(3):  # retry with the same key
        r = client.post(f"/internal/v1/music/tracks/{track['id']}/versions",
                        headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-v"},
                        json={"audio_asset_key": "a.wav", "mime_type": "audio/wav", "metadata_json": {"sha256": "abc"}})
        assert r.status_code == 201

    from sqlalchemy import text as sql_text

    with ENGINE.connect() as conn:
        tracks = conn.execute(sql_text("SELECT COUNT(*) FROM tracks")).scalar()
        versions = conn.execute(sql_text("SELECT COUNT(*) FROM track_versions")).scalar()
    assert tracks == 1 and versions == 1, f"retry duplicated rows: tracks={tracks} versions={versions}"


def test_bridge_request_key_is_unique_guard():
    client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={"user_id": "u1", "display_name": "U"})
    creator = client.post("/internal/v1/music/creators", headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-c"},
                          json={"user_id": "u1", "handle": "h1", "display_name": "h1"}).json()
    track = client.post("/internal/v1/music/tracks", headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-t"},
                        json={"creator_id": creator["id"], "title": "S"}).json()
    version = client.post(f"/internal/v1/music/tracks/{track['id']}/versions",
                          headers={**AUTH, "X-Moodify-Actor-User-Id": "u1", "Idempotency-Key": "k-v"},
                          json={"audio_asset_key": "a.wav", "mime_type": "audio/wav", "metadata_json": {"sha256": "abc"}}).json()

    first = client.post("/internal/v1/music/bridge/requests", headers={**AUTH, "X-Moodify-Actor-User-Id": "u1"},
                        json={"track_id": track["id"], "version_id": version["id"], "asset_sha256": "abc", "request_key": "br-1"})
    assert first.status_code == 201
    # same key, different track -> REQUEST_KEY_REUSED (unique guard at app layer)
    client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={"user_id": "u2", "display_name": "U2"})
    c2 = client.post("/internal/v1/music/creators", headers={**AUTH, "X-Moodify-Actor-User-Id": "u2", "Idempotency-Key": "k-c2"},
                     json={"user_id": "u2", "handle": "h2", "display_name": "h2"}).json()
    t2 = client.post("/internal/v1/music/tracks", headers={**AUTH, "X-Moodify-Actor-User-Id": "u2", "Idempotency-Key": "k-t2"},
                     json={"creator_id": c2["id"], "title": "S2"}).json()
    v2 = client.post(f"/internal/v1/music/tracks/{t2['id']}/versions",
                     headers={**AUTH, "X-Moodify-Actor-User-Id": "u2", "Idempotency-Key": "k-v2"},
                     json={"audio_asset_key": "b.wav", "mime_type": "audio/wav", "metadata_json": {"sha256": "def"}}).json()
    reused = client.post("/internal/v1/music/bridge/requests", headers={**AUTH, "X-Moodify-Actor-User-Id": "u2"},
                         json={"track_id": t2["id"], "version_id": v2["id"], "asset_sha256": "def", "request_key": "br-1"})
    assert reused.status_code == 409
    assert reused.json()["error"]["code"] == "REQUEST_KEY_REUSED"


def test_fail_closed_no_partial_writes_on_error():
    """A validation error must not leave orphan rows behind."""
    before = None
    with ENGINE.connect() as conn:
        from sqlalchemy import text as sql_text

        before = conn.execute(sql_text("SELECT COUNT(*) FROM tracks")).scalar()
    # unauthenticated actor write fails closed (401/403/404 all refuse the write)
    r = client.post("/internal/v1/music/tracks", headers={**AUTH, "Idempotency-Key": "k-x"},
                    json={"creator_id": "ghost", "title": "X"})
    assert r.status_code in (401, 403, 404)
    with ENGINE.connect() as conn:
        from sqlalchemy import text as sql_text

        after = conn.execute(sql_text("SELECT COUNT(*) FROM tracks")).scalar()
    assert after == before
