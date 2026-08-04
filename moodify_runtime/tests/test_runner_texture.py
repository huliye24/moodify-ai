"""Characterization tests for run_daily before temporal-texture split.

Freeze observable behavior: dry-run, rights gate (fail-closed), retry loop,
manifest/summary recording. DSK-MFY-TEMPORAL-TEXTURE-001 wave 1.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from moodify_runtime.runner import run_daily  # noqa: E402
from moodify_runtime.utils import read_csv_rows, read_json  # noqa: E402


def _task(task_id="t1", input_path="/tmp/s.wav"):
    return {
        "task_id": task_id, "sample_id": "s1", "preset": "warm_vocal",
        "input_path": input_path, "status": "pending", "priority": 5,
        "created_at": "2026-01-01T00:00:00Z", "attempts": 0,
    }


def _write_queue(queue_path, rows):
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
    )


class FakeCfg:
    def __init__(self, tmp_path):
        self.project_root = tmp_path
        self.output_root = tmp_path / "output"
        self.queue_path = tmp_path / "run_queue.jsonl"
        self.python = sys.executable
        self.min_free_disk_gb = "0.1"
        self.keep_last_n_runs = "3"
        self.max_retries_per_task = "0"
        self.stop_on_first_success_template = "false"
        self.sleep_seconds_between_tasks = "0"
        self.command_templates = ["{python} -c \"print('ok')\""]
        self.env = {}
        self.timeout_seconds_per_task = 30
        self.input_dirs = str(tmp_path / "input")
        self.recurse = "false"
        self._registry_path = tmp_path / "input_registry.jsonl"
        self._tidal_events_path = tmp_path / "tidal_events.jsonl"
        self._tidal_heartbeat_path = tmp_path / "tidal_heartbeat.json"
        self.craft_memory_dir = str(tmp_path / "craft_memory")

    def resolved(self):
        return self


def _ok_command(*_a, **_kw):
    return {"return_code": 0, "elapsed_seconds": 0.1,
            "stdout_tail": "ok", "stderr_tail": ""}


def _fail_command(*_a, **_kw):
    return {"return_code": 1, "elapsed_seconds": 0.1,
            "stdout_tail": "", "stderr_tail": "boom"}


def _setup(tmp_path, tasks, **cfg_kw):
    cfg = FakeCfg(tmp_path)
    _write_queue(cfg.queue_path, tasks)
    (tmp_path / "x.wav").write_text("fake")
    return cfg


class TestDryRun:
    def test_dry_run_never_invokes_command(self, tmp_path, monkeypatch) -> None:
        called = []
        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: called.append(a) or _ok_command(),
        )
        cfg = _setup(tmp_path, [_task()])
        summary = run_daily(cfg, dry_run=True)
        assert called == []
        assert summary["dry_run_tasks"] == 1
        assert summary["success"] == 0
        assert summary["failed"] == 0


class TestRightsGate:
    def test_rights_blocked_task_not_executed(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(
            "moodify_runtime.runner.run_command", _ok_command
        )
        monkeypatch.setattr(
            "moodify_runtime.runner.authorize_audio_source",
            lambda *_a, **_kw: (False, "not in manifest"),
        )
        cfg = _setup(tmp_path, [_task()])
        summary = run_daily(cfg, rights_manifest="m.yaml", rights_asset_id="a1")
        assert summary["rights_blocked"] == 1
        assert summary["success"] == 0
        assert summary["failed"] == 0
        # queue row updated to rights_blocked
        rows = [json.loads(l) for l in
                cfg.queue_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert rows[0]["status"] == "rights_blocked"

    def test_rights_gate_allows_execution(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(
            "moodify_runtime.runner.run_command", _ok_command
        )
        monkeypatch.setattr(
            "moodify_runtime.runner.authorize_audio_source",
            lambda *_a, **_kw: (True, ""),
        )
        cfg = _setup(tmp_path, [_task()])
        summary = run_daily(cfg, rights_manifest="m.yaml", rights_asset_id="a1")
        assert summary["rights_blocked"] == 0
        assert summary["success"] == 1


class TestTaskLifecycle:
    def test_success_task_recorded_in_manifest(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("moodify_runtime.runner.run_command", _ok_command)
        cfg = _setup(tmp_path, [_task()])
        summary = run_daily(cfg)
        assert summary["success"] == 1
        run_dir = Path(summary["run_dir"])
        rows = read_csv_rows(run_dir / "manifest.csv")
        assert len(rows) == 1
        assert rows[0]["task_id"] == "t1"
        assert rows[0]["status"] == "done"
        assert rows[0]["return_code"] == "0"

    def test_failed_task_recorded(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("moodify_runtime.runner.run_command", _fail_command)
        cfg = _setup(tmp_path, [_task()])
        summary = run_daily(cfg)
        assert summary["failed"] == 1
        run_dir = Path(summary["run_dir"])
        rows = read_csv_rows(run_dir / "manifest.csv")
        assert rows[0]["status"] == "failed"
        assert "boom" in rows[0]["error"]
        # full error log written
        assert (run_dir / "s1" / "warm_vocal" / ".moodify_error.log").exists()

    def test_retry_succeeds_on_second_attempt(self, tmp_path, monkeypatch) -> None:
        calls = {"n": 0}
        def flaky(*_a, **_kw):
            calls["n"] += 1
            return _fail_command() if calls["n"] == 1 else _ok_command()

        monkeypatch.setattr("moodify_runtime.runner.run_command", flaky)
        cfg = _setup(tmp_path, [_task()], max_retries_per_task="1")
        cfg.max_retries_per_task = "1"
        summary = run_daily(cfg)
        assert summary["success"] == 1
        assert calls["n"] == 2

    def test_insufficient_disk_records_fatal(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("moodify_runtime.runner.run_command", _ok_command)
        monkeypatch.setattr(
            "moodify_runtime.runner.check_disk_space",
            lambda *_a, **_kw: (False, 0.01),
        )
        cfg = _setup(tmp_path, [_task()])
        summary = run_daily(cfg)
        assert "fatal_error" in summary
        assert "disk" in summary["fatal_error"].lower()

    def test_summary_json_has_expected_keys(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("moodify_runtime.runner.run_command", _ok_command)
        cfg = _setup(tmp_path, [_task()])
        summary = run_daily(cfg)
        run_dir = Path(summary["run_dir"])
        data = read_json(run_dir / "summary.json")
        for key in ("run_id", "started_at", "success", "failed", "tasks",
                    "total_selected", "finished_at"):
            assert key in data
