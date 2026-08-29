"""MFY-ALIYUN-DATA-NODE-001 worker serial-execution tests."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from moodify.node.config import NodeConfig
from moodify.node.queue import JobQueue
from moodify.node.resources import ResourceSnapshot
from moodify.node.worker import run_forever


class _StopOnPoll:
    """Replaces worker-module `time` so the first poll exits the loop."""

    def sleep(self, _seconds):
        raise KeyboardInterrupt


def _config(tmp_path, poll_seconds=0.01) -> NodeConfig:
    return NodeConfig(state_dir=tmp_path, output_root=tmp_path / "out", poll_seconds=poll_seconds)


def _source(tmp_path, name="song.wav"):
    source = tmp_path / name
    source.write_bytes(b"test")
    return source


def _queue(tmp_path) -> JobQueue:
    # Must equal NodeConfig(state_dir=tmp_path).db_path.
    return JobQueue(tmp_path / "node.sqlite3", lease_seconds=60)


def test_worker_runs_jobs_serially_without_overlap(monkeypatch, tmp_path):
    q = _queue(tmp_path)
    q.enqueue(_source(tmp_path), tmp_path / "out")
    q.enqueue(_source(tmp_path, "song2.wav"), tmp_path / "out")

    state = {"active": 0, "max_active": 0, "completed": 0}

    def fake_run(source, output_root, scan_profile_id):
        state["active"] += 1
        state["max_active"] = max(state["max_active"], state["active"])
        time.sleep(0.02)
        state["active"] -= 1
        state["completed"] += 1
        return Path(output_root) / "cases" / "case_x"

    monkeypatch.setattr("moodify.node.worker.run_data_factory", fake_run)
    monkeypatch.setattr("moodify.node.worker.time", _StopOnPoll())

    with pytest.raises(KeyboardInterrupt):
        run_forever(_config(tmp_path))

    assert state["max_active"] == 1  # never two heavy jobs at once
    assert state["completed"] == 2  # both jobs processed serially
    assert q.counts()["SUCCEEDED"] == 2


def test_worker_records_failure_with_error(monkeypatch, tmp_path):
    q = _queue(tmp_path)
    q.enqueue(_source(tmp_path), tmp_path / "out")

    def boom(source, output_root, scan_profile_id):
        raise RuntimeError("kaput")

    monkeypatch.setattr("moodify.node.worker.run_data_factory", boom)
    monkeypatch.setattr("moodify.node.worker.time", _StopOnPoll())

    with pytest.raises(KeyboardInterrupt):
        run_forever(_config(tmp_path))

    job = q.list("FAILED")[0]
    assert job.status == "FAILED"
    assert "kaput" in job.last_error
    assert job.attempts >= 1


def test_worker_defers_when_resources_insufficient(monkeypatch, tmp_path):
    q = _queue(tmp_path)
    q.enqueue(_source(tmp_path), tmp_path / "out")

    processed: list[str] = []

    def fake_run(source, output_root, scan_profile_id):
        processed.append(str(source))
        return Path(output_root) / "cases" / "case_x"

    monkeypatch.setattr("moodify.node.worker.run_data_factory", fake_run)
    snap = ResourceSnapshot(available_memory_mb=100.0, free_disk_gb=10.0)
    monkeypatch.setattr(
        "moodify.node.worker.safe_to_start", lambda *_: (False, snap, "low memory")
    )
    monkeypatch.setattr("moodify.node.worker.time", _StopOnPoll())

    with pytest.raises(KeyboardInterrupt):
        run_forever(_config(tmp_path))

    assert processed == []  # deferred, never crashed
    assert q.counts()["QUEUED"] == 1
