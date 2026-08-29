"""Creator lifecycle failure-matrix tests (SQLite + TestClient)."""

from __future__ import annotations

import os

os.environ["MOODIFY_INTERNAL_API_KEY"] = "test-service-key"

import pytest
from fastapi.testclient import TestClient

from conftest import ENGINE
from sqlalchemy.orm import Session
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


def _seed() -> tuple[str, str, str]:
    """Returns (user_id, creator_id, other_user_id)."""
    u = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Alice"}).json()
    c = client.post("/internal/v1/music/creators", headers=AUTH, json={"user_id": u["id"], "handle": "alice"}).json()
    u2 = client.post("/internal/v1/music/users", headers=AUTH, json={"display_name": "Bob"}).json()
    return u["id"], c["id"], u2["id"]


def _draft(creator_id: str, title: str = "Draft Song") -> str:
    return client.post("/internal/v1/music/tracks", headers=AUTH, json={"creator_id": creator_id, "title": title}).json()["id"]


def test_drafts_list_and_stages():
    _, cid, _ = _seed()
    t1 = _draft(cid, "One")
    t2 = _draft(cid, "Two")
    r = client.get(f"/internal/v1/music/creators/{cid}/drafts", headers=AUTH)
    assert r.status_code == 200
    stages = {d["track_id"]: d["stage"] for d in r.json()["drafts"]}
    assert stages[t1] == "draft"
    assert stages[t2] == "draft"


def test_draft_isolation_cross_creator():
    _, cid, u2 = _seed()
    _draft(cid)
    r = client.get(f"/internal/v1/music/creators/{cid}/drafts", headers={**AUTH, "X-Moodify-Actor-User-Id": u2})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "OWNERSHIP_DENIED"


def test_resume_stage_transitions():
    _, cid, _ = _seed()
    t = _draft(cid)
    assert client.get(f"/internal/v1/music/drafts/{t}/resume", headers=AUTH).json()["stage"] == "draft"
    client.post(f"/internal/v1/music/tracks/{t}/versions", headers=AUTH, json={"audio_asset_key": "beta/one.wav", "duration_ms": 60000})
    assert client.get(f"/internal/v1/music/drafts/{t}/resume", headers=AUTH).json()["stage"] == "version_ready"
    client.put(f"/internal/v1/music/tracks/{t}/passport", headers=AUTH, json={"rights_statement": "mine"})
    assert client.get(f"/internal/v1/music/drafts/{t}/resume", headers=AUTH).json()["stage"] == "passport_ready"
    client.post(f"/internal/v1/music/tracks/{t}/publish", headers=AUTH, json={})
    resume = client.get(f"/internal/v1/music/drafts/{t}/resume", headers=AUTH).json()
    assert resume["stage"] == "published"
    assert resume["media"]["asset_key"] == "beta/one.wav"
    assert resume["media"]["sha256"] is None  # metadata not set -> null


def test_resume_rejected_for_other_creator():
    _, cid, u2 = _seed()
    t = _draft(cid)
    r = client.get(f"/internal/v1/music/drafts/{t}/resume", headers={**AUTH, "X-Moodify-Actor-User-Id": u2})
    assert r.status_code == 403


def test_abandon_draft():
    _, cid, _ = _seed()
    t = _draft(cid)
    r = client.post(f"/internal/v1/music/drafts/{t}/abandon", headers=AUTH, json={})
    assert r.status_code == 200
    assert r.json()["status"] == "archived"
    # abandon again is idempotent
    r2 = client.post(f"/internal/v1/music/drafts/{t}/abandon", headers=AUTH, json={})
    assert r2.status_code == 200 and r2.json()["already"] is True
    # audit recorded
    with Session(ENGINE) as s:
        from sqlalchemy import select
        actions = {a for (a,) in s.execute(select(M.AuditEvent.action))}
    assert "track.abandoned" in actions


def test_abandon_published_forbidden():
    _, cid, _ = _seed()
    t = _draft(cid)
    client.post(f"/internal/v1/music/tracks/{t}/versions", headers=AUTH, json={"audio_asset_key": "beta/one.wav"})
    client.put(f"/internal/v1/music/tracks/{t}/passport", headers=AUTH, json={"rights_statement": "mine"})
    client.post(f"/internal/v1/music/tracks/{t}/publish", headers=AUTH, json={})
    r = client.post(f"/internal/v1/music/drafts/{t}/abandon", headers=AUTH, json={})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "CANNOT_ABANDON_PUBLISHED"


def test_abandon_cross_creator_forbidden():
    _, cid, u2 = _seed()
    t = _draft(cid)
    r = client.post(f"/internal/v1/music/drafts/{t}/abandon", headers={**AUTH, "X-Moodify-Actor-User-Id": u2}, json={})
    assert r.status_code == 403


def test_media_references_only_referenced():
    _, cid, _ = _seed()
    t = _draft(cid)
    refs = client.get("/internal/v1/music/media/references", headers=AUTH).json()["references"]
    assert refs == []
    client.post(f"/internal/v1/music/tracks/{t}/versions", headers=AUTH, json={"audio_asset_key": "beta/one.wav"})
    refs = client.get("/internal/v1/music/media/references", headers=AUTH).json()["references"]
    assert refs == ["beta/one.wav"]


def test_publish_replay_is_safe():
    _, cid, _ = _seed()
    t = _draft(cid)
    client.post(f"/internal/v1/music/tracks/{t}/versions", headers=AUTH, json={"audio_asset_key": "beta/one.wav"})
    client.put(f"/internal/v1/music/tracks/{t}/passport", headers=AUTH, json={"rights_statement": "mine"})
    h = {**AUTH, "Idempotency-Key": "pub-key-1"}
    r1 = client.post(f"/internal/v1/music/tracks/{t}/publish", headers=h, json={})
    r2 = client.post(f"/internal/v1/music/tracks/{t}/publish", headers=h, json={})
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["status"] == "published" and r2.json()["status"] == "published"


def test_version_retry_no_duplicate():
    _, cid, _ = _seed()
    t = _draft(cid)
    h = {**AUTH, "Idempotency-Key": "ver-key-1"}
    body = {"audio_asset_key": "beta/one.wav"}
    v1 = client.post(f"/internal/v1/music/tracks/{t}/versions", headers=h, json=body).json()
    v2 = client.post(f"/internal/v1/music/tracks/{t}/versions", headers=h, json=body).json()
    assert v1["id"] == v2["id"]
    resume = client.get(f"/internal/v1/music/drafts/{t}/resume", headers=AUTH).json()
    assert resume["track"]["version"]["version_no"] == 1


def test_audit_event_endpoint():
    r = client.post("/internal/v1/music/audit-events", headers=AUTH, json={
        "action": "media.audit_applied", "resource_id": "beta/orphan.wav",
        "metadata": {"deleted": True},
    })
    assert r.status_code == 201
    with Session(ENGINE) as s:
        from sqlalchemy import select
        ev = s.scalar(select(M.AuditEvent).where(M.AuditEvent.action == "media.audit_applied"))
    assert ev is not None and ev.resource_id == "beta/orphan.wav"
