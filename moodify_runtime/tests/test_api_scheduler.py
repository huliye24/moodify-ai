"""MHP-043: API tests — Cloud GPU Scheduler endpoints (/scheduler/*)."""

import json
import os

from fastapi.testclient import TestClient


def _cfg_path(tmp_path):
    d = {
        "project_root": str(tmp_path),
        "output_root": "outputs",
        "report_dir": "reports",
        "operator_jobs_path": "operator_jobs.jsonl",
        "operator_detail_dir": "operator_details",
        "operator_deliveries_path": "operator_deliveries.jsonl",
        "operator_report_dir": "reports/operator_runs",
        "studio_data_dir": "studio",
        "scheduler_data_dir": "scheduler",
        "calibration_data_dir": "calibration",
        "craft_memory_dir": "craft_memory",
        "data_root": "data",
        "input_dirs": ["input"],
        "registry_path": "registry.jsonl",
        "queue_path": "queue.jsonl",
    }
    p = tmp_path / "runtime_config.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    return str(p)


def _api_client(tmp_path):
    cfg = _cfg_path(tmp_path)
    os.environ["MOODIFY_RUNTIME_CONFIG"] = cfg
    from moodify_runtime.operator_api import app
    return TestClient(app)


def test_create_request(tmp_path):
    client = _api_client(tmp_path)
    jr = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = jr.json()["job_id"]

    r = client.post("/scheduler/requests", params={
        "job_id": job_id,
        "compute_class": "gpu_standard",
        "priority": 3,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["request_id"].startswith("REQ_")
    assert data["compute_class"] == "gpu_standard"


def test_create_request_bad_class(tmp_path):
    client = _api_client(tmp_path)
    jr = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = jr.json()["job_id"]

    r = client.post("/scheduler/requests", params={
        "job_id": job_id,
        "compute_class": "INVALID",
    })
    assert r.status_code == 400


def test_list_requests_empty(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/scheduler/requests")
    assert r.status_code == 200
    assert r.json()["requests"] == []


def test_allocate_lease_and_record_run(tmp_path):
    client = _api_client(tmp_path)
    jr = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = jr.json()["job_id"]

    req_r = client.post("/scheduler/requests", params={"job_id": job_id, "compute_class": "gpu_deep"})
    req_id = req_r.json()["request_id"]

    # Allocate lease
    r = client.post(f"/scheduler/leases/{req_id}", params={
        "node_id": "gpu-node-001",
        "ttl_minutes": 60,
    })
    assert r.status_code == 200
    lease = r.json()
    assert lease["lease_id"].startswith("LSE_")

    # Record run
    r = client.post("/scheduler/runs", params={
        "lease_id": lease["lease_id"],
        "request_id": req_id,
        "job_id": job_id,
        "status": "completed",
        "duration_seconds": 45.5,
    })
    assert r.status_code == 200
    data = r.json()
    assert "run" in data
    assert "cost" in data
    assert data["cost"]["compute_class"] == "gpu_deep"
    assert data["cost"]["estimated_cost"] > 0

    # List runs
    r = client.get("/scheduler/runs")
    assert r.status_code == 200
    assert len(r.json()["runs"]) == 1

    # List costs
    r = client.get("/scheduler/costs")
    assert r.status_code == 200
    assert len(r.json()["costs"]) == 1


def test_allocate_lease_not_found(tmp_path):
    client = _api_client(tmp_path)
    r = client.post("/scheduler/leases/FAKE_REQ", params={"node_id": "node-001"})
    assert r.status_code == 404
