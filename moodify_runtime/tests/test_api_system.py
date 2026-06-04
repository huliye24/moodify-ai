"""MHP-043: API tests — System & Static endpoints."""

import json
import os

from fastapi.testclient import TestClient


def _cfg_path(tmp_path, extra=None):
    """Write a runtime config JSON and return its path."""
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
    if extra:
        d.update(extra)
    p = tmp_path / "runtime_config.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    return str(p)


def _api_client(tmp_path, extra=None):
    """Create a TestClient with isolated config."""
    cfg = _cfg_path(tmp_path, extra)
    os.environ["MOODIFY_RUNTIME_CONFIG"] = cfg
    from moodify_runtime.operator_api import app
    return TestClient(app)


def test_health(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["service"] == "moodify-operator"


def test_studio_os_status_empty(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/studio-os/status")
    assert r.status_code == 200
    data = r.json()
    assert data["total_jobs"] == 0
    assert data["total_deliveries"] == 0
    assert data["active_jobs"] == 0
    assert data["pending_gates"] == 0
    assert data["delivered_jobs"] == 0


def test_studio_os_status_with_jobs(tmp_path):
    client = _api_client(tmp_path)
    # Create a job first
    r = client.post("/operator/jobs", params={
        "source_audio": "input/test.wav",
        "processing_depth": "standard_process",
        "project_label": "test-project",
    })
    assert r.status_code == 200

    r = client.get("/studio-os/status")
    assert r.status_code == 200
    data = r.json()
    assert data["total_jobs"] == 1
    assert data["active_jobs"] == 1


def test_operator_console_html(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/operator")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "Moodify Operator Console" in r.text


def test_root_redirects_to_console(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/")
    assert r.status_code == 200
    assert "Moodify Operator Console" in r.text


def test_openapi_schema(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "paths" in schema
    # Verify subsystem routes exist
    paths = schema["paths"]
    assert "/studio/clients" in paths
    assert "/scheduler/requests" in paths
    assert "/calibration/sample-sets" in paths
    assert "/craft/records" in paths
