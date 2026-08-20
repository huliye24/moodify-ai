"""Result selection and failure classification (MFY-CR-P08).

Selection is conservative but not redundant: a HUMAN_REQUIRED verdict on one
candidate disqualifies only that candidate, while a MEDIUM-confidence objective
that entered planning always stops automation. SOURCE_WINS is a first-class
product outcome, never a failure.
"""

from __future__ import annotations

from dataclasses import dataclass

from moodify.reconstruction.pipeline import PipelineResult

from .contract import FailureInfo, JobStatus


@dataclass(frozen=True)
class SelectDecision:
    status: str
    selected_candidate: str
    plan_hash: str | None
    identity_status: str
    technical_status: str
    human_reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "selected_candidate": self.selected_candidate,
            "plan_hash": self.plan_hash,
            "identity_status": self.identity_status,
            "technical_status": self.technical_status,
            "human_reasons": list(self.human_reasons),
        }


def _objective_human_reasons(plans: list[dict]) -> list[str]:
    """P04: MEDIUM-confidence objectives that entered planning require human
    review even when a candidate looks auto-approvable."""
    reasons: list[str] = []
    seen: set[str] = set()
    for plan in plans:
        for ref in plan.get("objective_refs", []):
            if (":MEDIUM:" in ref or ref.endswith(":MEDIUM")) and ref not in seen:
                seen.add(ref)
                reasons.append(f"objective:{ref}:human_review")
    return reasons


def select_result(result: PipelineResult) -> SelectDecision:
    """Map the pipeline outcome to the product decision tree.

    1. Best auto-approvable candidate (hard gates passed) -> SUCCEEDED,
       unless a MEDIUM objective entered planning.
    2. MEDIUM objective entered planning -> HUMAN_REQUIRED (never auto-approve).
    3. No auto candidate but identity needs review -> HUMAN_REQUIRED.
    4. Otherwise -> SOURCE_WINS (original preserved).
    """
    auto = [
        r for r in result.ranking
        if r["candidate_id"] != "SOURCE"
        and r["auto_approvable"]
        and not result.candidates[r["candidate_id"]]["gates"]
    ]
    obj_human = _objective_human_reasons(result.plans)

    if auto and not obj_human:
        top = auto[0]
        return SelectDecision(
            status=JobStatus.SUCCEEDED.value,
            selected_candidate=top["candidate_id"],
            plan_hash=result.candidates[top["candidate_id"]]["plan_hash"],
            identity_status=top["guard_state"],
            technical_status="candidate_selected",
        )

    if obj_human:
        return SelectDecision(
            status=JobStatus.HUMAN_REQUIRED.value,
            selected_candidate="HUMAN_REQUIRED",
            plan_hash=None,
            identity_status="HUMAN_REQUIRED",
            technical_status="deferred",
            human_reasons=tuple(obj_human),
        )

    for cid, verdict in result.identity.items():
        if verdict.get("state") == "HUMAN_REQUIRED":
            return SelectDecision(
                status=JobStatus.HUMAN_REQUIRED.value,
                selected_candidate="HUMAN_REQUIRED",
                plan_hash=None,
                identity_status="HUMAN_REQUIRED",
                technical_status="deferred",
                human_reasons=(f"identity_guard:{cid}:HUMAN_REQUIRED",),
            )

    return SelectDecision(
        status=JobStatus.SOURCE_WINS.value,
        selected_candidate="SOURCE",
        plan_hash="source",
        identity_status="SOURCE_PRESERVED",
        technical_status="no_safe_candidate",
    )


def classify_pipeline_failure(exc: Exception, stage: str = "pipeline") -> FailureInfo:
    """Map execution exceptions to product failure semantics."""
    if isinstance(exc, MemoryError):
        return FailureInfo(
            failure_code="RESOURCE_LIMIT",
            stage=stage,
            retry_policy="PERMANENT",
            user_action="retry later",
            internal_detail="memory limit during pipeline",
            public_message_key="reconstruction_resource_limit",
        )
    return FailureInfo(
        failure_code="PIPELINE_FAILED",
        stage=stage,
        retry_policy="TRANSIENT",
        user_action="retry later",
        internal_detail=f"{type(exc).__name__}: {exc}",
        public_message_key="reconstruction_pipeline_failed",
    )
