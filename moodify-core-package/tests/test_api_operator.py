"""Smoke tests for Moodify operator-console API endpoints."""

import csv
import json

from fastapi.testclient import TestClient

from moodify.api.main import app


def _write_config(tmp_path):
    config_path = tmp_path / "runtime_config.json"
    config_path.write_text(
        json.dumps(
            {
                "project_root": str(tmp_path),
                "output_root": "outputs",
                "report_dir": "reports",
                "operator_jobs_path": "operator_jobs.jsonl",
                "operator_detail_dir": "operator_details",
            }
        ),
        encoding="utf-8",
    )
    return config_path


def _write_manifest(run_dir, rows):
    fields = [
        "run_id",
        "task_id",
        "sample_id",
        "input_path",
        "preset",
        "status",
        "return_code",
        "elapsed_seconds",
        "output_dir",
        "template_index",
        "pseudo_mrs_before",
        "pseudo_mrs_after",
        "pseudo_delta_mrs",
        "mrs_open_v031_before",
        "mrs_open_v031_after",
        "delta_mrs_open_v031",
        "mrs_open_flags",
        "error",
    ]
    run_dir.mkdir(parents=True)
    with (run_dir / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_operator_api_create_list_detail_and_attach(tmp_path, monkeypatch):
    config_path = _write_config(tmp_path)
    monkeypatch.setenv("MOODIFY_RUNTIME_CONFIG", str(config_path))
    client = TestClient(app)

    create_response = client.post(
        "/operator/jobs",
        json={
            "source_audio": "input/song.wav",
            "processing_depth": "standard_process",
            "project_label": "api-project",
            "priority": 3,
        },
    )
    assert create_response.status_code == 200
    job = create_response.json()
    assert job["job_id"].startswith("JOB_")
    assert job["project_label"] == "api-project"

    list_response = client.get("/operator/jobs")
    assert list_response.status_code == 200
    assert [row["job_id"] for row in list_response.json()["jobs"]] == [job["job_id"]]

    run_dir = tmp_path / "outputs" / "run_api"
    _write_manifest(
        run_dir,
        [
            {
                "run_id": "run_api",
                "task_id": "TASK_API",
                "sample_id": "SMP_API",
                "input_path": "input/song.wav",
                "preset": "clean_master",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "4.0",
                "output_dir": "outputs/run_api/SMP_API/clean_master",
                "template_index": "0",
                "pseudo_mrs_before": "10",
                "pseudo_mrs_after": "15",
                "pseudo_delta_mrs": "5",
                "mrs_open_v031_before": "1000",
                "mrs_open_v031_after": "1010",
                "delta_mrs_open_v031": "10",
                "mrs_open_flags": "",
                "error": "",
            }
        ],
    )

    attach_response = client.post(
        f"/operator/jobs/{job['job_id']}/attach-run",
        json={"run_id": "run_api", "required_mrs_delta": 0},
    )
    assert attach_response.status_code == 200
    attached = attach_response.json()
    assert attached["summary"]["candidate_count"] == 1
    assert attached["summary"]["gate_counts"] == {"approve": 1}

    detail_response = client.get(f"/operator/jobs/{job['job_id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["job"]["run_id"] == "run_api"
    assert detail["detail"]["score_results"][0]["mrs_score_delta"] == 10.0


def test_operator_api_rejects_unknown_depth(tmp_path, monkeypatch):
    config_path = _write_config(tmp_path)
    monkeypatch.setenv("MOODIFY_RUNTIME_CONFIG", str(config_path))
    client = TestClient(app)

    response = client.post(
        "/operator/jobs",
        json={"source_audio": "input/song.wav", "processing_depth": "instant"},
    )
    assert response.status_code == 400
    assert "unknown processing_depth" in response.json()["detail"]


def test_operator_api_returns_404_for_missing_job(tmp_path, monkeypatch):
    config_path = _write_config(tmp_path)
    monkeypatch.setenv("MOODIFY_RUNTIME_CONFIG", str(config_path))
    client = TestClient(app)

    response = client.get("/operator/jobs/JOB_DOES_NOT_EXIST")
    assert response.status_code == 404
