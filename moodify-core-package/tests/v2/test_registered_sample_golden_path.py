"""Golden-path acceptance using the registered two-stem song assets."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from moodify.domain import (
    ApprovalActorType,
    ApprovalDecision,
    ApprovalOutcome,
    AudioProject,
    AudioVersion,
    CreativeBrief,
    ProjectStatus,
    ProjectThread,
    ProjectWorkflow,
    ThreadRole,
    ThreadStatus,
    ThreadType,
    VersionStatus,
    WorkflowStage,
)
from moodify.services.archive import ArchiveService
from moodify.storage import WorkspaceStore

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = (
    REPO_ROOT
    / "data"
    / "workspace_v2"
    / "acceptance_samples"
    / "WSA_20260724_001.json"
)


def _now():
    return datetime.now(timezone.utc)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _passed_thread(
    store: WorkspaceStore,
    project_id: str,
    thread_id: str,
    thread_type: ThreadType,
    role: ThreadRole,
    outputs: dict,
) -> None:
    thread = ProjectThread(
        thread_id=thread_id,
        project_id=project_id,
        thread_type=thread_type,
        role=role,
        created_at=_now(),
        updated_at=_now(),
    )
    store.create_thread(thread)
    passed = (
        thread.transition_to(ThreadStatus.QUEUED)
        .transition_to(ThreadStatus.RUNNING)
        .transition_to(ThreadStatus.PASSED, outputs=outputs)
    )
    store.update_thread(passed)


def test_registered_two_stem_song_reaches_verified_final_archive(tmp_path):
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    project_id = manifest["sample_id"]
    store = WorkspaceStore(tmp_path)
    project_dir = tmp_path / "projects" / project_id
    source_dir = project_dir / "sources"
    source_dir.mkdir(parents=True)

    source_ids = []
    for stem in manifest["source"]["stems"]:
        source = REPO_ROOT / stem["path"]
        assert source.is_file()
        assert _sha256(source).upper() == stem["sha256"]
        source_id = stem["role"]
        source_ids.append(source_id)
        shutil.copyfile(source, source_dir / f"{source_id}.wav")

    now = _now()
    brief = CreativeBrief.model_validate(manifest["creative_brief_seed"])
    project = AudioProject(
        project_id=project_id,
        title=manifest["title"],
        source_audio_ids=source_ids,
        creative_brief=brief,
        privacy_policy={"sample_id": project_id, "local_only": True},
        created_at=now,
        updated_at=now,
    )
    store.create_project(project)
    workflow = ProjectWorkflow(
        project_id=project_id,
        stage=WorkflowStage.INTAKE,
        created_at=now,
        updated_at=now,
    )
    store.create_workflow(workflow)

    stages = [
        (ThreadType.BRIEF, ThreadRole.PRODUCER, {"brief_saved": True}),
        (ThreadType.DIAGNOSIS, ThreadRole.ANALYST, {"diagnosis": "persisted"}),
        (ThreadType.DESIGN, ThreadRole.DESIGNER, {"variants": 2}),
        (ThreadType.EXPORT, ThreadRole.WORKER, {"processed": True}),
    ]
    for index, (thread_type, role, outputs) in enumerate(stages, start=1):
        workflow = workflow.advance(at=_now(), reason=f"acceptance stage {index}")
        store.update_workflow(workflow)
        _passed_thread(
            store, project_id, f"{project_id}_{index}", thread_type, role, outputs
        )

    baseline_paths = [
        REPO_ROOT / manifest["baseline"]["delivery"]["path"],
        REPO_ROOT / manifest["baseline"]["instrumental"]["report_path"],
    ]
    candidate_audio = baseline_paths[0]
    assert candidate_audio.is_file()
    version_dir = project_dir / "versions"
    version_dir.mkdir()
    parent_id = None
    versions = []
    for index in (1, 2):
        target = version_dir / f"candidate-{index}.wav"
        shutil.copyfile(candidate_audio, target)
        version = AudioVersion(
            version_id=f"{project_id}_v{index}",
            project_id=project_id,
            parent_version_id=parent_id,
            branch="main" if index == 1 else "candidate-b",
            name=f"Registered sample candidate {index}",
            purpose="Workspace v2 golden-path acceptance",
            audio_path=f"versions/{target.name}",
            audio_sha256=_sha256(target),
            created_by=f"{project_id}_4",
            created_at=_now(),
            updated_at=_now(),
        )
        store.create_version_checked(version)
        versions.append(version)
        parent_id = version.version_id

    workflow = workflow.advance(at=_now(), reason="two candidates created")
    store.update_workflow(workflow)
    _passed_thread(
        store,
        project_id,
        f"{project_id}_judge",
        ThreadType.JUDGE,
        ThreadRole.JUDGE,
        {
            "version_id": versions[-1].version_id,
            "verdict": "pass",
            "mrs_version": "mrs_proxy_v01",
            "degraded_scoring_disclosed": True,
        },
    )

    workflow = workflow.advance(at=_now(), reason="judge passed")
    store.update_workflow(workflow)
    decision = ApprovalDecision(
        decision_id=f"{project_id}_approval",
        project_id=project_id,
        version_id=versions[-1].version_id,
        outcome=ApprovalOutcome.APPROVED,
        reason="Registered sample automated gates passed; human acceptance recorded",
        operator="Workspace v2 acceptance fixture",
        actor_type=ApprovalActorType.HUMAN,
        decided_at=_now(),
    )
    store.append_approval(decision)
    approved = versions[-1].transition_to(VersionStatus.REVIEWING).transition_to(
        VersionStatus.APPROVED, approval=decision
    )
    store.update_version(approved)
    project_payload = store.get_project(project_id).model_dump()
    project_payload.update(
        {
            "active_version_id": approved.version_id,
            "approved_version_id": approved.version_id,
            "status": ProjectStatus.APPROVED.value,
            "updated_at": _now(),
        }
    )
    store.update_project(AudioProject.model_validate(project_payload))

    workflow = workflow.advance(at=_now(), reason="human approval recorded")
    store.update_workflow(workflow)
    assert workflow.stage is WorkflowStage.FINAL
    outputs = ArchiveService(store).archive_project(
        project_id, f"{project_id}_archive"
    )
    verification = ArchiveService(store).verify_archive(project_id)

    assert outputs["final_approval_exists"] is True
    assert outputs["version_count"] == 2
    assert verification["verified"] is True
    assert store.get_project(project_id).status is ProjectStatus.ARCHIVED
