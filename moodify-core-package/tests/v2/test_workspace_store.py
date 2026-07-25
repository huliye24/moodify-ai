from datetime import datetime, timezone

import pytest

from moodify.domain import (
    ApprovalActorType,
    ApprovalDecision,
    ApprovalOutcome,
    AudioProject,
    AudioVersion,
    ProjectStatus,
    ProjectThread,
    ThreadRole,
    ThreadType,
    TreatmentAction,
    TreatmentPlan,
    TreatmentStepType,
    TreatmentVariant,
)
from moodify.storage import (
    StorageConflict,
    StorageCorruption,
    StorageNotFound,
    WorkspaceStore,
)


NOW = datetime(2026, 7, 25, tzinfo=timezone.utc)


def _project(project_id="project-001"):
    return AudioProject(
        project_id=project_id,
        title="验收歌曲",
        source_audio_ids=["source-001"],
        created_at=NOW,
        updated_at=NOW,
    )


def _thread():
    return ProjectThread(
        thread_id="thread-001",
        project_id="project-001",
        thread_type=ThreadType.DESIGN,
        role=ThreadRole.DESIGNER,
        created_at=NOW,
        updated_at=NOW,
    )


def _plan():
    action = TreatmentAction(
        action_id="action-001",
        order=1,
        step_type=TreatmentStepType.SPECTRAL_BALANCE,
        public_summary="平衡频谱",
        reason="控制刺激感",
    )
    variant = TreatmentVariant(
        variant_id="variant-a",
        label="A",
        name="Natural",
        objective="自然修复",
        problems=["高频刺激"],
        actions=[action],
        risks=["修复不足"],
        expected_output="平衡版本",
    )
    return TreatmentPlan(
        plan_id="plan-001",
        project_id="project-001",
        brief_revision=1,
        diagnosis_id="diagnosis-001",
        variants=[variant],
        created_by_thread_id="thread-001",
        created_at=NOW,
    )


def _version():
    return AudioVersion(
        version_id="version-001",
        project_id="project-001",
        branch="main",
        name="Original",
        purpose="baseline",
        audio_path="versions/v001.wav",
        audio_sha256="a" * 64,
        created_by="worker",
        created_at=NOW,
        updated_at=NOW,
    )


def _approval(decision_id="decision-001"):
    return ApprovalDecision(
        decision_id=decision_id,
        project_id="project-001",
        version_id="version-001",
        outcome=ApprovalOutcome.APPROVED,
        reason="符合目标",
        operator="user",
        actor_type=ApprovalActorType.HUMAN,
        decided_at=NOW,
    )


def test_project_create_read_update_round_trip(tmp_path):
    store = WorkspaceStore(tmp_path)
    project = _project()
    store.create_project(project)

    assert store.get_project(project.project_id) == project
    updated = project.model_copy(update={"status": ProjectStatus.BRIEFING})
    store.update_project(updated)
    assert store.get_project(project.project_id).status is ProjectStatus.BRIEFING


def test_thread_create_read_update_and_list(tmp_path):
    store = WorkspaceStore(tmp_path)
    store.create_project(_project())
    thread = _thread()
    store.create_thread(thread)
    store.update_thread(thread.model_copy(update={"current_task_id": "task-1"}))

    assert store.get_thread("project-001", "thread-001").current_task_id == "task-1"
    assert store.list_ids("project-001", "threads") == ["thread-001"]


def test_plan_and_version_are_create_once_snapshots(tmp_path):
    store = WorkspaceStore(tmp_path)
    store.create_project(_project())
    store.create_plan(_plan())
    store.create_version(_version())

    assert store.get_plan("project-001", "plan-001").plan_id == "plan-001"
    assert store.get_version("project-001", "version-001").version_id == "version-001"
    with pytest.raises(StorageConflict):
        store.create_version(_version())


def test_approval_log_is_append_only_and_ordered(tmp_path):
    store = WorkspaceStore(tmp_path)
    store.create_project(_project())
    store.append_approval(_approval("decision-001"))
    store.append_approval(_approval("decision-002"))

    assert [d.decision_id for d in store.list_approvals("project-001")] == [
        "decision-001",
        "decision-002",
    ]


def test_duplicate_approval_is_rejected(tmp_path):
    store = WorkspaceStore(tmp_path)
    store.create_project(_project())
    store.append_approval(_approval())
    with pytest.raises(StorageConflict):
        store.append_approval(_approval())


def test_missing_records_raise_not_found(tmp_path):
    store = WorkspaceStore(tmp_path)
    with pytest.raises(StorageNotFound):
        store.get_project("missing")
    with pytest.raises(StorageNotFound):
        store.update_thread(_thread())


@pytest.mark.parametrize("bad_id", ["../escape", "a/b", "a\\b", "", "."])
def test_identifiers_cannot_escape_workspace_root(tmp_path, bad_id):
    store = WorkspaceStore(tmp_path)
    with pytest.raises(ValueError):
        store.get_project(bad_id)


def test_corrupt_snapshot_is_detected_without_rewrite(tmp_path):
    store = WorkspaceStore(tmp_path)
    store.create_project(_project())
    path = tmp_path / "projects" / "project-001" / "project.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(StorageCorruption):
        store.get_project("project-001")
    assert path.read_text(encoding="utf-8") == "{broken"


def test_corrupt_jsonl_is_detected(tmp_path):
    store = WorkspaceStore(tmp_path)
    store.create_project(_project())
    path = tmp_path / "projects" / "project-001" / "approvals.jsonl"
    path.write_text('{"ok": true}\n{broken\n', encoding="utf-8")

    with pytest.raises(StorageCorruption):
        store.list_approvals("project-001")


def test_atomic_write_leaves_no_temp_files(tmp_path):
    store = WorkspaceStore(tmp_path)
    store.create_project(_project())
    store.create_thread(_thread())
    store.append_approval(_approval())

    assert not list(tmp_path.rglob("*.tmp"))


def test_unicode_round_trip_and_project_isolation(tmp_path):
    store = WorkspaceStore(tmp_path)
    first = _project("project-a")
    second = _project("project-b").model_copy(update={"title": "第二首歌"})
    store.create_project(first)
    store.create_project(second)

    assert store.get_project("project-a").title == "验收歌曲"
    assert store.get_project("project-b").title == "第二首歌"
