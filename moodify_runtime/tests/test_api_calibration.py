"""MHP-043: API tests — MRS Calibration Lab endpoints (/calibration/*)."""

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


def test_create_sample_set(tmp_path):
    client = _api_client(tmp_path)
    r = client.post("/calibration/sample-sets", params={
        "name": "alpha-set",
        "description": "First calibration set",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["set_id"].startswith("CALSET_")
    assert data["name"] == "alpha-set"


def test_list_sample_sets_empty(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/calibration/sample-sets")
    assert r.status_code == 200
    assert r.json()["sample_sets"] == []


def test_submit_review_and_audit(tmp_path):
    client = _api_client(tmp_path)

    # Create a job + candidate first for context
    jr = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    job_id = jr.json()["job_id"]

    # Create sample set
    sr = client.post("/calibration/sample-sets", params={"name": "review-set"})
    set_id = sr.json()["set_id"]

    # Submit review
    r = client.post("/calibration/reviews", params={
        "set_id": set_id,
        "candidate_id": "CAND_TEST",
        "human_decision": "better",
        "gate_decision": "approve",
        "notes": "sounds great",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["review_id"].startswith("CALREV_")
    assert data["matched"] is True

    # List reviews
    r = client.get("/calibration/reviews")
    assert r.status_code == 200
    assert len(r.json()["reviews"]) == 1

    # Run audit
    r = client.post(f"/calibration/audits/{set_id}")
    assert r.status_code == 200
    audit = r.json()
    assert audit["total_reviews"] == 1
    assert audit["accuracy"] == 1.0

    # List audits
    r = client.get("/calibration/audits")
    assert r.status_code == 200
    assert len(r.json()["audits"]) == 1


def test_submit_review_bad_decision(tmp_path):
    client = _api_client(tmp_path)
    sr = client.post("/calibration/sample-sets", params={"name": "bad-decision-set"})
    set_id = sr.json()["set_id"]

    r = client.post("/calibration/reviews", params={
        "set_id": set_id,
        "candidate_id": "CAND_X",
        "human_decision": "INVALID",
        "gate_decision": "approve",
    })
    assert r.status_code == 400


def test_propose_threshold(tmp_path):
    client = _api_client(tmp_path)
    r = client.post("/calibration/thresholds", params={
        "parameter": "mrs_score_delta",
        "current_value": 0.0,
        "proposed_value": 1.5,
        "justification": "alpha calibration adjustment",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["proposal_id"].startswith("THR_")
    assert data["parameter"] == "mrs_score_delta"
    assert data["proposed_value"] == 1.5


def test_list_thresholds_empty(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/calibration/thresholds")
    assert r.status_code == 200
    assert r.json()["thresholds"] == []
