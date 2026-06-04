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
