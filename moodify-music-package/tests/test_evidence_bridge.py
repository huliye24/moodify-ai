"""Evidence bridge tests — MFY_EAR_MUSIC_EVIDENCE_BRIDGE_001.

Nine scenarios: happy path; duplicate request; hash mismatch; non-owner;
Ear human-required/inconclusive/failed; not publish-safe blocked; detach
keeps audit; recovery after unavailability; internal fields never leak.
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


def _seed(owner: str = "u-owner", handle: str = "owner") -> tuple[str, str, str]:
    client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={"user_id": owner, "display_name": owner})
    creator = client.post("/internal/v1/music/creators", headers={**AUTH, "X-Moodify-Actor-User-Id": owner, "Idempotency-Key": f"idem-cr-{handle}"},
                          json={"user_id": owner, "handle": handle, "display_name": handle}).json()
    track = client.post("/internal/v1/music/tracks", headers={**AUTH, "X-Moodify-Actor-User-Id": owner, "Idempotency-Key": f"idem-tr-{handle}"},
                        json={"creator_id": creator["id"], "title": "Signal"}).json()
    version = client.post(f"/internal/v1/music/tracks/{track['id']}/versions",
                          headers={**AUTH, "X-Moodify-Actor-User-Id": owner, "Idempotency-Key": f"idem-ver-{handle}"},
                          json={"audio_asset_key": f"{handle}/sha256/abc123.wav", "mime_type": "audio/wav",
                                "metadata_json": {"sha256": "abc123", "bytes": 1000, "mime_type": "audio/wav"}}).json()
    return track["id"], version["id"], creator["id"]


def _request(track_id: str, version_id: str, key: str = "br-1", owner: str = "u-owner", sha: str = "abc123"):
    return client.post("/internal/v1/music/bridge/requests",
                       headers={**AUTH, "X-Moodify-Actor-User-Id": owner, "Idempotency-Key": key},
                       json={"track_id": track_id, "version_id": version_id, "asset_sha256": sha, "request_key": key})


def _update(bridge_id: str, status: str, **extra):
    return client.post(f"/internal/v1/music/bridge/requests/{bridge_id}/update", headers=AUTH,
                       json={"exchange_status": status, **extra})


def test_happy_path_evidence_ready_human_reviewed_attach():
    track_id, version_id, _ = _seed()
    created = _request(track_id, version_id)
    assert created.status_code == 201
    bridge = created.json()["bridge"]
    assert bridge["exchange_status"] == "requested"

    assert _update(bridge["id"], "processing").json()["bridge"]["exchange_status"] == "processing"
    ready = _update(bridge["id"], "evidence_ready", ear_case_ref="case-1", approved_evidence_ref="ev-1").json()["bridge"]
    assert ready["exchange_status"] == "evidence_ready"
    reviewed = _update(bridge["id"], "human_reviewed", publish_safe=True, reviewed_at="2026-08-14T01:00:00", reviewer="r1").json()["bridge"]
    assert reviewed["publish_safe"] is True and reviewed["reviewer"] == "r1"

    attached = client.post(f"/internal/v1/music/bridge/requests/{bridge['id']}/attach",
                           headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner"}, json={}).json()["bridge"]
    assert attached["attached"] is True and attached["exchange_status"] == "optionally_attached"
    track = client.get(f"/internal/v1/music/tracks/{track_id}", headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner"}).json()
    assert track["approved_evidence_ref"] == "ev-1"
    assert track["ear_production_case_ref"] == "case-1"


def test_duplicate_request_is_replayed_idempotently():
    track_id, version_id, _ = _seed()
    first = _request(track_id, version_id).json()
    second = _request(track_id, version_id)
    assert second.status_code == 201
    body = second.json()
    assert body["bridge"]["id"] == first["bridge"]["id"]
    assert body["replayed"] is True
    # same key on a different track is rejected
    t2, v2, _ = _seed("u-owner2", "owner2")
    reused = client.post("/internal/v1/music/bridge/requests", headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner2"},
                         json={"track_id": t2, "version_id": v2, "asset_sha256": "abc123", "request_key": "br-1"})
    assert reused.status_code == 409
    assert reused.json()["error"]["code"] == "REQUEST_KEY_REUSED"


def test_asset_hash_mismatch_is_rejected():
    track_id, version_id, _ = _seed()
    r = _request(track_id, version_id, sha="different-hash")
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "ASSET_HASH_MISMATCH"


def test_non_owner_request_is_forbidden():
    track_id, version_id, _ = _seed()
    r = client.post("/internal/v1/music/bridge/requests",
                    headers={**AUTH, "X-Moodify-Actor-User-Id": "u-attacker", "Idempotency-Key": "br-x"},
                    json={"track_id": track_id, "version_id": version_id, "asset_sha256": "abc123", "request_key": "br-x"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "OWNERSHIP_DENIED"


def test_ear_human_required_blocks_attach():
    track_id, version_id, _ = _seed()
    bridge = _request(track_id, version_id).json()["bridge"]
    _update(bridge["id"], "processing")
    _update(bridge["id"], "human_reviewed", ear_case_ref="case-1", authority_state="HUMAN_REQUIRED", publish_safe=False)
    attach = client.post(f"/internal/v1/music/bridge/requests/{bridge['id']}/attach",
                         headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner"}, json={})
    assert attach.status_code == 403
    assert attach.json()["error"]["code"] == "EVIDENCE_NOT_PUBLISH_SAFE"


def test_ear_inconclusive_and_failed_are_terminal():
    track_id, version_id, _ = _seed()
    bridge = _request(track_id, version_id).json()["bridge"]
    _update(bridge["id"], "processing")
    r = _update(bridge["id"], "inconclusive")
    assert r.status_code == 200 and r.json()["bridge"]["exchange_status"] == "inconclusive"
    # terminal: no further transitions
    blocked = _update(bridge["id"], "human_reviewed", publish_safe=True)
    assert blocked.status_code == 409

    bridge2 = _request(track_id, version_id, key="br-fail").json()["bridge"]
    _update(bridge2["id"], "failed", failure_code="PROCESSING_FAILED")
    assert _update(bridge2["id"], "evidence_ready").status_code == 409


def test_attach_before_human_review_is_conflict():
    track_id, version_id, _ = _seed()
    bridge = _request(track_id, version_id).json()["bridge"]
    _update(bridge["id"], "evidence_ready", ear_case_ref="c1", approved_evidence_ref="e1", publish_safe=True)
    attach = client.post(f"/internal/v1/music/bridge/requests/{bridge['id']}/attach",
                         headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner"}, json={})
    assert attach.status_code == 409
    assert attach.json()["error"]["code"] == "EXCHANGE_NOT_REVIEWED"


def test_detach_keeps_evidence_and_audit():
    track_id, version_id, _ = _seed()
    bridge = _request(track_id, version_id).json()["bridge"]
    _update(bridge["id"], "processing")
    _update(bridge["id"], "evidence_ready", ear_case_ref="case-1", approved_evidence_ref="ev-1")
    _update(bridge["id"], "human_reviewed", publish_safe=True, reviewer="r1", reviewed_at="2026-08-14T01:00:00")
    client.post(f"/internal/v1/music/bridge/requests/{bridge['id']}/attach",
                headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner"}, json={})
    detached = client.post(f"/internal/v1/music/bridge/requests/{bridge['id']}/detach",
                           headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner"}, json={}).json()["bridge"]
    assert detached["attached"] is False
    assert detached["approved_evidence_ref"] == "ev-1"  # evidence retained
    assert detached["exchange_status"] == "optionally_attached"  # exchange history retained
    track = client.get(f"/internal/v1/music/tracks/{track_id}", headers={**AUTH, "X-Moodify-Actor-User-Id": "u-owner"}).json()
    assert track["approved_evidence_ref"] is None  # display removed only


def test_recovery_after_unavailability_replays_same_request():
    track_id, version_id, _ = _seed()
    first = _request(track_id, version_id).json()["bridge"]
    # simulate the client retrying after a lost response: same key
    retry = _request(track_id, version_id, key=first["request_key"])
    assert retry.status_code == 201
    assert retry.json()["replayed"] is True
    assert retry.json()["bridge"]["id"] == first["id"]


def test_internal_fields_never_leak_in_public_shape():
    track_id, version_id, _ = _seed()
    bridge = _request(track_id, version_id).json()["bridge"]
    payload = bridge
    for token in ["/var/", "C:\\", "case_dir", "state_dir", "prompt", "source_path", "private"]:
        assert token not in str(payload).lower()
