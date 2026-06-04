"""MHP-328: Operator Core Tests — Job Board, Approval Flow, Audit Trail."""

import uuid
from pathlib import Path

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.operator_dashboard import (
    add_to_board,
    assign_board_job,
    list_board,
    transition_board_job,
    submit_approval,
    list_approvals,
    record_audit,
    list_audit_trail,
    JOB_BOARD_STATUSES,
    VALID_BOARD_TRANSITIONS,
)


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


# ── Job Board ─────────────────────────────────────────────────────────


def test_add_to_board(tmp_path):
    cfg = _make_cfg(tmp_path)
    j = add_to_board(cfg, "JOB_001", priority=3, client_id="CLI_001", tags=["urgent"])
    assert j["operator_job_id"] == "JOB_001"
    assert j["status"] == "unassigned"
    assert j["priority"] == 3


def test_assign_board_job(tmp_path):
    cfg = _make_cfg(tmp_path)
    j = add_to_board(cfg, "JOB_002")
    assigned = assign_board_job(cfg, j["board_id"], "operator_alice")
    assert assigned["status"] == "assigned"
    assert assigned["assigned_to"] == "operator_alice"


def test_assign_twice_fails(tmp_path):
    cfg = _make_cfg(tmp_path)
    j = add_to_board(cfg, "JOB_003")
    assign_board_job(cfg, j["board_id"], "alice")
    import pytest
    with pytest.raises(KeyError):
        assign_board_job(cfg, j["board_id"], "bob")


def test_list_board_filters(tmp_path):
    cfg = _make_cfg(tmp_path)
    add_to_board(cfg, "JOB_A", priority=1)
    j2 = add_to_board(cfg, "JOB_B", priority=10)
    assign_board_job(cfg, j2["board_id"], "alice")

    all_jobs = list_board(cfg)
    assert len(all_jobs) == 2

    alice_jobs = list_board(cfg, assigned_to="alice")
    assert len(alice_jobs) == 1

    unassigned = list_board(cfg, status="unassigned")
    assert len(unassigned) == 1


def test_valid_transitions(tmp_path):
    cfg = _make_cfg(tmp_path)
    j = add_to_board(cfg, "JOB_T")
    assign_board_job(cfg, j["board_id"], "alice")
    transition_board_job(cfg, j["board_id"], "in_review")
    transition_board_job(cfg, j["board_id"], "approved")
    transition_board_job(cfg, j["board_id"], "delivered")

    rows = list_board(cfg)
    assert rows[0]["status"] == "delivered"


def test_invalid_transition_raises(tmp_path):
    cfg = _make_cfg(tmp_path)
    j = add_to_board(cfg, "JOB_X")
    import pytest
    with pytest.raises(ValueError):
        transition_board_job(cfg, j["board_id"], "delivered")  # can't skip to delivered


# ── Approval Flow ─────────────────────────────────────────────────────


def test_submit_approval_approve(tmp_path):
    cfg = _make_cfg(tmp_path)
    j = add_to_board(cfg, "JOB_APR")
    assign_board_job(cfg, j["board_id"], "alice")
    transition_board_job(cfg, j["board_id"], "in_review")

    apr = submit_approval(cfg, j["board_id"], "JOB_APR", "reviewer_bob", "approve", "Sounds great")
    assert apr["action"] == "approve"
    assert apr["reviewer"] == "reviewer_bob"


def test_submit_approval_reject(tmp_path):
    cfg = _make_cfg(tmp_path)
    j = add_to_board(cfg, "JOB_REJ")
    assign_board_job(cfg, j["board_id"], "alice")
    transition_board_job(cfg, j["board_id"], "in_review")

    apr = submit_approval(cfg, j["board_id"], "JOB_REJ", "bob", "reject", "Over-dark detected")
    assert apr["action"] == "reject"


def test_list_approvals(tmp_path):
    cfg = _make_cfg(tmp_path)
    j = add_to_board(cfg, "JOB_LIST")
    assign_board_job(cfg, j["board_id"], "alice")
    transition_board_job(cfg, j["board_id"], "in_review")
    submit_approval(cfg, j["board_id"], "JOB_LIST", "bob", "approve")

    approvals = list_approvals(cfg, board_id=j["board_id"])
    assert len(approvals) == 1


# ── Audit Trail ───────────────────────────────────────────────────────


def test_audit_trail_append_only(tmp_path):
    cfg = _make_cfg(tmp_path)
    record_audit(cfg, "job.create", actor="alice", target_type="job", target_id="J1")
    record_audit(cfg, "board.assign", actor="alice", target_type="board_job", target_id="B1")
    record_audit(cfg, "approval.submit", actor="bob", target_type="approval", target_id="A1")

    trail = list_audit_trail(cfg)
    assert len(trail) == 3


def test_audit_trail_filter_by_actor(tmp_path):
    cfg = _make_cfg(tmp_path)
    record_audit(cfg, "job.create", actor="alice", target_type="job")
    record_audit(cfg, "job.create", actor="bob", target_type="job")

    alice = list_audit_trail(cfg, actor="alice")
    assert len(alice) == 1
    assert alice[0]["actor"] == "alice"


def test_audit_trail_filter_by_target(tmp_path):
    cfg = _make_cfg(tmp_path)
    record_audit(cfg, "job.create", actor="alice", target_type="job", target_id="J1")
    record_audit(cfg, "board.assign", actor="alice", target_type="board_job", target_id="B1")

    jobs = list_audit_trail(cfg, target_type="job")
    assert len(jobs) == 1
    assert jobs[0]["target_type"] == "job"
