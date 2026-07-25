from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from moodify.domain import (
    AudioProject,
    ProjectWorkflow,
    WorkflowAction,
    WorkflowStage,
)
from moodify.storage import StorageConflict, StorageNotFound, WorkspaceStore


BASE = datetime(2026, 7, 25, 9, 0, tzinfo=timezone.utc)


def _workflow(**overrides):
    data = {
        "project_id": "project-001",
        "created_at": BASE,
        "updated_at": BASE,
    }
    data.update(overrides)
    return ProjectWorkflow(**data)


def test_workflow_starts_at_intake_and_round_trips():
    workflow = _workflow()
    restored = ProjectWorkflow.model_validate_json(workflow.model_dump_json())

    assert restored == workflow
    assert workflow.stage is WorkflowStage.INTAKE
    assert workflow.schema_version == "project_workflow.v1"


def test_happy_path_reaches_final_in_fixed_order():
    workflow = _workflow()
    visited = [workflow.stage]
    for offset in range(1, 8):
        workflow = workflow.advance(at=BASE + timedelta(seconds=offset))
        visited.append(workflow.stage)

    assert visited == [
        WorkflowStage.INTAKE,
        WorkflowStage.BRIEF,
        WorkflowStage.DIAGNOSIS,
        WorkflowStage.DESIGN,
        WorkflowStage.PROCESS,
        WorkflowStage.JUDGE,
        WorkflowStage.APPROVAL,
        WorkflowStage.FINAL,
    ]
    assert len(workflow.history) == 7


def test_advance_cannot_skip_or_leave_terminal_stage():
    workflow = _workflow()
    with pytest.raises(ValidationError):
        ProjectWorkflow.model_validate(
            {**workflow.model_dump(), "stage": WorkflowStage.DESIGN}
        )

    for offset in range(1, 8):
        workflow = workflow.advance(at=BASE + timedelta(seconds=offset))
    with pytest.raises(ValueError, match="cannot advance"):
        workflow.advance(at=BASE + timedelta(seconds=8))


def test_pause_and_resume_return_to_exact_stage():
    design = _workflow()
    for offset in range(1, 4):
        design = design.advance(at=BASE + timedelta(seconds=offset))
    paused = design.pause(
        at=BASE + timedelta(seconds=4), reason="waiting for user"
    )
    resumed = paused.resume(at=BASE + timedelta(seconds=5))

    assert paused.stage is WorkflowStage.PAUSED
    assert paused.paused_from is WorkflowStage.DESIGN
    assert resumed.stage is WorkflowStage.DESIGN
    assert resumed.history[-1].action is WorkflowAction.RESUME


def test_only_active_nonfinal_workflow_can_pause():
    paused = _workflow().pause(at=BASE + timedelta(seconds=1))
    with pytest.raises(ValueError):
        paused.pause(at=BASE + timedelta(seconds=2))
    failed = _workflow().fail("broken", at=BASE + timedelta(seconds=1))
    with pytest.raises(ValueError):
        failed.pause(at=BASE + timedelta(seconds=2))


def test_only_paused_workflow_can_resume():
    with pytest.raises(ValueError, match="only a PAUSED"):
        _workflow().resume(at=BASE + timedelta(seconds=1))


def test_failure_records_reason_and_is_terminal():
    failed = _workflow().fail(
        "DSP unavailable", at=BASE + timedelta(seconds=1)
    )

    assert failed.stage is WorkflowStage.FAILED
    assert failed.failure_reason == "DSP unavailable"
    assert failed.history[-1].reason == "DSP unavailable"
    with pytest.raises(ValueError):
        failed.advance(at=BASE + timedelta(seconds=2))
    with pytest.raises(ValueError):
        failed.fail("again", at=BASE + timedelta(seconds=2))


def test_transition_timestamps_must_be_monotonic_and_aware():
    workflow = _workflow()
    with pytest.raises(ValueError, match="timezone-aware"):
        workflow.advance(at=datetime(2026, 7, 25))
    with pytest.raises(ValueError, match="must not precede"):
        workflow.advance(at=BASE - timedelta(seconds=1))


def test_invalid_paused_and_failed_snapshots_are_rejected():
    with pytest.raises(ValidationError):
        _workflow(stage=WorkflowStage.PAUSED)
    with pytest.raises(ValidationError):
        _workflow(stage=WorkflowStage.FAILED)
    with pytest.raises(ValidationError):
        _workflow(failure_reason="not failed")


def test_workflow_is_frozen_and_rejects_unknown_fields():
    workflow = _workflow()
    with pytest.raises(ValidationError):
        workflow.stage = WorkflowStage.BRIEF
    with pytest.raises(ValidationError):
        ProjectWorkflow.model_validate(
            {**workflow.model_dump(), "unknown": True}
        )


def test_workspace_store_persists_and_updates_workflow_atomically(tmp_path):
    store = WorkspaceStore(tmp_path)
    store.create_project(
        AudioProject(
            project_id="project-001",
            title="状态机测试",
            source_audio_ids=["source-001"],
            created_at=BASE,
            updated_at=BASE,
        )
    )
    workflow = _workflow()
    store.create_workflow(workflow)
    advanced = workflow.advance(at=BASE + timedelta(seconds=1))
    store.update_workflow(advanced)

    assert store.get_workflow("project-001") == advanced
    assert not list(tmp_path.rglob("*.tmp"))


def test_workflow_storage_enforces_project_and_identity(tmp_path):
    store = WorkspaceStore(tmp_path)
    with pytest.raises(StorageNotFound):
        store.create_workflow(_workflow())

    store.create_project(
        AudioProject(
            project_id="project-001",
            title="状态机测试",
            source_audio_ids=["source-001"],
            created_at=BASE,
            updated_at=BASE,
        )
    )
    store.create_workflow(_workflow())
    with pytest.raises(StorageConflict):
        store.create_workflow(_workflow())
    with pytest.raises(StorageConflict):
        store.update_workflow(
            _workflow(
                created_at=BASE + timedelta(seconds=1),
                updated_at=BASE + timedelta(seconds=1),
            )
        )
