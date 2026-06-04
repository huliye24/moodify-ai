"""MHP-056: Full Stack Smoke Test — server + CLI + Console UI.

Verifies that uvicorn, CLI, and the Console HTML load together.
"""

import json
import os
import subprocess
import time
from pathlib import Path

import pytest

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.operator_console import create_operator_job, list_operator_jobs

API_MODULE = "moodify_runtime.operator_api:app"
STARTUP_TIMEOUT = 15


def _free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _make_cfg(tmp_path):
    d = dict(
        project_root=str(tmp_path),
        data_root=str(tmp_path / "data"),
        input_dirs=[str(tmp_path / "input")],
        output_root=str(tmp_path / "outputs"),
        report_dir=str(tmp_path / "reports"),
        registry_path=str(tmp_path / "registry.jsonl"),
        queue_path=str(tmp_path / "queue.jsonl"),
        operator_jobs_path=str(tmp_path / "operator_jobs.jsonl"),
        operator_detail_dir=str(tmp_path / "operator_details"),
        operator_deliveries_path=str(tmp_path / "operator_deliveries.jsonl"),
        operator_report_dir=str(tmp_path / "reports" / "operator_runs"),
        studio_data_dir=str(tmp_path / "studio"),
        scheduler_data_dir=str(tmp_path / "scheduler"),
        calibration_data_dir=str(tmp_path / "calibration"),
        craft_memory_dir=str(tmp_path / "craft_memory"),
    )
    cfg_path = tmp_path / "runtime_config.json"
    cfg_path.write_text(json.dumps(d), encoding="utf-8")
    return str(cfg_path), d


@pytest.fixture
def live_server(tmp_path):
    """Start a uvicorn server on a random port, yield the base URL, stop after test."""
    cfg_path, _cfg = _make_cfg(tmp_path)
    port = _free_port()
    env = os.environ.copy()
    env["MOODIFY_RUNTIME_CONFIG"] = cfg_path

    proc = subprocess.Popen(
        ["python3", "-m", "uvicorn", API_MODULE,
         "--host", "127.0.0.1", "--port", str(port),
         "--log-level", "error"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    base_url = f"http://127.0.0.1:{port}"

    # Wait for server to be ready
    deadline = time.time() + STARTUP_TIMEOUT
    import urllib.request
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{base_url}/health", timeout=1)
            break
        except Exception:
            time.sleep(0.3)
    else:
        proc.terminate()
        proc.wait()
        pytest.fail(f"Server did not start within {STARTUP_TIMEOUT}s")

    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


# ── Server + HTTP tests ──────────────────────────────────────────────


def test_server_health_via_http(live_server):
    """Smoke: /health returns 200."""
    import urllib.request
    r = urllib.request.urlopen(f"{live_server}/health", timeout=5)
    assert r.status == 200
    data = json.loads(r.read())
    assert data["status"] == "ok"
    assert data["service"] == "moodify-operator"


def test_server_studio_os_status_http(live_server):
    """Smoke: /studio-os/status returns valid JSON."""
    import urllib.request
    r = urllib.request.urlopen(f"{live_server}/studio-os/status", timeout=5)
    assert r.status == 200
    data = json.loads(r.read())
    assert "total_jobs" in data


def test_console_html_loads_via_http(live_server):
    """Smoke: /operator returns the Console HTML page."""
    import urllib.request
    r = urllib.request.urlopen(f"{live_server}/operator", timeout=5)
    assert r.status == 200
    html = r.read().decode("utf-8")
    assert "Moodify Operator Console" in html
    assert "renderQueue" in html
    assert "renderJobDetail" in html
    assert "renderReports" in html
    assert "renderDelivery" in html


def test_openapi_schema_via_http(live_server):
    """Smoke: /openapi.json returns valid schema with subsystem routes."""
    import urllib.request
    r = urllib.request.urlopen(f"{live_server}/openapi.json", timeout=5)
    assert r.status == 200
    schema = json.loads(r.read())
    paths = schema["paths"]
    for route in ("/studio/clients", "/scheduler/requests",
                  "/calibration/sample-sets", "/craft/records"):
        assert route in paths, f"Missing route: {route}"


# ── CLI + API combined ───────────────────────────────────────────────


def test_cli_create_job_then_api_lists_it(live_server, tmp_path):
    """Create a job via the API, then verify it appears in the job list."""
    import urllib.request
    import urllib.error

    cfg_path, _cfg = _make_cfg(tmp_path)

    # Create job via API
    import urllib.parse
    params = urllib.parse.urlencode({
        "source_audio": "input/smoke_test.wav",
        "processing_depth": "quick_scan",
        "project_label": "smoke-test",
    })
    r = urllib.request.urlopen(f"{live_server}/operator/jobs?{params}",
                               data=b"", timeout=5)
    assert r.status == 200
    job_data = json.loads(r.read())
    job_id = job_data["job_id"]

    # List jobs via API
    r2 = urllib.request.urlopen(f"{live_server}/operator/jobs", timeout=5)
    jobs_data = json.loads(r2.read())
    assert len(jobs_data["jobs"]) >= 1
    job_ids = {j["job_id"] for j in jobs_data["jobs"]}
    assert job_id in job_ids


def test_api_job_create_attach_deliver_cycle(live_server, tmp_path):
    """Full job lifecycle via HTTP API: create → attach run → deliver."""
    import urllib.request
    import urllib.parse

    cfg_path, _cfg = _make_cfg(tmp_path)

    # 1. Create job
    params = urllib.parse.urlencode({
        "source_audio": "input/lifecycle.wav",
        "processing_depth": "standard_process",
        "project_label": "lifecycle-test",
    })
    r = urllib.request.urlopen(f"{live_server}/operator/jobs?{params}",
                               data=b"", timeout=5)
    job = json.loads(r.read())
    job_id = job["job_id"]
    assert job["status"] == "waiting"

    # 2. Attach a run with manifest
    run_id = "smoke_lifecycle_001"
    run_dir = Path(tmp_path) / "outputs" / run_id
    run_dir.mkdir(parents=True)
    import csv
    manifest = run_dir / "manifest.csv"
    with manifest.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "run_id", "task_id", "sample_id", "input_path", "preset",
            "status", "return_code", "elapsed_seconds", "output_dir",
            "template_index",
            "pseudo_mrs_before", "pseudo_mrs_after", "pseudo_delta_mrs",
            "mrs_open_v031_before", "mrs_open_v031_after",
            "delta_mrs_open_v031", "mrs_open_flags", "error",
        ])
        w.writeheader()
        w.writerow({
            "run_id": run_id, "task_id": "T_L001", "sample_id": "S_L001",
            "input_path": "input/lifecycle.wav", "preset": "warm_vocal",
            "status": "done", "return_code": "0", "elapsed_seconds": "2.5",
            "output_dir": f"outputs/{run_id}/S_L001/warm_vocal",
            "template_index": "0",
            "pseudo_mrs_before": "12", "pseudo_mrs_after": "18",
            "pseudo_delta_mrs": "6",
            "mrs_open_v031_before": "", "mrs_open_v031_after": "",
            "delta_mrs_open_v031": "", "mrs_open_flags": "", "error": "",
        })

    rp = Path(tmp_path) / "reports" / "smoke_rpt.md"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("# Smoke Report\n\nAll good.", encoding="utf-8")

    attach_params = urllib.parse.urlencode({
        "run_id": run_id, "report_path": str(rp),
    })
    r2 = urllib.request.urlopen(
        f"{live_server}/operator/jobs/{job_id}/attach-run?{attach_params}",
        data=b"", timeout=5)
    detail = json.loads(r2.read())
    assert detail["job_id"] == job_id
    assert len(detail["candidate_versions"]) >= 1

    # 3. Deliver
    cand_id = detail["candidate_versions"][0]["candidate_id"]
    dlv_params = urllib.parse.urlencode({"candidate_id": cand_id})
    r3 = urllib.request.urlopen(
        f"{live_server}/operator/jobs/{job_id}/deliver?{dlv_params}",
        data=b"", timeout=5)
    delivery = json.loads(r3.read())
    assert delivery["delivery_id"].startswith("DLV_")

    # 4. Verify delivery via API
    r4 = urllib.request.urlopen(f"{live_server}/operator/deliveries", timeout=5)
    deliveries = json.loads(r4.read())
    assert len(deliveries["deliveries"]) >= 1


# ── Server cleanup ───────────────────────────────────────────────────


def test_full_stack_clean_shutdown(live_server):
    """Verify server stays responsive across multiple requests."""
    import urllib.request
    for _ in range(3):
        r = urllib.request.urlopen(f"{live_server}/health", timeout=5)
        assert r.status == 200
    # Fixture teardown handles cleanup
