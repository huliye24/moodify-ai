"""MHP-043: API tests — Operator Jobs endpoints (/operator/jobs/*)."""

import json

from fastapi.testclient import TestClient


def _cfg_path(tmp_path, extra=None):
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
    import os
    cfg = _cfg_path(tmp_path, extra)
    os.environ["MOODIFY_RUNTIME_CONFIG"] = cfg
    from moodify_runtime.operator_api import app
    return TestClient(app)


def _authorize_api_job(client, tmp_path, job_id, source_audio="input/s.wav"):
    rights = tmp_path / f"rights_{job_id}.json"
    rights.write_text(json.dumps({
        "schema_version": "1.0.0",
        "gate_id": "TEST",
        "assets": [{
            "asset_id": "TEST-ASSET",
            "source_path": str((tmp_path / source_audio).resolve()),
            "status": "ready",
        }],
    }), encoding="utf-8")
    response = client.post(f"/operator/jobs/{job_id}/authorize-rights", params={
        "rights_manifest": str(rights),
        "rights_asset_id": "TEST-ASSET",
    })
    assert response.status_code == 200, response.text


def _write_manifest(run_dir, rows):
    import csv
    fields = [
        "run_id", "task_id", "sample_id", "input_path", "preset", "status",
        "return_code", "elapsed_seconds", "output_dir", "template_index",
        "pseudo_mrs_before", "pseudo_mrs_after", "pseudo_delta_mrs",
        "mrs_open_v031_before", "mrs_open_v031_after", "delta_mrs_open_v031",
        "mrs_open_flags", "error",
    ]
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


# ── Create & List ──────────────────────────────────────────────────


def test_create_job(tmp_path):
    client = _api_client(tmp_path)
    r = client.post("/operator/jobs", params={
        "source_audio": "input/song.wav",
        "processing_depth": "deep_process",
        "project_label": "album-a",
        "priority": 2,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["job_id"].startswith("JOB_")
    assert data["status"] == "waiting"
    assert data["processing_depth"] == "deep_process"


def test_list_jobs_empty(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/operator/jobs")
    assert r.status_code == 200
    assert r.json()["jobs"] == []


def test_list_jobs_with_data(tmp_path):
    client = _api_client(tmp_path)
    client.post("/operator/jobs", params={"source_audio": "input/a.wav", "processing_depth": "quick_scan"})
    client.post("/operator/jobs", params={"source_audio": "input/b.wav", "processing_depth": "standard_process"})
    r = client.get("/operator/jobs")
    assert r.status_code == 200
    assert len(r.json()["jobs"]) == 2


def test_list_jobs_filter_by_status(tmp_path):
    client = _api_client(tmp_path)
    client.post("/operator/jobs", params={"source_audio": "input/a.wav", "processing_depth": "quick_scan"})
    r = client.get("/operator/jobs", params={"status": "delivered"})
    assert r.status_code == 200
    assert r.json()["jobs"] == []


def test_get_job_not_found(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/operator/jobs/FAKE_ID")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_get_job_detail(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]
    r = client.get(f"/operator/jobs/{job_id}")
    assert r.status_code == 200
    data = r.json()
    assert "job" in data
    assert data["job"]["job_id"] == job_id


def test_create_job_rejects_bad_depth(tmp_path):
    client = _api_client(tmp_path)
    r = client.post("/operator/jobs", params={
        "source_audio": "input/s.wav",
        "processing_depth": "INVALID",
    })
    assert r.status_code == 400


# ── Runtime ─────────────────────────────────────────────────────────


def test_plan_runtime_requires_existing_file(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={
        "source_audio": "/nonexistent/song.wav",
        "processing_depth": "quick_scan",
    })
    job_id = create_r.json()["job_id"]
    r = client.post(f"/operator/jobs/{job_id}/plan-runtime")
    assert r.status_code == 400  # FileNotFoundError


def test_run_job_dry_run(tmp_path):
    client = _api_client(tmp_path)
    # Need an actual file to plan runtime first
    from pathlib import Path
    test_wav = Path(__file__).resolve().parents[2] / "moodify-core-package" / "tests" / "baseline" / "test_audio" / "piano.wav"
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "piano.wav").write_bytes(test_wav.read_bytes())

    create_r = client.post("/operator/jobs", params={
        "source_audio": str(input_dir / "piano.wav"),
        "processing_depth": "quick_scan",
    })
    job_id = create_r.json()["job_id"]

    # Plan first
    client.post(f"/operator/jobs/{job_id}/plan-runtime")

    # Dry run (default)
    r = client.post(f"/operator/jobs/{job_id}/run")
    assert r.status_code == 200
    data = r.json()
    assert data["dry_run"] is True
    assert data["status"] == "dry_run_complete"


# ── Attach Run ──────────────────────────────────────────────────────


def test_attach_run_to_job(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]

    run_dir = tmp_path / "outputs" / "api_run"
    _write_manifest(run_dir, [{
        "run_id": "api_run", "task_id": "TASK_A", "sample_id": "SMP_A",
        "input_path": "input/s.wav", "preset": "clean_master",
        "status": "done", "return_code": "0", "elapsed_seconds": "5.0",
        "output_dir": "outputs/api_run/SMP_A/clean_master", "template_index": "0",
        "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "",
    }])
    report_p = tmp_path / "reports" / "daily_report_api.md"
    report_p.parent.mkdir(parents=True, exist_ok=True)
    report_p.write_text("# report", encoding="utf-8")

    r = client.post(f"/operator/jobs/{job_id}/attach-run", params={
        "run_id": "api_run",
        "report_path": str(report_p),
    })
    assert r.status_code == 200
    data = r.json()
    assert data["summary"]["candidate_count"] == 1


def test_attach_run_job_not_found(tmp_path):
    client = _api_client(tmp_path)
    r = client.post("/operator/jobs/FAKE/attach-run", params={"run_id": "run_x"})
    assert r.status_code == 404


# ── Reports ─────────────────────────────────────────────────────────


def test_build_report(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]

    run_dir = tmp_path / "outputs" / "api_rpt"
    _write_manifest(run_dir, [{
        "run_id": "api_rpt", "task_id": "TASK_B", "sample_id": "SMP_B",
        "input_path": "input/s.wav", "preset": "warm_vocal",
        "status": "done", "return_code": "0", "elapsed_seconds": "3.0",
        "output_dir": "outputs/api_rpt/SMP_B/warm_vocal", "template_index": "0",
        "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "",
    }])
    report_p = tmp_path / "reports" / "daily_report_api_rpt.md"
    report_p.parent.mkdir(parents=True, exist_ok=True)
    report_p.write_text("# report", encoding="utf-8")

    client.post(f"/operator/jobs/{job_id}/attach-run", params={
        "run_id": "api_rpt", "report_path": str(report_p),
    })

    r = client.post(f"/operator/jobs/{job_id}/report")
    assert r.status_code == 200
    data = r.json()
    assert "report_path" in data
    assert "summary.md" in data["files"]


def test_get_report_missing(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]
    r = client.get(f"/operator/jobs/{job_id}/report")
    assert r.status_code == 404


# ── Delivery ────────────────────────────────────────────────────────


def test_deliver_candidate(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]
    _authorize_api_job(client, tmp_path, job_id)

    run_dir = tmp_path / "outputs" / "api_dlv"
    _write_manifest(run_dir, [{
        "run_id": "api_dlv", "task_id": "TASK_DLV", "sample_id": "SMP_DLV",
        "input_path": "input/s.wav", "preset": "clean_master",
        "status": "done", "return_code": "0", "elapsed_seconds": "2.0",
        "output_dir": "outputs/api_dlv/SMP_DLV/clean_master", "template_index": "0",
        "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "",
    }])
    report_p = tmp_path / "reports" / "daily_report_api_dlv.md"
    report_p.parent.mkdir(parents=True, exist_ok=True)
    report_p.write_text("# report", encoding="utf-8")

    detail_r = client.post(f"/operator/jobs/{job_id}/attach-run", params={
        "run_id": "api_dlv", "report_path": str(report_p),
    })
    cand_id = detail_r.json()["candidate_versions"][0]["candidate_id"]

    blocked = client.post(f"/operator/jobs/{job_id}/deliver", params={
        "candidate_id": cand_id,
        "operator_decision": "approved",
    })
    assert blocked.status_code == 400
    assert "human listening approval required" in blocked.text

    r = client.post(f"/operator/jobs/{job_id}/deliver", params={
        "candidate_id": cand_id,
        "operator_decision": "approved",
        "notes": "api test delivery",
        "human_approved": True,
        "approved_by": "test-reviewer",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["delivery_id"].startswith("DLV_")


def test_deliver_bad_candidate(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]
    r = client.post(f"/operator/jobs/{job_id}/deliver", params={"candidate_id": "NONEXISTENT"})
    assert r.status_code == 400


def test_get_delivery_record(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]
    r = client.get(f"/operator/jobs/{job_id}/delivery")
    assert r.status_code == 200
    assert r.json() == {}


def test_list_deliveries_empty(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/operator/deliveries")
    assert r.status_code == 200
    assert r.json()["deliveries"] == []


# ── Craft Writeback ─────────────────────────────────────────────────


def test_writeback_craft(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]
    _authorize_api_job(client, tmp_path, job_id)

    run_dir = tmp_path / "outputs" / "api_craft"
    _write_manifest(run_dir, [{
        "run_id": "api_craft", "task_id": "TASK_CRFT", "sample_id": "SMP_CRFT",
        "input_path": "input/s.wav", "preset": "wide_space",
        "status": "done", "return_code": "0", "elapsed_seconds": "1.0",
        "output_dir": "outputs/api_craft/SMP_CRFT/wide_space", "template_index": "0",
        "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "",
    }])
    report_p = tmp_path / "reports" / "daily_report_api_craft.md"
    report_p.parent.mkdir(parents=True, exist_ok=True)
    report_p.write_text("# report", encoding="utf-8")

    detail_r = client.post(f"/operator/jobs/{job_id}/attach-run", params={
        "run_id": "api_craft", "report_path": str(report_p),
    })
    cand_id = detail_r.json()["candidate_versions"][0]["candidate_id"]

    blocked = client.post(f"/operator/jobs/{job_id}/writeback-craft", params={
        "candidate_id": cand_id,
        "adoption_status": "candidate",
    })
    assert blocked.status_code == 400

    delivered = client.post(f"/operator/jobs/{job_id}/deliver", params={
        "candidate_id": cand_id,
        "operator_decision": "approved",
        "human_approved": True,
        "approved_by": "test-reviewer",
    })
    assert delivered.status_code == 200, delivered.text

    r = client.post(f"/operator/jobs/{job_id}/writeback-craft", params={
        "candidate_id": cand_id,
        "adoption_status": "candidate",
        "operator_notes": "api test",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["craft_id"].startswith("CRFT_")


def test_list_craft_records(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/craft/records")
    assert r.status_code == 200
    assert "records" in r.json()
