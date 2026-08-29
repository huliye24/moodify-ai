"""Playlist checkpoint tests — privacy, duplicates, container-only deletion."""

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


def _playlist(uid: str, title: str = "My List", visibility: str = "private") -> dict:
    return client.post("/internal/v1/music/playlists", headers={**AUTH, "X-Moodify-Actor-User-Id": uid},
                       json={"owner_user_id": uid, "title": title, "visibility": visibility}).json()


def test_create_and_private_read_rule():
    uid, _, _, u2 = _seed()
    p = _playlist(uid)
    # owner can read
    r = client.get(f"/internal/v1/music/playlists/{p['id']}", headers={**AUTH, "X-Moodify-Actor-User-Id": uid})
    assert r.status_code == 200 and r.json()["title"] == "My List"
    # other user cannot read private
    r2 = client.get(f"/internal/v1/music/playlists/{p['id']}", headers={**AUTH, "X-Moodify-Actor-User-Id": u2})
    assert r2.status_code == 403


def test_public_playlist_readable_by_anyone():
    uid, _, _, u2 = _seed()
    p = _playlist(uid, visibility="public")
    r = client.get(f"/internal/v1/music/playlists/{p['id']}", headers={**AUTH, "X-Moodify-Actor-User-Id": u2})
    assert r.status_code == 200


def test_add_duplicate_rejected():
    uid, _, tid, _ = _seed()
    p = _playlist(uid)
    h = {**AUTH, "X-Moodify-Actor-User-Id": uid}
    assert client.post(f"/internal/v1/music/playlists/{p['id']}/items", headers=h, json={"track_id": tid}).status_code == 201
    r = client.post(f"/internal/v1/music/playlists/{p['id']}/items", headers=h, json={"track_id": tid})
    assert r.status_code == 409 and r.json()["error"]["code"] == "DUPLICATE_ITEM"


def test_remove_missing_idempotent():
    uid, _, tid, _ = _seed()
    p = _playlist(uid)
    h = {**AUTH, "X-Moodify-Actor-User-Id": uid}
    client.post(f"/internal/v1/music/playlists/{p['id']}/items", headers=h, json={"track_id": tid})
    r1 = client.delete(f"/internal/v1/music/playlists/{p['id']}/items/{tid}", headers=h)
    assert r1.json()["removed"] is True
    r2 = client.delete(f"/internal/v1/music/playlists/{p['id']}/items/{tid}", headers=h)
    assert r2.json()["removed"] is False  # idempotent


def test_delete_playlist_keeps_track_and_media():
    uid, _, tid, _ = _seed()
    p = _playlist(uid)
    h = {**AUTH, "X-Moodify-Actor-User-Id": uid}
    client.post(f"/internal/v1/music/playlists/{p['id']}/items", headers=h, json={"track_id": tid})
    r = client.delete(f"/internal/v1/music/playlists/{p['id']}", headers=h)
    assert r.status_code == 200
    # track still exists and referenced media unchanged
    t = client.get(f"/internal/v1/music/tracks/{tid}", headers=AUTH)
    assert t.status_code == 200
    # playlist gone
    assert client.get(f"/internal/v1/music/playlists/{p['id']}", headers=h).status_code == 404


def test_cross_user_edit_forbidden():
    uid, _, _, u2 = _seed()
    p = _playlist(uid)
    r = client.patch(f"/internal/v1/music/playlists/{p['id']}", headers={**AUTH, "X-Moodify-Actor-User-Id": u2}, json={"title": "hijack"})
    assert r.status_code == 403
    r2 = client.delete(f"/internal/v1/music/playlists/{p['id']}", headers={**AUTH, "X-Moodify-Actor-User-Id": u2})
    assert r2.status_code == 403


def test_my_playlists_and_visibility_toggle():
    uid, _, _, _ = _seed()
    _playlist(uid, "A")
    _playlist(uid, "B", visibility="public")
    r = client.get(f"/internal/v1/music/users/{uid}/playlists", headers={**AUTH, "X-Moodify-Actor-User-Id": uid})
    assert len(r.json()["playlists"]) == 2
    titles = {p["title"] for p in r.json()["playlists"]}
    assert titles == {"A", "B"}
    # toggle A to public
    pid = next(p["id"] for p in r.json()["playlists"] if p["title"] == "A")
    up = client.patch(f"/internal/v1/music/playlists/{pid}", headers={**AUTH, "X-Moodify-Actor-User-Id": uid}, json={"visibility": "public"})
    assert up.json()["visibility"] == "public"
