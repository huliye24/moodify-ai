"""CWC ledger invariants and transaction replay tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from moodify.access.ledger import AccessLedger, InsufficientCWCError


def _ledger(tmp_path: Path) -> AccessLedger:
    return AccessLedger(tmp_path / "access")


def test_grant_and_balance(tmp_path: Path):
    ledger = _ledger(tmp_path)
    ledger.grant("u1", 100.0, operation="starter_credit")
    balance = ledger.balance("u1")
    assert balance.available_cwc == 100.0
    assert balance.lifetime_granted_cwc == 100.0


def test_reserve_consume_settles(tmp_path: Path):
    ledger = _ledger(tmp_path)
    ledger.grant("u1", 100.0)
    ledger.reserve("u1", 5.0, job_id="job-1", operation="pairwise_ab_judge")
    assert ledger.balance("u1").reserved_cwc == 5.0
    assert ledger.balance("u1").available_cwc == 95.0
    ledger.consume("u1", 5.0, job_id="job-1", operation="pairwise_ab_judge")
    balance = ledger.balance("u1")
    assert balance.reserved_cwc == 0.0
    assert balance.available_cwc == 95.0
    assert balance.lifetime_consumed_cwc == 5.0


def test_release_and_refund(tmp_path: Path):
    ledger = _ledger(tmp_path)
    ledger.grant("u1", 100.0)
    ledger.reserve("u1", 10.0, job_id="job-1", operation="full_analysis")
    ledger.release("u1", 10.0, job_id="job-1")
    assert ledger.balance("u1").available_cwc == 100.0

    ledger.reserve("u1", 10.0, job_id="job-2", operation="full_analysis")
    ledger.consume("u1", 6.0, job_id="job-2", operation="full_analysis")
    ledger.refund("u1", 4.0, job_id="job-2")
    balance = ledger.balance("u1")
    assert balance.available_cwc == 98.0
    assert balance.lifetime_refunded_cwc == 4.0


def test_insufficient_reserve_rejected(tmp_path: Path):
    ledger = _ledger(tmp_path)
    ledger.grant("u1", 3.0)
    with pytest.raises(InsufficientCWCError):
        ledger.reserve("u1", 5.0, job_id="job-1", operation="pairwise_ab_judge")


def test_available_never_negative(tmp_path: Path):
    ledger = _ledger(tmp_path)
    ledger.grant("u1", 10.0)
    ledger.reserve("u1", 10.0, job_id="job-1", operation="full_analysis")
    ledger.consume("u1", 10.0, job_id="job-1", operation="full_analysis")
    assert ledger.balance("u1").available_cwc == 0.0


def test_transactions_append_only(tmp_path: Path):
    ledger = _ledger(tmp_path)
    ledger.grant("u1", 100.0)
    ledger.reserve("u1", 5.0, job_id="job-1", operation="pairwise_ab_judge")
    txns = ledger.transactions()
    assert len(txns) == 2
    assert txns[0].type == "GRANT"
    assert txns[1].type == "RESERVE"


def test_referral_reward_counts_as_grant(tmp_path: Path):
    ledger = _ledger(tmp_path)
    ledger.grant("u1", 100.0)
    ledger.referral_reward("u1", 10.0, metadata={"kind": "referral_inviter"})
    balance = ledger.balance("u1")
    assert balance.available_cwc == 110.0
    assert balance.lifetime_granted_cwc == 110.0


def test_user_registration_with_starter(tmp_path: Path):
    ledger = _ledger(tmp_path)
    profile = ledger.register_user("u1", "OPEN")
    assert profile.registration_mode == "OPEN"
    assert ledger.balance("u1").available_cwc == 100.0
