"""MHP-040: Studio OS Alpha — integration smoke test.

Exercises the full pipeline:
  Client → Project → Order → Operator Job → Runtime → Delivery → Craft Writeback
"""


from moodify_runtime.config import RuntimeConfig
from moodify_runtime.operator_console import (
    attach_run_report_to_job,
    create_delivery_record,
    create_operator_job,
    get_operator_job,
    list_operator_jobs,
    plan_operator_runtime,
)
from moodify_runtime.studio import (
    create_client,
    create_order,
    create_project,
    create_staff_note,
    get_order_context,
    link_job_to_order,
    list_clients,
    list_orders,
    list_projects,
)
from moodify_runtime.craft_memory import writeback_delivery_to_craft_record, list_craft_records
from moodify_runtime.scheduler import schedule_job, allocate_lease, record_compute_run
from moodify_runtime.mrs_calibration import (
    create_calibration_sample_set,
    submit_calibration_review,
    run_gate_audit,
    propose_threshold,
)

from moodify_runtime.tests.test_operator_console import _write_manifest

BASELINE = __import__("pathlib").Path(
    "/home/ubuntu/moodify-mainline/moodify-core-package/tests/baseline/test_audio"
)


def test_studio_os_alpha_end_to_end(tmp_path):
    """Full pipeline: Client → Order → Job → Delivery → Craft → Calibration."""
    cfg = RuntimeConfig(
        project_root=tmp_path,
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
        operator_report_dir=tmp_path / "reports" / "operator_runs",
        studio_data_dir=tmp_path / "studio",
        scheduler_data_dir=tmp_path / "scheduler",
        calibration_data_dir=tmp_path / "calibration",
        craft_memory_dir=tmp_path / "craft_memory",
        data_root=tmp_path / "data",
        input_dirs=[tmp_path / "input"],
        registry_path=tmp_path / "registry.jsonl",
        queue_path=tmp_path / "queue.jsonl",
    )

    # ── 1. Studio: Client → Project → Order ──
    client = create_client(cfg, name="Test Studio", contact="test@studio.com")
    assert len(list_clients(cfg)) == 1

    project = create_project(cfg, client_id=client["client_id"], name="Album Mastering")
    assert len(list_projects(cfg)) == 1

    order = create_order(cfg, project_id=project["project_id"], client_id=client["client_id"],
                         description="Master 3 tracks", processing_package="standard", priority=3)
    assert len(list_orders(cfg)) == 1

    staff_note = create_staff_note(cfg, target_type="order", target_id=order["order_id"],
                                   content="Priority client, handle with care")
    assert staff_note["note_id"].startswith("NOTE_")

    # ── 2. Operator Job ──
    src = BASELINE / "piano.wav"
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "piano.wav").write_bytes(src.read_bytes())

    job = create_operator_job(cfg, source_audio=str(input_dir / "piano.wav"),
                              processing_depth="standard_process", project_label="Album Mastering")
    assert job["status"] == "waiting"

    # ── 3. Link job to order ──
    updated_order = link_job_to_order(cfg, order_id=order["order_id"], job_id=job["job_id"])
    assert job["job_id"] in updated_order["linked_job_ids"]

    # ── 4. Plan runtime ──
    plan = plan_operator_runtime(cfg, job_id=job["job_id"])
    assert plan["queue"]["added"] >= 1

    # ── 5. Simulate run via manifest attach ──
    run_dir = tmp_path / "outputs" / "alpha_run"
    _write_manifest(run_dir, [{
        "run_id": "alpha_run", "task_id": "TASK_A", "sample_id": "SMP_A",
        "input_path": "input/piano.wav", "preset": "clean_master",
        "status": "done", "return_code": "0", "elapsed_seconds": "5.0",
        "output_dir": "outputs/alpha_run/SMP_A/clean_master", "template_index": "0",
        "pseudo_mrs_before": "10", "pseudo_mrs_after": "15", "pseudo_delta_mrs": "5",
        "mrs_open_v031_before": "", "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
        "mrs_open_flags": "", "error": "",
    }])
    report_path = tmp_path / "reports" / "daily_report_alpha.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# alpha report", encoding="utf-8")

    detail = attach_run_report_to_job(cfg, job_id=job["job_id"], run_id="alpha_run", report_path=report_path)
    assert detail["summary"]["candidate_count"] == 1

    # ── 6. Delivery ──
    cand_id = detail["candidate_versions"][0]["candidate_id"]
    delivery = create_delivery_record(cfg, job_id=job["job_id"], candidate_id=cand_id,
                                      operator_decision="approved", notes="alpha delivery")
    assert delivery["delivery_id"].startswith("DLV_")
    assert get_operator_job(cfg, job["job_id"])["status"] == "delivered"

    # ── 7. Craft writeback ──
    craft = writeback_delivery_to_craft_record(cfg, job_id=job["job_id"], candidate_id=cand_id,
                                               adoption_status="candidate", operator_notes="alpha demo")
    assert craft["craft_id"].startswith("CRFT_")
    assert len(list_craft_records(cfg)) == 1

    # ── 8. Scheduler ──
    req = schedule_job(cfg, job_id=job["job_id"], compute_class="gpu_standard")
    lease = allocate_lease(cfg, request_id=req["request_id"], node_id="node-001")
    run_rec = record_compute_run(cfg, lease_id=lease["lease_id"], request_id=req["request_id"],
                                 job_id=job["job_id"], status="completed", duration_seconds=30.0)
    assert "run" in run_rec
    assert "cost" in run_rec

    # ── 9. Calibration lab ──
    cal_set = create_calibration_sample_set(cfg, name="alpha-sample-set", sample_ids=["SMP_A"])
    rev = submit_calibration_review(cfg, set_id=cal_set["set_id"], candidate_id=cand_id,
                                    human_decision="better", gate_decision="approve",
                                    notes="alpha review")
    assert rev["matched"] is True

    audit = run_gate_audit(cfg, set_id=cal_set["set_id"])
    assert audit["total_reviews"] == 1
    assert audit["accuracy"] == 1.0

    thr = propose_threshold(cfg, parameter="mrs_score_delta", current_value=0.0,
                            proposed_value=1.5, justification="alpha calibration")
    assert thr["proposal_id"].startswith("THR_")

    # ── 10. Order context check ──
    ctx = get_order_context(cfg, order_id=order["order_id"])
    assert len(ctx["linked_jobs"]) == 1
    assert ctx["delivery_status"]["delivered"] == 1

    # ── 11. System status ──
    jobs = list_operator_jobs(cfg)
    assert len(jobs) == 1
    assert jobs[0]["status"] == "delivered"
