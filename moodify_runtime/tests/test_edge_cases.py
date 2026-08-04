"""MHP-050: Edge Cases & Boundary Validation.

Tests for state transitions, empty sub-objects, double-submit scenarios.
"""

import json

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.operator_console import (
    attach_run_report_to_job,
    build_operator_report_bundle,
    create_delivery_record,
    create_operator_job,
    get_operator_job,
    run_operator_job,
)
from moodify_runtime.tests.gate_helpers import create_test_delivery
from moodify_runtime.scheduler import (
    list_scheduler_costs,
    record_compute_run,
    schedule_job,
)
from moodify_runtime.mrs_calibration import (
    create_calibration_sample_set,
    run_gate_audit,
    submit_calibration_review,
)
from moodify_runtime.craft_memory import (
    writeback_delivery_to_craft_record,
    list_craft_records,
)
from moodify_runtime.studio import get_order_context, create_client, create_project, create_order
from moodify_runtime.tests.test_operator_console import _write_manifest


# ── Delivery Edge Cases ────────────────────────────────────────────


def test_double_delivery_same_candidate(tmp_path):
    """Delivering the same candidate twice should create two records (not crash)."""
    cfg = RuntimeConfig(
        project_root=tmp_path, output_root=tmp_path / "outputs", report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
    )
    job = create_operator_job(cfg, source_audio="input/s.wav", processing_depth="quick_scan")
    run_dir = tmp_path / "outputs" / "double_dlv"
    _write_manifest(run_dir, [{
        "run_id": "double_dlv", "task_id": "TASK_D", "sample_id": "SMP_D",
        "input_path": "input/s.wav", "preset": "clean_master",
        "status": "done", "return_code": "0", "elapsed_seconds": "1.0",
        "output_dir": "outputs/double_dlv/SMP_D/clean_master", "template_index": "0",
        "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "",
    }])
    rp = tmp_path / "reports" / "rpt.md"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("# report", encoding="utf-8")
    detail = attach_run_report_to_job(cfg, job_id=job["job_id"], run_id="double_dlv", report_path=rp)
    cand_id = detail["candidate_versions"][0]["candidate_id"]

    d1 = create_test_delivery(cfg, job, cand_id)
    d2 = create_test_delivery(cfg, job, cand_id, operator_decision="approved", override=True)
    assert d1["delivery_id"] != d2["delivery_id"]


def test_writeback_without_delivery_is_blocked(tmp_path):
    """Craft writeback must not bypass delivery and human approval."""
    cfg = RuntimeConfig(
        project_root=tmp_path, output_root=tmp_path / "outputs", report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        craft_memory_dir=tmp_path / "craft_memory",
    )
    job = create_operator_job(cfg, source_audio="input/s.wav", processing_depth="quick_scan")
    run_dir = tmp_path / "outputs" / "wb_nodel"
    _write_manifest(run_dir, [{
        "run_id": "wb_nodel", "task_id": "TASK_W", "sample_id": "SMP_W",
        "input_path": "input/s.wav", "preset": "warm_vocal",
        "status": "done", "return_code": "0", "elapsed_seconds": "1.0",
        "output_dir": "outputs/wb_nodel/SMP_W/warm_vocal", "template_index": "0",
        "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "",
    }])
    rp = tmp_path / "reports" / "rpt_wb.md"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("# report", encoding="utf-8")
    detail = attach_run_report_to_job(cfg, job_id=job["job_id"], run_id="wb_nodel", report_path=rp)
    cand_id = detail["candidate_versions"][0]["candidate_id"]

    # Writeback without delivery — should succeed
    import pytest
    with pytest.raises(ValueError, match="delivery record"):
        writeback_delivery_to_craft_record(
            cfg, job_id=job["job_id"], candidate_id=cand_id,
            adoption_status="experimental"
        )
    job = get_operator_job(cfg, job["job_id"])
    assert job["status"] == "gate_review"  # not delivered


def test_delivery_without_attach_fails(tmp_path):
    """Delivery should fail if no detail has been attached to the job."""
    cfg = RuntimeConfig(
        project_root=tmp_path, operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
        output_root=tmp_path / "outputs", report_dir=tmp_path / "reports",
    )
    job = create_operator_job(cfg, source_audio="input/s.wav", processing_depth="quick_scan")
    import pytest
    with pytest.raises(ValueError, match="candidate_id"):
        create_delivery_record(cfg, job_id=job["job_id"], candidate_id="ANYTHING")


# ── Report Bundle Edge Cases ───────────────────────────────────────


def test_report_bundle_for_failed_job(tmp_path):
    """Report bundle should handle a job with failed candidates (no crash, valid output)."""
    cfg = RuntimeConfig(
        project_root=tmp_path, output_root=tmp_path / "outputs", report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_report_dir=tmp_path / "reports/operator_runs",
    )
    job = create_operator_job(cfg, source_audio="input/s.wav", processing_depth="quick_scan")
    run_dir = tmp_path / "outputs" / "failed_run"
    _write_manifest(run_dir, [{
        "run_id": "failed_run", "task_id": "TASK_F", "sample_id": "SMP_F",
        "input_path": "input/s.wav", "preset": "clean_master",
        "status": "failed", "return_code": "1", "elapsed_seconds": "0.5",
        "output_dir": "outputs/failed_run/SMP_F/clean_master", "template_index": "0",
        "pseudo_mrs_before": "", "pseudo_mrs_after": "", "pseudo_delta_mrs": "",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "crashed",
    }])
    rp = tmp_path / "reports" / "rpt_f.md"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("# report", encoding="utf-8")
    attach_run_report_to_job(cfg, job_id=job["job_id"], run_id="failed_run", report_path=rp)

    result = build_operator_report_bundle(cfg, job_id=job["job_id"])
    assert "report_path" in result
    assert "summary.md" in result["files"]


def test_report_bundle_empty_detail(tmp_path):
    """Report bundle on a job with no attached detail should not crash."""
    cfg = RuntimeConfig(
        project_root=tmp_path, output_root=tmp_path / "outputs", report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_report_dir=tmp_path / "reports/operator_runs",
    )
    job = create_operator_job(cfg, source_audio="input/s.wav", processing_depth="quick_scan")
    # No attach_run — build report on a bare job
    result = build_operator_report_bundle(cfg, job_id=job["job_id"])
    assert "report_path" in result
    # Should produce files even with zero candidates
    assert result["summary"]["candidate_count"] == 0


# ── Scheduler Edge Cases ───────────────────────────────────────────


def test_zero_duration_cost_record(tmp_path):
    """Cost for zero-duration run should be 0.0, not NaN or negative."""
    cfg = RuntimeConfig(
        project_root=tmp_path, scheduler_data_dir=tmp_path / "scheduler",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    job = create_operator_job(cfg, source_audio="input/s.wav", processing_depth="quick_scan")
    req = schedule_job(cfg, job_id=job["job_id"], compute_class="gpu_deep")
    from moodify_runtime.scheduler import allocate_lease
    lease = allocate_lease(cfg, request_id=req["request_id"], node_id="node-0")

    result = record_compute_run(cfg, lease_id=lease["lease_id"], request_id=req["request_id"],
                                job_id=job["job_id"], duration_seconds=0.0)
    assert result["cost"]["estimated_cost"] == 0.0

    costs = list_scheduler_costs(cfg)
    assert costs[0]["estimated_cost"] == 0.0


def test_scheduler_request_bad_compute_class(tmp_path):
    """Scheduler should reject unknown compute classes."""
    import pytest
    cfg = RuntimeConfig(
        project_root=tmp_path, scheduler_data_dir=tmp_path / "scheduler",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    job = create_operator_job(cfg, source_audio="input/s.wav", processing_depth="quick_scan")
    with pytest.raises(ValueError):
        schedule_job(cfg, job_id=job["job_id"], compute_class="quantum")


# ── Calibration Edge Cases ─────────────────────────────────────────


def test_audit_with_zero_reviews(tmp_path):
    """Running a gate audit on a set with zero reviews should return accuracy=0."""
    cfg = RuntimeConfig(
        project_root=tmp_path, calibration_data_dir=tmp_path / "calibration",
    )
    cal_set = create_calibration_sample_set(cfg, name="empty-set")
    audit = run_gate_audit(cfg, set_id=cal_set["set_id"])
    assert audit["total_reviews"] == 0
    assert audit["accuracy"] == 0.0
    assert audit["false_positives"] == 0
    assert audit["false_negatives"] == 0


def test_review_mismatch_detection(tmp_path):
    """Human 'better' vs gate 'reject' should be flagged as unmatched."""
    cfg = RuntimeConfig(
        project_root=tmp_path, calibration_data_dir=tmp_path / "calibration",
    )
    cal_set = create_calibration_sample_set(cfg, name="mismatch-set")
    rev = submit_calibration_review(cfg, set_id=cal_set["set_id"], candidate_id="CAND_X",
                                    human_decision="better", gate_decision="reject")
    assert rev["matched"] is False

    audit = run_gate_audit(cfg, set_id=cal_set["set_id"])
    assert audit["false_positives"] == 1


# ── Studio Edge Cases ──────────────────────────────────────────────


def test_order_context_with_no_linked_jobs(tmp_path):
    """get_order_context on an order with no linked jobs should return empty list."""
    cfg = RuntimeConfig(
        project_root=tmp_path, studio_data_dir=tmp_path / "studio",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    client = create_client(cfg, name="Test Client")
    project = create_project(cfg, client_id=client["client_id"], name="Test Project")
    order = create_order(cfg, project_id=project["project_id"], client_id=client["client_id"])

    ctx = get_order_context(cfg, order_id=order["order_id"])
    assert ctx["order"]["order_id"] == order["order_id"]
    assert ctx["linked_jobs"] == []
    assert ctx["delivery_status"]["total"] == 0
    assert ctx["delivery_status"]["delivered"] == 0


# ── Runtime Edge Cases ─────────────────────────────────────────────


def test_run_operator_job_records_timestamps_on_failure(tmp_path):
    """A failed run_operator_job should still record run_finished_at."""
    cfg = RuntimeConfig(
        project_root=tmp_path, data_root=tmp_path / "data",
        queue_path=tmp_path / "queue.jsonl",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    job = create_operator_job(cfg, source_audio="input/s.wav", processing_depth="quick_scan")
    result = run_operator_job(cfg, job_id=job["job_id"], dry_run=False)
    assert result["status"] == "failed"

    updated = get_operator_job(cfg, job["job_id"])
    assert updated.get("run_started_at") is not None
    assert updated.get("run_finished_at") is not None
    assert "No pending tasks" in (updated.get("last_error") or "")


def test_run_operator_job_dry_run_preserves_status(tmp_path):
    """Dry-run should revert job status to waiting after completion."""
    cfg = RuntimeConfig(
        project_root=tmp_path, data_root=tmp_path / "data",
        queue_path=tmp_path / "queue.jsonl",
        registry_path=tmp_path / "registry.jsonl",
        input_dirs=[tmp_path / "input"],
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
    )
    # Need an actual audio file for plan + dry-run
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "moodify-core-package" / "tests" / "baseline" / "test_audio" / "piano.wav"
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "piano.wav").write_bytes(src.read_bytes())

    job = create_operator_job(cfg, source_audio=str(input_dir / "piano.wav"), processing_depth="quick_scan")
    from moodify_runtime.operator_console import plan_operator_runtime
    plan_operator_runtime(cfg, job_id=job["job_id"])

    result = run_operator_job(cfg, job_id=job["job_id"], dry_run=True)
    assert result["status"] == "dry_run_complete"

    updated = get_operator_job(cfg, job["job_id"])
    assert updated["status"] == "waiting"

    # Timestamps should be present
    assert updated.get("run_started_at") is not None
    assert updated.get("run_finished_at") is not None
