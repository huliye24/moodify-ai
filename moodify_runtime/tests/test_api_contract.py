"""MHP-044: API Contract Verification — Console UI ↔ API alignment.

Every field the Operator Console JS accesses must exist in the API response.
This test file codifies the contract so neither side silently diverges.
"""

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


# ══════════════════════════════════════════════════════════════════════
# Job list contract
# JS: renderQueue → api('/operator/jobs') → data.jobs → j.job_id, j.status, etc.
# ══════════════════════════════════════════════════════════════════════

JOB_LIST_FIELDS = {
    "job_id", "status", "processing_depth", "project_label",
    "current_step", "updated_at", "priority", "source_audio",
    "created_at", "customer_label", "target_notes", "delivery_mode",
}


def test_job_list_contract(tmp_path):
    client = _api_client(tmp_path)
    client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    r = client.get("/operator/jobs")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["jobs"], list)
    for job in data["jobs"]:
        present = JOB_LIST_FIELDS & set(job.keys())
        assert present == JOB_LIST_FIELDS, f"Missing fields: {JOB_LIST_FIELDS - set(job.keys())}"


# ══════════════════════════════════════════════════════════════════════
# Job detail contract
# JS: selectJob → api('/operator/jobs/{id}') → data.job + data.detail
# ══════════════════════════════════════════════════════════════════════

JOB_DETAIL_JOB_FIELDS = {
    "job_id", "status", "source_audio", "processing_depth",
    "project_label", "run_id", "report_path", "current_step", "updated_at",
}

DETAIL_SECTION_FIELDS = {
    "candidate_versions", "score_results", "gate_decisions", "summary",
}

CANDIDATE_FIELDS = {"candidate_id", "preset", "output_path"}
SCORE_FIELDS = {"mrs_score", "mrs_score_delta", "over_dark_triggered", "candidate_id"}
GATE_FIELDS = {"decision", "reasons", "candidate_id"}
SUMMARY_FIELDS = {"candidate_count", "gate_counts", "required_mrs_delta"}


def test_job_detail_contract(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]

    # Attach detail first
    run_dir = tmp_path / "outputs" / "contract_run"
    _write_manifest(run_dir, [{
        "run_id": "contract_run", "task_id": "TASK_C", "sample_id": "SMP_C",
        "input_path": "input/s.wav", "preset": "clean_master",
        "status": "done", "return_code": "0", "elapsed_seconds": "3.0",
        "output_dir": "outputs/contract_run/SMP_C/clean_master", "template_index": "0",
        "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "",
    }])
    report_p = tmp_path / "reports" / "contract_report.md"
    report_p.parent.mkdir(parents=True, exist_ok=True)
    report_p.write_text("# report", encoding="utf-8")
    client.post(f"/operator/jobs/{job_id}/attach-run", params={
        "run_id": "contract_run", "report_path": str(report_p),
    })

    r = client.get(f"/operator/jobs/{job_id}")
    assert r.status_code == 200
    data = r.json()

    # Job-level fields
    assert "job" in data
    job = data["job"]
    missing_job = JOB_DETAIL_JOB_FIELDS - set(job.keys())
    assert not missing_job, f"Missing job fields: {missing_job}"

    # Detail-level sections
    assert "detail" in data
    detail = data["detail"]
    missing_detail = DETAIL_SECTION_FIELDS - set(detail.keys())
    assert not missing_detail, f"Missing detail sections: {missing_detail}"

    # Candidate shape
    for c in detail.get("candidate_versions", []):
        missing_c = CANDIDATE_FIELDS - set(c.keys())
        assert not missing_c, f"Missing candidate fields: {missing_c}"

    # Score shape
    for s in detail.get("score_results", []):
        missing_s = SCORE_FIELDS - set(s.keys())
        assert not missing_s, f"Missing score fields: {missing_s}"

    # Gate shape
    for g in detail.get("gate_decisions", []):
        missing_g = GATE_FIELDS - set(g.keys())
        assert not missing_g, f"Missing gate fields: {missing_g}"

    # Summary shape
    summary = detail.get("summary", {})
    missing_sum = SUMMARY_FIELDS - set(summary.keys())
    assert not missing_sum, f"Missing summary fields: {missing_sum}"


# ══════════════════════════════════════════════════════════════════════
# Status values contract
# JS: badge(job.status) expects these exact CSS classes
# ══════════════════════════════════════════════════════════════════════

EXPECTED_JOB_STATUSES = {"waiting", "running", "gate_review", "reprocess", "delivered", "failed"}
EXPECTED_GATE_DECISIONS = {"approve", "reject", "reprocess"}


def test_status_values_are_known(tmp_path):
    """Every job status value must have a CSS badge class."""
    client = _api_client(tmp_path)
    r = client.get("/operator/jobs")
    jobs = r.json()["jobs"]
    for job in jobs:
        assert job["status"] in EXPECTED_JOB_STATUSES, (
            f"Unknown status '{job['status']}' — add CSS badge class in operator_console.html"
        )


def test_gate_decision_values_are_known(tmp_path):
    """Every gate decision must be in the expected set."""
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]

    run_dir = tmp_path / "outputs" / "gate_contract"
    _write_manifest(run_dir, [
        {"run_id": "gate_contract", "task_id": "TASK_G1", "sample_id": "SMP_G1",
         "input_path": "input/s.wav", "preset": "clean_master",
         "status": "done", "return_code": "0", "elapsed_seconds": "1.0",
         "output_dir": "outputs/gate_contract/SMP_G1/clean_master", "template_index": "0",
         "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
         "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
         "mrs_open_flags": "", "error": ""},
        {"run_id": "gate_contract", "task_id": "TASK_G2", "sample_id": "SMP_G2",
         "input_path": "input/s.wav", "preset": "wide_space",
         "status": "done", "return_code": "0", "elapsed_seconds": "1.0",
         "output_dir": "outputs/gate_contract/SMP_G2/wide_space", "template_index": "0",
         "pseudo_mrs_before": "10", "pseudo_mrs_after": "8", "pseudo_delta_mrs": "-2",
         "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
         "mrs_open_flags": "over_dark", "error": ""},
        {"run_id": "gate_contract", "task_id": "TASK_G3", "sample_id": "SMP_G3",
         "input_path": "input/s.wav", "preset": "warm_vocal",
         "status": "failed", "return_code": "1", "elapsed_seconds": "0.5",
         "output_dir": "outputs/gate_contract/SMP_G3/warm_vocal", "template_index": "0",
         "pseudo_mrs_before": "", "pseudo_mrs_after": "", "pseudo_delta_mrs": "",
         "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
         "mrs_open_flags": "", "error": "crash"},
    ])
    report_p = tmp_path / "reports" / "gate_report.md"
    report_p.parent.mkdir(parents=True, exist_ok=True)
    report_p.write_text("# report", encoding="utf-8")
    client.post(f"/operator/jobs/{job_id}/attach-run", params={
        "run_id": "gate_contract", "report_path": str(report_p),
    })

    r = client.get(f"/operator/jobs/{job_id}")
    for g in r.json()["detail"]["gate_decisions"]:
        assert g["decision"] in EXPECTED_GATE_DECISIONS, (
            f"Unknown gate decision '{g['decision']}'"
        )


# ══════════════════════════════════════════════════════════════════════
# Empty state contracts
# ══════════════════════════════════════════════════════════════════════


def test_empty_jobs_returns_list_not_null(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/operator/jobs")
    assert r.json()["jobs"] == []


def test_empty_deliveries_returns_list_not_null(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/operator/deliveries")
    assert r.json()["deliveries"] == []


def test_empty_craft_records_returns_list_not_null(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/craft/records")
    assert isinstance(r.json()["records"], list)


def test_studio_os_status_all_zeros_on_empty(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/studio-os/status")
    s = r.json()
    assert all(s[k] == 0 for k in ("active_jobs", "pending_gates", "delivered_jobs", "total_jobs", "total_deliveries"))


# ══════════════════════════════════════════════════════════════════════
# Delivery contract (JS accesses these fields)
# ══════════════════════════════════════════════════════════════════════

DELIVERY_LIST_FIELDS = {"delivery_id", "job_id", "candidate_id", "operator_decision", "delivered_at"}


def test_delivery_record_contract(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = create_r.json()["job_id"]

    run_dir = tmp_path / "outputs" / "dlv_contract"
    _write_manifest(run_dir, [{
        "run_id": "dlv_contract", "task_id": "TASK_D", "sample_id": "SMP_D",
        "input_path": "input/s.wav", "preset": "clean_master",
        "status": "done", "return_code": "0", "elapsed_seconds": "1.0",
        "output_dir": "outputs/dlv_contract/SMP_D/clean_master", "template_index": "0",
        "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "",
    }])
    report_p = tmp_path / "reports" / "dlv_report.md"
    report_p.parent.mkdir(parents=True, exist_ok=True)
    report_p.write_text("# report", encoding="utf-8")
    detail_r = client.post(f"/operator/jobs/{job_id}/attach-run", params={
        "run_id": "dlv_contract", "report_path": str(report_p),
    })
    cand_id = detail_r.json()["candidate_versions"][0]["candidate_id"]

    client.post(f"/operator/jobs/{job_id}/deliver", params={"candidate_id": cand_id})

    r = client.get("/operator/deliveries")
    for d in r.json()["deliveries"]:
        missing_d = DELIVERY_LIST_FIELDS - set(d.keys())
        assert not missing_d, f"Missing delivery fields: {missing_d}"


# ══════════════════════════════════════════════════════════════════════
# Studio OS Status contract
# ══════════════════════════════════════════════════════════════════════

STUDIO_OS_FIELDS = {"active_jobs", "pending_gates", "delivered_jobs", "total_jobs", "total_deliveries"}


def test_studio_os_status_contract(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/studio-os/status")
    data = r.json()
    missing = STUDIO_OS_FIELDS - set(data.keys())
    assert not missing, f"Missing studio-os status fields: {missing}"
    for k in STUDIO_OS_FIELDS:
        assert isinstance(data[k], int), f"studio-os/{k} should be int, got {type(data[k])}"


# ══════════════════════════════════════════════════════════════════════
# Error state contracts (404, 400)
# ══════════════════════════════════════════════════════════════════════


def test_404_has_detail_message(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/operator/jobs/NONEXISTENT")
    assert r.status_code == 404
    assert "detail" in r.json()


def test_400_has_detail_message(tmp_path):
    client = _api_client(tmp_path)
    create_r = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    r = client.post(f"/operator/jobs/{create_r.json()['job_id']}/deliver", params={"candidate_id": "NONEXISTENT"})
    assert r.status_code == 400
    assert "detail" in r.json()
