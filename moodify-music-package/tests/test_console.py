"""Creator console checkpoint tests — grouping, unpublish/republish, concurrency."""

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


def test_console_grouping():
    uid, cid, t1, _ = _seed()
    h = {**AUTH, "X-Moodify-Actor-User-Id": uid}
    t2 = client.post("/internal/v1/music/tracks", headers=AUTH, json={"creator_id": cid, "title": "Drafty"}).json()
    _publish(t1, uid)
    client.post(f"/internal/v1/music/drafts/{t2['id']}/abandon", headers=h, json={})
    r = client.get(f"/internal/v1/music/creators/{cid}/tracks", headers=h)
    assert r.status_code == 200
    by_status = {t["id"]: t["status"] for t in r.json()["tracks"]}
    assert by_status[t1] == "published"
    assert by_status[t2["id"]] == "archived"
    # status filter
    drafts = client.get(f"/internal/v1/music/creators/{cid}/tracks?status=draft", headers=h).json()["tracks"]
    assert all(t["status"] == "draft" for t in drafts)


def test_console_cross_creator_forbidden():
    _, cid, _, u2 = _seed()
    r = client.get(f"/internal/v1/music/creators/{cid}/tracks", headers={**AUTH, "X-Moodify-Actor-User-Id": u2})
    assert r.status_code == 403


def test_unpublish_lifecycle():
    uid, cid, t1, _ = _seed()
    h = {**AUTH, "X-Moodify-Actor-User-Id": uid}
    _publish(t1, uid)
    # unpublish
    r = client.post(f"/internal/v1/music/tracks/{t1}/unpublish", headers=h, json={})
    assert r.status_code == 200
    assert r.json()["status"] == "archived" and r.json()["public_url_live"] is False
    # not published again -> 409
    r2 = client.post(f"/internal/v1/music/tracks/{t1}/unpublish", headers=h, json={})
    assert r2.status_code == 409 and r2.json()["error"]["code"] == "NOT_PUBLISHED"
    # gone from catalogue after unpublish
    cat = client.get("/internal/v1/music/catalogue", headers=AUTH).json()["tracks"]
    assert all(t["id"] != t1 for t in cat)
    # republish via publish endpoint
    r3 = client.post(f"/internal/v1/music/tracks/{t1}/publish", headers=h, json={})
    assert r3.status_code == 200 and r3.json()["status"] == "published"


def test_unpublish_cross_creator_forbidden():
    _, _, t1, u2 = _seed()
    _publish(t1, "x") if False else None
    # publish as creator's user first
    uid = client.get(f"/internal/v1/music/creators/by-handle/alice", headers=AUTH).json()["user_id"]
    h = {**AUTH, "X-Moodify-Actor-User-Id": uid}
    _publish(t1, uid)
    r = client.post(f"/internal/v1/music/tracks/{t1}/unpublish", headers={**AUTH, "X-Moodify-Actor-User-Id": u2}, json={})
    assert r.status_code == 403


def test_patch_concurrency_guard():
    uid, _, t1, _ = _seed()
    h = {**AUTH, "X-Moodify-Actor-User-Id": uid}
    track = client.get(f"/internal/v1/music/tracks/{t1}", headers=AUTH).json()
    updated_at = track["updated_at"]
    assert updated_at
    ok = client.patch(f"/internal/v1/music/tracks/{t1}", headers={**h, "If-Match": updated_at}, json={"title": "Renamed"})
    assert ok.status_code == 200 and ok.json()["title"] == "Renamed"
    # stale If-Match -> 412
    stale = client.patch(f"/internal/v1/music/tracks/{t1}", headers={**h, "If-Match": updated_at}, json={"title": "Again"})
    assert stale.status_code == 412
    assert stale.json()["error"]["code"] == "PRECONDITION_FAILED"
