from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from moodify.domain.project import AudioProject, LegacyReference, ProjectStatus


def make_project(**overrides):
    data = {
        "project_id": "PRJ_001",
        "title": "Golden Path Song",
        "source_audio_ids": ["ART_VOCALS", "ART_INSTRUMENTAL"],
    }
    data.update(overrides)
    return AudioProject(**data)


def test_audio_project_round_trip_json_preserves_schema_and_enums():
    project = make_project(
        creative_brief={
            "goal": "warm and intimate",
            "preserve": ["natural dynamics"],
            "avoid": ["harsh highs"],
            "platform": "streaming",
        },
        legacy_refs=[
            LegacyReference(
                source_type="studio_project",
                legacy_id="PRJ_LEGACY",
                source_hash="abc123",
            )
        ],
    )

    restored = AudioProject.model_validate_json(project.model_dump_json())

    assert restored == project
    assert restored.schema_version == "audio_project.v1"
    assert restored.status is ProjectStatus.CREATED
    assert restored.creative_brief is not None
    assert restored.creative_brief.goal == "warm and intimate"
    assert restored.legacy_refs[0].migration_key == (
        "studio_project:PRJ_LEGACY:abc123"
    )


def test_audio_project_rejects_unknown_fields():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        make_project(untracked_internal_value="secret")


@pytest.mark.parametrize(
    "source_ids",
    [
        [],
        ["ART_1", "ART_1"],
        ["ART_1", "   "],
    ],
)
def test_audio_project_requires_nonempty_unique_source_audio_ids(source_ids):
    with pytest.raises(ValidationError):
        make_project(source_audio_ids=source_ids)


def test_delivered_project_requires_the_same_approved_and_delivered_version():
    with pytest.raises(ValidationError, match="approved_version_id"):
        make_project(
            status=ProjectStatus.DELIVERED,
            delivered_version_id="VER_002",
        )

    with pytest.raises(ValidationError, match="must equal"):
        make_project(
            status=ProjectStatus.DELIVERED,
            approved_version_id="VER_001",
            delivered_version_id="VER_002",
        )

    project = make_project(
        status=ProjectStatus.DELIVERED,
        active_version_id="VER_001",
        approved_version_id="VER_001",
        delivered_version_id="VER_001",
    )
    assert project.status is ProjectStatus.DELIVERED


def test_project_timestamps_are_ordered_and_timezone_aware():
    created_at = datetime(2026, 7, 25, tzinfo=timezone.utc)

    with pytest.raises(ValidationError, match="timezone-aware"):
        make_project(created_at=created_at.replace(tzinfo=None))

    with pytest.raises(ValidationError, match="earlier than"):
        make_project(
            created_at=created_at,
            updated_at=created_at - timedelta(seconds=1),
        )


def test_assignment_is_validated():
    project = make_project()

    with pytest.raises(ValidationError):
        project.source_audio_ids = ["ART_1", "ART_1"]
