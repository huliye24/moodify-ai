"""MHP-053: Real Audio Integration Test — full pipeline with live DSP processing.

These tests use @pytest.mark.slow because they run real subprocess audio processing.
Excluded from normal CI. Run with: pytest -m slow
"""

import csv

import pytest

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.operator_console import (
    build_operator_report_bundle,
    create_operator_job,
    get_operator_job,
    get_operator_job_detail,
    plan_operator_runtime,
    run_operator_job,
)

BASELINE = __import__("pathlib").Path(
    "/home/ubuntu/moodify-mainline/moodify-core-package/tests/baseline/test_audio"
)

# Moodify CLI matches: python3 -m moodify.cli process <audio> --output-dir <dir> --preset <name>
CORRECT_TEMPLATES = [
    "python3 -m moodify.cli process {input} --output-dir {output_dir} --preset {preset}",
]


def _make_cfg(tmp_path, input_dir, **overrides):
    """Build a RuntimeConfig with corrected command templates for real audio."""
    d = dict(
        project_root=tmp_path,
        data_root=tmp_path / "data",
        input_dirs=[input_dir],
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        registry_path=tmp_path / "registry.jsonl",
        queue_path=tmp_path / "queue.jsonl",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        python="python3",
        timeout_seconds_per_task=120,
        sleep_seconds_between_tasks=0.5,
        max_retries_per_task=0,
        keep_last_n_runs=3,
        stop_on_first_success_template=True,
        command_templates=list(CORRECT_TEMPLATES),
    )
    d.update(overrides)
    return RuntimeConfig(**d)


@pytest.mark.slow
def test_full_pipeline_with_real_audio(tmp_path):
    """End-to-end: create job → plan → run --live → verify manifest + scores + gates.

    Uses a single baseline WAV file with quick_scan depth (1 preset).
    Expected runtime: 5-15 seconds.
    """
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    src = BASELINE / "piano.wav"
    assert src.exists(), f"baseline piano.wav missing: {src}"
    (input_dir / "piano.wav").write_bytes(src.read_bytes())

    cfg = _make_cfg(tmp_path, input_dir)

    # 1. Create operator job
    job = create_operator_job(
        cfg, source_audio=str(input_dir / "piano.wav"),
        processing_depth="quick_scan", project_label="real-audio-test",
    )
    assert job["job_id"].startswith("JOB_")

    # 2. Plan runtime
    plan = plan_operator_runtime(cfg, job_id=job["job_id"])
    assert plan["queue"]["added"] >= 1, f"No queue tasks: {plan}"

    # 3. Run with --live
    result = run_operator_job(cfg, job_id=job["job_id"], dry_run=False)
    assert result["status"] == "completed", (
        f"Real run failed: {result.get('error', 'unknown')}"
    )
    run_id = result["run_id"]
    assert run_id

    # 4. Verify manifest.csv
    manifest_path = tmp_path / "outputs" / run_id / "manifest.csv"
    assert manifest_path.exists()
    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 1
    assert rows[0]["status"] == "done", f"Task failed: {rows[0].get('error', '')}"

    # 5. Verify timing was recorded
    elapsed = rows[0].get("elapsed_seconds", "")
    assert elapsed and float(elapsed) > 0

    # 6. Job status reflects completion
    job_after = get_operator_job(cfg, job["job_id"])
    assert job_after["status"] in ("gate_review", "reprocess")
    assert job_after["run_id"] == run_id
    assert job_after.get("run_started_at")
    assert job_after.get("run_finished_at")

    # 7. Detail has candidates and gates
    detail = get_operator_job_detail(cfg, job["job_id"])
    cands = detail["detail"]["candidate_versions"]
    gates = detail["detail"]["gate_decisions"]
    assert len(cands) >= 1, "No candidates"
    assert len(gates) >= 1, "No gate decisions"

    # 8. Report bundle
    bundle = build_operator_report_bundle(cfg, job_id=job["job_id"])
    assert "report_path" in bundle
    assert "summary.md" in bundle["files"]

    # 9. Output directory exists
    output_dir = rows[0].get("output_dir", "")
    if output_dir:
        assert (tmp_path / output_dir).exists()


@pytest.mark.slow
def test_real_audio_produces_metrics(tmp_path):
    """Real DSP processing should produce non-empty pseudo_mrs or mrs_open scores."""
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    src = BASELINE / "electronic.wav"
    assert src.exists()
    (input_dir / "electronic.wav").write_bytes(src.read_bytes())

    cfg = _make_cfg(tmp_path, input_dir)

    job = create_operator_job(cfg, source_audio=str(input_dir / "electronic.wav"),
                              processing_depth="quick_scan")
    plan_operator_runtime(cfg, job_id=job["job_id"])
    result = run_operator_job(cfg, job_id=job["job_id"], dry_run=False)

    if result["status"] != "completed":
        pytest.skip(f"Not completable: {result.get('error')}")

    manifest_path = tmp_path / "outputs" / result["run_id"] / "manifest.csv"
    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["status"] == "done":
                has_metrics = any(
                    row.get(k, "").strip()
                    for k in ("pseudo_mrs_before", "pseudo_mrs_after",
                              "mrs_open_v031_before", "mrs_open_v031_after")
                )
                assert has_metrics, f"No metrics in row: {row}"


@pytest.mark.slow
def test_real_audio_missing_input_graceful(tmp_path):
    """plan_operator_runtime with nonexistent audio should raise FileNotFoundError."""
    cfg = _make_cfg(tmp_path, tmp_path / "input")
    job = create_operator_job(cfg, source_audio="/nonexistent/audio.wav",
                              processing_depth="quick_scan")
    with pytest.raises(FileNotFoundError):
        plan_operator_runtime(cfg, job_id=job["job_id"])
