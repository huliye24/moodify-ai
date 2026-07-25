"""End-to-end golden path test for Moodify Workspace v2.

Runs the full workflow: create project -> brief -> diagnosis -> design ->
process -> judge -> approval -> archive.

Requires: MOODIFY_WORKSPACE_ROOT env var pointing to a test workspace.
Run: pytest tests/v2/test_e2e_golden_path.py -v -s
"""

from __future__ import annotations

import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest


@pytest.fixture
def workspace_root():
    root = tempfile.mkdtemp(prefix="ws_e2e_")
    yield Path(root)
    shutil.rmtree(root, ignore_errors=True)


@pytest.fixture
def store(workspace_root):
    from moodify.storage import WorkspaceStore
    return WorkspaceStore(workspace_root)


def _utc_now():
    return datetime.now(timezone.utc)


class TestGoldenPath:
    """Step 30: End-to-end acceptance test — create project to Final."""

    def test_full_golden_path(self, store, workspace_root):
        from moodify.domain import (
            AudioProject, AudioVersion, CreativeBrief,
            ProjectThread, ProjectWorkflow, ProjectStatus,
            ThreadRole, ThreadStatus, ThreadType, VersionStatus,
            WorkflowStage, TreatmentAction, TreatmentPlan, TreatmentStepType, TreatmentVariant,
            ApprovalActorType, ApprovalDecision, ApprovalOutcome,
        )

        pid = "GP_20260725_001"
        source_audio_id = "acceptance_sample"

        # --- INTAKE: Create project ---
        now = _utc_now()
        project = AudioProject(
            project_id=pid,
            title="Golden Path E2E Test",
            source_audio_ids=[source_audio_id],
            created_at=now,
            updated_at=now,
        )
        store.create_project(project)

        workflow = ProjectWorkflow(
            project_id=pid,
            stage=WorkflowStage.INTAKE,
            created_at=now,
            updated_at=now,
        )
        store.create_workflow(workflow)

        # --- BRIEF: Create creative brief ---
        brief = CreativeBrief(
            goal="Warm, dynamic master for streaming",
            preserve=["vocal presence", "transient detail"],
            avoid=["harshness above 8kHz", "over-compression"],
            platform="streaming",
            reference=["ref_warm_master"],
        )
        project_data = project.model_dump()
        project_data["creative_brief"] = brief.model_dump()
        project_data["updated_at"] = _utc_now()
        updated = AudioProject.model_validate(project_data)
        store.update_project(updated)

        workflow = workflow.advance(at=_utc_now(), reason="brief created")
        store.update_workflow(workflow)
        assert workflow.stage is WorkflowStage.BRIEF

        # --- DIAGNOSIS: Create diagnosis thread ---
        workflow = workflow.advance(at=_utc_now(), reason="starting diagnosis")
        store.update_workflow(workflow)
        assert workflow.stage is WorkflowStage.DIAGNOSIS

        diag_thread = ProjectThread(
            thread_id=f"{pid}_diag_001",
            project_id=pid,
            thread_type=ThreadType.DIAGNOSIS,
            role=ThreadRole.ANALYST,
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        store.create_thread(diag_thread)
        diag_thread = (
            diag_thread.transition_to(ThreadStatus.QUEUED)
            .transition_to(ThreadStatus.RUNNING)
            .transition_to(ThreadStatus.PASSED, outputs={"diagnosis_summary": "ok"})
        )
        store.update_thread(diag_thread)

        # --- DESIGN: Create treatment plan ---
        workflow = workflow.advance(at=_utc_now(), reason="diagnosis complete")
        store.update_workflow(workflow)

        plan = TreatmentPlan(
            plan_id=f"{pid}_plan_001",
            project_id=pid,
            brief_revision=1,
            diagnosis_id=diag_thread.thread_id,
            created_by_thread_id=diag_thread.thread_id,
            variants=[
                TreatmentVariant(
                    variant_id="vA",
                    label="A",
                    name="Natural Preservation",
                    objective="Keep source character",
                    problems=["Dynamic range could be wider"],
                    risks=["May reduce perceived loudness"],
                    expected_output="Mastered WAV with preserved dynamics",
                    actions=[
                        TreatmentAction(
                            action_id="act_001",
                            order=1,
                            step_type=TreatmentStepType.DYNAMIC_SHAPING,
                            public_summary="Gentle dynamic shaping",
                            reason="Preserve natural dynamics",
                        ),
                        TreatmentAction(
                            action_id="act_002",
                            order=2,
                            step_type=TreatmentStepType.LOUDNESS_NORMALIZATION,
                            public_summary="LUFS normalization",
                            reason="Meet streaming platform standard",
                        ),
                    ],
                ),
            ],
        )
        store.create_plan(plan)

        # --- PROCESS: Simulate DSP processing ---
        workflow = workflow.advance(at=_utc_now(), reason="plan designed")
        store.update_workflow(workflow)
        assert workflow.stage is WorkflowStage.PROCESS

        # Create a dummy audio file for version staging
        versions_dir = workspace_root / "projects" / pid / "versions"
        versions_dir.mkdir(parents=True, exist_ok=True)
        dummy_wav = versions_dir / "v001.wav"
        dummy_wav.write_bytes(b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")

        version = AudioVersion(
            version_id=f"{pid}_v001",
            project_id=pid,
            name="Golden Path v1 · Natural Preservation",
            purpose="First processing pass",
            audio_path="versions/v001.wav",
            audio_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            treatment_plan_id=plan.plan_id,
            treatment_variant_id="vA",
            treatment_record_id=diag_thread.thread_id,
            created_by="e2e_test",
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        store.create_version(version)

        project_data = project.model_dump()
        project_data["active_version_id"] = version.version_id
        project_data["updated_at"] = _utc_now()
        store.update_project(AudioProject.model_validate(project_data))

        # --- JUDGE: Create judge thread ---
        workflow = workflow.advance(at=_utc_now(), reason="processing complete")
        store.update_workflow(workflow)
        assert workflow.stage is WorkflowStage.JUDGE

        judge_thread = ProjectThread(
            thread_id=f"{pid}_judge_001",
            project_id=pid,
            thread_type=ThreadType.JUDGE,
            role=ThreadRole.JUDGE,
            inputs={"version_id": version.version_id},
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        store.create_thread(judge_thread)
        judge_thread = (
            judge_thread.transition_to(ThreadStatus.QUEUED)
            .transition_to(ThreadStatus.RUNNING)
            .transition_to(
                ThreadStatus.PASSED,
                outputs={
                    "version_id": version.version_id,
                    "verdict": "pass",
                    "mrs_score": 82.5,
                    "mrs_version": "mrs_proxy_v01",
                    "checks": {"structural": {"passed": True}},
                },
            )
        )
        store.update_thread(judge_thread)

        # --- APPROVAL: Create approval decision ---
        workflow = workflow.advance(at=_utc_now(), reason="judge passed")
        store.update_workflow(workflow)
        assert workflow.stage is WorkflowStage.APPROVAL

        decision = ApprovalDecision(
            decision_id=f"{pid}_dec_001",
            project_id=pid,
            version_id=version.version_id,
            outcome=ApprovalOutcome.APPROVED,
            reason="All quality gates passed, ready for delivery",
            operator="Test Engineer",
            actor_type=ApprovalActorType.HUMAN,
            decided_at=_utc_now(),
        )
        store.append_approval(decision)

        reviewing = version.transition_to(VersionStatus.REVIEWING)
        approved = reviewing.transition_to(VersionStatus.APPROVED, approval=decision)
        store.update_version(approved)

        project_data = project.model_dump()
        project_data["approved_version_id"] = version.version_id
        project_data["status"] = ProjectStatus.APPROVED.value
        project_data["updated_at"] = _utc_now()
        store.update_project(AudioProject.model_validate(project_data))

        # --- ARCHIVE: Create archive thread ---
        workflow = workflow.advance(at=_utc_now(), reason="approved")
        store.update_workflow(workflow)
        assert workflow.stage is WorkflowStage.FINAL

        archive_thread = ProjectThread(
            thread_id=f"{pid}_archive_001",
            project_id=pid,
            thread_type=ThreadType.ARCHIVE,
            role=ThreadRole.ARCHIVE,
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        store.create_thread(archive_thread)
        archive_thread = (
            archive_thread.transition_to(ThreadStatus.QUEUED)
            .transition_to(ThreadStatus.RUNNING)
            .transition_to(
                ThreadStatus.PASSED,
                outputs={
                    "manifest_path": "archive/archive_manifest.json",
                    "version_count": 1,
                    "final_approval_exists": True,
                },
            )
        )
        store.update_thread(archive_thread)

        project = store.get_project(pid)
        project_data = project.model_dump()
        project_data["status"] = ProjectStatus.ARCHIVED.value
        project_data["updated_at"] = _utc_now()
        store.update_project(AudioProject.model_validate(project_data))

        # --- VERIFY: Golden path assertions ---
        final_project = store.get_project(pid)
        assert final_project.status is ProjectStatus.ARCHIVED
        assert final_project.approved_version_id == version.version_id

        final_workflow = store.get_workflow(pid)
        assert final_workflow.stage is WorkflowStage.FINAL
        assert len(final_workflow.history) >= 6

        all_threads = store.list_threads(pid)
        thread_statuses = {t.thread_type: t.status for t in all_threads}
        assert thread_statuses.get(ThreadType.JUDGE) is ThreadStatus.PASSED
        assert thread_statuses.get(ThreadType.ARCHIVE) is ThreadStatus.PASSED

        all_approvals = store.list_approvals(pid)
        assert len(all_approvals) == 1
        assert all_approvals[0].outcome is ApprovalOutcome.APPROVED

        all_versions = store.list_versions(pid)
        assert len(all_versions) == 1
        assert all_versions[0].status is VersionStatus.APPROVED
