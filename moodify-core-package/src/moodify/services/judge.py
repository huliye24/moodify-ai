"""Judge adapter for workspace v2 quality gate evaluation."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from moodify.domain import (
    ProjectThread,
    ThreadRole,
    ThreadStatus,
    ThreadType,
    WorkflowStage,
)
from moodify.storage import WorkspaceStore

Clock = Callable[[], datetime]


def _run_quality_checks(
    original_path: str,
    processed_path: str,
    *_,
    **__,
) -> dict[str, Any]:
    """Run quality checks on a processed audio file versus original.

    Returns a dict with pass/reject/reprocess verdict and per-check results.
    Falls back to a basic structural check when MRS engine is unavailable.
    """
    results: dict[str, Any] = {
        "verdict": "pass",
        "checks": {},
        "warnings": [],
    }

    try:
        import soundfile as sf

        orig_info = sf.info(original_path)
        proc_info = sf.info(processed_path)

        if proc_info.samplerate != orig_info.samplerate:
            results["warnings"].append(
                f"sample rate changed: {orig_info.samplerate} -> {proc_info.samplerate}"
            )

        if proc_info.duration <= 0:
            results["verdict"] = "reject"
            results["checks"]["duration"] = {
                "passed": False,
                "reason": "processed audio has zero duration",
            }
            return results

        duration_ratio = proc_info.duration / max(orig_info.duration, 0.001)
        if duration_ratio < 0.9 or duration_ratio > 1.1:
            results["verdict"] = "reject"
            results["checks"]["duration"] = {
                "passed": False,
                "reason": f"duration mismatch: {duration_ratio:.2%}",
            }
        else:
            results["checks"]["duration"] = {"passed": True}

        results["checks"]["structural"] = {"passed": True}
    except Exception as exc:
        results["verdict"] = "reprocess"
        results["checks"]["structural"] = {
            "passed": False,
            "reason": str(exc),
        }

    try:
        from moodify.mrs_adapter import score_for_quality_gate

        gate = score_for_quality_gate(
            before_path=original_path,
            after_path=processed_path,
        )
        results["mrs_version"] = gate.mrs_version
        results["mrs_score"] = gate.mrs_score

        if gate.mrs_score is not None:
            if gate.mrs_score < 60:
                results["verdict"] = "reject"
                results["checks"]["mrs"] = {
                    "passed": False,
                    "score": gate.mrs_score,
                    "reason": f"MRS below threshold: {gate.mrs_score:.1f}",
                }
            elif gate.mrs_score < 75:
                results["warnings"].append(f"marginal MRS: {gate.mrs_score:.1f}")
                results["checks"]["mrs"] = {"passed": True, "score": gate.mrs_score}
            else:
                results["checks"]["mrs"] = {"passed": True, "score": gate.mrs_score}

        if gate.loudness_pass is not None and not gate.loudness_pass:
            results["verdict"] = "reprocess"
            results["checks"]["loudness"] = {
                "passed": False,
                "reason": "loudness target not met",
            }
        elif gate.loudness_pass is not None:
            results["checks"]["loudness"] = {"passed": True}

    except Exception as exc:
        results["warnings"].append(f"MRS engine unavailable, using structural only: {exc}")
        results["mrs_version"] = "degraded"

    return results


class JudgeService:
    """Evaluates processed audio versions against quality gates.

    Creates JUDGE threads, runs quality checks (MRS, loudness, dynamics,
    structural), and outputs pass/reject/reprocess verdicts.
    When MRS is unavailable, degrades gracefully to structural checks.
    """

    def __init__(
        self,
        store: WorkspaceStore,
        *,
        runner: Callable[..., dict[str, Any]] = _run_quality_checks,
        clock: Clock | None = None,
    ) -> None:
        self.store = store
        self.runner = runner
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def judge_version(
        self,
        project_id: str,
        thread_id: str,
        version_id: str,
    ) -> ProjectThread:
        project = self.store.get_project(project_id)
        workflow = self.store.get_workflow(project_id)
        if workflow.stage is not WorkflowStage.JUDGE:
            raise ValueError("Judge can run only during JUDGE stage")

        version = self.store.get_version(project_id, version_id)
        started_at = self.clock()

        thread = ProjectThread(
            thread_id=thread_id,
            project_id=project_id,
            thread_type=ThreadType.JUDGE,
            role=ThreadRole.JUDGE,
            inputs={
                "version_id": version_id,
                "audio_path": version.audio_path,
                "treatment_plan_id": version.treatment_plan_id,
                "treatment_variant_id": version.treatment_variant_id,
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
            source_audio_id = project.source_audio_ids[0]
            original_path = str(
                self.store.resolve_source_audio(project_id, source_audio_id)
            )
            processed_path = str(
                self.store._project_dir(project_id) / version.audio_path
            )

            quality_result = self.runner(original_path, processed_path)
            finished_at = self.clock()

            outputs = {
                "version_id": version_id,
                "verdict": quality_result.get("verdict", "pass"),
                "checks": quality_result.get("checks", {}),
                "warnings": quality_result.get("warnings", []),
                "mrs_version": quality_result.get("mrs_version", "degraded"),
                "mrs_score": quality_result.get("mrs_score"),
                "judged_at": finished_at.isoformat(),
            }

            verdict = outputs["verdict"]
            if verdict == "pass":
                final_thread = running.transition_to(
                    ThreadStatus.PASSED, at=finished_at, outputs=outputs
                )
                advanced = workflow.advance(
                    at=finished_at,
                    reason=f"Judge passed: {thread_id}",
                )
            elif verdict == "reprocess":
                final_thread = running.transition_to(
                    ThreadStatus.REJECTED, at=finished_at, outputs=outputs
                )
                advanced = workflow.fail(
                    f"Judge requested reprocess: {thread_id}",
                    at=finished_at,
                )
            else:
                final_thread = running.transition_to(
                    ThreadStatus.REJECTED, at=finished_at, outputs=outputs
                )
                advanced = workflow.fail(
                    f"Judge rejected: {thread_id}",
                    at=finished_at,
                )

            self.store.update_thread(final_thread)
            self.store.update_workflow(advanced)
            return final_thread

        except Exception as exc:
            failed_at = self.clock()
            message = str(exc) or exc.__class__.__name__
            failed = running.transition_to(
                ThreadStatus.FAILED, at=failed_at, error=message,
            )
            failed_workflow = workflow.fail(
                f"Judge failed: {message}", at=failed_at,
            )
            self.store.update_thread(failed)
            self.store.update_workflow(failed_workflow)
            return failed
