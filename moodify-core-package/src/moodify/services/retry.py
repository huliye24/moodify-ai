"""Auto-retry orchestration for workspace v2 workflows.

When Judge rejects a version, this service routes the workflow back to the
DSP Worker stage with retry limit enforcement.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from moodify.domain import (
    ProjectThread,
    ThreadStatus,
    ThreadType,
    WorkflowAction,
    WorkflowEvent,
    WorkflowStage,
)
from moodify.storage import WorkspaceStore

Clock = Callable[[], datetime]


class RetryOrchestrator:
    """Routes rejected versions back to PROCESS for DSP Worker retry.

    Enforcement rules:
    - Default max 2 retries per thread (configured on ProjectThread)
    - Tracks retry count in thread.retry_count
    - Creates a new DSP Worker thread on each retry
    - Fails permanently when retry limit is reached
    """

    def __init__(
        self,
        store: WorkspaceStore,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.store = store
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def handle_judge_rejection(
        self,
        project_id: str,
        judge_thread_id: str,
        *,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Handle a Judge rejection with retry routing.

        Returns a dict with the action taken and next thread info.
        """
        self.store.get_project(project_id)
        workflow = self.store.get_workflow(project_id)

        judge_thread = self.store.get_thread(project_id, judge_thread_id)
        if judge_thread.thread_type is not ThreadType.JUDGE:
            raise ValueError("only JUDGE threads can trigger rejection retry")
        if judge_thread.status is not ThreadStatus.REJECTED:
            raise ValueError("only REJECTED threads can be retried")

        version_id = judge_thread.inputs.get("version_id")
        if version_id is None:
            raise ValueError("JUDGE thread missing version_id in inputs")

        worker_threads = [
            t for t in self.store.list_threads(project_id)
            if t.thread_type in {
                ThreadType.EXPORT,
                ThreadType.VOCAL,
                ThreadType.SPECTRUM,
                ThreadType.DYNAMICS,
                ThreadType.SPACE,
                ThreadType.LOUDNESS,
            }
            and t.inputs.get("version_id") == version_id
        ]

        if not worker_threads:
            return {
                "action": "no_worker_found",
                "detail": f"no DSP Worker thread found for version {version_id}",
            }

        latest_worker = max(worker_threads, key=lambda t: t.created_at)

        if latest_worker.retry_count >= latest_worker.max_retries:
            now = self.clock()
            failed_workflow = workflow.fail(
                f"retry limit reached for version {version_id}: "
                f"{latest_worker.retry_count}/{latest_worker.max_retries}",
                at=now,
            )
            self.store.update_workflow(failed_workflow)
            return {
                "action": "retry_limit_reached",
                "retry_count": latest_worker.retry_count,
                "max_retries": latest_worker.max_retries,
                "detail": "workflow failed permanently",
            }

        now = self.clock()
        new_retry_count = latest_worker.retry_count + 1

        if latest_worker.status in {ThreadStatus.REJECTED, ThreadStatus.FAILED}:
            retried_worker = latest_worker.queue_retry(at=now)
        else:
            data = latest_worker.model_dump()
            data.update({
                "status": ThreadStatus.QUEUED.value,
                "error": None,
                "retry_count": new_retry_count,
                "updated_at": now,
                "started_at": None,
                "finished_at": None,
            })
            retried_worker = ProjectThread.model_validate(data)

        self.store.update_thread(retried_worker)

        rollback_event = WorkflowEvent(
            action=WorkflowAction.PAUSE,
            from_stage=workflow.stage,
            to_stage=WorkflowStage.PAUSED,
            at=now,
            reason=f"Judge rejection, retry #{retried_worker.retry_count}: {reason or 'quality gate not met'}",
        )
        resume_event = WorkflowEvent(
            action=WorkflowAction.RESUME,
            from_stage=WorkflowStage.PAUSED,
            to_stage=WorkflowStage.PROCESS,
            at=now,
            reason=f"retry #{retried_worker.retry_count}: routing back to PROCESS",
        )

        workflow_data = workflow.model_dump()
        workflow_data.update({
            "stage": WorkflowStage.PROCESS,
            "paused_from": None,
            "failure_reason": None,
            "updated_at": now,
            "history": (*workflow.history, rollback_event, resume_event),
        })

        from moodify.domain.workflow import ProjectWorkflow
        rolled_back = ProjectWorkflow.model_validate(workflow_data)
        self.store.update_workflow(rolled_back)

        return {
            "action": "retry_queued",
            "retry_count": retried_worker.retry_count,
            "max_retries": retried_worker.max_retries,
            "worker_thread_id": latest_worker.thread_id,
            "version_id": version_id,
            "detail": f"workflow rolled back to PROCESS for retry #{retried_worker.retry_count}",
        }

    def handle_workflow_failure(
        self,
        project_id: str,
        *,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Check if a failed workflow can be recovered via retry.

        Scans recent threads for retry-eligible failures and attempts recovery.
        """
        workflow = self.store.get_workflow(project_id)
        if workflow.stage is not WorkflowStage.FAILED:
            return {"action": "not_failed", "stage": workflow.stage.value}

        threads = self.store.list_threads(project_id)
        rejected_judges = [
            t for t in threads
            if t.thread_type is ThreadType.JUDGE
            and t.status is ThreadStatus.REJECTED
        ]

        if rejected_judges:
            latest_judge = max(rejected_judges, key=lambda t: t.finished_at or t.created_at)
            return self.handle_judge_rejection(
                project_id, latest_judge.thread_id, reason=reason
            )

        return {
            "action": "unrecoverable",
            "detail": "no retry-eligible threads found",
            "failure_reason": workflow.failure_reason,
        }
