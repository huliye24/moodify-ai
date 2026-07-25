"""Failure and recovery tests for Moodify Workspace v2.

Step 31: Covers audio missing, DSP failure, MRS degradation, Judge reject,
and service restart scenarios.
"""

from __future__ import annotations

import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest


@pytest.fixture
def workspace_root():
    root = tempfile.mkdtemp(prefix="ws_fr_")
    yield Path(root)
    shutil.rmtree(root, ignore_errors=True)


@pytest.fixture
def store(workspace_root):
    from moodify.storage import WorkspaceStore
    return WorkspaceStore(workspace_root)


def _utc_now():
    return datetime.now(timezone.utc)


def _setup_project(store, pid="FR_001"):
    from moodify.domain import (
        AudioProject, ProjectWorkflow, WorkflowStage,
    )
    now = _utc_now()
    project = AudioProject(
        project_id=pid,
        title="Failure Recovery Test",
        source_audio_ids=["test_source"],
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
    for _ in range(4):
        workflow = store.get_workflow(pid)
        advanced = workflow.advance(at=_utc_now(), reason="advancing test project")
        store.update_workflow(advanced)
    return project


class TestAudioMissing:
    def test_resolve_missing_source_raises_not_found(self, store):
        pid = "FR_MISSING_SOURCE"
        from moodify.domain import AudioProject
        store.create_project(AudioProject(
            project_id=pid, title="Missing Source",
            source_audio_ids=["nonexistent"],
            created_at=_utc_now(), updated_at=_utc_now(),
        ))
        from moodify.storage import StorageNotFound
        with pytest.raises(StorageNotFound):
            store.resolve_source_audio(pid, "nonexistent")


class TestDspFailure:
    def test_dsp_worker_failure_transitions_to_failed(self, store):
        _setup_project(store, "FR_DSP_FAIL")

        from moodify.domain import (
            ProjectThread, ThreadRole, ThreadStatus, ThreadType, WorkflowStage,
        )
        workflow = store.get_workflow("FR_DSP_FAIL")

        # Simulate a DSP worker that fails
        worker = ProjectThread(
            thread_id="FR_DSP_FAIL_w1",
            project_id="FR_DSP_FAIL",
            thread_type=ThreadType.EXPORT,
            role=ThreadRole.WORKER,
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        store.create_thread(worker)
        running = worker.transition_to(ThreadStatus.QUEUED).transition_to(ThreadStatus.RUNNING)
        store.update_thread(running)

        failed = running.transition_to(ThreadStatus.FAILED, error="DSP process crashed")
        store.update_thread(failed)

        failed_wf = workflow.fail("DSP Worker failed: DSP process crashed")
        store.update_workflow(failed_wf)

        retrieved = store.get_thread("FR_DSP_FAIL", "FR_DSP_FAIL_w1")
        assert retrieved.status is ThreadStatus.FAILED
        assert retrieved.error == "DSP process crashed"

        final_wf = store.get_workflow("FR_DSP_FAIL")
        assert final_wf.stage is WorkflowStage.FAILED

    def test_dsp_worker_retry_after_failure(self, store):
        _setup_project(store, "FR_DSP_RETRY")

        from moodify.domain import (
            ProjectThread, ThreadRole, ThreadStatus, ThreadType,
        )
        worker = ProjectThread(
            thread_id="FR_DSP_RETRY_w1",
            project_id="FR_DSP_RETRY",
            thread_type=ThreadType.EXPORT,
            role=ThreadRole.WORKER,
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        store.create_thread(worker)
        failed = (
            worker.transition_to(ThreadStatus.QUEUED)
            .transition_to(ThreadStatus.RUNNING)
            .transition_to(ThreadStatus.FAILED, error="DSP crash")
        )
        store.update_thread(failed)

        retrieved = store.get_thread("FR_DSP_RETRY", "FR_DSP_RETRY_w1")
        assert retrieved.retry_count == 0
        assert retrieved.max_retries == 2

        retried = retrieved.queue_retry()
        assert retried.status is ThreadStatus.QUEUED
        assert retried.retry_count == 1


class TestMrsDegradation:
    def test_judge_degrades_gracefully_when_mrs_unavailable(self, store):
        """Judge should produce a verdict even without MRS engine."""
        from moodify.services.judge import _run_quality_checks
        import os
        temp_dir = tempfile.mkdtemp()
        try:
            import soundfile as sf
            import numpy as np
            orig = os.path.join(temp_dir, "orig.wav")
            proc = os.path.join(temp_dir, "proc.wav")
            data = np.zeros((44100, 2), dtype=np.float32)
            sf.write(orig, data, 44100)
            sf.write(proc, data, 44100)

            result = _run_quality_checks(orig, proc)
            assert result["verdict"] in ("pass", "reject", "reprocess")
            assert "checks" in result
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestJudgeReject:
    def test_judge_rejection_marks_thread_rejected(self, store):
        _setup_project(store, "FR_JUDGE_REJECT")

        from moodify.domain import (
            ProjectThread, ThreadRole, ThreadStatus, ThreadType, WorkflowStage,
        )
        workflow = store.get_workflow("FR_JUDGE_REJECT")

        judge = ProjectThread(
            thread_id="FR_JUDGE_REJECT_j1",
            project_id="FR_JUDGE_REJECT",
            thread_type=ThreadType.JUDGE,
            role=ThreadRole.JUDGE,
            inputs={"version_id": "v001"},
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        store.create_thread(judge)
        running = judge.transition_to(ThreadStatus.QUEUED).transition_to(ThreadStatus.RUNNING)
        store.update_thread(running)

        rejected = running.transition_to(
            ThreadStatus.REJECTED,
            outputs={"verdict": "reject", "reason": "MRS below threshold"},
        )
        store.update_thread(rejected)

        failed_wf = workflow.fail("Judge rejected: FR_JUDGE_REJECT_j1")
        store.update_workflow(failed_wf)

        retrieved = store.get_thread("FR_JUDGE_REJECT", "FR_JUDGE_REJECT_j1")
        assert retrieved.status is ThreadStatus.REJECTED

        final_wf = store.get_workflow("FR_JUDGE_REJECT")
        assert final_wf.stage is WorkflowStage.FAILED

    def test_retry_orchestrator_handles_rejection(self, store):
        _setup_project(store, "FR_RETRY_ORCH")

        from moodify.domain import (
            ProjectThread, ThreadRole, ThreadStatus, ThreadType,
        )
        # Create worker thread
        worker = ProjectThread(
            thread_id="FR_RETRY_ORCH_w1",
            project_id="FR_RETRY_ORCH",
            thread_type=ThreadType.EXPORT,
            role=ThreadRole.WORKER,
            inputs={"version_id": "v001"},
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        store.create_thread(worker)
        worker = (
            worker.transition_to(ThreadStatus.QUEUED)
            .transition_to(ThreadStatus.RUNNING)
            .transition_to(ThreadStatus.PASSED, outputs={"version_id": "v001"})
        )
        store.update_thread(worker)

        # Create rejected judge thread
        judge = ProjectThread(
            thread_id="FR_RETRY_ORCH_j1",
            project_id="FR_RETRY_ORCH",
            thread_type=ThreadType.JUDGE,
            role=ThreadRole.JUDGE,
            inputs={"version_id": "v001"},
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        store.create_thread(judge)
        judge = (
            judge.transition_to(ThreadStatus.QUEUED)
            .transition_to(ThreadStatus.RUNNING)
            .transition_to(
                ThreadStatus.REJECTED,
                outputs={"verdict": "reprocess", "version_id": "v001"},
            )
        )
        store.update_thread(judge)

        from moodify.services.retry import RetryOrchestrator
        orch = RetryOrchestrator(store)
        result = orch.handle_judge_rejection("FR_RETRY_ORCH", "FR_RETRY_ORCH_j1")

        assert result["action"] == "retry_queued"
        assert result["retry_count"] == 1

        retried = store.get_thread("FR_RETRY_ORCH", "FR_RETRY_ORCH_w1")
        assert retried.status is ThreadStatus.QUEUED


class TestServiceRestart:
    def test_workflow_state_persists_and_is_recoverable(self, store):
        pid = "FR_RESTART"
        _setup_project(store, pid)

        from moodify.domain import WorkflowStage
        workflow = store.get_workflow(pid)
        assert workflow.stage is WorkflowStage.PROCESS

        # Simulate restart: re-read from store
        del workflow
        re_read = store.get_workflow(pid)
        assert re_read.stage is WorkflowStage.PROCESS
        assert re_read.project_id == pid

        # Can continue from where we left off
        advanced = re_read.advance(at=_utc_now(), reason="recovered after restart")
        store.update_workflow(advanced)
        assert store.get_workflow(pid).stage is WorkflowStage.JUDGE

    def test_no_orphan_final_without_approval(self, store):
        """A version should never reach DELIVERED without APPROVED status."""
        pid = "FR_NO_ORPHAN"
        from moodify.domain import (
            AudioProject, AudioVersion, VersionStatus,
        )
        now = _utc_now()
        project = AudioProject(
            project_id=pid, title="No Orphan Final",
            source_audio_ids=["src"],
            created_at=now, updated_at=now,
        )
        store.create_project(project)

        version = AudioVersion(
            version_id=f"{pid}_v001",
            project_id=pid,
            name="Test",
            purpose="Test",
            audio_path="versions/v001.wav",
            audio_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            created_by="test",
            created_at=now,
            updated_at=now,
        )

        # Cannot go directly from DRAFT to DELIVERED
        with pytest.raises(ValueError):
            version.transition_to(VersionStatus.DELIVERED)

        # Cannot go from DRAFT to APPROVED without approval evidence
        with pytest.raises(ValueError):
            version.transition_to(VersionStatus.APPROVED)
