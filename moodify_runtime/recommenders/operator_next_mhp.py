"""Operator Next-MHP Writer (Loop D).

MHP-818: Implement Operator Next-MHP Writer.

Analyzes the full night-metric record and produces a morning operator decision
(PASS/HOLD/REWORK) with the next MHP direction.
"""

from __future__ import annotations

from typing import Any

from moodify_runtime.recommenders.base import Recommendation, RecommendationBundle
from moodify_runtime.utils import utc_now_iso


class OperatorNextMhpWriter:
    """Produce operator morning brief and next-MHP direction from the full record.

    Usage:
        writer = OperatorNextMhpWriter()
        bundle = writer.decide(night_metric_record, loop_recommendations)
    """

    def decide(
        self,
        record: dict[str, Any],
        recommendations: list[Recommendation],
    ) -> RecommendationBundle:
        """Make the operator gate decision and produce a recommendation bundle."""
        run_id = record.get("run_id", "")

        # Count by severity
        high = [r for r in recommendations if r.severity == "high"]
        medium = [r for r in recommendations if r.severity == "medium"]
        needs_review = [r for r in recommendations if r.needs_human_review]

        # Decision logic
        fatal = record.get("runtime", {}).get("fatal_error")
        failed = record.get("runtime", {}).get("failed", 0)
        disagreements = record.get("scoring", {}).get("disagreement_count", 0)
        flagged = record.get("craft", {}).get("flagged_count", 0)

        if fatal or failed > 0:
            decision = "HOLD"
            decision_reason = (
                f"Night run has {len(high)} high-severity issues"
                + (f" including fatal error" if fatal else "")
                + (f" and {failed} task failure(s)" if failed else "")
                + ". Fix before accepting this batch."
            )
        elif len(high) >= 3:
            decision = "HOLD"
            decision_reason = f"{len(high)} high-severity recommendations require attention before accepting."
        elif len(needs_review) > 0:
            decision = "HOLD"
            decision_reason = f"{len(needs_review)} recommendation(s) need human review."
        elif len(recommendations) == 0:
            decision = "PASS"
            decision_reason = "No recommendations generated. Night run is clean."
        else:
            decision = "PASS"
            decision_reason = (
                f"All {len(recommendations)} recommendations are medium/low severity "
                f"with {disagreements} disagreements and {flagged} flags. Acceptable."
            )

        # Next MHP direction
        if decision == "HOLD":
            if fatal or failed:
                next_mhp = "MHP runtime reliability fix"
            elif disagreements >= 2:
                next_mhp = "MHP scoring calibration session"
            elif flagged >= 2:
                next_mhp = "MHP craft preset review"
            else:
                next_mhp = "MHP operator review"
        else:
            try:
                next_num = int(run_id.split("_")[0])
                next_mhp = f"MHP-{next_num} next cycle"
            except (ValueError, IndexError):
                next_mhp = f"MHP next cycle ({run_id})" if run_id else "MHP next cycle"

        # Build operator recommendation
        op_rec = Recommendation(
            task_id=f"{run_id}:operator",
            loop="operator_report",
            severity="high" if decision == "HOLD" else "low",
            reason=decision_reason[:180],
            next_action=f"{decision}: {next_mhp}"[:220],
            needs_human_review=(decision != "PASS"),
            source_signal="operator_decision",
            owner_subsystem="operator",
            estimated_effort="S",
        )

        all_recs = list(recommendations) + [op_rec]

        return RecommendationBundle(
            run_id=run_id,
            generated_at=utc_now_iso(),
            recommendations=all_recs,
            summary={
                "decision": decision,
                "decision_reason": decision_reason,
                "next_mhp": next_mhp,
                "high_count": len(high),
                "medium_count": len(medium),
                "needs_review_count": len(needs_review),
                "fatal_error": bool(fatal),
                "failed": failed,
                "disagreements": disagreements,
                "flagged": flagged,
            },
        )
