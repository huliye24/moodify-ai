"""StemStore persistence and billing-usage tests (LALAL-STEMS-001)."""

from __future__ import annotations

import json

import pytest

from moodify.stems.service import estimate_duration, estimate_pro_minutes
from moodify.stems.store import StemStatus, StemStore


def _make_job(store: StemStore, tmp_path, stems=("vocals", "drum")):
    source = tmp_path / "song.wav"
    source.write_bytes(b"x" * 1000)
    return store.create(
        source_name="song.wav",
        source_path=source,
        source_bytes=1000,
        stems=list(stems),
        extraction_level="deep_extraction",
        splitter="auto",
        duration_seconds=61.0,
        estimated_pro_minutes=estimate_pro_minutes(61.0, len(stems)),
    )


def test_create_get_roundtrip(tmp_path):
    store = StemStore(tmp_path / "stems.sqlite3")
    job = _make_job(store, tmp_path)

    got = store.get(job.job_id)
    assert got is not None
    assert got.job_id == job.job_id
    assert got.stems == ["vocals", "drum"]
    assert got.status == StemStatus.PROCESSING.value
    assert got.progress == 0
    assert got.source_name == "song.wav"
    assert got.source_bytes == 1000
    assert got.duration_seconds == 61.0
    assert got.estimated_pro_minutes == 4.0  # ceil(61/60)=2 * 2 stems
    assert got.dereverb_enabled is False
    assert got.task_ids == {}
    assert got.result_urls == {}
    assert got.finished_at is None


def test_update_submitted_and_status_transitions(tmp_path):
    store = StemStore(tmp_path / "stems.sqlite3")
    job = _make_job(store, tmp_path)

    store.update_submitted(job.job_id, "src_1", {"vocals": "t1", "drum": "t2"})
    got = store.get(job.job_id)
    assert got.source_id == "src_1"
    assert got.task_ids == {"vocals": "t1", "drum": "t2"}
    assert got.status == StemStatus.PROCESSING.value

    store.update_status(job.job_id, status=StemStatus.SUCCEEDED, progress=100,
                        result_urls={"vocals": "https://cdn/v.wav", "drum": "https://cdn/d.wav"})
    got = store.get(job.job_id)
    assert got.status == StemStatus.SUCCEEDED.value
    assert got.progress == 100
    assert got.result_urls == {"vocals": "https://cdn/v.wav", "drum": "https://cdn/d.wav"}
    assert got.finished_at is not None
    assert got.is_terminal

    store.update_status(job.job_id, status=StemStatus.FAILED, last_error="boom")
    got = store.get(job.job_id)
    assert got.status == StemStatus.FAILED.value
    assert "boom" in (got.last_error or "")


def test_persists_across_store_instances(tmp_path):
    db = tmp_path / "stems.sqlite3"
    store = StemStore(db)
    job = _make_job(store, tmp_path)
    store.update_submitted(job.job_id, "src_x", {"vocals": "t_x"})

    fresh = StemStore(db)
    got = fresh.get(job.job_id)
    assert got.source_id == "src_x"
    assert got.task_ids == {"vocals": "t_x"}


def test_list_filters_by_status(tmp_path):
    store = StemStore(tmp_path / "stems.sqlite3")
    j1 = _make_job(store, tmp_path)
    _make_job(store, tmp_path)
    store.update_status(j1.job_id, status=StemStatus.SUCCEEDED)

    all_jobs = store.list()
    assert len(all_jobs) == 2
    succeeded = store.list(status=StemStatus.SUCCEEDED.value)
    assert [j.job_id for j in succeeded] == [j1.job_id]
    assert store.list(status="NOPE") == []


def test_usage_aggregates(tmp_path):
    store = StemStore(tmp_path / "stems.sqlite3")
    j1 = _make_job(store, tmp_path, stems=("vocals",))
    _make_job(store, tmp_path, stems=("vocals", "drum", "bass"))
    store.update_status(j1.job_id, status=StemStatus.SUCCEEDED)

    usage = store.usage()
    assert usage["total_tasks"] == 2
    assert usage["succeeded"] == 1
    assert usage["failed"] == 0
    assert usage["total_source_bytes"] == 2000
    # 1 stem * 2 min + 3 stems * 2 min
    assert usage["total_estimated_pro_minutes"] == 8.0
    assert len(usage["recent"]) == 2
    assert json.loads(json.dumps(usage["recent"][0]["stems"]))  # JSON-safe


def test_usage_empty_db(tmp_path):
    usage = StemStore(tmp_path / "stems.sqlite3").usage()
    assert usage["total_tasks"] == 0
    assert usage["total_estimated_pro_minutes"] == 0.0


def test_delete_source_file_removes_copy(tmp_path):
    store = StemStore(tmp_path / "stems.sqlite3")
    job = _make_job(store, tmp_path)
    source = tmp_path / "song.wav"
    assert source.is_file()

    store.delete_source_file(job.job_id)
    assert not source.is_file()


def test_prune_old_sources_clears_stale(tmp_path):
    store = StemStore(tmp_path / "stems.sqlite3")
    job = _make_job(store, tmp_path)
    source = tmp_path / "song.wav"

    # Simulate an old job by rewriting its created_at.
    import sqlite3

    with sqlite3.connect(tmp_path / "stems.sqlite3") as con:
        con.execute(
            "UPDATE stem_jobs SET created_at='2020-01-01T00:00:00+00:00' WHERE job_id=?",
            (job.job_id,),
        )

    assert store.prune_old_sources(age_days=7) == 1
    assert not source.is_file()
    assert store.get(job.job_id).source_path == ""


def test_estimate_duration_and_minutes(mock_wav):
    assert estimate_duration(__import__("pathlib").Path(mock_wav)) == pytest.approx(10.0, abs=0.2)
    assert estimate_pro_minutes(10.0, 2) == 2  # ceil(10/60)=1 * 2
    assert estimate_pro_minutes(61.0, 1) == 2  # ceil(61/60)=2 * 1
    assert estimate_pro_minutes(None, 1) is None
