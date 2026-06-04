"""Tests for runtime_events."""
from moodify_runtime.runtime_events import (
    RuntimeEvent, EventWriter,
    make_task_started, make_task_completed, make_task_failed,
    make_heartbeat, make_run_summary,
)
import tempfile
from pathlib import Path

class TestRuntimeEvent:
    def test_default(self):
        e = RuntimeEvent(event_id="ev1", event_type="test", run_id="R1")
        assert e.event_type == "test"
    def test_full(self):
        e = RuntimeEvent(event_id="ev2", event_type="task_started",
                         run_id="R1", task_id="T1", sample_id="S1", preset="warm_vocal")
        d = e.to_dict()
        assert d["run_id"] == "R1"

class TestEventWriter:
    def test_write(self):
        d = tempfile.mkdtemp(); p = Path(d) / "e.jsonl"
        w = EventWriter(p)
        w.emit(RuntimeEvent(event_id="e1", event_type="test"))
        w.emit(RuntimeEvent(event_id="e2", event_type="test", run_id="R2"))
        assert len(p.read_text().strip().split("\n")) == 1

class TestFactories:
    def test_started(self):
        e = make_task_started("R1", "T1", "S1", "warm_vocal", "/tmp/in.wav")
        assert e.event_type == "task_started"
    def test_completed(self):
        e = make_task_completed("R1", "T1", "S1", "warm_vocal", 0.5, {"rms": 0.3})
        assert e.event_type == "task_completed"
    def test_failed(self):
        e = make_task_failed("R1", "T1", "S1", "warm_vocal", "crashed", 1, 0)
        assert e.event_type == "task_failed"
    def test_heartbeat(self):
        e = make_heartbeat("R1", 3, 10, 0, 45.0, 8.0)
        assert e.event_type == "heartbeat"
