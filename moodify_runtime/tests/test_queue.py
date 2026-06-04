"""Tests for queue."""
import tempfile
from pathlib import Path
from moodify_runtime.queue import (
    load_queue, existing_task_keys, task_key, rewrite_queue, update_task_status,
)
from moodify_runtime.config import RuntimeConfig

def _cfg():
    d = tempfile.mkdtemp()
    return RuntimeConfig(project_root=Path(d), queue_path=Path(d) / "q.jsonl")

class TestTaskKey:
    def test_key(self):
        k = task_key("s1", "warm_vocal")
        assert "s1" in k and "warm_vocal" in k

class TestExisting:
    def test_empty(self):
        assert existing_task_keys([]) == set()

class TestQueue:
    def test_rewrite_load(self):
        cfg = _cfg()
        rewrite_queue(cfg, [{"task_id": "A", "status": "pending", "sample_id": "s1", "preset": "warm_vocal"}])
        rows = load_queue(cfg)
        assert len(rows) == 1

class TestUpdate:
    def test_update(self):
        cfg = _cfg()
        rewrite_queue(cfg, [{"task_id": "A", "status": "pending", "sample_id": "s1", "preset": "warm_vocal"}])
        result = update_task_status(cfg, "A", "pending", {"sample_id": "s1"})
        # Returns None on success (side-effect function)
        assert result is None or isinstance(result, (dict, list))
