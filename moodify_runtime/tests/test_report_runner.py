"""Tests for report.py (daily report) and runner.py (task selection, queue processing)."""
import csv
import json
import tempfile
from pathlib import Path

import pytest

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.report import (
    _read_manifest, _to_float, _fmt_float, generate_daily_report,
)
from moodify_runtime.runner import (
    select_pending_tasks, MANIFEST_FIELDS,
)
from moodify_runtime.queue import load_queue


@pytest.fixture
def cfg():
    d = tempfile.mkdtemp()
    c = RuntimeConfig(project_root=Path(d), output_root=Path(d) / "outputs",
                      report_dir=Path(d) / "reports")
    c.output_root.mkdir(parents=True, exist_ok=True)
    c.report_dir.mkdir(parents=True, exist_ok=True)
    return c


class TestManifestReader:
    def test_read_missing_manifest(self):
        assert _read_manifest(Path("/nonexistent/manifest.csv")) == []

    def test_read_empty_manifest(self, cfg):
        p = cfg.output_root / "manifest.csv"
        p.write_text("")
        rows = _read_manifest(p)
        assert isinstance(rows, list)

    def test_read_populated_manifest(self, cfg):
        p = cfg.output_root / "manifest.csv"
        p.write_text("run_id,task_id,sample_id,preset\nR1,T1,S1,warm_vocal\n")
        rows = _read_manifest(p)
        assert len(rows) >= 1


class TestFloatHelpers:
    def test_to_float_normal(self):
        assert _to_float("3.14") == pytest.approx(3.14)

    def test_to_float_empty(self):
        assert _to_float("") is None

    def test_to_float_none(self):
        assert _to_float(None) is None

    def test_to_float_bad(self):
        assert _to_float("abc") is None

    def test_fmt_float_normal(self):
        assert _fmt_float(3.14159, digits=2) == "3.14"

    def test_fmt_float_none(self):
        assert _fmt_float(None) == "-"


class TestDailyReport:
    def test_no_runs_raises(self, cfg):
        cfg.output_root = Path(tempfile.mkdtemp())  # empty dir
        cfg.output_root.mkdir(parents=True, exist_ok=True)
        with pytest.raises(FileNotFoundError):
            generate_daily_report(cfg)


class TestTaskSelection:
    def test_select_pending(self):
        queue = [
            {"task_id": "A", "status": "pending", "priority": "1",
             "created_at": "2026-01-01"},
            {"task_id": "B", "status": "done", "priority": "1",
             "created_at": "2026-01-01"},
            {"task_id": "C", "status": "pending", "priority": "5",
             "created_at": "2026-01-02"},
        ]
        selected = select_pending_tasks(queue)
        assert len(selected) == 2
        assert {r["task_id"] for r in selected} == {"A", "C"}

    def test_select_with_limit(self):
        queue = [
            {"task_id": f"T{i}", "status": "pending", "priority": str(i),
             "created_at": f"2026-01-{i:02d}"}
            for i in range(1, 11)
        ]
        selected = select_pending_tasks(queue, limit=3)
        assert len(selected) == 3

    def test_select_empty(self):
        assert select_pending_tasks([]) == []

    def test_select_all_done(self):
        queue = [{"task_id": "D", "status": "done", "priority": "1",
                  "created_at": "2026-01-01"}]
        assert select_pending_tasks(queue) == []

    def test_retry_status_selected(self):
        queue = [{"task_id": "R", "status": "retry", "priority": "1",
                  "created_at": "2026-01-01"}]
        selected = select_pending_tasks(queue)
        assert len(selected) == 1

    def test_priority_sorting(self):
        queue = [
            {"task_id": "low", "status": "pending", "priority": "9",
             "created_at": "2026-01-01"},
            {"task_id": "high", "status": "pending", "priority": "1",
             "created_at": "2026-01-01"},
        ]
        selected = select_pending_tasks(queue)
        assert selected[0]["task_id"] == "high"


class TestManifestFields:
    def test_has_required_fields(self):
        required = ["run_id", "task_id", "sample_id", "input_path", "preset",
                     "status", "return_code", "elapsed_seconds",
                     "pseudo_mrs_before", "pseudo_mrs_after"]
        for field in required:
            assert field in MANIFEST_FIELDS, f"Missing: {field}"
