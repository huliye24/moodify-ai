"""Search checkpoint tests — public-only results, validation, no static data."""

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


def _seed_published(title: str = "Ocean Breeze") -> str:
    u = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Alice"}).json()
    c = client.post("/internal/v1/music/creators", headers=AUTH, json={"user_id": u["id"], "handle": "alice"}).json()
    t = client.post("/internal/v1/music/tracks", headers=AUTH, json={"creator_id": c["id"], "title": title}).json()
    h = {**AUTH, "X-Moodify-Actor-User-Id": u["id"]}
    client.post(f"/internal/v1/music/tracks/{t['id']}/versions", headers=h, json={"audio_asset_key": "beta/ocean.wav"})
    client.put(f"/internal/v1/music/tracks/{t['id']}/passport", headers=h, json={"rights_statement": "mine"})
    client.post(f"/internal/v1/music/tracks/{t['id']}/publish", headers=h, json={})
    return t["id"]


def test_search_published_only():
    _seed_published("Ocean Breeze")
    # draft track must not appear
    u = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Bob"}).json()
    c = client.post("/internal/v1/music/creators", headers=AUTH, json={"user_id": u["id"], "handle": "bob"}).json()
    client.post("/internal/v1/music/tracks", headers=AUTH, json={"creator_id": c["id"], "title": "Ocean Draft"}).json()
    r = client.get("/internal/v1/music/search", headers=AUTH, params={"q": "ocean"})
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()["tracks"]]
    assert "Ocean Breeze" in titles
    assert "Ocean Draft" not in titles


def test_search_creator():
    _seed_published()
    r = client.get("/internal/v1/music/search", headers=AUTH, params={"q": "ali", "type": "creator"})
    assert r.status_code == 200
    handles = [c["handle"] for c in r.json()["creators"]]
    assert "alice" in handles


def test_search_query_too_short():
    r = client.get("/internal/v1/music/search", headers=AUTH, params={"q": "a"})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "QUERY_TOO_SHORT"


def test_search_limit_and_type_validation():
    r1 = client.get("/internal/v1/music/search", headers=AUTH, params={"q": "abc", "limit": 99})
    assert r1.status_code == 400 and r1.json()["error"]["code"] == "INVALID_LIMIT"
    r2 = client.get("/internal/v1/music/search", headers=AUTH, params={"q": "abc", "type": "album"})
    assert r2.status_code == 400 and r2.json()["error"]["code"] == "INVALID_TYPE"


def test_search_like_escape():
    u = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Alice"}).json()
    c = client.post("/internal/v1/music/creators", headers=AUTH, json={"user_id": u["id"], "handle": "wild_100%"}).json()
    t = client.post("/internal/v1/music/tracks", headers=AUTH, json={"creator_id": c["id"], "title": "Wild"}).json()
    h = {**AUTH, "X-Moodify-Actor-User-Id": u["id"]}
    client.post(f"/internal/v1/music/tracks/{t['id']}/versions", headers=h, json={"audio_asset_key": "beta/w.wav"})
    client.put(f"/internal/v1/music/tracks/{t['id']}/passport", headers=h, json={"rights_statement": "mine"})
    client.post(f"/internal/v1/music/tracks/{t['id']}/publish", headers=h, json={})
    r = client.get("/internal/v1/music/search", headers=AUTH, params={"q": "%%", "type": "creator"})
    assert r.status_code == 200
    assert r.json()["creators"] == []  # % is escaped, no wildcard match-all
