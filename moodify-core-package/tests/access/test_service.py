"""Access service: open registration and referral reward rules."""

from __future__ import annotations

from pathlib import Path

from moodify.access.service import AccessService


def _service(tmp_path: Path) -> AccessService:
    return AccessService(tmp_path / "access")


def test_open_registration_without_code(tmp_path: Path):
    service = _service(tmp_path)
    result = service.register("u1")
    assert result["registration_mode"] == "OPEN"
    assert result["balance"]["available_cwc"] == 100.0
    assert result["referral_code_used"] is None


def test_registration_with_referral_grants_both(tmp_path: Path):
    service = _service(tmp_path)
    service.register("inviter")
    result = service.register("invitee", referral_code="inviter")
    assert result["registration_mode"] == "REFERRAL"
    assert result["referral"]["state"] == "GRANTED"
    assert service.balance("inviter")["available_cwc"] == 110.0
    assert service.balance("invitee")["available_cwc"] == 105.0


def test_self_referral_rejected(tmp_path: Path):
    service = _service(tmp_path)
    service.register("u1")
    result = service.register("u2", referral_code="u2")
    assert result["referral"]["state"] == "SELF_REFERRAL_REJECTED"
    assert service.balance("u2")["available_cwc"] == 100.0


def test_inviter_reward_one_time(tmp_path: Path):
    service = _service(tmp_path)
    service.register("inviter")
    service.register("i1", referral_code="inviter")
    result = service.register("i2", referral_code="inviter")
    assert result["referral"]["state"] == "INVITER_ALREADY_REWARDED"
    assert service.balance("inviter")["available_cwc"] == 110.0  # one bonus only


def test_unknown_inviter_no_reward(tmp_path: Path):
    service = _service(tmp_path)
    result = service.register("u1", referral_code="ghost")
    assert result["referral"]["state"] == "INVALID_INVITER"
    assert service.balance("u1")["available_cwc"] == 100.0


def test_invitee_rewarded_once(tmp_path: Path):
    service = _service(tmp_path)
    service.register("a")
    service.register("b")
    service.register("u1", referral_code="a")
    result = service.grant_referral_reward("b", "u1")
    assert result["state"] == "INVITEE_ALREADY_REWARDED"


def test_referral_status(tmp_path: Path):
    service = _service(tmp_path)
    service.register("inviter")
    service.register("i1", referral_code="inviter")
    status = service.referral_status("inviter")
    assert len(status["referral_records"]) == 1
    assert status["total_rewarded_cwc"] == 10.0


def test_history_lists_user_transactions(tmp_path: Path):
    service = _service(tmp_path)
    service.register("u1")
    service.admit("u1", "quick_scan")
    history = service.history("u1")
    assert len(history) >= 2  # GRANT + RESERVE
    assert all(t["owner_id"] == "u1" for t in history)
