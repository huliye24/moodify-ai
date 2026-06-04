"""Tests for MHP-033: Operator Report Bundle System."""

import json

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.operator_console import (
    attach_run_report_to_job,
    build_operator_report_bundle,
    create_operator_job,
    create_delivery_record,
    get_operator_job,
)
from moodify_runtime.cli import main
from moodify_runtime.utils import read_jsonl

from moodify_runtime.tests.test_operator_console import _write_manifest


def test_build_report_bundle_from_attached_run(tmp_path):
    """Report bundle should output all required files."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
        operator_report_dir=tmp_path / "reports" / "operator_runs",
    )

    job = create_operator_job(cfg, source_audio="input/song.wav", processing_depth="deep_process")
    run_dir = tmp_path / "outputs" / "run_rpt"
    _write_manifest(
        run_dir,
        [
            {
                "run_id": "run_rpt",
                "task_id": "TASK_RPT",
                "sample_id": "SMP_RPT",
                "input_path": "input/song.wav",
                "preset": "warm_vocal",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "8.0",
                "output_dir": "outputs/run_rpt/SMP_RPT/warm_vocal",
                "template_index": "0",
                "pseudo_mrs_before": "10",
                "pseudo_mrs_after": "18",
                "pseudo_delta_mrs": "8",
                "mrs_open_v031_before": "",
                "mrs_open_v031_after": "",
                "delta_mrs_open_v031": "",
                "mrs_open_flags": "",
                "error": "",
            }
        ],
    )
    report_path = tmp_path / "reports" / "daily_report_run_rpt.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# daily report", encoding="utf-8")

    attach_run_report_to_job(cfg, job_id=job["job_id"], run_id="run_rpt", report_path=report_path)

    result = build_operator_report_bundle(cfg, job_id=job["job_id"])
    assert "report_path" in result

    bundle_dir = tmp_path / "reports" / "operator_runs" / job["job_id"]
    assert bundle_dir.is_dir()
    assert (bundle_dir / "summary.md").exists()
    assert (bundle_dir / "summary.json").exists()
    assert (bundle_dir / "candidate_versions.jsonl").exists()
    assert (bundle_dir / "score_results.jsonl").exists()
    assert (bundle_dir / "gate_decisions.jsonl").exists()
    assert (bundle_dir / "manifest.csv").exists()
    assert (bundle_dir / "delivery.md").exists()

    # Verify content
    cv = read_jsonl(bundle_dir / "candidate_versions.jsonl")
    assert len(cv) == 1
    assert cv[0]["preset"] == "warm_vocal"

    gd = read_jsonl(bundle_dir / "gate_decisions.jsonl")
    assert len(gd) == 1
    assert gd[0]["decision"] == "approve"

    summary_json = json.loads((bundle_dir / "summary.json").read_text())
    assert summary_json["candidate_count"] == 1


def test_report_bundle_includes_delivery_when_delivered(tmp_path):
    """Report delivery.md should reflect delivery state."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
        operator_report_dir=tmp_path / "reports" / "operator_runs",
    )

    job = create_operator_job(cfg, source_audio="input/song.wav", processing_depth="deep_process")
    run_dir = tmp_path / "outputs" / "run_dlvrep"
    _write_manifest(
        run_dir,
        [
            {
                "run_id": "run_dlvrep",
                "task_id": "TASK_DLV",
                "sample_id": "SMP_DLV",
                "input_path": "input/song.wav",
                "preset": "clean_master",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "2.0",
                "output_dir": "outputs/run_dlvrep/SMP_DLV/clean_master",
                "template_index": "0",
                "pseudo_mrs_before": "10",
                "pseudo_mrs_after": "15",
                "pseudo_delta_mrs": "5",
                "mrs_open_v031_before": "",
                "mrs_open_v031_after": "",
                "delta_mrs_open_v031": "",
                "mrs_open_flags": "",
                "error": "",
            }
        ],
    )
    report_path = tmp_path / "reports" / "daily_report_run_dlvrep.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# daily report", encoding="utf-8")

    detail = attach_run_report_to_job(cfg, job_id=job["job_id"], run_id="run_dlvrep", report_path=report_path)
    cand_id = detail["candidate_versions"][0]["candidate_id"]

    # Deliver
    create_delivery_record(cfg, job_id=job["job_id"], candidate_id=cand_id)

    # Build report
    build_operator_report_bundle(cfg, job_id=job["job_id"])
    bundle_dir = tmp_path / "reports" / "operator_runs" / job["job_id"]
    dl_md = (bundle_dir / "delivery.md").read_text()
    assert "Delivered" in dl_md
    assert cand_id in dl_md


def test_report_bundle_updates_job_report_path(tmp_path):
    """Build report should update the job's report_path."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
        operator_report_dir=tmp_path / "reports" / "operator_runs",
    )

    job = create_operator_job(cfg, source_audio="input/song.wav", processing_depth="deep_process")
    run_dir = tmp_path / "outputs" / "run_path"
    _write_manifest(
        run_dir,
        [
            {
                "run_id": "run_path",
                "task_id": "TASK_PATH",
                "sample_id": "SMP_PATH",
                "input_path": "input/song.wav",
                "preset": "wide_space",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "1.0",
                "output_dir": "outputs/run_path/SMP_PATH/wide_space",
                "template_index": "0",
                "pseudo_mrs_before": "",
                "pseudo_mrs_after": "",
                "pseudo_delta_mrs": "",
                "mrs_open_v031_before": "",
                "mrs_open_v031_after": "",
                "delta_mrs_open_v031": "",
                "mrs_open_flags": "",
                "error": "",
            }
        ],
    )
    report_path = tmp_path / "reports" / "daily_report_run_path.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# report", encoding="utf-8")

    attach_run_report_to_job(cfg, job_id=job["job_id"], run_id="run_path", report_path=report_path)
    build_operator_report_bundle(cfg, job_id=job["job_id"])

    updated = get_operator_job(cfg, job["job_id"])
    assert "operator_runs" in str(updated.get("report_path", ""))


def test_operator_report_cli(tmp_path, capsys):
    """CLI operator-report should build and print the bundle path."""
    config_path = tmp_path / "runtime_config.json"
    config_path.write_text(
        '{"project_root":"%s","output_root":"outputs","report_dir":"reports",'
        '"operator_jobs_path":"operator_jobs.jsonl",'
        '"operator_detail_dir":"operator_details",'
        '"operator_deliveries_path":"operator_deliveries.jsonl",'
        '"operator_report_dir":"reports/operator_runs"}' % tmp_path.as_posix(),
        encoding="utf-8",
    )
    run_dir = tmp_path / "outputs" / "run_cli_rpt"
    _write_manifest(
        run_dir,
        [
            {
                "run_id": "run_cli_rpt",
                "task_id": "TASK_CLI_RPT",
                "sample_id": "SMP_CLI_RPT",
                "input_path": "input/song.wav",
                "preset": "clean_master",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "3.0",
                "output_dir": "outputs/run_cli_rpt/SMP_CLI_RPT/clean_master",
                "template_index": "0",
                "pseudo_mrs_before": "",
                "pseudo_mrs_after": "",
                "pseudo_delta_mrs": "",
                "mrs_open_v031_before": "",
                "mrs_open_v031_after": "",
                "delta_mrs_open_v031": "",
                "mrs_open_flags": "",
                "error": "",
            }
        ],
    )
    report_path = tmp_path / "reports" / "daily_report_run_cli_rpt.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# report", encoding="utf-8")

    # Create job
    assert main(["--config", str(config_path), "operator-create",
                 "--source-audio", "input/song.wav", "--depth", "standard_process"]) == 0
    job = json.loads(capsys.readouterr().out)

    # Attach run
    assert main(["--config", str(config_path), "operator-attach-run",
                 "--job-id", job["job_id"], "--run-id", "run_cli_rpt"]) == 0
    _ = capsys.readouterr().out

    # Build report
    assert main(["--config", str(config_path), "operator-report",
                 "--job-id", job["job_id"]]) == 0
    report = json.loads(capsys.readouterr().out)
    assert "report_path" in report
    assert "files" in report
    assert "summary.md" in report["files"]
