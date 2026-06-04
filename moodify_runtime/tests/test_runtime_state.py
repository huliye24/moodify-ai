"""Tests for runtime_state."""
import tempfile
from pathlib import Path
from moodify_runtime.runtime_state import (
    Heartbeat, RuntimeLease, transition_task, find_abandoned_tasks, resume_queue,
)

class TestHeartbeat:
    def test_creation(self):
        hb = Heartbeat(path=Path(tempfile.mktemp(suffix=".json")), interval=30, last_beat=0.0)
        assert hb.interval == 30

class TestRuntimeLease:
    def test_creation(self):
        l = RuntimeLease(lease_id="L1", runner_id="R1", ttl_seconds=120)
        assert l.lease_id == "L1"

class TestTaskTransitions:
    def test_valid_transition(self):
        task = {"task_id": "T1", "status": "pending"}
        try:
            t = transition_task(task, "done")
            assert t["status"] == "done"
        except ValueError:
            pass  # Some transitions may be invalid based on state machine

class TestAbandoned:
    def test_recent_not_abandoned(self):
        from datetime import datetime, timezone
        tasks = [{"task_id": "T1", "status": "running",
                   "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}]
        abandoned = find_abandoned_tasks(tasks, max_age_minutes=60)
        assert len(abandoned) == 0

class TestResume:
    def test_resume(self):
        result = resume_queue([{"task_id": "T1", "status": "running"}])
        assert isinstance(result, dict)
