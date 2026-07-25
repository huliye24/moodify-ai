from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from moodify.domain import (
    ApprovalActorType,
    ApprovalDecision,
    ApprovalOutcome,
    AudioVersion,
    VersionStatus,
)


SHA256 = "a" * 64
CREATED = datetime(2026, 7, 25, 10, 0, tzinfo=timezone.utc)


def _version(**overrides) -> AudioVersion:
    data = {
        "version_id": "version-001",
        "project_id": "project-001",
        "parent_version_id": "version-000",
        "branch": "warm-narrative",
        "name": "Warm Narrative v1",
        "purpose": "A/B candidate",
        "audio_path": "versions/v001_warm_narrative_draft.wav",
        "audio_sha256": SHA256,
        "treatment_plan_id": "plan-001",
        "treatment_variant_id": "variant-b",
        "treatment_record_id": "record-001",
        "created_by": "thread-worker-001",
        "created_at": CREATED,
        "updated_at": CREATED,
    }
    data.update(overrides)
    return AudioVersion(**data)


def _approval(
    outcome: ApprovalOutcome = ApprovalOutcome.APPROVED,
    at: datetime | None = None,
) -> ApprovalDecision:
    return ApprovalDecision(
        decision_id="decision-001",
        project_id="project-001",
        version_id="version-001",
        outcome=outcome,
        reason="听感符合目标",
        operator="user",
        actor_type=ApprovalActorType.HUMAN,
        decided_at=at or CREATED + timedelta(minutes=5),
    )


def test_audio_version_round_trip_json():
    version = _version()

    restored = AudioVersion.model_validate_json(version.model_dump_json())

    assert restored == version
    assert restored.schema_version == "audio_version.v1"


def test_version_accepts_root_and_child_nodes():
    root = _version(
        version_id="version-000",
        parent_version_id=None,
        branch="main",
        name="Original",
        purpose="Original source baseline",
        audio_path="versions/v000_original.wav",
        treatment_plan_id=None,
        treatment_variant_id=None,
        treatment_record_id=None,
    )
    child = _version(parent_version_id=root.version_id)

    assert root.parent_version_id is None
    assert child.parent_version_id == root.version_id


def test_version_cannot_be_its_own_parent():
    with pytest.raises(ValidationError):
        _version(parent_version_id="version-001")


def test_audio_path_must_be_safe_relative_and_lossless():
    for invalid in [
        "C:/audio/version.wav",
        "../versions/version.wav",
        "artifacts/version.wav",
        "versions/version.mp3",
    ]:
        with pytest.raises(ValidationError):
            _version(audio_path=invalid)

    assert _version(audio_path=r"versions\v001.flac").audio_path == (
        "versions/v001.flac"
    )


def test_sha256_must_be_canonical():
    assert _version(audio_sha256="A" * 64).audio_sha256 == SHA256

    with pytest.raises(ValidationError):
        _version(audio_sha256="not-a-hash")


def test_treatment_plan_and_variant_must_appear_together():
    with pytest.raises(ValidationError):
        _version(treatment_variant_id=None)

    with pytest.raises(ValidationError):
        _version(treatment_plan_id=None)


def test_happy_path_review_approval_delivery_archive():
    reviewing = _version().transition_to(
        VersionStatus.REVIEWING,
        at=CREATED + timedelta(minutes=1),
    )
    approval = _approval()
    approved = reviewing.transition_to(
        VersionStatus.APPROVED,
        at=CREATED + timedelta(minutes=5),
        approval=approval,
    )
    delivered = approved.transition_to(
        VersionStatus.DELIVERED,
        at=CREATED + timedelta(minutes=6),
    )
    archived = delivered.transition_to(
        VersionStatus.ARCHIVED,
        at=CREATED + timedelta(minutes=7),
    )

    assert archived.status is VersionStatus.ARCHIVED
    assert archived.audio_path == reviewing.audio_path
    assert archived.audio_sha256 == reviewing.audio_sha256


def test_rejected_version_requires_rejected_approval():
    reviewing = _version().transition_to(
        VersionStatus.REVIEWING,
        at=CREATED + timedelta(minutes=1),
    )

    with pytest.raises(ValidationError):
        reviewing.transition_to(
            VersionStatus.REJECTED,
            at=CREATED + timedelta(minutes=5),
            approval=_approval(ApprovalOutcome.APPROVED),
        )

    rejected = reviewing.transition_to(
        VersionStatus.REJECTED,
        at=CREATED + timedelta(minutes=5),
        approval=_approval(ApprovalOutcome.REJECTED),
    )
    assert rejected.approval.outcome is ApprovalOutcome.REJECTED


def test_approved_and_delivered_require_human_evidence():
    with pytest.raises(ValidationError):
        _version(status=VersionStatus.APPROVED)

    with pytest.raises(ValidationError):
        _version(status=VersionStatus.DELIVERED)


def test_illegal_transition_is_rejected():
    with pytest.raises(ValueError):
        _version().transition_to(VersionStatus.DELIVERED)

    archived = _version(
        status=VersionStatus.ARCHIVED,
        approval=_approval(),
    )
    with pytest.raises(ValueError):
        archived.transition_to(VersionStatus.REVIEWING)


def test_rejected_audio_is_not_reworked_in_place():
    rejected = _version(
        status=VersionStatus.REJECTED,
        approval=_approval(ApprovalOutcome.REJECTED),
    )

    with pytest.raises(ValueError):
        rejected.transition_to(VersionStatus.REVIEWING)

    child = _version(
        version_id="version-002",
        parent_version_id=rejected.version_id,
        audio_path="versions/v002_repair_draft.wav",
        audio_sha256="b" * 64,
    )
    assert child.parent_version_id == rejected.version_id


def test_timestamps_must_be_aware_and_ordered():
    with pytest.raises(ValidationError):
        _version(created_at=datetime(2026, 7, 25))

    with pytest.raises(ValidationError):
        _version(updated_at=CREATED - timedelta(seconds=1))

    with pytest.raises(ValidationError):
        _version(approval=_approval(at=CREATED - timedelta(seconds=1)))


def test_models_are_frozen_and_reject_unknown_fields():
    version = _version()

    with pytest.raises(ValidationError):
        version.audio_path = "versions/overwrite.wav"

    with pytest.raises(ValidationError):
        AudioVersion.model_validate({**version.model_dump(), "unknown": True})
