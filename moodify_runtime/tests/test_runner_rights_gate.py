"""Rights-gate coverage for run_daily, run_operator_job, and CLI flags.

Phase 1A of DSK-MFY-THICKNESS road-widening: verifies that the per-task
rights gate engages fail-closed in the core execution path, operator scope
isolation prevents cross-job task execution, and CLI flags are wired through.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ── Helpers ────────────────────────────────────────────────────────────


def _task(task_id="t1", reason="daily_run", input_path="/tmp/s.wav"):
    return {
        "task_id": task_id,
        "sample_id": "s1",
        "preset": "warm_vocal",
        "input_path": input_path,
        "status": "pending",
        "priority": 5,
        "created_at": "2026-01-01T00:00:00Z",
        "attempts": 0,
        "reason": reason,
    }


def _write_queue(queue_path, rows):
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
    )


def _write_manifest(manifest_path, assets):
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {"schema_version": "1.0.0", "gate_id": "GATE_1", "assets": assets},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


class FakeCfg:
    """Minimal config stand-in for run_daily / operator paths."""

    def __init__(self, tmp_path, extra=None):
        self.project_root = tmp_path
        self.output_root = tmp_path / "output"
        self.queue_path = tmp_path / "run_queue.jsonl"
        self.python = sys.executable
        self.min_free_disk_gb = "0.1"
        self.keep_last_n_runs = "3"
        self.max_retries_per_task = "0"
        self.stop_on_first_success_template = "false"
        self.sleep_seconds_between_tasks = "0"
        self.command_templates = [
            "{python} -c \"print('ok')\""
        ]
        self.env = {}
        self.timeout_seconds_per_task = 30
        self.input_dirs = str(tmp_path / "input")
        self.recurse = "false"
        self._registry_path = tmp_path / "input_registry.jsonl"
        self._tidal_events_path = tmp_path / "tidal_events.jsonl"
        self._tidal_heartbeat_path = tmp_path / "tidal_heartbeat.json"
        self.craft_memory_dir = str(tmp_path / "craft_memory")
        self.operator_jobs_path = (
            tmp_path / "operator_data" / "operator_jobs.jsonl"
        )
        self.operator_reports_path = (
            tmp_path / "operator_data" / "operator_reports"
        )
        self.operator_deliveries_path = (
            tmp_path / "operator_data" / "operator_deliveries.jsonl"
        )
        self.report_dir = tmp_path / "reports"
        self.manifest_dir = tmp_path / "manifests"
        self.operator_detail_dir = tmp_path / "operator_data" / "operator_job_details"
        self.operator_report_dir = tmp_path / "reports" / "operator_runs"
        self.work_dir = tmp_path / "work"
        self.bridge_dir = tmp_path / "bridge"

    def resolved(self):
        return self


# ── Fake run_command (avoid actual subprocess) ────────────────────────

_SENTINEL = object()


# ═══════════════════════════════════════════════════════════════════════
# TestRunDailyRightsGateBlocked
# ═══════════════════════════════════════════════════════════════════════


class TestRunDailyRightsGateBlocked:
    """Per-task rights gate in run_daily."""

    def test_no_manifest_executes_all(self, tmp_path, monkeypatch):
        """Without a manifest the gate is not engaged — existing behaviour."""
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        _write_queue(cfg.queue_path, [_task("t1"), _task("t2")])

        calls = []
        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: calls.append(1) or {
                "return_code": 0, "elapsed_seconds": 0.1,
                "stdout_tail": "", "stderr_tail": "",
            },
        )

        summary = run_daily(cfg)
        assert summary["success"] == 2
        assert summary["rights_blocked"] == 0
        assert len(calls) == 2

    def test_authorized_tasks_execute(self, tmp_path, monkeypatch):
        """All tasks whose source matches an authorized asset run."""
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(tmp_path / "audio" / "song.wav"), "status": "ready"},
        ])
        task_path = tmp_path / "audio" / "song.wav"
        task_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.write_text("fake audio")

        _write_queue(cfg.queue_path, [_task("t1", input_path=str(task_path))])

        calls = []
        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: calls.append(1) or {
                "return_code": 0, "elapsed_seconds": 0.1,
                "stdout_tail": "", "stderr_tail": "",
            },
        )

        summary = run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A1")
        assert summary["success"] == 1
        assert summary["rights_blocked"] == 0

    def test_unauthorized_path_blocked(self, tmp_path, monkeypatch):
        """Task whose source path doesn't match the asset is blocked."""
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(tmp_path / "audio" / "authorized.wav"), "status": "ready"},
        ])
        bad = tmp_path / "audio" / "unauthorized.wav"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text("fake")

        _write_queue(cfg.queue_path, [_task("t1", input_path=str(bad))])

        ran = []
        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: ran.append(1)
            or {"return_code": 0, "elapsed_seconds": 0, "stdout_tail": "", "stderr_tail": ""},
        )

        summary = run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A1")
        assert summary["rights_blocked"] == 1
        assert summary["success"] == 0
        assert len(ran) == 0  # never executed

    def test_blocked_task_does_not_increment_attempts(self, tmp_path, monkeypatch):
        """The attempt counter stays at 0 for blocked tasks."""
        from moodify_runtime.runner import run_daily
        from moodify_runtime.queue import load_queue

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(tmp_path / "good.wav"), "status": "ready"},
        ])
        bad = tmp_path / "bad.wav"
        bad.write_text("fake")

        _write_queue(cfg.queue_path, [_task("t1", input_path=str(bad))])

        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: pytest.fail("should not execute"),
        )

        run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A1")
        queue_after = load_queue(cfg)
        blocked = [r for r in queue_after if r["task_id"] == "t1"]
        assert blocked[0]["attempts"] == 0
        assert blocked[0]["status"] == "rights_blocked"

    def test_dry_run_skips_gate(self, tmp_path, monkeypatch):
        """Dry-run does not engage the rights gate."""
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(tmp_path / "good.wav"), "status": "ready"},
        ])
        bad = tmp_path / "bad.wav"
        bad.write_text("fake")

        _write_queue(cfg.queue_path, [_task("t1", input_path=str(bad))])

        summary = run_daily(cfg, dry_run=True, rights_manifest=str(manifest), rights_asset_id="A1")
        assert summary["dry_run_tasks"] == 1
        assert summary["rights_blocked"] == 0

    def test_all_blocked_no_execution(self, tmp_path, monkeypatch):
        """When every task is blocked, nothing executes and counts are correct."""
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(tmp_path / "good.wav"), "status": "ready"},
        ])
        tasks = []
        for i, name in enumerate(["b1.wav", "b2.wav", "b3.wav"]):
            p = tmp_path / name
            p.write_text("fake")
            tasks.append(_task(f"t{i}", input_path=str(p)))
        _write_queue(cfg.queue_path, tasks)

        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: pytest.fail("no execution expected"),
        )

        summary = run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A1")
        assert summary["rights_blocked"] == 3
        assert summary["success"] == 0
        assert summary["failed"] == 0

    def test_manifest_missing_fail_open_preserved(self, tmp_path, monkeypatch):
        """A missing manifest is handled by authorize_audio_source as blocked,
        not a fatal crash of run_daily."""
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        missing = tmp_path / "nonexistent.json"
        _write_queue(cfg.queue_path, [_task("t1", input_path=str(tmp_path / "x.wav"))])
        (tmp_path / "x.wav").write_text("fake")

        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: pytest.fail("should not execute"),
        )

        summary = run_daily(cfg, rights_manifest=str(missing), rights_asset_id="A1")
        assert summary["rights_blocked"] == 1

    def test_mixed_authorized_and_blocked(self, tmp_path, monkeypatch):
        """One authorized task runs, one blocked task does not."""
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        good = tmp_path / "good.wav"
        good.write_text("fake")
        bad = tmp_path / "bad.wav"
        bad.write_text("fake")
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(good), "status": "ready"},
        ])

        _write_queue(cfg.queue_path, [
            _task("t-good", input_path=str(good)),
            _task("t-bad", input_path=str(bad)),
        ])

        calls = []
        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: calls.append(1)
            or {"return_code": 0, "elapsed_seconds": 0, "stdout_tail": "", "stderr_tail": ""},
        )

        summary = run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A1")
        assert summary["success"] == 1
        assert summary["rights_blocked"] == 1
        assert len(calls) == 1


# ═══════════════════════════════════════════════════════════════════════
# TestOperatorJobScopeIsolation
# ═══════════════════════════════════════════════════════════════════════


class TestOperatorJobScopeIsolation:
    """run_operator_job only executes tasks belonging to its own job."""

    def test_only_own_tasks_executed(self, tmp_path, monkeypatch):
        from moodify_runtime.operator_console import run_operator_job, create_operator_job

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        good = tmp_path / "good.wav"
        good.write_text("fake")
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(good), "status": "ready"},
        ])

        job = create_operator_job(cfg, source_audio=str(good), processing_depth="quick_scan",
                                  project_label="proj", priority=5)
        job_id = job["job_id"]

        _write_queue(cfg.queue_path, [
            _task("t-job", reason=f"operator_job:{job_id}:proj", input_path=str(good)),
            _task("t-other", reason="daily_run", input_path=str(good)),
        ])

        calls = []
        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: calls.append(a)
            or {"return_code": 0, "elapsed_seconds": 0, "stdout_tail": "", "stderr_tail": ""},
        )

        run_operator_job(cfg, job_id=job_id, dry_run=False,
                         rights_manifest=str(manifest), rights_asset_id="A1")

        from moodify_runtime.queue import load_queue
        queue_after = load_queue(cfg)
        other = [r for r in queue_after if r["task_id"] == "t-other"]
        assert other[0]["status"] == "pending"

    def test_no_pending_for_job_fails_cleanly(self, tmp_path):
        from moodify_runtime.operator_console import run_operator_job, create_operator_job

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": "/nonexistent", "status": "ready"},
        ])
        _write_queue(cfg.queue_path, [_task("t-other", reason="daily_run")])

        job = create_operator_job(cfg, source_audio="/nonexistent",
                                  processing_depth="quick_scan", project_label="p", priority=5)

        result = run_operator_job(cfg, job_id=job["job_id"], dry_run=False,
                                  rights_manifest=str(manifest), rights_asset_id="A1")
        assert result["status"] == "failed"
        assert "No pending tasks for this job" in result["error"]

    def test_other_job_tasks_untouched(self, tmp_path, monkeypatch):
        from moodify_runtime.operator_console import run_operator_job, create_operator_job

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        good = tmp_path / "good.wav"
        good.write_text("fake")
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(good), "status": "ready"},
        ])

        job = create_operator_job(cfg, source_audio=str(good), processing_depth="quick_scan",
                                  project_label="p", priority=5)
        job_id = job["job_id"]

        _write_queue(cfg.queue_path, [
            _task("t-j1", reason=f"operator_job:{job_id}:p", input_path=str(good)),
            _task("t-j2", reason="operator_job:J2:p", input_path=str(good)),
        ])

        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: {"return_code": 0, "elapsed_seconds": 0, "stdout_tail": "", "stderr_tail": ""},
        )

        run_operator_job(cfg, job_id=job_id, dry_run=False,
                         rights_manifest=str(manifest), rights_asset_id="A1")

        from moodify_runtime.queue import load_queue
        queue_after = load_queue(cfg)
        j2 = [r for r in queue_after if r["task_id"] == "t-j2"]
        assert j2[0]["status"] == "pending"

    def test_dry_run_bypasses_preflight(self, tmp_path):
        from moodify_runtime.operator_console import run_operator_job, create_operator_job

        cfg = FakeCfg(tmp_path)
        _write_queue(cfg.queue_path, [])

        job = create_operator_job(cfg, source_audio="/x.wav",
                                  processing_depth="quick_scan", project_label="p", priority=5)

        result = run_operator_job(cfg, job_id=job["job_id"], dry_run=True)
        assert result["dry_run"] is True

    def test_missing_rights_manifest_blocked_in_live(self, tmp_path):
        from moodify_runtime.operator_console import run_operator_job, create_operator_job

        cfg = FakeCfg(tmp_path)
        good = tmp_path / "good.wav"
        good.write_text("fake")

        job = create_operator_job(cfg, source_audio=str(good), processing_depth="quick_scan",
                                  project_label="p", priority=5)
        job_id = job["job_id"]

        _write_queue(cfg.queue_path, [_task("t1", reason=f"operator_job:{job_id}:p", input_path=str(good))])

        result = run_operator_job(cfg, job_id=job_id, dry_run=False)
        assert result["status"] == "failed"
        assert "rights_manifest" in result["error"].lower()


# ═══════════════════════════════════════════════════════════════════════
# TestRightsGateFailClosed
# ═══════════════════════════════════════════════════════════════════════


class TestRightsGateFailClosed:
    """Edge cases for the rights gate — malformed manifests, bad inputs."""

    def test_malformed_manifest_blocks_all(self, tmp_path, monkeypatch):
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        manifest.write_text("not json", encoding="utf-8")
        (tmp_path / "x.wav").write_text("fake")
        _write_queue(cfg.queue_path, [_task("t1", input_path=str(tmp_path / "x.wav"))])

        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: pytest.fail("should not execute"),
        )

        summary = run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A1")
        assert summary["rights_blocked"] == 1

    def test_empty_assets_blocks_all(self, tmp_path, monkeypatch):
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [])
        (tmp_path / "x.wav").write_text("fake")
        _write_queue(cfg.queue_path, [_task("t1", input_path=str(tmp_path / "x.wav"))])

        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: pytest.fail("should not execute"),
        )

        summary = run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A1")
        assert summary["rights_blocked"] == 1

    def test_pending_asset_blocks(self, tmp_path, monkeypatch):
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(tmp_path / "x.wav"), "status": "pending"},
        ])
        (tmp_path / "x.wav").write_text("fake")
        _write_queue(cfg.queue_path, [_task("t1", input_path=str(tmp_path / "x.wav"))])

        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: pytest.fail("should not execute"),
        )

        summary = run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A1")
        assert summary["rights_blocked"] == 1

    def test_blocked_asset_blocks(self, tmp_path, monkeypatch):
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(tmp_path / "x.wav"), "status": "blocked"},
        ])
        (tmp_path / "x.wav").write_text("fake")
        _write_queue(cfg.queue_path, [_task("t1", input_path=str(tmp_path / "x.wav"))])

        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: pytest.fail("should not execute"),
        )

        summary = run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A1")
        assert summary["rights_blocked"] == 1

    def test_unknown_asset_id_blocked(self, tmp_path, monkeypatch):
        from moodify_runtime.runner import run_daily

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(tmp_path / "x.wav"), "status": "ready"},
        ])
        (tmp_path / "x.wav").write_text("fake")
        _write_queue(cfg.queue_path, [_task("t1", input_path=str(tmp_path / "x.wav"))])

        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: pytest.fail("should not execute"),
        )

        summary = run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A2")
        assert summary["rights_blocked"] == 1

    def test_rights_blocked_status_persists_in_queue(self, tmp_path, monkeypatch):
        from moodify_runtime.runner import run_daily
        from moodify_runtime.queue import load_queue

        cfg = FakeCfg(tmp_path)
        manifest = tmp_path / "rights.json"
        _write_manifest(manifest, [
            {"asset_id": "A1", "source_path": str(tmp_path / "good.wav"), "status": "ready"},
        ])
        (tmp_path / "bad.wav").write_text("fake")
        _write_queue(cfg.queue_path, [_task("t1", input_path=str(tmp_path / "bad.wav"))])

        monkeypatch.setattr(
            "moodify_runtime.runner.run_command",
            lambda *a, **kw: pytest.fail("should not execute"),
        )

        run_daily(cfg, rights_manifest=str(manifest), rights_asset_id="A1")
        rows = load_queue(cfg)
        t = [r for r in rows if r["task_id"] == "t1"]
        assert t[0]["status"] == "rights_blocked"
        assert "rights:" in str(t[0].get("last_error", ""))


# ═══════════════════════════════════════════════════════════════════════
# TestCliRightsFlags
# ═══════════════════════════════════════════════════════════════════════


class TestCliRightsFlags:
    """CLI parser accepts rights flags on relevant subcommands."""

    def test_run_accepts_rights_flags(self):
        from moodify_runtime.cli import build_parser
        p = build_parser()
        args = p.parse_args(["run", "--rights-manifest", "rm.json", "--rights-asset-id", "A1"])
        assert args.rights_manifest == "rm.json"
        assert args.rights_asset_id == "A1"

    def test_all_accepts_rights_flags(self):
        from moodify_runtime.cli import build_parser
        p = build_parser()
        args = p.parse_args(["all", "--rights-manifest", "rm.json", "--rights-asset-id", "A1"])
        assert args.rights_manifest == "rm.json"
        assert args.rights_asset_id == "A1"

    def test_runtime_supervisor_start_accepts_rights_flags(self):
        from moodify_runtime.cli import build_parser
        p = build_parser()
        args = p.parse_args(["runtime-supervisor-start", "--rights-manifest", "rm.json", "--rights-asset-id", "A1"])
        assert args.rights_manifest == "rm.json"
        assert args.rights_asset_id == "A1"

    def test_craft_run_accepts_rights_flags(self):
        from moodify_runtime.cli import build_parser
        p = build_parser()
        args = p.parse_args(["craft-run", "--wav", "test.wav", "--rights-manifest", "rm.json", "--rights-asset-id", "A1"])
        assert args.rights_manifest == "rm.json"
        assert args.rights_asset_id == "A1"

    def test_run_without_rights_flags_defaults(self):
        from moodify_runtime.cli import build_parser
        p = build_parser()
        args = p.parse_args(["run"])
        assert args.rights_manifest is None
        assert args.rights_asset_id == ""

    def test_passthrough_to_run_daily(self, tmp_path, monkeypatch):
        from moodify_runtime.cli import build_parser

        monkeypatch.setattr("moodify_runtime.cli.load_config", lambda _: FakeCfg(tmp_path))
        caught = None

        def _capture(*a, **kw):
            nonlocal caught
            caught = kw
            return {"success": 0, "failed": 0, "rights_blocked": 0, "tasks": []}

        monkeypatch.setattr("moodify_runtime.cli.run_daily", _capture)

        p = build_parser()
        args = p.parse_args(["run", "--rights-manifest", "rm.json", "--rights-asset-id", "A1"])
        from moodify_runtime.cli import main
        main(["run", "--rights-manifest", "rm.json", "--rights-asset-id", "A1"])

        assert caught is not None
        assert caught["rights_manifest"] == "rm.json"
        assert caught["rights_asset_id"] == "A1"
