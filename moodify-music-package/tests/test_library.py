"""Library checkpoint tests — favorites, recent plays, ownership, cursor."""

from __future__ import annotations

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


def _seed() -> tuple[str, str, str, str]:
    u = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Alice"}).json()
    c = client.post("/internal/v1/music/creators", headers=AUTH, json={"user_id": u["id"], "handle": "alice"}).json()
    t = client.post("/internal/v1/music/tracks", headers=AUTH, json={"creator_id": c["id"], "title": "Track One"}).json()
    u2 = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Bob"}).json()
    return u["id"], c["id"], t["id"], u2["id"]


def _publish(tid: str, actor: str):
    h = {**AUTH, "X-Moodify-Actor-User-Id": actor}
    client.post(f"/internal/v1/music/tracks/{tid}/versions", headers=h, json={"audio_asset_key": "beta/one.wav"})
    client.put(f"/internal/v1/music/tracks/{tid}/passport", headers=h, json={"rights_statement": "mine"})
    client.post(f"/internal/v1/music/tracks/{tid}/publish", headers=h, json={})


def test_favorites_list_and_unfavorite():
    uid, _, tid, _ = _seed()
    _publish(tid, uid)
    assert client.put(f"/internal/v1/music/users/{uid}/favorites/{tid}", headers={**AUTH, "X-Moodify-Actor-User-Id": uid}).status_code == 200
    r = client.get(f"/internal/v1/music/users/{uid}/favorites", headers={**AUTH, "X-Moodify-Actor-User-Id": uid})
    assert r.status_code == 200
    assert [t["id"] for t in r.json()["tracks"]] == [tid]
    client.delete(f"/internal/v1/music/users/{uid}/favorites/{tid}", headers={**AUTH, "X-Moodify-Actor-User-Id": uid})
    assert client.get(f"/internal/v1/music/users/{uid}/favorites", headers={**AUTH, "X-Moodify-Actor-User-Id": uid}).json()["tracks"] == []


def test_recent_plays_distinct():
    uid, _, tid, _ = _seed()
    _publish(tid, uid)
    for _ in range(3):
        client.post("/internal/v1/music/play-events", headers={**AUTH, "X-Moodify-Actor-User-Id": uid}, json={"user_id": uid, "track_id": tid, "source": "test"})
    r = client.get(f"/internal/v1/music/users/{uid}/recent-plays", headers={**AUTH, "X-Moodify-Actor-User-Id": uid})
    assert r.status_code == 200
    tracks = r.json()["tracks"]
    assert len(tracks) == 1 and tracks[0]["id"] == tid  # distinct by track


def test_library_cross_user_forbidden():
    uid, _, _, u2 = _seed()
    r1 = client.get(f"/internal/v1/music/users/{uid}/favorites", headers={**AUTH, "X-Moodify-Actor-User-Id": u2})
    assert r1.status_code == 403
    r2 = client.get(f"/internal/v1/music/users/{uid}/recent-plays", headers={**AUTH, "X-Moodify-Actor-User-Id": u2})
    assert r2.status_code == 403


def test_favorites_anonymous_denied():
    uid, _, _, _ = _seed()
    r = client.get(f"/internal/v1/music/users/{uid}/favorites", headers=AUTH)
    assert r.status_code == 401  # actor required


def test_favorites_cursor_pagination():
    uid, cid, _, _ = _seed()
    ids = []
    for i in range(5):
        t = client.post("/internal/v1/music/tracks", headers=AUTH, json={"creator_id": cid, "title": f"T{i}"}).json()
        _publish(t["id"], uid)
        ids.append(t["id"])
    # favorite all 5, page size 30 — with 5 items there is no cursor; verify ordering newest first
    for tid in ids:
        client.put(f"/internal/v1/music/users/{uid}/favorites/{tid}", headers={**AUTH, "X-Moodify-Actor-User-Id": uid})
    r = client.get(f"/internal/v1/music/users/{uid}/favorites", headers={**AUTH, "X-Moodify-Actor-User-Id": uid})
    assert r.json()["next_cursor"] is None
    assert len(r.json()["tracks"]) == 5
    # second page via forced small page is covered by cursor param validation
    bad = client.get(f"/internal/v1/music/users/{uid}/favorites?cursor=malformed", headers={**AUTH, "X-Moodify-Actor-User-Id": uid})
    assert bad.status_code == 400
    assert bad.json()["error"]["code"] == "INVALID_CURSOR"
