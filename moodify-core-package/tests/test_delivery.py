"""W01-P06 Delivery tests — TST-01..10 (service side; Android side in Kotlin)."""

from __future__ import annotations

import time

import pytest

from moodify.data_plane.adapter import LocalFileAdapter
from moodify.data_plane.control import JobControlPlane
from moodify.data_plane.delivery import DeliveryError, DeliveryService, PlaybackMetadata
from moodify.data_plane.ids import new_id
from moodify.data_plane.repository import DataPlaneRepository


@pytest.fixture()
def env(tmp_path):
    repo = DataPlaneRepository(tmp_path / "plane.sqlite3")
    cp = JobControlPlane(repo)
    store = LocalFileAdapter(tmp_path / "store")
    dv = DeliveryService(repo, store, uri_signer_secret="test-secret")
    yield {"repo": repo, "cp": cp, "store": store, "dv": dv, "tmp": tmp_path}
    repo.close()


def _make_ready_track(env, *, track_id=None, owner_scope=None, data=b"fake-render-wav-bytes"):
    repo, cp, store = env["repo"], env["cp"], env["store"]
    track_id = track_id or new_id("track")
    job_id = new_id("job")
    cp.enqueue(job_id=job_id, track_id=track_id, job_type="reconstruction")
    claimed = cp.claim(job_id=job_id, worker_id="worker-a")
    obj_id = new_id("object")
    key = f"moodify/tracks/{track_id}/jobs/{job_id}/renders/{obj_id}.wav"
    h = store.put("moodify", key, data)
    repo.register_track(track_id=track_id, source_hash="0" * 64, source_object_id=None, owner_scope=owner_scope)
    repo.register_object(object_id=obj_id, track_id=track_id, job_id=job_id, artifact_type="renders",
                         artifact_role="render_final", bucket="moodify", object_key=key,
                         content_hash=h, byte_size=len(data), producer="moodify-pipeline",
                         pipeline_version="pipeline-v0.1", retention_class="render_versioned")
    cp.complete(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a",
                ready_object_id=obj_id, verification_evidence=True)
    return track_id, obj_id


# TST-01 — READY only: non-READY track rejected
def test_tst01_ready_only(env):
    repo, cp, dv = env["repo"], env["cp"], env["dv"]
    track_id = new_id("track")
    job_id = new_id("job")
    repo.register_track(track_id=track_id, source_hash="0" * 64)
    cp.enqueue(job_id=job_id, track_id=track_id, job_type="reconstruction")  # QUEUED, never READY
    with pytest.raises(DeliveryError) as ei:
        dv.playback_metadata(track_id=track_id)
    assert ei.value.code == "TRACK_NOT_READY"


# TST-02 — Valid playback metadata for READY track
def test_tst02_valid_metadata(env):
    dv = env["dv"]
    track_id, obj_id = _make_ready_track(env)
    meta = dv.playback_metadata(track_id=track_id)
    assert isinstance(meta, PlaybackMetadata)
    assert meta.render_object_id == obj_id
    assert meta.playback_uri.startswith("moodify://deliver/")
    assert meta.supports_range is True
    assert meta.etag.startswith('"')


# TST-03 — Object missing: DB READY but store missing -> no URI
def test_tst03_object_missing(env):
    repo, store, dv = env["repo"], env["store"], env["dv"]
    track_id, obj_id = _make_ready_track(env)
    obj = repo.get_object(obj_id)
    store.delete(obj["bucket"], obj["object_key"])
    with pytest.raises(DeliveryError) as ei:
        dv.playback_metadata(track_id=track_id)
    assert ei.value.code == "OBJECT_NOT_FOUND"


# TST-04 — URL expiry refresh: expired URL rejects, refresh returns new URI, same identity
def test_tst04_url_expiry_refresh(env):
    dv = env["dv"]
    track_id, obj_id = _make_ready_track(env)
    meta = dv.playback_metadata(track_id=track_id)
    # simulate expiry by rewriting stored session? simpler: forge an expired URI
    from moodify.data_plane.delivery import DeliveryService

    dv2 = DeliveryService(env["repo"], env["store"], uri_signer_secret="test-secret")
    expired = dv2._sign_uri(track_id=track_id, render_object_id=obj_id,
                            expires_at=str(int(time.time()) - 10))
    with pytest.raises(DeliveryError) as ei:
        dv2._verify_uri(expired, track_id=track_id, render_object_id=obj_id)
    assert ei.value.code == "DELIVERY_URI_EXPIRED"
    # refresh: same track/render identity, new URI
    refreshed = dv.refresh(track_id=track_id)
    assert refreshed.render_object_id == obj_id
    assert refreshed.playback_uri != meta.playback_uri


# TST-05 — Range/seek: supports_range advertised; resolver returns object for byte-range delivery
def test_tst05_range_support(env):
    dv = env["dv"]
    track_id, obj_id = _make_ready_track(env)
    meta = dv.playback_metadata(track_id=track_id)
    assert meta.supports_range is True
    bucket, key = dv.resolve_object(meta.playback_uri, track_id=track_id, render_object_id=obj_id)
    assert bucket == "moodify" and key.endswith(".wav")


# TST-06 — Buffering recovery: refresh after network drop preserves identity (no reprocessing)
def test_tst06_buffering_recovery(env):
    dv = env["dv"]
    track_id, _ = _make_ready_track(env)
    m1 = dv.playback_metadata(track_id=track_id)
    m2 = dv.playback_metadata(track_id=track_id)
    assert m2.render_object_id == m1.render_object_id  # no reprocessing, same render


# TST-07 — Unauthorized access: wrong scope cannot obtain URI
def test_tst07_unauthorized(env):
    dv = env["dv"]
    track_id, obj_id = _make_ready_track(env, owner_scope="alice")
    with pytest.raises(DeliveryError) as ei:
        dv.playback_metadata(track_id=track_id, user_scope="bob")
    assert ei.value.code == "ACCESS_DENIED"
    # owner scope can
    meta = dv.playback_metadata(track_id=track_id, user_scope="alice")
    assert meta.render_object_id == obj_id


# TST-08 — No client secret: metadata carries only signed short-TTL URI, never credentials
def test_tst08_no_client_secret(env):
    dv = env["dv"]
    track_id, _ = _make_ready_track(env)
    meta = dv.playback_metadata(track_id=track_id)
    blob = meta.to_json()
    assert "accesskey" not in blob.lower() and "secret" not in blob.lower()
    assert "moodify://deliver/" in meta.playback_uri


# TST-09 — Playback failure isolation: delivery error never changes job state
def test_tst09_failure_isolation(env):
    repo, store, dv = env["repo"], env["store"], env["dv"]
    track_id, obj_id = _make_ready_track(env)
    obj = repo.get_object(obj_id)
    store.delete(obj["bucket"], obj["object_key"])
    try:
        dv.playback_metadata(track_id=track_id)
    except DeliveryError as e:
        assert e.code == "OBJECT_NOT_FOUND"
    job_row = repo._conn.execute(
        "SELECT current_state FROM jobs WHERE track_id=?", (track_id,)
    ).fetchone()
    assert job_row["current_state"] == "READY"  # unchanged (DLV-INV-09)


# TST-10 — Track identity stable: refresh keeps same track/render identity
def test_tst10_track_identity_stable(env):
    dv = env["dv"]
    track_id, obj_id = _make_ready_track(env)
    m1 = dv.playback_metadata(track_id=track_id)
    m2 = dv.refresh(track_id=track_id)
    assert m1.track_id == m2.track_id == track_id
    assert m1.render_object_id == m2.render_object_id == obj_id
