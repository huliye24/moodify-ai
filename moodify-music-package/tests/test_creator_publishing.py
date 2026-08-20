"""Creator publishing V1 gap tests — MFY_MUSIC_CREATOR_PUBLISHING_V1_001.

Covers the scenarios not already asserted elsewhere: passport IDOR,
publish-response-lost recovery by reading authoritative state, and abandoned
drafts retaining referenced media (no silent deletion).
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


def _seed_user(user_id: str, display_name: str) -> None:
    r = client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={"user_id": user_id, "display_name": display_name})
    assert r.status_code == 201


def _seed_creator(user_id: str, handle: str) -> str:
    r = client.post("/internal/v1/music/creators", headers={**AUTH, "X-Moodify-Actor-User-Id": user_id},
                    json={"user_id": user_id, "handle": handle, "display_name": handle})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _seed_track(creator_id: str, owner_user: str, title: str = "Signal") -> str:
    r = client.post("/internal/v1/music/tracks", headers={**AUTH, "X-Moodify-Actor-User-Id": owner_user, "Idempotency-Key": f"idem-{title}"},
                    json={"creator_id": creator_id, "title": title})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_passport_write_is_owner_only():
    _seed_user("u-owner", "Owner")
    _seed_user("u-attacker", "Attacker")
    c1 = _seed_creator("u-owner", "owner")
    _seed_creator("u-attacker", "attacker")
    t1 = _seed_track(c1, "u-owner")

    forged = client.put(f"/internal/v1/music/tracks/{t1}/passport",
                        headers={**AUTH, "X-Moodify-Actor-User-Id": "u-attacker", "Idempotency-Key": "idem-forge"},
                        json={"origin_type": "human"})
    assert forged.status_code == 403
    assert forged.json()["error"]["code"] == "OWNERSHIP_DENIED"

    ok = client.put(f"/internal/v1/music/tracks/{t1}/passport",
                    headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-ok"},
                    json={"origin_type": "human", "generation_tool": "none"})
    assert ok.status_code == 200
    assert ok.json()["origin_type"] == "human"


def test_publish_requires_passport_and_recovery_reads_authoritative_state():
    _seed_user("u-owner", "Owner")
    c1 = _seed_creator("u-owner", "owner")
    t1 = _seed_track(c1, "u-owner")

    # version first, then publish without passport must fail with a blocker
    ver = client.post(f"/internal/v1/music/tracks/{t1}/versions",
                      headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-v1"},
                      json={"audio_asset_key": "owner/sha256/abc.wav", "mime_type": "audio/wav"})
    assert ver.status_code == 201
    blocked = client.post(f"/internal/v1/music/tracks/{t1}/publish",
                          headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-p1"},
                          json={})
    assert blocked.status_code == 409
    assert blocked.json()["error"]["code"] == "PUBLISH_REQUIRES_PASSPORT"

    client.put(f"/internal/v1/music/tracks/{t1}/passport",
               headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-pp"},
               json={"origin_type": "ai_assisted"})
    published = client.post(f"/internal/v1/music/tracks/{t1}/publish",
                            headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-p2"},
                            json={})
    assert published.status_code == 200
    assert published.json()["status"] == "published"

    # publish response lost: recovery reads the authoritative track state
    state = client.get(f"/internal/v1/music/tracks/{t1}", headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner"})
    assert state.status_code == 200
    assert state.json()["status"] == "published"
    assert state.json()["current_version_id"] is not None


def test_abandon_keeps_referenced_media_no_silent_delete():
    _seed_user("u-owner", "Owner")
    c1 = _seed_creator("u-owner", "owner")
    t1 = _seed_track(c1, "u-owner")
    ver = client.post(f"/internal/v1/music/tracks/{t1}/versions",
                      headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-v1"},
                      json={"audio_asset_key": "owner/sha256/keep.wav", "mime_type": "audio/wav"})
    assert ver.status_code == 201

    abandoned = client.post(f"/internal/v1/music/drafts/{t1}/abandon",
                            headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-ab"},
                            json={})
    assert abandoned.status_code == 200
    assert abandoned.json()["status"] == "archived"

    # referenced media is retained; the API exposes it for a dry-run cleanup
    state = client.get(f"/internal/v1/music/tracks/{t1}", headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner"})
    assert state.json()["status"] == "archived"
    assert state.json()["current_version_id"] is not None
    # no delete endpoint exists that removes media: silence is the default
    media_delete = client.request("DELETE", f"/internal/v1/music/tracks/{t1}/media", headers=AUTH)
    assert media_delete.status_code == 404


def test_publish_replay_with_same_key_is_safe():
    _seed_user("u-owner", "Owner")
    c1 = _seed_creator("u-owner", "owner")
    t1 = _seed_track(c1, "u-owner")
    client.post(f"/internal/v1/music/tracks/{t1}/versions",
                headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-v1"},
                json={"audio_asset_key": "owner/sha256/x.wav", "mime_type": "audio/wav"})
    client.put(f"/internal/v1/music/tracks/{t1}/passport",
               headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-pp"},
               json={"origin_type": "human"})
    first = client.post(f"/internal/v1/music/tracks/{t1}/publish",
                        headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-pub"},
                        json={})
    assert first.status_code == 200
    replay = client.post(f"/internal/v1/music/tracks/{t1}/publish",
                         headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner", "Idempotency-Key": "idem-pub"},
                         json={})
    assert replay.status_code == 200
    assert replay.json()["status"] == "published"
    # no duplicate audit rows from replay (idempotent replay, not a second action)
    from sqlalchemy import text as sql_text

    with ENGINE.connect() as conn:
        count = conn.execute(
            sql_text("SELECT COUNT(*) FROM idempotency_keys WHERE idempotency_key='idem-pub' AND scope='publish'"),
        ).scalar()
    assert count == 1
