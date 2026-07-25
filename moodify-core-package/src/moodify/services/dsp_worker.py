"""DSP Worker adapter for the existing v0.1 processing chain."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from moodify.domain import (
    AudioProject,
    AudioVersion,
    ProjectThread,
    ThreadRole,
    ThreadStatus,
    ThreadType,
    TreatmentStepType,
    WorkflowStage,
)
from moodify.storage import WorkspaceStore
from moodify.v01_pipeline import process_audio


Clock = Callable[[], datetime]
ProcessRunner = Callable[[Path, str, Path], dict[str, Any]]


def _run_v01_process(
    source_path: Path, preset: str, output_dir: Path
) -> dict[str, Any]:
    result = process_audio(
        str(source_path),
        preset=preset,
        output_dir=str(output_dir),
    )
    if not result.success:
        raise RuntimeError(result.error or "v0.1 processing failed")
    return {
        "output_audio": result.output_path,
        "report_file": Path(result.report_path).name if result.report_path else None,
        "quality_gate": result.quality_gate.to_dict(),
        "stage_timings": dict(result.stage_timings),
        "applied_preset": result.preset,
    }


class DspWorkerService:
    def __init__(
        self,
        store: WorkspaceStore,
        *,
        runner: ProcessRunner = _run_v01_process,
        clock: Clock | None = None,
    ) -> None:
        self.store = store
        self.runner = runner
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def process_variant(
        self,
        project_id: str,
        thread_id: str,
        plan_id: str,
        variant_id: str,
        version_id: str,
        *,
        source_audio_id: str | None = None,
        branch: str = "main",
    ) -> ProjectThread:
        project = self.store.get_project(project_id)
        workflow = self.store.get_workflow(project_id)
        if workflow.stage is not WorkflowStage.PROCESS:
            raise ValueError("DSP Worker can run only during PROCESS")
        started_at = self.clock()
        thread = ProjectThread(
            thread_id=thread_id,
            project_id=project_id,
            thread_type=ThreadType.EXPORT,
            role=ThreadRole.WORKER,
            inputs={
                "plan_id": plan_id,
                "variant_id": variant_id,
                "version_id": version_id,
                "source_audio_id": source_audio_id
                or project.source_audio_ids[0],
            },
            created_at=started_at,
            updated_at=started_at,
        )
        self.store.create_thread(thread)
        running = thread.transition_to(
            ThreadStatus.QUEUED, at=started_at
        ).transition_to(ThreadStatus.RUNNING, at=started_at)
        self.store.update_thread(running)
        try:
            plan = self.store.get_plan(project_id, plan_id)
            variant = next(
                (item for item in plan.variants if item.variant_id == variant_id),
                None,
            )
            if variant is None:
                raise ValueError("variant does not belong to TreatmentPlan")
            preset = self._preset_for_variant(variant)
            selected_source = (
                source_audio_id or project.source_audio_ids[0]
            )
            source_path = self.store.resolve_source_audio(
                project_id, selected_source
            )
            output_dir = self.store.processing_output_dir(
                project_id, thread_id
            )
            process_result = self.runner(source_path, preset, output_dir)
            output_audio = Path(str(process_result.get("output_audio", "")))
            relative_audio, audio_sha256 = self.store.stage_version_audio(
                project_id, version_id, output_audio
            )
            created_at = self.clock()
            if project.active_version_id is not None:
                self.store.get_version(project_id, project.active_version_id)
            version = AudioVersion(
                version_id=version_id,
                project_id=project_id,
                parent_version_id=project.active_version_id,
                branch=branch,
                name=f"{variant.label} · {variant.name}",
                purpose=variant.objective,
                audio_path=relative_audio,
                audio_sha256=audio_sha256,
                treatment_plan_id=plan.plan_id,
                treatment_variant_id=variant.variant_id,
                treatment_record_id=thread_id,
                created_by=thread_id,
                created_at=created_at,
                updated_at=created_at,
            )
            self.store.create_version_checked(version)
            project_payload = project.model_dump()
            project_payload["active_version_id"] = version.version_id
            project_payload["updated_at"] = created_at
            updated_project = AudioProject.model_validate(project_payload)
            finished_at = self.clock()
            outputs = {
                "plan_id": plan.plan_id,
                "variant_id": variant.variant_id,
                "version_id": version.version_id,
                "preset": preset,
                "audio_path": version.audio_path,
                "audio_sha256": version.audio_sha256,
                "report_file": process_result.get("report_file"),
                "quality_gate": process_result.get("quality_gate", {}),
                "stage_timings": process_result.get("stage_timings", {}),
                "processed_at": finished_at.isoformat(),
            }
            passed = running.transition_to(
                ThreadStatus.PASSED,
                at=finished_at,
                outputs=outputs,
            )
            advanced = workflow.advance(
                at=finished_at,
                reason=f"DSP Worker passed: {thread_id}",
            )
            self.store.update_project(updated_project)
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
                f"DSP Worker failed: {message}",
                at=failed_at,
            )
            self.store.update_thread(failed)
            self.store.update_workflow(failed_workflow)
            return failed

    @staticmethod
    def _preset_for_variant(variant) -> str:
        step_types = {action.step_type for action in variant.actions}
        if {
            TreatmentStepType.SPACE_DESIGN,
            TreatmentStepType.STEREO_CONTROL,
        } & step_types:
            return "wide_space"
        if {
            TreatmentStepType.DYNAMIC_SHAPING,
            TreatmentStepType.TRUE_PEAK_LIMITING,
            TreatmentStepType.LOUDNESS_NORMALIZATION,
        } & step_types:
            return "clean_master"
        return "warm_vocal"
