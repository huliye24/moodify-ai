"""Deterministic rule-based Designer for Workspace v2."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from moodify.domain import (
    ProjectThread,
    ThreadRole,
    ThreadStatus,
    ThreadType,
    TreatmentAction,
    TreatmentPlan,
    TreatmentStepType,
    TreatmentVariant,
    WorkflowStage,
)
from moodify.storage import WorkspaceStore


Clock = Callable[[], datetime]


class DesignerService:
    def __init__(
        self,
        store: WorkspaceStore,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.store = store
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def generate_plan(
        self,
        project_id: str,
        thread_id: str,
        plan_id: str,
    ) -> ProjectThread:
        project = self.store.get_project(project_id)
        workflow = self.store.get_workflow(project_id)
        if workflow.stage is not WorkflowStage.DESIGN:
            raise ValueError("Designer can run only during DESIGN")
        started_at = self.clock()
        thread = ProjectThread(
            thread_id=thread_id,
            project_id=project_id,
            thread_type=ThreadType.DESIGN,
            role=ThreadRole.DESIGNER,
            inputs={"plan_id": plan_id},
            created_at=started_at,
            updated_at=started_at,
        )
        self.store.create_thread(thread)
        running = thread.transition_to(
            ThreadStatus.QUEUED, at=started_at
        ).transition_to(ThreadStatus.RUNNING, at=started_at)
        self.store.update_thread(running)
        try:
            if project.creative_brief is None:
                raise ValueError("Designer requires a CreativeBrief")
            diagnosis_thread = self._latest_diagnosis(project_id)
            plan = self._build_plan(
                project_id=project_id,
                thread_id=thread_id,
                plan_id=plan_id,
                diagnosis_thread=diagnosis_thread,
                brief=project.creative_brief,
                created_at=self.clock(),
            )
            self.store.create_plan(plan)
            finished_at = self.clock()
            passed = running.transition_to(
                ThreadStatus.PASSED,
                at=finished_at,
                outputs={
                    "plan_id": plan.plan_id,
                    "diagnosis_id": plan.diagnosis_id,
                    "variant_ids": [
                        variant.variant_id for variant in plan.variants
                    ],
                    "recommended_variant_id": plan.recommended_variant_id,
                    "designed_at": finished_at.isoformat(),
                },
            )
            advanced = workflow.advance(
                at=finished_at,
                reason=f"design thread passed: {thread_id}",
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
                f"Designer failed: {message}",
                at=failed_at,
            )
            self.store.update_thread(failed)
            self.store.update_workflow(failed_workflow)
            return failed

    def _latest_diagnosis(self, project_id: str) -> ProjectThread:
        candidates = [
            thread
            for thread in self.store.list_threads(project_id)
            if thread.thread_type is ThreadType.DIAGNOSIS
            and thread.status is ThreadStatus.PASSED
        ]
        if not candidates:
            raise ValueError("Designer requires a passed Diagnosis Thread")
        return max(
            candidates,
            key=lambda thread: (thread.updated_at, thread.thread_id),
        )

    @staticmethod
    def _build_plan(
        *,
        project_id: str,
        thread_id: str,
        plan_id: str,
        diagnosis_thread: ProjectThread,
        brief,
        created_at: datetime,
    ) -> TreatmentPlan:
        diagnosis = diagnosis_thread.outputs.get("diagnosis")
        if not isinstance(diagnosis, dict):
            raise ValueError("Diagnosis Thread has no structured diagnosis")
        issues = [
            str(issue).strip()
            for issue in diagnosis.get("issues", [])
            if str(issue).strip()
        ] or ["No critical issue; preserve current tonal balance"]
        health = str(diagnosis.get("overall_health", "fair")).casefold()
        platform_lufs = -14.0 if "stream" in brief.platform.casefold() else -16.0
        preserve = list(brief.preserve)
        shared_metrics = {
            "integrated_lufs": platform_lufs,
            "true_peak_dbtp": -1.0,
        }
        variant_a = TreatmentVariant(
            variant_id=f"{plan_id}-a",
            label="A",
            name="Natural Preservation",
            objective=f"{brief.goal}；优先保留原始质感",
            problems=issues,
            preserve=preserve,
            actions=[
                TreatmentAction(
                    action_id="a-spectral",
                    order=1,
                    step_type=TreatmentStepType.SPECTRAL_BALANCE,
                    public_summary="温和修正诊断中最突出的频谱问题",
                    reason=issues[0],
                    parameter_bounds={"spectral_adjustment_db": (-2.0, 2.0)},
                    prerequisites=["diagnosis-ready"],
                ),
                TreatmentAction(
                    action_id="a-dynamics",
                    order=2,
                    step_type=TreatmentStepType.DYNAMIC_SHAPING,
                    public_summary="保留瞬态前提下稳定动态",
                    reason="满足 preserve 约束并避免过度压缩",
                    parameter_bounds={"gain_reduction_db": (0.0, 2.0)},
                    prerequisites=["spectral-balance-complete"],
                ),
                TreatmentAction(
                    action_id="a-loudness",
                    order=3,
                    step_type=TreatmentStepType.LOUDNESS_NORMALIZATION,
                    public_summary=f"匹配 {brief.platform} 发布响度",
                    reason="保证平台播放一致性",
                    target_metrics=shared_metrics,
                    prerequisites=["dynamic-shaping-complete"],
                ),
            ],
            risks=["修正幅度保守，部分问题可能仍可感知"],
            expected_output="更平衡且保持原始动态和情绪的自然版本",
            target_metrics=shared_metrics,
        )
        variant_b = TreatmentVariant(
            variant_id=f"{plan_id}-b",
            label="B",
            name="Focused Correction",
            objective=f"{brief.goal}；优先解决已识别问题",
            problems=issues,
            preserve=preserve,
            actions=[
                TreatmentAction(
                    action_id="b-spectral",
                    order=1,
                    step_type=TreatmentStepType.SPECTRAL_BALANCE,
                    public_summary="针对诊断问题执行更明确的频谱修正",
                    reason="问题优先方案需要更高修正确定性",
                    parameter_bounds={"spectral_adjustment_db": (-4.0, 3.0)},
                    prerequisites=["diagnosis-ready"],
                ),
                TreatmentAction(
                    action_id="b-stereo",
                    order=2,
                    step_type=TreatmentStepType.STEREO_CONTROL,
                    public_summary="控制空间宽度并检查单声道兼容",
                    reason="提高不同播放系统上的稳定性",
                    parameter_bounds={"stereo_width": (0.8, 1.15)},
                    prerequisites=["spectral-balance-complete"],
                ),
                TreatmentAction(
                    action_id="b-loudness",
                    order=3,
                    step_type=TreatmentStepType.TRUE_PEAK_LIMITING,
                    public_summary=f"达到 {brief.platform} 目标并限制真峰值",
                    reason="提供更稳定的发布电平",
                    target_metrics=shared_metrics,
                    prerequisites=["stereo-control-complete"],
                ),
            ],
            risks=["修正更明显，可能削弱部分原始个性"],
            expected_output="问题更少、平台一致性更高的聚焦版本",
            target_metrics=shared_metrics,
        )
        recommend_b = health == "poor" and len(issues) >= 3
        recommended = variant_b if recommend_b else variant_a
        return TreatmentPlan(
            plan_id=plan_id,
            project_id=project_id,
            brief_revision=1,
            diagnosis_id=diagnosis_thread.thread_id,
            variants=[variant_a, variant_b],
            recommended_variant_id=recommended.variant_id,
            recommendation_reason=(
                "诊断健康度较差且问题较多，优先采用聚焦修正"
                if recommend_b
                else "优先满足 CreativeBrief 的保留约束并控制处理风险"
            ),
            created_by_thread_id=thread_id,
            created_at=created_at,
            metadata={
                "designer": "rules.v1",
                "platform": brief.platform,
                "avoid": list(brief.avoid),
                "diagnosis_health": health,
            },
        )
