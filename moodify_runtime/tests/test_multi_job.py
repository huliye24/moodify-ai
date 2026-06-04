"""MHP-055: Multi-Job Stability — concurrent operations across 10+ jobs."""

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.operator_console import (
    attach_run_report_to_job,
    create_delivery_record,
    create_operator_job,
    get_operator_job,
    list_operator_jobs,
)
from moodify_runtime.studio import (
    create_client,
    create_order,
    create_project,
    get_order_context,
    link_job_to_order,
)
from moodify_runtime.craft_memory import (
    list_craft_records,
    writeback_delivery_to_craft_record,
)
from moodify_runtime.tests.test_operator_console import _write_manifest


def _make_cfg(tmp_path):
    return RuntimeConfig(
        project_root=tmp_path,
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
        craft_memory_dir=tmp_path / "craft_memory",
        studio_data_dir=tmp_path / "studio",
    )


def _attach_and_get_candidates(cfg, job_id, run_id, manifest_rows):
    run_dir = cfg.output_root / run_id
    _write_manifest(run_dir, manifest_rows)
    rp = cfg.report_dir / f"rpt_{run_id}.md"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("# rpt", encoding="utf-8")
    detail = attach_run_report_to_job(cfg, job_id=job_id, run_id=run_id, report_path=rp)
    return detail["candidate_versions"]


def test_ten_jobs_no_cross_contamination(tmp_path):
    """Create 10 jobs, attach unique runs, verify each job has its own data."""
    cfg = _make_cfg(tmp_path)
    jobs = []
    for i in range(10):
        j = create_operator_job(cfg, source_audio=f"input/song_{i}.wav",
                                processing_depth="quick_scan",
                                project_label=f"batch-{i}")
        jobs.append(j)

    assert len(list_operator_jobs(cfg)) == 10

    # Attach unique runs to first 5 jobs
    for i in range(5):
        run_id = f"multi_{i:03d}"
        rows = [{
            "run_id": run_id, "task_id": f"TASK_{i}", "sample_id": f"SMP_{i}",
            "input_path": f"input/song_{i}.wav", "preset": "clean_master",
            "status": "done", "return_code": "0", "elapsed_seconds": "1.0",
            "output_dir": f"outputs/{run_id}/SMP_{i}/clean_master", "template_index": "0",
            "pseudo_mrs_before": str(10 + i), "pseudo_mrs_after": str(15 + i),
            "pseudo_delta_mrs": str(5), "mrs_open_v031_before": "",
            "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
            "mrs_open_flags": "", "error": "",
        }]
        _attach_and_get_candidates(cfg, jobs[i]["job_id"], run_id, rows)

    # Verify each job has correct status
    for i in range(10):
        j = get_operator_job(cfg, jobs[i]["job_id"])
        if i < 5:
            assert j["status"] in ("gate_review", "reprocess"), f"Job {i}: {j['status']}"
        else:
            assert j["status"] == "waiting", f"Job {i} should be waiting, got {j['status']}"


def test_deliver_three_jobs_to_same_order(tmp_path):
    """Deliver 3 candidates to one order and verify context."""
    cfg = _make_cfg(tmp_path)

    client = create_client(cfg, name="Multi-Job Client")
    project = create_project(cfg, client_id=client["client_id"], name="Multi-Project")
    order = create_order(cfg, project_id=project["project_id"], client_id=client["client_id"],
                         description="3 deliveries")

    delivered_ids = []
    for i in range(3):
        job = create_operator_job(cfg, source_audio=f"input/d_{i}.wav",
                                  processing_depth="quick_scan",
                                  project_label=f"delivery-{i}")
        run_id = f"dlv_{i:03d}"
        rows = [{
            "run_id": run_id, "task_id": f"T_D{i}", "sample_id": f"S_D{i}",
            "input_path": f"input/d_{i}.wav", "preset": "warm_vocal",
            "status": "done", "return_code": "0", "elapsed_seconds": "2.0",
            "output_dir": f"outputs/{run_id}/S_D{i}/warm_vocal", "template_index": "0",
            "pseudo_mrs_before": "10", "pseudo_mrs_after": "18",
            "pseudo_delta_mrs": "8", "mrs_open_v031_before": "",
            "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
            "mrs_open_flags": "", "error": "",
        }]
        cands = _attach_and_get_candidates(cfg, job["job_id"], run_id, rows)
        cand_id = cands[0]["candidate_id"]
        create_delivery_record(cfg, job_id=job["job_id"], candidate_id=cand_id)
        link_job_to_order(cfg, order_id=order["order_id"], job_id=job["job_id"])
        delivered_ids.append(job["job_id"])

    ctx = get_order_context(cfg, order_id=order["order_id"])
    assert ctx["delivery_status"]["total"] == 3
    assert ctx["delivery_status"]["delivered"] == 3
    assert set(j["job_id"] for j in ctx["linked_jobs"]) == set(delivered_ids)


def test_writeback_multiple_craft_records(tmp_path):
    """Write back 3 deliveries and verify craft records."""
    cfg = _make_cfg(tmp_path)

    for i in range(3):
        job = create_operator_job(cfg, source_audio=f"input/cr_{i}.wav",
                                  processing_depth="quick_scan",
                                  project_label=f"craft-{i}")
        run_id = f"crft_{i:03d}"
        rows = [{
            "run_id": run_id, "task_id": f"T_C{i}", "sample_id": f"S_C{i}",
            "input_path": f"input/cr_{i}.wav", "preset": "clean_master",
            "status": "done", "return_code": "0", "elapsed_seconds": "1.0",
            "output_dir": f"outputs/{run_id}/S_C{i}/clean_master", "template_index": "0",
            "pseudo_mrs_before": "10", "pseudo_mrs_after": str(15 + i),
            "pseudo_delta_mrs": str(5 + i), "mrs_open_v031_before": "",
            "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
            "mrs_open_flags": "", "error": "",
        }]
        cands = _attach_and_get_candidates(cfg, job["job_id"], run_id, rows)
        writeback_delivery_to_craft_record(cfg, job_id=job["job_id"],
                                           candidate_id=cands[0]["candidate_id"],
                                           adoption_status="candidate")

    records = list_craft_records(cfg)
    assert len(records) == 3
    craft_ids = {r["craft_id"] for r in records}
    assert len(craft_ids) == 3  # all unique


def test_sequential_job_lifecycle_loop(tmp_path):
    """Create → attach → deliver → writeback loop for 5 jobs."""
    cfg = _make_cfg(tmp_path)
    statuses = []
    job_ids = []

    for i in range(5):
        job = create_operator_job(cfg, source_audio=f"input/lc_{i}.wav",
                                  processing_depth="quick_scan",
                                  project_label=f"lifecycle-{i}")
        assert job["status"] == "waiting"
        job_ids.append(job["job_id"])
        statuses.append(("created", job["status"]))

        run_id = f"life_{i:03d}"
        rows = [{
            "run_id": run_id, "task_id": f"T_L{i}", "sample_id": f"S_L{i}",
            "input_path": f"input/lc_{i}.wav", "preset": "clean_master",
            "status": "done", "return_code": "0", "elapsed_seconds": "1.0",
            "output_dir": f"outputs/{run_id}/S_L{i}/clean_master", "template_index": "0",
            "pseudo_mrs_before": "10", "pseudo_mrs_after": "15",
            "pseudo_delta_mrs": "5", "mrs_open_v031_before": "",
            "mrs_open_v031_after": "", "delta_mrs_open_v031": "",
            "mrs_open_flags": "", "error": "",
        }]
        cands = _attach_and_get_candidates(cfg, job["job_id"], run_id, rows)
        j = get_operator_job(cfg, job["job_id"])
        statuses.append(("attached", j["status"]))

        cand_id = cands[0]["candidate_id"]
        create_delivery_record(cfg, job_id=job["job_id"], candidate_id=cand_id)
        j = get_operator_job(cfg, job["job_id"])
        assert j["status"] == "delivered", f"Job {i}: {j['status']}"

        writeback_delivery_to_craft_record(cfg, job_id=job["job_id"],
                                           candidate_id=cand_id)
        statuses.append(("delivered+crafted", j["status"]))

    # All 5 should be delivered — verify by stored job_id
    for jid in job_ids:
        j = get_operator_job(cfg, jid)
        assert j["status"] == "delivered"
    assert len(list_craft_records(cfg)) == 5
