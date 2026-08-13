"""Internal Data API integration tests (SQLite + TestClient).

Sets MOODIFY_INTERNAL_API_KEY before importing deps so auth is enforced.
"""

from __future__ import annotations

import os

os.environ["MOODIFY_INTERNAL_API_KEY"] = "test-service-key"
os.environ["MOODIFY_DB_HOST"] = "127.0.0.1"

import pytest
from fastapi.testclient import TestClient

from conftest import ENGINE
from moodify_music import models as M
from moodify_music.api.main import app

client = TestClient(app)
AUTH = {"X-Moodify-Service-Key": "test-service-key"}
IDEM = {"Idempotency-Key": "idem-1"}


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with ENGINE.begin() as conn:
        for table in reversed(M.Base.metadata.sorted_tables):
            conn.execute(table.delete())


def test_auth_required():
    assert client.post("/internal/v1/music/users", json={"display_name": "x"}).status_code == 401
    assert client.get("/health").status_code == 200  # health public


def test_error_model():
    r = client.get("/internal/v1/music/users/nope", headers=AUTH)
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "request_id" in body["error"]


def test_unhandled_error_is_normalized(monkeypatch):
    from moodify_music.api import main

    def explode():
        raise RuntimeError("private database detail")

    main.app.add_api_route("/internal/v1/music/__error_probe__", explode, methods=["GET"])
    response = client.get("/internal/v1/music/__error_probe__", headers=AUTH)
    assert response.status_code == 500
    body = response.json()["error"]
    assert body["code"] == "INTERNAL_ERROR"
    assert "request_id" in body
    assert "private database detail" not in response.text


def _seed_user_creator():
    u = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Alice", "email": "a@b.c"}).json()
    c = client.post("/internal/v1/music/creators", headers=AUTH, json={"user_id": u["id"], "handle": "alice"}).json()
    return u, c


def test_full_track_flow():
    u, c = _seed_user_creator()
    t = client.post("/internal/v1/music/tracks", headers=AUTH, json={"creator_id": c["id"], "title": "First Song"}).json()
    assert t["status"] == "draft"
    v = client.post(
        f"/internal/v1/music/tracks/{t['id']}/versions", headers=AUTH,
        json={"audio_asset_key": "cadeau10-album1/first.wav", "duration_ms": 180000},
    ).json()
    assert v["version_no"] == 1
    # publish without passport -> 409
    r = client.post(f"/internal/v1/music/tracks/{t['id']}/publish", headers=AUTH, json={})
    assert r.status_code == 409
    client.put(
        f"/internal/v1/music/tracks/{t['id']}/passport", headers=AUTH,
        json={"origin_type": "ai", "generation_tool": "suno", "rights_statement": "mine"},
    )
    p = client.post(f"/internal/v1/music/tracks/{t['id']}/publish", headers=AUTH, json={}).json()
    assert p["status"] == "published"
    assert p["published_at"] is not None
    return u, c, t, v


def test_social_and_intents():
    u, c, t, v = test_full_track_flow()
    u2 = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Bob"}).json()
    # follow + favorite
    actor_headers = {**AUTH, "X-Moodify-Actor-User-Id": u2["id"]}
    assert client.put(f"/internal/v1/music/users/{u2['id']}/follows/{c['id']}", headers=actor_headers).status_code == 200
    assert client.put(f"/internal/v1/music/users/{u2['id']}/favorites/{t['id']}", headers=actor_headers).status_code == 200
    # play event
    ev = client.post("/internal/v1/music/play-events", headers=AUTH, json={"track_id": t["id"], "played_ms": 30000, "source": "track_page"}).json()
    assert ev["id"]
    # license intent
    li = client.post(
        "/internal/v1/music/license-intents", headers=AUTH,
        json={"track_id": t["id"], "license_type": "sync", "usage_description": "short film", "requester_name": "Film Co", "budget_amount_minor": 50000, "budget_currency": "CNY"},
    ).json()
    assert li["status"] == "submitted"
    # creator inbox
    inbox = client.get(
        f"/internal/v1/music/creators/{c['id']}/license-intents",
        headers={**AUTH, "X-Moodify-Actor-User-Id": u["id"]},
    ).json()
    assert len(inbox["intents"]) == 1
    assert inbox["intents"][0]["id"] == li["id"]
    # support intent
    si = client.post("/internal/v1/music/support-intents", headers=AUTH, json={"creator_id": c["id"], "amount_minor": 10000, "currency": "CNY"}).json()
    assert si["status"] == "expressed"
    # creator page aggregate
    page = client.get(f"/internal/v1/music/creators/{c['id']}/page", headers=AUTH).json()
    assert page["follower_count"] == 1
    assert len(page["tracks"]) == 1


def test_idempotency_same_key():
    u, c = _seed_user_creator()
    h = {**AUTH, "Idempotency-Key": "idem-track-1"}
    body = {"creator_id": c["id"], "title": "Same"}
    r1 = client.post("/internal/v1/music/tracks", headers=h, json=body).json()
    r2 = client.post("/internal/v1/music/tracks", headers=h, json=body).json()
    assert r1["id"] == r2["id"]
    # different payload same key -> 409
    r3 = client.post("/internal/v1/music/tracks", headers=h, json={"creator_id": c["id"], "title": "Different"})
    assert r3.status_code == 409
    assert r3.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"


def test_ownership_denied():
    u, c = _seed_user_creator()
    t = client.post("/internal/v1/music/tracks", headers=AUTH, json={"creator_id": c["id"], "title": "Mine"}).json()
    other = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Other"}).json()
    r = client.patch(
        f"/internal/v1/music/tracks/{t['id']}", headers={**AUTH, "X-Moodify-Actor-User-Id": other["id"]}, json={"title": "hijack"}
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "OWNERSHIP_DENIED"


def test_social_path_identity_cannot_override_actor():
    u, c = _seed_user_creator()
    other = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Other"}).json()
    response = client.put(
        f"/internal/v1/music/users/{other['id']}/follows/{c['id']}",
        headers={**AUTH, "X-Moodify-Actor-User-Id": u["id"]},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "OWNERSHIP_DENIED"


def test_handle_normalization_and_uniqueness():
    u = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Alice"}).json()
    c1 = client.post("/internal/v1/music/creators", headers=AUTH, json={"user_id": u["id"], "handle": "AliceStudio"}).json()
    assert c1["handle"] == "alicestudio"
    by_handle = client.get("/internal/v1/music/creators/by-handle/alicestudio", headers=AUTH).json()
    assert by_handle["id"] == c1["id"]
    u2 = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Bob"}).json()
    r = client.post("/internal/v1/music/creators", headers=AUTH, json={"user_id": u2["id"], "handle": "alicestudio"})
    assert r.status_code == 409


def test_cwc_ledger_atomic():
    u, c = _seed_user_creator()
    acc = client.post("/internal/v1/music/cwc/accounts", headers=AUTH, json={"user_id": u["id"], "balance_units": 100}).json()
    assert acc["balance_units"] == 100
    m = client.post("/internal/v1/music/cwc/ledger", headers=AUTH, json={"user_id": u["id"], "delta_units": -30, "reason": "usage"}).json()
    assert m["balance_units"] == 70
    r = client.post("/internal/v1/music/cwc/ledger", headers=AUTH, json={"user_id": u["id"], "delta_units": -100, "reason": "over"})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "CWC_INSUFFICIENT"
