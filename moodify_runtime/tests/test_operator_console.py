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


# ── Delivery Record tests ────────────────────────────────────────


def test_create_delivery_record_for_approved_candidate(tmp_path):
    from moodify_runtime.operator_console import (
        attach_run_report_to_job,
        create_delivery_record,
        get_delivery_record,
        get_operator_job,
    )

    cfg = RuntimeConfig(
        project_root=tmp_path,
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
    )
    job = create_operator_job(cfg, source_audio="input/song.wav", processing_depth="deep_process")
    run_dir = tmp_path / "outputs" / "run_dlv"
    _write_manifest(
        run_dir,
        [
            {
                "run_id": "run_dlv",
                "task_id": "TASK_A",
                "sample_id": "SMP_A",
                "input_path": "input/song.wav",
                "preset": "clean_master",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "5.0",
                "output_dir": "outputs/run_dlv/SMP_A/clean_master",
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
    report_path = tmp_path / "reports" / "daily_report_run_dlv.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# report", encoding="utf-8")

    attach_run_report_to_job(cfg, job_id=job["job_id"], run_id="run_dlv", report_path=report_path)

    # Read the actual candidate_id from the detail
    import json as _j
    detail_file = tmp_path / "operator_details" / f"{job['job_id']}.json"
    detail = _j.loads(detail_file.read_text())
    cand_id = detail["candidate_versions"][0]["candidate_id"]

    delivery = create_delivery_record(
        cfg,
        job_id=job["job_id"],
        candidate_id=cand_id,
        operator_decision="approved",
        notes="operator signed off",
    )
    assert delivery["delivery_id"].startswith("DLV_")
    assert delivery["job_id"] == job["job_id"]

    updated = get_operator_job(cfg, job["job_id"])
    assert updated["status"] == "delivered"

    d = get_delivery_record(cfg, job["job_id"])
    assert d["delivery_id"] == delivery["delivery_id"]


def test_delivery_rejects_missing_candidate(tmp_path):
    from moodify_runtime.operator_console import create_delivery_record, create_operator_job

    cfg = RuntimeConfig(
        project_root=tmp_path,
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
    )
    job = create_operator_job(cfg, source_audio="input/song.wav")
    # No detail attached → candidate lookup will fail
    with pytest.raises(ValueError, match="candidate_id"):
        create_delivery_record(cfg, job_id=job["job_id"], candidate_id="NONEXISTENT")


def test_delivery_override_allows_reprocess(tmp_path):
    from moodify_runtime.operator_console import (
        attach_run_report_to_job,
        create_delivery_record,
        create_operator_job,
    )

    cfg = RuntimeConfig(
        project_root=tmp_path,
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
    )
    job = create_operator_job(cfg, source_audio="input/song.wav", processing_depth="deep_process")
    run_dir = tmp_path / "outputs" / "run_ovr"
    _write_manifest(
        run_dir,
        [
            {
                "run_id": "run_ovr",
                "task_id": "TASK_OVR",
                "sample_id": "SMP_OVR",
                "input_path": "input/song.wav",
                "preset": "clean_master",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "5.0",
                "output_dir": "outputs/run_ovr/SMP_OVR/clean_master",
                "template_index": "0",
                "pseudo_mrs_before": "10",
                "pseudo_mrs_after": "9",
                "pseudo_delta_mrs": "-1",
                "mrs_open_v031_before": "",
                "mrs_open_v031_after": "",
                "delta_mrs_open_v031": "",
                "mrs_open_flags": "over_dark",
                "error": "",
            }
        ],
    )
    report_path = tmp_path / "reports" / "daily_report_run_ovr.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# report", encoding="utf-8")

    attach_run_report_to_job(cfg, job_id=job["job_id"], run_id="run_ovr", report_path=report_path)

    # Without override, reprocess should fail
    detail_dir = tmp_path / "operator_details"
    detail_file = detail_dir / f"{job['job_id']}.json"
    import json
    detail = json.loads(detail_file.read_text())
    cand_id = detail["candidate_versions"][0]["candidate_id"]

    with pytest.raises(ValueError, match="override"):
        create_delivery_record(cfg, job_id=job["job_id"], candidate_id=cand_id)

    # With override it should succeed
    delivery = create_delivery_record(
        cfg,
        job_id=job["job_id"],
        candidate_id=cand_id,
        override=True,
        notes="manual override after review",
    )
    assert delivery["delivery_id"].startswith("DLV_")


def test_list_delivery_records(tmp_path):
    from moodify_runtime.operator_console import (
        attach_run_report_to_job,
        create_delivery_record,
        create_operator_job,
        list_delivery_records,
    )

    cfg = RuntimeConfig(
        project_root=tmp_path,
        output_root=tmp_path / "outputs",
        report_dir=tmp_path / "reports",
        operator_jobs_path=tmp_path / "operator_jobs.jsonl",
        operator_detail_dir=tmp_path / "operator_details",
        operator_deliveries_path=tmp_path / "operator_deliveries.jsonl",
    )

    deliveries = []
    for i in range(2):
        job = create_operator_job(cfg, source_audio=f"input/song_{i}.wav", processing_depth="deep_process")
        run_dir = tmp_path / "outputs" / f"run_lst_{i}"
        _write_manifest(
            run_dir,
            [
                {
                    "run_id": f"run_lst_{i}",
                    "task_id": f"TASK_{i}",
                    "sample_id": f"SMP_{i}",
                    "input_path": f"input/song_{i}.wav",
                    "preset": "clean_master",
                    "status": "done",
                    "return_code": "0",
                    "elapsed_seconds": "3.0",
                    "output_dir": f"outputs/run_lst_{i}/SMP_{i}/clean_master",
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
        report_path = tmp_path / "reports" / f"daily_report_run_lst_{i}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("# report", encoding="utf-8")
        attach_run_report_to_job(cfg, job_id=job["job_id"], run_id=f"run_lst_{i}", report_path=report_path)

        detail_dir = tmp_path / "operator_details"
        import json as jmod
        detail = jmod.loads((detail_dir / f"{job['job_id']}.json").read_text())
        cand_id = detail["candidate_versions"][0]["candidate_id"]

        deliveries.append(create_delivery_record(cfg, job_id=job["job_id"], candidate_id=cand_id))

    records = list_delivery_records(cfg)
    assert len(records) == 2
    delivery_ids = {r["delivery_id"] for r in records}
    assert deliveries[0]["delivery_id"] in delivery_ids
    assert deliveries[1]["delivery_id"] in delivery_ids


def test_operator_deliver_cli(tmp_path, capsys):
    import json as jmod

    config_path = tmp_path / "runtime_config.json"
    config_path.write_text(
        '{"project_root":"%s","output_root":"outputs","report_dir":"reports",'
        '"operator_jobs_path":"operator_jobs.jsonl",'
        '"operator_detail_dir":"operator_details",'
        '"operator_deliveries_path":"operator_deliveries.jsonl"}' % tmp_path.as_posix(),
        encoding="utf-8",
    )
    run_dir = tmp_path / "outputs" / "run_cli_dlv"
    _write_manifest(
        run_dir,
        [
            {
                "run_id": "run_cli_dlv",
                "task_id": "TASK_CLI_DLV",
                "sample_id": "SMP_CLI_DLV",
                "input_path": "input/song.wav",
                "preset": "clean_master",
                "status": "done",
                "return_code": "0",
                "elapsed_seconds": "2.0",
                "output_dir": "outputs/run_cli_dlv/SMP_CLI_DLV/clean_master",
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
    report_path = tmp_path / "reports" / "daily_report_run_cli_dlv.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# report", encoding="utf-8")

    # Create job
    assert main(["--config", str(config_path), "operator-create",
                 "--source-audio", "input/song.wav", "--depth", "standard_process"]) == 0
    job = jmod.loads(capsys.readouterr().out)
    job_id = job["job_id"]

    # Attach run
    assert main(["--config", str(config_path), "operator-attach-run",
                 "--job-id", job_id, "--run-id", "run_cli_dlv"]) == 0
    _ = capsys.readouterr().out  # flush

    # Get detail to find candidate_id
    assert main(["--config", str(config_path), "operator-detail", "--job-id", job_id]) == 0
    detail = jmod.loads(capsys.readouterr().out)
    cand_id = detail["detail"]["candidate_versions"][0]["candidate_id"]

    # Deliver
    assert main(["--config", str(config_path), "operator-deliver",
                 "--job-id", job_id, "--candidate-id", cand_id]) == 0
    delivered = jmod.loads(capsys.readouterr().out)
    assert delivered["job_id"] == job_id
    assert delivered["delivery_id"].startswith("DLV_")

    # Get delivery
    assert main(["--config", str(config_path), "operator-delivery-get",
                 "--job-id", job_id]) == 0
    d = jmod.loads(capsys.readouterr().out)
    assert d["delivery_id"] == delivered["delivery_id"]

    # List deliveries — at minimum our delivery should appear
    assert main(["--config", str(config_path), "operator-delivery-list"]) == 0
    dl = jmod.loads(capsys.readouterr().out)
    assert len(dl["deliveries"]) >= 1
    our_ids = {d["delivery_id"] for d in dl["deliveries"]}
    assert delivered["delivery_id"] in our_ids
