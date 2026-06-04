"""Tests for scheduler."""
import tempfile
from pathlib import Path
import pytest
from moodify_runtime.scheduler import (
    ComputeRequest, ComputeLease, ComputeRun, CostRecord, _sid,
    schedule_job, allocate_lease, record_compute_run,
    list_scheduler_requests, list_scheduler_leases,
    list_scheduler_runs, list_scheduler_costs,
)
from moodify_runtime.config import RuntimeConfig

@pytest.fixture
def scfg():
    d = tempfile.mkdtemp()
    c = RuntimeConfig(project_root=Path(d), scheduler_data_dir=Path(d) / "sched")
    c.scheduler_data_dir.mkdir(parents=True, exist_ok=True)
    return c

class TestIdHelper:
    def test_sid(self):
        assert "req" in _sid("req")

class TestDataClasses:
    def test_request(self):
        r = ComputeRequest(request_id="R1", job_id="J1", compute_class="cpu")
        assert r.job_id == "J1"
    def test_lease(self):
        ll = ComputeLease(lease_id="L1", request_id="R1", job_id="J1", node_id="n1", compute_class="cpu")
        assert ll.node_id == "n1"
    def test_cost(self):
        c = CostRecord(cost_id="C1", run_id="RUN1", job_id="J1", compute_class="cpu", duration_seconds=120.0, estimated_cost=0.05)
        assert c.estimated_cost == 0.05

class TestCRUD:
    def test_schedule(self, scfg):
        r = schedule_job(scfg, "job-1", "cpu_standard", 1)
        assert r["job_id"] == "job-1"
    def test_lease(self, scfg):
        r = schedule_job(scfg, "job-2", "cpu_standard")
        ll = allocate_lease(scfg, r["request_id"], "node-1")
        assert ll["node_id"] == "node-1"
    def test_run(self, scfg):
        r = schedule_job(scfg, "job-3", "gpu_standard", 3)
        ll = allocate_lease(scfg, r["request_id"], "node-1")
        run = record_compute_run(scfg, ll["lease_id"], True, 120.0, 10, "ok")
        assert isinstance(run, dict)
    def test_lists(self, scfg):
        assert isinstance(list_scheduler_requests(scfg), list)
        assert isinstance(list_scheduler_leases(scfg), list)
        assert isinstance(list_scheduler_runs(scfg), list)
        assert isinstance(list_scheduler_costs(scfg), list)
