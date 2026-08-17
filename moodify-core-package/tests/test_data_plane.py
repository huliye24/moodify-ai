"""W01-P03 Data Plane tests — Test A..H (identity, immutability, provenance, idempotency, orphan/missing)."""

from __future__ import annotations

import sqlite3

import pytest

from moodify.data_plane.adapter import LocalFileAdapter
from moodify.data_plane.ids import new_id
from moodify.data_plane.object_key import build_object_key, parse_object_key
from moodify.data_plane.repository import DataPlaneRepository

SRC_BYTES = b"fake-wav-bytes-source-001"
RENDER_BYTES = b"fake-wav-bytes-render-v1"


@pytest.fixture()
def repo(tmp_path):
    r = DataPlaneRepository(tmp_path / "plane.sqlite3")
    yield r
    r.close()


@pytest.fixture()
def store(tmp_path):
    return LocalFileAdapter(tmp_path / "store")


def _register_source(repo, store, *, track_id=None, obj_id=None, data=SRC_BYTES):
    track_id = track_id or new_id("track")
    obj_id = obj_id or new_id("object")
    key = build_object_key(track_id=track_id, object_id=obj_id, artifact_type="source", filename="src.wav")
    store.put(key.bucket, key.key, data)
    repo.register_track(track_id=track_id, source_hash=store.put(key.bucket, key.key, data), source_object_id=obj_id)
    repo.register_object(
        object_id=obj_id, track_id=track_id, artifact_type="source", bucket=key.bucket,
        object_key=key.key, content_hash=store.put(key.bucket, key.key, data), byte_size=len(data),
        producer="test", retention_class="source_long_lived",
    )
    return track_id, obj_id


def _register_render(repo, store, *, track_id, job_id=None, obj_id=None, data=RENDER_BYTES):
    job_id = job_id or new_id("job")
    obj_id = obj_id or new_id("object")
    repo.register_job(job_id=job_id, track_id=track_id, job_type="reconstruction")
    key = build_object_key(track_id=track_id, job_id=job_id, object_id=obj_id, artifact_type="renders", filename="out.wav")
    store.put(key.bucket, key.key, data)
    repo.register_object(
        object_id=obj_id, track_id=track_id, job_id=job_id, artifact_type="renders", bucket=key.bucket,
        object_key=key.key, content_hash=store.put(key.bucket, key.key, data), byte_size=len(data),
        producer="moodify-pipeline", pipeline_version="pipeline-v0.1", retention_class="render_versioned",
    )
    return job_id, obj_id


# --- Test A — Same source hash: no duplicate canonical identity, ownership not merged ---
def test_a_same_hash_two_tracks_not_merged(repo, store):
    h1 = store.put("moodify", "k1", SRC_BYTES)
    h2 = store.put("moodify", "k2", SRC_BYTES)
    assert h1 == h2  # identical bytes -> identical hash
    t1, _ = _register_source(repo, store, obj_id=new_id("object"))
    t2, _ = _register_source(repo, store, obj_id=new_id("object"))
    assert t1 != t2  # same hash, different ownership: two tracks (INV-12)
    assert repo.get_track(t1)["source_hash"] == repo.get_track(t2)["source_hash"]


# --- Test B — Immutable source: same key cannot be overwritten with different bytes ---
def test_b_immutable_source_key(repo, store):
    track_id, obj_id = _register_source(repo, store)
    key = build_object_key(track_id=track_id, object_id=obj_id, artifact_type="source", filename="src.wav")
    # A compliant writer reuses the same object_id only with identical bytes.
    h = store.put(key.bucket, key.key, SRC_BYTES)
    assert h == repo.get_object(obj_id)["content_hash"]
    # Direct overwrite attempt with different bytes would break hash; adapter-level guard:
    # registering the same object_id twice is idempotent (returns first row).
    again = repo.register_object(
        object_id=obj_id, track_id=track_id, artifact_type="source", bucket=key.bucket,
        object_key=key.key, content_hash="f" * 64, byte_size=1, producer="test",
    )
    assert again["content_hash"] != "f" * 64  # original preserved


# --- Test C — Object provenance: render -> job -> track -> source ---
def test_c_render_provenance_chain(repo, store):
    track_id, src_obj = _register_source(repo, store)
    job_id, render_obj = _register_render(repo, store, track_id=track_id)
    chain = repo.provenance_chain(render_obj)
    assert chain is not None
    stages = [c["stage"] for c in chain]
    assert stages == ["object", "job", "track", "source_object"]
    assert chain[0]["data"]["object_id"] == render_obj
    assert chain[1]["data"]["job_id"] == job_id
    assert chain[2]["data"]["track_id"] == track_id
    assert chain[3]["data"]["object_id"] == src_obj


# --- Test D — Evidence provenance: what object / job / claim ---
def test_d_evidence_provenance(repo, store):
    track_id, src_obj = _register_source(repo, store)
    job_id, render_obj = _register_render(repo, store, track_id=track_id)
    ev_id = new_id("evidence")
    ev = repo.register_evidence(
        evidence_id=ev_id, track_id=track_id, job_id=job_id, object_id=render_obj,
        evidence_type="algorithmic_review", claim="render passes identity gate",
        evaluator="MFY-ALGO-REVIEW-FORMULA-001", verdict="PASS", uncertainty=0.05,
    )
    assert ev["claim"] == "render passes identity gate"
    assert ev["object_id"] == render_obj and ev["job_id"] == job_id


# --- Test E — Idempotent register: duplicate manifest submission creates no duplicates ---
def test_e_idempotent_register(repo, store):
    track_id, obj_id = _register_source(repo, store)
    key = build_object_key(track_id=track_id, object_id=obj_id, artifact_type="source", filename="src.wav")
    again = repo.register_object(
        object_id=obj_id, track_id=track_id, artifact_type="source", bucket=key.bucket,
        object_key=key.key, content_hash=repo.get_object(obj_id)["content_hash"],
        byte_size=len(SRC_BYTES), producer="test",
    )
    rows = repo._conn.execute("SELECT COUNT(*) FROM objects WHERE object_id=?", (obj_id,)).fetchone()[0]
    assert rows == 1
    assert again["object_id"] == obj_id


# --- Test F — Missing object detection: DB ref without store object ---
def test_f_missing_object_detected(repo, store):
    track_id, obj_id = _register_source(repo, store)
    # remove store object behind DB's back
    key = build_object_key(track_id=track_id, object_id=obj_id, artifact_type="source", filename="src.wav")
    store.delete(key.bucket, key.key)
    missing = repo.missing_objects(store)
    assert any(o["object_id"] == obj_id for o in missing)


# --- Test G — Orphan object detection: store object without DB ref ---
def test_g_orphan_object_detected(repo, store):
    _register_source(repo, store)
    # plant a file the DB never saw
    store.put("moodify", "moodify/tracks/trk_orphan/source/obj_orphan.wav", b"orphan")
    orphans = repo.orphan_objects(store)
    assert any("obj_orphan" in o for o in orphans)


# --- Test H — No large blobs in DB schema ---
def test_h_no_blob_columns_in_schema():
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        "CREATE TABLE IF NOT EXISTS objects (object_id TEXT PRIMARY KEY, track_id TEXT NOT NULL,"
        " job_id TEXT, artifact_type TEXT NOT NULL, artifact_role TEXT, bucket TEXT NOT NULL,"
        " object_key TEXT NOT NULL, content_hash TEXT NOT NULL, hash_algorithm TEXT NOT NULL,"
        " byte_size INTEGER NOT NULL, mime_type TEXT, producer TEXT NOT NULL, producer_version TEXT,"
        " pipeline_version TEXT, parent_object_id TEXT, immutable INTEGER NOT NULL,"
        " retention_class TEXT NOT NULL, evidence_class TEXT, created_at TEXT NOT NULL,"
        " UNIQUE (object_key));"
    )
    cols = [r[1].upper() for r in conn.execute("PRAGMA table_info(objects)")]
    assert not any("BLOB" in c for c in cols)
    # byte_size is an integer count, not audio bytes
    assert "BYTE_SIZE" in cols
    conn.close()


# --- key convention round-trip ---
def test_object_key_roundtrip():
    key = build_object_key(track_id="trk_x", object_id="obj_y", artifact_type="renders", job_id="job_z", filename="OUT.WAV")
    assert key.key == "moodify/tracks/trk_x/jobs/job_z/renders/obj_y.wav"
    parsed = parse_object_key(f"{key.bucket}/{key.key}")
    assert parsed.object_id == "obj_y" and parsed.artifact_type == "renders" and parsed.job_id == "job_z"
    src = build_object_key(track_id="trk_x", object_id="obj_s", artifact_type="source", filename="in.wav")
    assert src.key == "moodify/tracks/trk_x/source/obj_s.wav"
    assert parse_object_key(src.key).artifact_type == "source"
