"""Tests for MHP-032: Operator Job Runner."""

import pytest

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.operator_console import (
    create_operator_job,
    get_operator_job,
    plan_operator_runtime,
    run_operator_job,
    show_operator_runtime_plan,
)
from moodify_runtime.cli import main

BASELINE = __import__("pathlib").Path(__file__).resolve().parents[2] / "moodify-core-package" / "tests" / "baseline" / "test_audio"


def test_plan_operator_runtime_with_single_file(tmp_path):
    """plan_operator_runtime should register a file and create queue tasks."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        data_root=tmp_path / "data",
        input_dirs=[tmp_path / "input"],
        registry_path=tmp_path / "registry.jsonl",
        queue_path=tmp_path / "queue.jsonl",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    # Copy a test audio file into the expected input dir
    src = BASELINE / "piano.wav"
    assert src.exists(), f"baseline audio not found: {src}"
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    dest = input_dir / "piano.wav"
    dest.write_bytes(src.read_bytes())

    job = create_operator_job(
        cfg,
        source_audio=str(dest),
        processing_depth="standard_process",
        project_label="test-project",
    )

    result = plan_operator_runtime(cfg, job_id=job["job_id"])
    assert result["queue"]["added"] >= 1

    # Job status should reflect runtime planned
    updated = get_operator_job(cfg, job["job_id"])
    assert updated["current_step"] == "runtime_planned"


def test_plan_operator_runtime_with_directory(tmp_path):
    """plan_operator_runtime with a directory should discover all audio files."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        data_root=tmp_path / "data",
        input_dirs=[tmp_path / "input"],
        registry_path=tmp_path / "registry.jsonl",
        queue_path=tmp_path / "queue.jsonl",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    input_dir = tmp_path / "batch_input"
    input_dir.mkdir(parents=True)
    for name in ["piano.wav", "electronic.wav"]:
        s = BASELINE / name
        assert s.exists()
        (input_dir / name).write_bytes(s.read_bytes())

    job = create_operator_job(
        cfg,
        source_audio=str(input_dir),
        processing_depth="deep_process",
    )
    result = plan_operator_runtime(cfg, job_id=job["job_id"])
    # Should discover both files, each with 3 presets for deep_process
    assert result["queue"]["added"] >= 2


def test_plan_operator_runtime_missing_source(tmp_path):
    """plan_operator_runtime should fail if source_audio doesn't exist."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    job = create_operator_job(cfg, source_audio="/nonexistent/song.wav")
    with pytest.raises(FileNotFoundError, match="source_audio"):
        plan_operator_runtime(cfg, job_id=job["job_id"])


def test_show_operator_runtime_plan(tmp_path):
    """show_operator_runtime_plan should list commands without running."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        data_root=tmp_path / "data",
        input_dirs=[tmp_path / "input"],
        registry_path=tmp_path / "registry.jsonl",
        queue_path=tmp_path / "queue.jsonl",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    src = BASELINE / "piano.wav"
    assert src.exists()
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    dest = input_dir / "piano.wav"
    dest.write_bytes(src.read_bytes())

    job = create_operator_job(
        cfg,
        source_audio=str(dest),
        processing_depth="quick_scan",
    )
    result = show_operator_runtime_plan(cfg, job_id=job["job_id"])
    assert result["planned_tasks"] >= 1
    assert len(result["commands"]) >= 1
    assert "command" in result["commands"][0]


def test_run_operator_job_dry_run(tmp_path):
    """run_operator_job --dry-run should not execute but show the plan."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        data_root=tmp_path / "data",
        input_dirs=[tmp_path / "input"],
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        registry_path=tmp_path / "registry.jsonl",
        queue_path=tmp_path / "queue.jsonl",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    src = BASELINE / "piano.wav"
    assert src.exists()
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    dest = input_dir / "piano.wav"
    dest.write_bytes(src.read_bytes())

    job = create_operator_job(cfg, source_audio=str(dest), processing_depth="quick_scan")
    plan_operator_runtime(cfg, job_id=job["job_id"])

    result = run_operator_job(cfg, job_id=job["job_id"], dry_run=True)
    assert result["status"] == "dry_run_complete"
    assert result["dry_run"] is True


def test_operator_plan_runtime_cli(tmp_path, capsys):
    """CLI operator-plan-runtime should produce JSON output."""
    import json as jmod

    config_path = tmp_path / "runtime_config.json"
    config_path.write_text(
        '{"project_root":"%s","data_root":"data","input_dirs":["input"],'
        '"registry_path":"registry.jsonl","queue_path":"queue.jsonl",'
        '"operator_jobs_path":"operator_jobs.jsonl",'
        '"operator_detail_dir":"operator_details"}' % tmp_path.as_posix(),
        encoding="utf-8",
    )
    src = BASELINE / "piano.wav"
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "piano.wav").write_bytes(src.read_bytes())

    assert main([
        "--config", str(config_path),
        "operator-create",
        "--source-audio", str(input_dir / "piano.wav"),
        "--depth", "standard_process",
    ]) == 0
    job = jmod.loads(capsys.readouterr().out)

    assert main([
        "--config", str(config_path),
        "operator-plan-runtime",
        "--job-id", job["job_id"],
    ]) == 0
    plan_out = capsys.readouterr().out
    assert "queue" in plan_out


def test_operator_show_plan_cli(tmp_path, capsys):
    """CLI operator-show-plan should print commands."""
    import json as jmod

    config_path = tmp_path / "runtime_config.json"
    config_path.write_text(
        '{"project_root":"%s","data_root":"data","input_dirs":["input"],'
        '"registry_path":"registry.jsonl","queue_path":"queue.jsonl",'
        '"operator_jobs_path":"operator_jobs.jsonl",'
        '"operator_detail_dir":"operator_details"}' % tmp_path.as_posix(),
        encoding="utf-8",
    )
    src = BASELINE / "piano.wav"
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "piano.wav").write_bytes(src.read_bytes())

    assert main([
        "--config", str(config_path),
        "operator-create",
        "--source-audio", str(input_dir / "piano.wav"),
        "--depth", "quick_scan",
    ]) == 0
    job = jmod.loads(capsys.readouterr().out)

    assert main([
        "--config", str(config_path),
        "operator-show-plan",
        "--job-id", job["job_id"],
    ]) == 0
    plan = jmod.loads(capsys.readouterr().out)
    assert "commands" in plan
    assert len(plan["commands"]) >= 1


# ── MHP-042: Real Runtime Integration tests ────────────────────────


def test_run_operator_job_fails_on_empty_queue(tmp_path):
    """run_operator_job with --live should fail if queue is empty."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        data_root=tmp_path / "data",
        queue_path=tmp_path / "queue.jsonl",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    job = create_operator_job(cfg, source_audio="input/song.wav", processing_depth="quick_scan")
    # No plan-runtime called — queue is empty

    result = run_operator_job(cfg, job_id=job["job_id"], dry_run=False)  # --live
    assert result["status"] == "failed"
    assert "No pending tasks" in result["error"]

    updated = get_operator_job(cfg, job["job_id"])
    assert updated["status"] == "failed"
    assert "No pending tasks" in (updated.get("last_error") or "")


def test_live_operator_job_fails_closed_without_rights_evidence(tmp_path):
    cfg = RuntimeConfig(
        project_root=tmp_path,
        data_root=tmp_path / "data",
        input_dirs=[tmp_path / "input"],
        output_root=tmp_path / "outputs",
        registry_path=tmp_path / "registry.jsonl",
        queue_path=tmp_path / "queue.jsonl",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    source = tmp_path / "input" / "piano.wav"
    source.parent.mkdir(parents=True)
    source.write_bytes((BASELINE / "piano.wav").read_bytes())
    job = create_operator_job(cfg, source_audio=str(source), processing_depth="quick_scan")
    plan_operator_runtime(cfg, job_id=job["job_id"])

    result = run_operator_job(cfg, job_id=job["job_id"], dry_run=False)

    assert result["status"] == "failed"
    assert "rights_manifest" in result["error"]
    updated = get_operator_job(cfg, job["job_id"])
    assert updated["current_step"] == "rights_gate_blocked"


def test_run_operator_job_records_timestamps(tmp_path):
    """run_operator_job should record run_started_at and run_finished_at."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        data_root=tmp_path / "data",
        input_dirs=[tmp_path / "input"],
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        registry_path=tmp_path / "registry.jsonl",
        queue_path=tmp_path / "queue.jsonl",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    src = BASELINE / "piano.wav"
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "piano.wav").write_bytes(src.read_bytes())

    job = create_operator_job(cfg, source_audio=str(input_dir / "piano.wav"), processing_depth="quick_scan")
    plan_operator_runtime(cfg, job_id=job["job_id"])

    # Dry-run should still record timestamps
    result = run_operator_job(cfg, job_id=job["job_id"], dry_run=True)
    assert result["status"] == "dry_run_complete"

    updated = get_operator_job(cfg, job["job_id"])
    assert updated.get("run_started_at") is not None
    assert updated.get("run_finished_at") is not None


def test_operator_run_cli_live_flag(tmp_path, capsys):
    """CLI operator-run --live should fail cleanly on empty queue (not crash)."""
    import json as jmod

    config_path = tmp_path / "runtime_config.json"
    config_path.write_text(
        '{"project_root":"%s","data_root":"data","input_dirs":["input"],'
        '"output_root":"outputs","report_dir":"reports",'
        '"registry_path":"registry.jsonl","queue_path":"queue.jsonl",'
        '"operator_jobs_path":"operator_jobs.jsonl",'
        '"operator_detail_dir":"operator_details"}' % tmp_path.as_posix(),
        encoding="utf-8",
    )
    assert main([
        "--config", str(config_path),
        "operator-create",
        "--source-audio", "/nonexistent/file.wav",
        "--depth", "quick_scan",
    ]) == 0
    job = jmod.loads(capsys.readouterr().out)

    # Run with --live on empty queue should exit cleanly with error JSON
    rc = main([
        "--config", str(config_path),
        "operator-run",
        "--job-id", job["job_id"],
        "--live",
    ])
    assert rc == 0  # CLI returns 0 even for failed jobs (error is in JSON)
    out = jmod.loads(capsys.readouterr().out)
    assert out["status"] == "failed"
    assert "No pending tasks" in out.get("error", "")
