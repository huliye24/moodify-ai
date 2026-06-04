import pytest

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.operator_console import (
    PROCESSING_DEPTHS,
    create_operator_job,
    decide_candidate_gate,
    list_operator_jobs,
)
from moodify_runtime.cli import main


def test_create_and_list_operator_jobs(tmp_path):
    cfg = RuntimeConfig(project_root=tmp_path, operator_jobs_path=tmp_path / "operator_jobs.jsonl")

    job = create_operator_job(
        cfg,
        source_audio="input/song.wav",
        processing_depth="deep_process",
        project_label="album-a",
        customer_label="internal",
        priority=2,
    )

    assert job["job_id"].startswith("JOB_")
    assert job["status"] == "waiting"
    assert job["processing_depth"] == "deep_process"
    assert job["current_step"] == "intake"

    jobs = list_operator_jobs(cfg)
    assert [row["job_id"] for row in jobs] == [job["job_id"]]
    assert list_operator_jobs(cfg, status="delivered") == []


def test_create_operator_job_rejects_unknown_depth(tmp_path):
    cfg = RuntimeConfig(project_root=tmp_path, operator_jobs_path=tmp_path / "operator_jobs.jsonl")
    with pytest.raises(ValueError):
        create_operator_job(cfg, source_audio="input/song.wav", processing_depth="instant_magic")

    assert "studio_process" in PROCESSING_DEPTHS


def test_gate_decision_approves_clean_candidate():
    decision = decide_candidate_gate(
        candidate_id="CAND_1",
        job_id="JOB_1",
        runtime_success=True,
        mrs_score_delta=2.5,
        required_mrs_delta=1.0,
        over_dark_triggered=False,
        transient_damage=0.2,
        loudness_penalty=0.1,
    )
    assert decision["decision"] == "approve"
    assert decision["reasons"] == ["all_gates_passed"]


def test_gate_decision_reprocesses_low_mrs_or_overdark():
    low = decide_candidate_gate(
        candidate_id="CAND_1",
        job_id="JOB_1",
        runtime_success=True,
        mrs_score_delta=0.1,
        required_mrs_delta=1.0,
    )
    assert low["decision"] == "reprocess"
    assert "mrs_delta_below_threshold" in low["reasons"]

    dark = decide_candidate_gate(
        candidate_id="CAND_2",
        job_id="JOB_1",
        runtime_success=True,
        mrs_score_delta=2.0,
        required_mrs_delta=1.0,
        over_dark_triggered=True,
    )
    assert dark["decision"] == "reprocess"
    assert "over_dark_triggered" in dark["reasons"]


def test_gate_decision_rejects_runtime_or_damage():
    failed = decide_candidate_gate(
        candidate_id="CAND_1",
        job_id="JOB_1",
        runtime_success=False,
        mrs_score_delta=3.0,
    )
    assert failed["decision"] == "reject"
    assert "runtime_failed" in failed["reasons"]

    damaged = decide_candidate_gate(
        candidate_id="CAND_2",
        job_id="JOB_1",
        runtime_success=True,
        mrs_score_delta=3.0,
        transient_damage=2.0,
        transient_threshold=1.0,
    )
    assert damaged["decision"] == "reject"
    assert "transient_damage_above_threshold" in damaged["reasons"]


def test_operator_cli_create_and_list(tmp_path, capsys):
    config_path = tmp_path / "runtime_config.json"
    config_path.write_text(
        '{"project_root":"%s","operator_jobs_path":"operator_jobs.jsonl"}' % tmp_path.as_posix(),
        encoding="utf-8",
    )

    rc = main([
        "--config",
        str(config_path),
        "operator-create",
        "--source-audio",
        "input/song.wav",
        "--depth",
        "standard_process",
        "--project-label",
        "project-x",
    ])
    assert rc == 0
    created = capsys.readouterr().out
    assert "standard_process" in created

    rc = main(["--config", str(config_path), "operator-list"])
    assert rc == 0
    listed = capsys.readouterr().out
    assert "project-x" in listed



def _write_manifest(run_dir, rows):
    import csv

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


def test_attach_run_report_to_job_builds_detail(tmp_path):
    from moodify_runtime.operator_console import attach_run_report_to_job, get_operator_job_detail

    cfg = RuntimeConfig(
        project_root=tmp_path,
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    job = create_operator_job(cfg, source_audio="input/song.wav", processing_depth="deep_process")
    run_dir = tmp_path / "outputs" / "run_001"
    _write_manifest(
        run_dir,
        [
            {
                "run_id": "run_001",
                "task_id": "TASK_A",
                "sample_id": "SMP_A",
                "input_path": "input/song.wav",
                "preset": "clean_master",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "12.5",
                "output_dir": "outputs/run_001/SMP_A/clean_master",
                "template_index": "0",
                "pseudo_mrs_before": "10",
                "pseudo_mrs_after": "12",
                "pseudo_delta_mrs": "2",
                "mrs_open_v031_before": "1000",
                "mrs_open_v031_after": "1005",
                "delta_mrs_open_v031": "5",
                "mrs_open_flags": "",
                "error": "",
            },
            {
                "run_id": "run_001",
                "task_id": "TASK_B",
                "sample_id": "SMP_A",
                "input_path": "input/song.wav",
                "preset": "wide_space",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "11.0",
                "output_dir": "outputs/run_001/SMP_A/wide_space",
                "template_index": "0",
                "pseudo_mrs_before": "10",
                "pseudo_mrs_after": "9",
                "pseudo_delta_mrs": "-1",
                "mrs_open_v031_before": "1000",
                "mrs_open_v031_after": "999",
                "delta_mrs_open_v031": "-1",
                "mrs_open_flags": "over_dark",
                "error": "",
            },
        ],
    )
    report_path = tmp_path / "reports" / "daily_report_run_001.md"
    report_path.parent.mkdir(parents=True)
    report_path.write_text("# report", encoding="utf-8")

    detail = attach_run_report_to_job(
        cfg,
        job_id=job["job_id"],
        run_id="run_001",
        report_path=report_path,
        required_mrs_delta=0.0,
    )

    assert detail["summary"]["candidate_count"] == 2
    assert detail["summary"]["gate_counts"] == {"approve": 1, "reprocess": 1}
    assert detail["score_results"][0]["mrs_score"] == 1005.0
    assert detail["gate_decisions"][1]["decision"] == "reprocess"

    loaded = get_operator_job_detail(cfg, job["job_id"])
    assert loaded["job"]["status"] == "reprocess"
    assert loaded["job"]["run_id"] == "run_001"
    assert loaded["detail"]["report_path"] == str(report_path)


def test_operator_cli_attach_and_detail(tmp_path, capsys):
    config_path = tmp_path / "runtime_config.json"
    config_path.write_text(
        '{"project_root":"%s","output_root":"outputs","report_dir":"reports",'
        '"operator_jobs_path":"operator_jobs.jsonl",'
        '"operator_detail_dir":"operator_details"}' % tmp_path.as_posix(),
        encoding="utf-8",
    )
    run_dir = tmp_path / "outputs" / "run_cli"
    _write_manifest(
        run_dir,
        [
            {
                "run_id": "run_cli",
                "task_id": "TASK_CLI",
                "sample_id": "SMP_CLI",
                "input_path": "input/song.wav",
                "preset": "clean_master",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "4.0",
                "output_dir": "outputs/run_cli/SMP_CLI/clean_master",
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

    assert main([
        "--config", str(config_path),
        "operator-create",
        "--source-audio", "input/song.wav",
        "--depth", "standard_process",
    ]) == 0
    created = capsys.readouterr().out
    import json

    job_id = json.loads(created)["job_id"]
    assert main([
        "--config", str(config_path),
        "operator-attach-run",
        "--job-id", job_id,
        "--run-id", "run_cli",
    ]) == 0
    attached = capsys.readouterr().out
    assert "candidate_versions" in attached

    assert main(["--config", str(config_path), "operator-detail", "--job-id", job_id]) == 0
    detail = json.loads(capsys.readouterr().out)
    assert detail["job"]["status"] == "gate_review"
    assert detail["detail"]["summary"]["gate_counts"] == {"approve": 1}
