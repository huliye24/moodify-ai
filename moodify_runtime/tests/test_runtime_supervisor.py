"""MHP-095 + MHP-112: Runtime Supervisor Tests — supervisor, heartbeat, state machine, events, failures."""

import json
import tempfile
import time
from pathlib import Path

from moodify_runtime.supervisor import run_supervised, SupervisedRun
from moodify_runtime.runtime_state import (
    Heartbeat, transition_task, find_abandoned_tasks, resume_queue, VALID_TRANSITIONS,
)
from moodify_runtime.runtime_events import (
    EventWriter, make_task_started, make_task_completed, make_task_failed,
    make_heartbeat, make_run_summary,
)
from moodify_runtime.runtime_failures import (
    classify_failure, should_retry, backoff_delay, Severity,
)


def test_supervised_success():
    """Supervisor wraps a successful command and returns exit_code=0."""
    r = run_supervised(["echo", "hello"], timeout=5, max_retries=0)
    assert r.exit_code == 0
    assert not r.crashed
    assert not r.timed_out
    assert r.attempts == 1


def test_supervised_failure_no_retry():
    """Exit code != 0 with max_retries=0 should mark crashed."""
    r = run_supervised(["python3", "-c", "exit(1)"], timeout=5, max_retries=0)
    assert r.exit_code == 1
    assert r.crashed
    assert r.attempts == 1


def test_supervised_failure_with_retry():
    """With max_retries=2, should retry on failure."""
    r = run_supervised(["python3", "-c", "exit(1)"], timeout=5, max_retries=2, retry_delay=0.1)
    assert r.crashed
    assert r.attempts == 3  # 1 initial + 2 retries


def test_supervised_timeout():
    """sleep longer than timeout should trigger timeout detection."""
    r = run_supervised(["sleep", "2"], timeout=0.5, max_retries=0)
    assert r.timed_out
    assert r.crashed


def test_supervised_command_not_found():
    """Nonexistent command should crash."""
    r = run_supervised(["/nonexistent/cmd_xyz"], timeout=5, max_retries=0)
    assert r.crashed
    assert r.exit_code != 0 or r.error != ""


def test_supervised_retry_eventually_succeeds():
    """A command that fails once then succeeds should return success after retry."""
    # Use a temp file to track attempts
    import tempfile, pathlib
    tmp = pathlib.Path(tempfile.mkdtemp())
    state_file = tmp / "state.txt"
    script = tmp / "flaky.py"
    script.write_text(f"""
import sys
p = __import__('pathlib').Path('{state_file}')
count = 0
if p.exists():
    count = int(p.read_text())
p.write_text(str(count + 1))
if count < 1:
    sys.exit(1)
print("success")
sys.exit(0)
""")
    r = run_supervised(["python3", str(script)], timeout=5, max_retries=2, retry_delay=0.1)
    assert r.exit_code == 0
    assert not r.crashed
    assert r.attempts == 2  # failed once, succeeded on retry


def test_supervised_to_dict():
    """to_dict() should produce serializable output."""
    r = run_supervised(["echo", "test"], timeout=5, max_retries=0)
    d = r.to_dict()
    assert d["exit_code"] == 0
    assert not d["crashed"]
    assert "echo test" in d["command"]


# ── MHP-112: Heartbeat tests ────────────────────────────────────────


def test_heartbeat_writes_and_detects_age(tmp_path):
    hb = Heartbeat(path=tmp_path / "heartbeat.json", interval=15)
    assert hb.age_seconds() == float("inf")  # no file yet
    elapsed = hb.beat()
    assert elapsed >= 0
    assert hb.path.exists()
    assert hb.is_alive(max_age=60)
    assert hb.age_seconds() <= 1


def test_heartbeat_stale_detection(tmp_path):
    hb = Heartbeat(path=tmp_path / "stale.json", interval=15)
    hb.beat()
    # Artificially age the file
    aged = time.time() - 120
    hb.path.touch()
    import os
    os.utime(str(hb.path), (aged, aged))
    assert not hb.is_alive(max_age=60)
    assert hb.age_seconds() >= 60


# ── MHP-109: State machine tests ─────────────────────────────────────


def test_valid_transitions():
    assert transition_task({"status": "pending"}, "claimed")["status"] == "claimed"
    assert transition_task({"status": "claimed"}, "running")["status"] == "running"
    assert transition_task({"status": "running"}, "done")["status"] == "done"
    assert transition_task({"status": "running"}, "failed")["status"] == "failed"
    assert transition_task({"status": "failed"}, "pending")["status"] == "pending"


def test_invalid_transition_raises():
    import pytest
    with pytest.raises(ValueError):
        transition_task({"status": "done"}, "running")  # done is terminal


def test_find_abandoned_tasks():
    tasks = [
        {"task_id": "T1", "status": "claimed", "status_updated_at": "2020-01-01T00:00:00Z"},
        {"task_id": "T2", "status": "running", "status_updated_at": "2020-01-01T00:00:00Z"},
        {"task_id": "T3", "status": "pending", "status_updated_at": "2020-01-01T00:00:00Z"},
    ]
    abandoned = find_abandoned_tasks(tasks, max_age_minutes=0)
    assert len(abandoned) == 2
    assert abandoned[0]["task_id"] == "T1"


def test_resume_queue_recycles_abandoned():
    tasks = [
        {"task_id": "T1", "status": "claimed", "status_updated_at": "2020-01-01T00:00:00Z"},
        {"task_id": "T2", "status": "done", "status_updated_at": "2020-01-01T00:00:00Z"},
    ]
    result = resume_queue(tasks)
    assert result["recycled"] == 1
    assert tasks[0]["status"] == "pending"


# ── MHP-110: Event writer tests ──────────────────────────────────────


def test_event_writer_appends_jsonl(tmp_path):
    path = tmp_path / "events.jsonl"
    w = EventWriter(path)
    w.emit(make_task_started("R1", "T1", "S1", "warm_vocal", "input/s.wav"))
    w.emit(make_task_completed("R1", "T1", "S1", "warm_vocal", 2.5, 0, 5.0))
    w.emit(make_task_failed("R1", "T2", "S2", "clean_master", "exit_code=1", 1, 1))
    w.emit(make_heartbeat("R1", 3, 2, 1, 60.0, 49.5))
    w.emit(make_run_summary("R1", 5, 4, 1, 120.0))
    assert w.count == 5
    assert path.exists()
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 5
    for line in lines:
        ev = json.loads(line)
        assert "event_type" in ev
        assert "run_id" in ev


# ── MHP-111: Failure classifier tests ────────────────────────────────


def test_classify_critical_failure():
    fr = classify_failure(-1, "killed: out of memory", 0)
    assert fr.severity == Severity.CRITICAL
    assert not fr.retryable


def test_classify_high_failure_retryable():
    fr = classify_failure(1, "subprocess error", 0)
    assert fr.severity == Severity.HIGH
    assert fr.retryable


def test_classify_file_not_found_not_retryable():
    fr = classify_failure(1, "No such file: input.wav", 0)
    assert fr.severity == Severity.MEDIUM
    assert not fr.retryable


def test_should_retry_policy():
    fr = classify_failure(1, "timeout", 0)
    assert should_retry(fr)  # attempt 0 < max_retries 2
    fr.attempt = 2
    assert not should_retry(fr)  # exhausted


def test_backoff_delay():
    d0 = backoff_delay(0)  # 1.0 * 2^0 = 1.0
    d1 = backoff_delay(1)  # 1.0 * 2^1 = 2.0
    d3 = backoff_delay(3)  # 1.0 * 2^3 = 8.0
    assert d0 == 1.0
    assert d1 == 2.0
    assert d3 == 8.0
    assert backoff_delay(10, max_delay=30) == 30.0  # capped
