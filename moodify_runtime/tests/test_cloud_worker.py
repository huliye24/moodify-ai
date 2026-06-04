"""MHP-274: Cloud Core Tests — worker lease, parallel tasks, artifact probe, cost, failure isolation."""

import tempfile
import time
from pathlib import Path

from moodify_runtime.cloud_worker import (
    WorkerLease,
    acquire_worker_lease,
    release_worker_lease,
    heartbeat_worker_lease,
    find_expired_leases,
    run_parallel_tasks,
    probe_shared_artifact_access,
    estimate_task_cost,
    probe_failure_isolation,
)


# ── Worker Lease ──────────────────────────────────────────────────────


def test_worker_lease_not_expired(tmp_path):
    store = tmp_path / "leases.jsonl"
    wl = acquire_worker_lease("worker_1", ["T1", "T2"], store, ttl_seconds=9999)
    assert not wl.is_expired()


def test_worker_lease_heartbeat(tmp_path):
    store = tmp_path / "leases.jsonl"
    wl = acquire_worker_lease("worker_1", ["T1"], store, ttl_seconds=9999)
    heartbeat_worker_lease(wl.lease_id, store)
    assert not wl.is_expired()


def test_find_expired_leases(tmp_path):
    store = tmp_path / "leases.jsonl"
    wl = acquire_worker_lease("worker_1", ["T1"], store, ttl_seconds=-1)  # immediately expired
    time.sleep(0.1)
    expired = find_expired_leases(store)
    assert len(expired) >= 1


def test_release_lease(tmp_path):
    store = tmp_path / "leases.jsonl"
    wl = acquire_worker_lease("worker_1", ["T1"], store, ttl_seconds=9999)
    assert release_worker_lease(wl.lease_id, store)


# ── Multi-Process ─────────────────────────────────────────────────────


def test_parallel_tasks():
    cmds = [["echo", f"hello_{i}"] for i in range(4)]
    results = run_parallel_tasks(cmds, max_workers=2)
    assert len(results) == 4
    assert all(r["ok"] for r in results)


def test_parallel_mixed_failure():
    cmds = [
        ["echo", "ok1"],
        ["python3", "-c", "exit(1)"],
        ["echo", "ok2"],
    ]
    results = run_parallel_tasks(cmds, max_workers=3)
    succeeded = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]
    assert len(succeeded) == 2
    assert len(failed) == 1


# ── Artifact Probe ────────────────────────────────────────────────────


def test_shared_artifact_access(tmp_path):
    r1 = probe_shared_artifact_access(tmp_path, "w1")
    r2 = probe_shared_artifact_access(tmp_path, "w2")
    assert r1["can_read_all_markers"]
    assert r2["marker_count"] >= 2


# ── Cost Record ───────────────────────────────────────────────────────


def test_estimate_task_cost():
    r = estimate_task_cost(3600.0, "cpu_standard")  # 1 hour
    assert r.cost_estimate == 0.05  # $0.05/hour
    assert r.compute_class == "cpu_standard"

    r2 = estimate_task_cost(7200.0, "gpu_standard")  # 2 hours GPU
    assert r2.cost_estimate == 1.0  # 2 × $0.50 = $1.00


# ── Failure Isolation ─────────────────────────────────────────────────


def test_failure_isolation():
    cmds = [["echo", f"ok_{i}"] for i in range(5)]
    result = probe_failure_isolation(cmds, fail_index=2)
    assert result["total_tasks"] == 5
    assert result["failed_tasks"] == 1
    assert result["failure_contained"]
    assert result["succeeded_tasks"] == 4
