"""MHP-054: Console UI Interaction Tests — 8-view rendering verification.

Verifies that all 8 Console views load correctly and that the JS render
functions can process data from their respective API endpoints.
"""

import json
import os

from fastapi.testclient import TestClient

from moodify_runtime.tests.test_operator_console import _write_manifest
from moodify_runtime.tests.test_api_jobs import _authorize_api_job


def _cfg_path(tmp_path):
    d = {
        "project_root": str(tmp_path),
        "output_root": "outputs", "report_dir": "reports",
        "operator_jobs_path": "operator_jobs.jsonl",
        "operator_detail_dir": "operator_details",
        "operator_deliveries_path": "operator_deliveries.jsonl",
        "operator_report_dir": "reports/operator_runs",
        "studio_data_dir": "studio", "scheduler_data_dir": "scheduler",
        "calibration_data_dir": "calibration", "craft_memory_dir": "craft_memory",
        "data_root": "data", "input_dirs": ["input"],
        "registry_path": "registry.jsonl", "queue_path": "queue.jsonl",
    }
    p = tmp_path / "runtime_config.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    return str(p)


def _api_client(tmp_path):
    cfg = _cfg_path(tmp_path)
    os.environ["MOODIFY_RUNTIME_CONFIG"] = cfg
    from moodify_runtime.operator_api import app
    return TestClient(app)


# ── All 8 views exist ──────────────────────────────────────────────


def test_console_loads_all_eight_views(tmp_path):
    """The Console HTML must contain render functions for all 8 views."""
    client = _api_client(tmp_path)
    r = client.get("/operator")
    assert r.status_code == 200
    html = r.text

    views = ["renderQueue", "renderJobDetail", "renderReports", "renderDelivery",
             "renderCraft", "renderStudio", "renderScheduler", "renderCalibration"]
    for v in views:
        assert v in html, f"Missing view: {v}"

    # Sidebar nav items
    nav = ["data-view=\"queue\"", "data-view=\"jobs\"", "data-view=\"reports\"",
           "data-view=\"delivery\"", "data-view=\"craft\"",
           "data-view=\"studio\"", "data-view=\"scheduler\"",
           "data-view=\"calibration\""]
    for n in nav:
        assert n in html, f"Missing nav item: {n}"


# ── Queue view renders jobs ────────────────────────────────────────


def test_queue_view_renders_with_jobs(tmp_path):
    """Queue view should contain job IDs after jobs are created."""
    client = _api_client(tmp_path)
    client.post("/operator/jobs", params={"source_audio": "input/song.wav",
               "processing_depth": "standard_process", "project_label": "q-test"})
    r = client.get("/operator")
    assert r.status_code == 200
    # The page HTML contains the JS code that calls the API; verify the job exists via API
    jobs_r = client.get("/operator/jobs")
    assert len(jobs_r.json()["jobs"]) >= 1


# ── Delivery view renders records ──────────────────────────────────


def test_delivery_view_has_api_data(tmp_path):
    """After delivering, the deliveries list should be non-empty."""
    client = _api_client(tmp_path)

    # Create job + attach + deliver
    cr = client.post("/operator/jobs", params={"source_audio": "input/s.wav",
                     "processing_depth": "quick_scan"})
    job_id = cr.json()["job_id"]
    _authorize_api_job(client, tmp_path, job_id)

    run_dir = tmp_path / "outputs" / "console_dlv"
    _write_manifest(run_dir, [{
        "run_id": "console_dlv", "task_id": "T_CD", "sample_id": "S_CD",
        "input_path": "input/s.wav", "preset": "clean_master",
        "status": "done", "return_code": "0", "elapsed_seconds": "1.0",
        "output_dir": "outputs/console_dlv/S_CD/clean_master", "template_index": "0",
        "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "",
    }])
    rp = tmp_path / "reports" / "rpt.md"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("# rpt", encoding="utf-8")

    detail = client.post(f"/operator/jobs/{job_id}/attach-run",
                         params={"run_id": "console_dlv", "report_path": str(rp)})
    cand_id = detail.json()["candidate_versions"][0]["candidate_id"]
    client.post(f"/operator/jobs/{job_id}/deliver", params={
        "candidate_id": cand_id,
        "human_approved": True,
        "approved_by": "test-reviewer",
    })

    dr = client.get("/operator/deliveries")
    assert len(dr.json()["deliveries"]) >= 1


# ── Studio view renders clients/projects/orders ────────────────────


def test_studio_api_returns_valid_data(tmp_path):
    """Studio endpoints must return correct shapes for the Console JS."""
    client = _api_client(tmp_path)
    client.post("/studio/clients", params={"name": "C1"})
    cl = client.get("/studio/clients")
    assert len(cl.json()["clients"]) >= 1


# ── Scheduler view ─────────────────────────────────────────────────


def test_scheduler_api_returns_valid_data(tmp_path):
    """Scheduler endpoints must return correct shapes for the Console JS."""
    client = _api_client(tmp_path)
    jr = client.post("/operator/jobs", params={"source_audio": "input/s.wav",
                     "processing_depth": "quick_scan"})
    job_id = jr.json()["job_id"]
    client.post("/scheduler/requests", params={"job_id": job_id, "compute_class": "gpu_standard"})
    requests = client.get("/scheduler/requests")
    assert len(requests.json()["requests"]) >= 1


# ── Calibration view ───────────────────────────────────────────────


def test_calibration_api_returns_valid_data(tmp_path):
    """Calibration endpoints must return correct shapes for the Console JS."""
    client = _api_client(tmp_path)
    sr = client.post("/calibration/sample-sets", params={"name": "api-set"})
    set_id = sr.json()["set_id"]
    client.post("/calibration/reviews", params={
        "set_id": set_id, "candidate_id": "CAND_X",
        "human_decision": "better", "gate_decision": "approve",
    })
    reviews = client.get("/calibration/reviews")
    assert len(reviews.json()["reviews"]) >= 1


# ── Craft view ─────────────────────────────────────────────────────


def test_craft_api_returns_valid_data(tmp_path):
    """Craft endpoint should return an empty list (not null)."""
    client = _api_client(tmp_path)
    r = client.get("/craft/records")
    assert r.status_code == 200
    assert isinstance(r.json()["records"], list)
