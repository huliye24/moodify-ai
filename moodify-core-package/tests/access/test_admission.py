"""Compute admission: estimate, concurrency, queue, settle, limits."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from moodify.access.admission import AdmissionController
from moodify.access.policy import AccessPolicy


def _controller(tmp_path: Path, **overrides) -> AdmissionController:
    policy = AccessPolicy.from_yaml()
    if overrides:
        policy = replace(policy, **overrides)
    return AdmissionController(tmp_path / "access", policy=policy)


def _register(controller: AdmissionController, user_id: str) -> None:
    controller.ledger.register_user(user_id, "OPEN", policy=controller.policy)


def test_estimate_known_operation(tmp_path: Path):
    controller = _controller(tmp_path)
    estimate = controller.estimate("pairwise_ab_judge")
    assert estimate["estimated_cwc"] == 5.0
    assert estimate["policy_version"] == "access_policy_v1"


def test_estimate_unknown_operation_rejected(tmp_path: Path):
    controller = _controller(tmp_path)
    with pytest.raises(ValueError):
        controller.estimate("no_such_operation")


def test_admit_reserves_and_increments_concurrency(tmp_path: Path):
    controller = _controller(tmp_path)
    _register(controller, "u1")
    result = controller.admit("u1", "pairwise_ab_judge")
    assert result["queue_state"] == "ADMITTED"
    assert controller.ledger.balance("u1").reserved_cwc == 5.0
    assert controller.quota("u1")["concurrency_active"] == 1


def test_concurrency_full_queues(tmp_path: Path):
    controller = _controller(tmp_path)
    _register(controller, "u1")
    first = controller.admit("u1", "pairwise_ab_judge")
    assert first["queue_state"] == "ADMITTED"
    second = controller.admit("u1", "pairwise_ab_judge")
    assert second["queue_state"] == "QUEUED"
    assert controller.ledger.balance("u1").reserved_cwc == 5.0  # queued reserves nothing


def test_settle_consumes_and_refunds_difference(tmp_path: Path):
    controller = _controller(tmp_path)
    _register(controller, "u1")
    admitted = controller.admit("u1", "pairwise_ab_judge")
    result = controller.settle(admitted["admission_id"], actual_cwc=4.0)
    assert result["queue_state"] == "COMPLETED"
    balance = controller.ledger.balance("u1")
    # reserve 5 -> consume 4 -> release 1: available = 100 - 4
    assert balance.available_cwc == 96.0
    assert balance.lifetime_consumed_cwc == 4.0
    assert controller.quota("u1")["concurrency_active"] == 0


def test_fail_releases_reservation(tmp_path: Path):
    controller = _controller(tmp_path)
    _register(controller, "u1")
    admitted = controller.admit("u1", "full_analysis")
    result = controller.fail(admitted["admission_id"], failure_reason="decode_error")
    assert result["queue_state"] == "FAILED"
    assert controller.ledger.balance("u1").available_cwc == 100.0


def test_insufficient_balance_rejected(tmp_path: Path):
    controller = _controller(tmp_path, tier_rate_limits={"free": 1000, "creator": 1000, "enterprise": 1000})
    _register(controller, "u1")
    for _ in range(40):
        admitted = controller.admit("u1", "full_analysis")
        if admitted["queue_state"] == "ADMITTED":
            controller.settle(admitted["admission_id"], actual_cwc=3.0)
    result = controller.admit("u1", "pairwise_ab_judge")
    assert result["queue_state"] == "REJECTED_INSUFFICIENT"
    assert result["failure_reason"] == "INSUFFICIENT_CWC"


def test_rate_limit_enforced(tmp_path: Path):
    controller = _controller(tmp_path)
    _register(controller, "u1")
    controller.admit("u1", "quick_scan")
    controller.admit("u1", "quick_scan")
    third = controller.admit("u1", "quick_scan")
    assert third["queue_state"] in ("ADMITTED", "QUEUED")
    fourth = controller.admit("u1", "quick_scan")
    assert fourth["failure_reason"] == "RATE_LIMITED"


def test_daily_quota_enforced(tmp_path: Path):
    controller = _controller(tmp_path)
    _register(controller, "u1")
    # free tier allows 2 ranking_10_tracks per day
    for i in range(2):
        admitted = controller.admit("u1", "ranking_10_tracks")
        assert admitted["queue_state"] == "ADMITTED"
        controller.settle(admitted["admission_id"], actual_cwc=20.0)
    result = controller.admit("u1", "ranking_10_tracks")
    assert result["failure_reason"] == "DAILY_QUOTA_EXCEEDED"


def test_queue_depth_capped(tmp_path: Path):
    controller = _controller(tmp_path, max_queue_depth=3,
                             tier_rate_limits={"free": 1000, "creator": 1000, "enterprise": 1000})
    _register(controller, "u1")
    first = controller.admit("u1", "quick_scan")  # ADMITTED -> concurrency 1
    assert first["queue_state"] == "ADMITTED"
    for _ in range(3):
        controller.admit("u1", "quick_scan")  # QUEUED x3
    result = controller.admit("u1", "quick_scan")
    assert result["failure_reason"] == "QUEUE_FULL"
