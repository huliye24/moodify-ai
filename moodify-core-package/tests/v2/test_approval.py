from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from moodify.domain import (
    ApprovalActorType,
    ApprovalDecision,
    ApprovalOutcome,
    ThreadType,
)


def _decision(**overrides) -> ApprovalDecision:
    data = {
        "decision_id": "decision-001",
        "project_id": "project-001",
        "version_id": "version-001",
        "outcome": ApprovalOutcome.APPROVED,
        "reason": "听感符合目标，可以作为 Final",
        "operator": "producer@example.com",
        "actor_type": ApprovalActorType.HUMAN,
    }
    data.update(overrides)
    return ApprovalDecision(**data)


def test_approval_decision_round_trip_json():
    decision = _decision()

    restored = ApprovalDecision.model_validate_json(decision.model_dump_json())

    assert restored == decision
    assert restored.schema_version == "approval_decision.v1"


@pytest.mark.parametrize(
    "outcome",
    [ApprovalOutcome.APPROVED, ApprovalOutcome.REJECTED],
)
def test_approve_and_reject_do_not_use_return_node(outcome):
    decision = _decision(outcome=outcome)
    assert decision.return_to_thread is None


def test_returned_decision_requires_return_node():
    with pytest.raises(ValidationError):
        _decision(outcome=ApprovalOutcome.RETURNED)

    decision = _decision(
        outcome=ApprovalOutcome.RETURNED,
        return_to_thread=ThreadType.VOCAL,
    )
    assert decision.return_to_thread is ThreadType.VOCAL


def test_non_returned_decision_rejects_return_node():
    with pytest.raises(ValidationError):
        _decision(return_to_thread=ThreadType.SPECTRUM)


def test_final_approval_must_be_human():
    with pytest.raises(ValidationError):
        _decision(actor_type=ApprovalActorType.SYSTEM)

    system_rejection = _decision(
        outcome=ApprovalOutcome.REJECTED,
        actor_type=ApprovalActorType.SYSTEM,
    )
    assert system_rejection.actor_type is ApprovalActorType.SYSTEM


def test_reason_and_operator_are_required():
    with pytest.raises(ValidationError):
        _decision(reason=" ")

    with pytest.raises(ValidationError):
        _decision(operator="")


def test_decision_cannot_supersede_itself():
    with pytest.raises(ValidationError):
        _decision(supersedes_decision_id="decision-001")


def test_decided_at_must_be_timezone_aware():
    with pytest.raises(ValidationError):
        _decision(decided_at=datetime(2026, 7, 25))

    aware = _decision(decided_at=datetime(2026, 7, 25, tzinfo=timezone.utc))
    assert aware.decided_at.utcoffset() is not None


def test_decision_is_frozen_and_rejects_unknown_fields():
    decision = _decision()

    with pytest.raises(ValidationError):
        decision.reason = "changed"

    with pytest.raises(ValidationError):
        ApprovalDecision.model_validate(
            {**decision.model_dump(), "unknown": True}
        )
