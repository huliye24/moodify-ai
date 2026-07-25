"""Analyst service that adapts the v0.1 scanner and diagnosis pipeline."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from moodify.domain import (
    ProjectThread,
    ThreadRole,
    ThreadStatus,
    ThreadType,
    WorkflowStage,
)
from moodify.storage import WorkspaceStore
from moodify.v01_analyzer import analyze, spectrum_png_path
from moodify.v01_diagnostics import diagnose
from moodify.v01_pipeline import scan_audio


DiagnosisRunner = Callable[[Path, Path], dict[str, Any]]
Clock = Callable[[], datetime]


def _run_v01_diagnosis(source_path: Path, output_dir: Path) -> dict[str, Any]:
    scan = scan_audio(str(source_path))
    if not scan.exists:
        raise FileNotFoundError(str(source_path))
    if not scan.readable:
        raise ValueError("source audio is not readable")
    metrics = analyze(
        str(source_path),
        str(output_dir),
        label="diagnosis",
    )
    report = diagnose(metrics)
    spectrum = Path(
        spectrum_png_path(
            str(source_path),
            str(output_dir),
            label="diagnosis",
        )
    )
    return {
        "scan": scan.to_dict(),
        "metrics": metrics.to_dict(),
        "diagnosis": report.to_dict(),
        "spectrum_path": spectrum.name if spectrum.exists() else None,
    }


class AnalystService:
    def __init__(
        self,
        store: WorkspaceStore,
        *,
        runner: DiagnosisRunner = _run_v01_diagnosis,
        clock: Clock | None = None,
    ) -> None:
        self.store = store
        self.runner = runner
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def run_diagnosis(
        self,
        project_id: str,
        thread_id: str,
        *,
        source_audio_id: str | None = None,
    ) -> ProjectThread:
        project = self.store.get_project(project_id)
        workflow = self.store.get_workflow(project_id)
        if workflow.stage is not WorkflowStage.DIAGNOSIS:
            raise ValueError("Analyst can run only during DIAGNOSIS")
        selected_source = source_audio_id or project.source_audio_ids[0]
        started_at = self.clock()
        thread = ProjectThread(
            thread_id=thread_id,
            project_id=project_id,
            thread_type=ThreadType.DIAGNOSIS,
            role=ThreadRole.ANALYST,
            inputs={"source_audio_id": selected_source},
            created_at=started_at,
            updated_at=started_at,
        )
        self.store.create_thread(thread)
        running = thread.transition_to(
            ThreadStatus.QUEUED, at=started_at
        ).transition_to(ThreadStatus.RUNNING, at=started_at)
        self.store.update_thread(running)
        try:
            source_path = self.store.resolve_source_audio(
                project_id, selected_source
            )
            output_dir = self.store.diagnostic_output_dir(
                project_id, thread_id
            )
            result = self.runner(source_path, output_dir)
            finished_at = self.clock()
            outputs = {
                **result,
                "source_audio_id": selected_source,
                "analyzed_at": finished_at.isoformat(),
            }
            passed = running.transition_to(
                ThreadStatus.PASSED,
                at=finished_at,
                outputs=outputs,
            )
            advanced = workflow.advance(
                at=finished_at,
                reason=f"diagnosis thread passed: {thread_id}",
            )
            self.store.update_thread(passed)
            self.store.update_workflow(advanced)
            return passed
        except Exception as exc:
            failed_at = self.clock()
            message = str(exc) or exc.__class__.__name__
            failed = running.transition_to(
                ThreadStatus.FAILED,
                at=failed_at,
                error=message,
            )
            failed_workflow = workflow.fail(
                f"Analyst failed: {message}",
                at=failed_at,
            )
            self.store.update_thread(failed)
            self.store.update_workflow(failed_workflow)
            return failed
