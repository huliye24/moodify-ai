"""MHP-381/387: Velocity Core Tests — worktree, exec queue, auto report, failure replay."""

import tempfile
from pathlib import Path

from moodify_runtime.velocity import (
    enqueue_mhp,
    dequeue_next,
    mark_mhp_done,
    list_exec_queue,
    auto_summary,
    auto_gate_decision,
    auto_next_action,
    catalog_failure,
    lookup_failure,
    write_velocity_metrics,
    list_worktrees,
)


# ── Executable MHP Queue ──────────────────────────────────────────────


def test_enqueue_and_dequeue(tmp_path, monkeypatch):
    import moodify_runtime.velocity as v
    monkeypatch.setattr(v, '_exec_queue_path', lambda: tmp_path / "exec_queue.jsonl")

    enqueue_mhp("MHP-001", "docs/plan/MHP-001.md")
    enqueue_mhp("MHP-002", "docs/plan/MHP-002.md")

    next_mhp = dequeue_next()
    assert next_mhp is not None
    assert next_mhp.mhp_id == "MHP-001"
    assert next_mhp.status == "queued"


def test_mark_mhp_done(tmp_path, monkeypatch):
    import moodify_runtime.velocity as v
    monkeypatch.setattr(v, '_exec_queue_path', lambda: tmp_path / "exec_queue.jsonl")

    enqueue_mhp("MHP-003", "docs/plan/MHP-003.md")
    mark_mhp_done("MHP-003", exit_code=0, summary="All tests pass")

    queue = list_exec_queue()
    assert queue[0]["status"] == "done"
    assert queue[0]["exit_code"] == 0


def test_mark_mhp_failed(tmp_path, monkeypatch):
    import moodify_runtime.velocity as v
    monkeypatch.setattr(v, '_exec_queue_path', lambda: tmp_path / "exec_queue.jsonl")

    enqueue_mhp("MHP-004", "docs/plan/MHP-004.md")
    mark_mhp_done("MHP-004", exit_code=1, error="ImportError")

    queue = list_exec_queue()
    assert queue[0]["status"] == "failed"


# ── Auto Reporter ─────────────────────────────────────────────────────


def test_auto_summary_empty(tmp_path):
    s = auto_summary(tmp_path)
    assert s["total_cycles"] == 0
    assert s["health"] == "healthy"


def test_auto_gate_adopt():
    g = auto_gate_decision({"tasks_succeeded": 100, "tasks_failed": 0, "error_count": 0})
    assert g["decision"] == "ADOPT"


def test_auto_gate_hold():
    g = auto_gate_decision({"tasks_succeeded": 80, "tasks_failed": 20, "error_count": 2})
    assert g["decision"] == "HOLD"


def test_auto_gate_rebuild():
    g = auto_gate_decision({"tasks_succeeded": 50, "tasks_failed": 50, "error_count": 10})
    assert g["decision"] == "REBUILD"


def test_auto_next_action():
    assert "进入下一" in auto_next_action({"decision": "ADOPT"})
    assert "审查失败" in auto_next_action({"decision": "HOLD"})
    assert "回退" in auto_next_action({"decision": "REBUILD"})


# ── Failure Replay Library ────────────────────────────────────────────


def test_catalog_and_lookup(tmp_path, monkeypatch):
    import moodify_runtime.velocity as v
    monkeypatch.setattr(v, '_replay_lib_path', lambda: tmp_path / "failure_lib.jsonl")

    catalog_failure("ImportError: no module X", "import_error", "Missing pip install")
    result = lookup_failure("ImportError: no module X")
    assert result is not None
    assert result["error_type"] == "import_error"
    assert result["root_cause"] == "Missing pip install"


def test_catalog_dedup(tmp_path, monkeypatch):
    import moodify_runtime.velocity as v
    monkeypatch.setattr(v, '_replay_lib_path', lambda: tmp_path / "failure_lib.jsonl")

    catalog_failure("timeout", "timeout", "Network slow")
    catalog_failure("timeout", "timeout", "Network slow")  # same signature
    result = lookup_failure("timeout")
    assert result["occurred_count"] == 2


def test_unknown_failure(tmp_path, monkeypatch):
    import moodify_runtime.velocity as v
    monkeypatch.setattr(v, '_replay_lib_path', lambda: tmp_path / "failure_lib.jsonl")

    assert lookup_failure("nonexistent error") is None


# ── Velocity Metrics ──────────────────────────────────────────────────


def test_write_velocity_metrics(tmp_path):
    m = write_velocity_metrics(tmp_path, cycles_completed=5, tasks_per_hour=120.5, success_rate=0.95)
    assert m["cycles_completed"] == 5
    assert m["tasks_per_hour"] == 120.5

    path = tmp_path / "velocity_metrics.jsonl"
    assert path.exists()


# ── Worktree listing (read-only, no actual git needed) ────────────────


def test_list_worktrees_no_error():
    """list_worktrees should not crash even without git."""
    wts = list_worktrees()
    assert isinstance(wts, list)
