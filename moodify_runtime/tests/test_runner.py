"""Tests for runner."""
import tempfile
from pathlib import Path
from moodify_runtime.runner import select_pending_tasks, replace_task, MANIFEST_FIELDS
from moodify_runtime.config import RuntimeConfig


class TestSelect:
    def test_empty(self):
        assert select_pending_tasks([]) == []
    def test_pending(self):
        q = [{"task_id": "A", "status": "pending", "priority": "1", "created_at": "2026-01-01"}]
        assert len(select_pending_tasks(q)) == 1
    def test_done_filtered(self):
        q = [{"task_id": "A", "status": "done", "priority": "1", "created_at": "2026-01-01"}]
        assert select_pending_tasks(q) == []
    def test_retry(self):
        q = [{"task_id": "A", "status": "retry", "priority": "1", "created_at": "2026-01-01"}]
        assert len(select_pending_tasks(q)) == 1
    def test_limit(self):
        q = [{"task_id": f"T{i}", "status": "pending", "priority": str(i), "created_at": f"2026-01-{i:02d}"} for i in range(1, 11)]
        assert len(select_pending_tasks(q, limit=3)) == 3
    def test_priority_sort(self):
        q = [{"task_id": "low", "status": "pending", "priority": "9", "created_at": "2026-01-01"},
             {"task_id": "high", "status": "pending", "priority": "1", "created_at": "2026-01-01"}]
        assert select_pending_tasks(q)[0]["task_id"] == "high"


class TestReplaceTask:
    def test_replaces(self):
        q = [{"task_id": "A", "status": "pending", "sample_id": "s1", "preset": "warm_vocal"}]
        r = replace_task(q, {"task_id": "A", "status": "running", "sample_id": "s1", "preset": "warm_vocal"})
        assert r[0]["status"] == "running"


class TestManifestFields:
    def test_required(self):
        for f in ["run_id", "task_id", "sample_id", "input_path", "preset", "status"]:
            assert f in MANIFEST_FIELDS
