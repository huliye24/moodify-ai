"""Score Disagreement Recommender (Loop B).

MHP-815: Implement Score Disagreement Recommender.

Analyzes pseudo-MRS vs MRS Open sign disagreements and produces scoring
calibration proposals.
"""

from __future__ import annotations

from typing import Any

from moodify_runtime.recommenders.base import Recommendation


class ScoreDisagreementRecommender:
    """Produce calibration recommendations from pseudo/MRS Open disagreements.

    Thresholds:
      - abs(open_delta) > 50 or abs(pseudo_delta) > 15 → high severity
      - disagreement with moderate magnitude → medium severity
      - small disagreement → low severity

    Usage:
        rec = ScoreDisagreementRecommender()
        recommendations = rec.analyze(disagreement_tasks)
    """

    # Thresholds for severity classification
    HIGH_OPEN_DELTA = 50.0
    HIGH_PSEUDO_DELTA = 15.0

    def analyze(self, tasks: list[dict[str, Any]]) -> list[Recommendation]:
        """Analyze scoring disagreements and return calibration recommendations."""
        recommendations: list[Recommendation] = []
        for task in tasks:
            if not task.get("score_direction_disagreement"):
                continue
            rec = self._analyze_one(task)
            recommendations.append(rec)
        return recommendations

    def _analyze_one(self, task: dict[str, Any]) -> Recommendation:
        task_id = task.get("task_id", "")
        preset = task.get("preset", "")
        pseudo = task.get("pseudo_delta_mrs") or 0
        open_d = task.get("delta_mrs_open_v031") or 0
        abs_open = abs(open_d)
        abs_pseudo = abs(pseudo)
        gap = abs(pseudo - open_d)

        # Severity classification
        if abs_open > self.HIGH_OPEN_DELTA or abs_pseudo > self.HIGH_PSEUDO_DELTA:
            severity = "high"
            needs_review = True
        elif gap > 20:
            severity = "medium"
            needs_review = gap > 30
        else:
            severity = "low"
            needs_review = False

        # Reason
        reason = (
            f"Pseudo MRS delta {pseudo:+.1f} vs MRS Open v0.3.1 delta {open_d:+.1f} "
            f"(gap {gap:.0f}). Signs disagree — calibration may be needed."
        )

        # Next action
        if severity == "high":
            action = (
                f"Flag {preset} for calibration review. "
                f"Large sign disagreement (pseudo {pseudo:+.0f} vs open {open_d:+.0f}) "
                f"suggests weight mismatch. Log for MRS weight tuning session."
            )
        elif severity == "medium":
            action = (
                f"Log {preset} as medium-priority calibration note. "
                f"Accumulate evidence across 3+ nights before adjusting weights."
            )
        else:
            action = (
                f"Note {preset} as low-priority disagreement. "
                f"No threshold change needed yet."
            )

        return Recommendation(
            task_id=f"{task_id}:score",
            loop="scoring_calibration",
            severity=severity,
            reason=reason[:180],
            next_action=action[:220],
            needs_human_review=needs_review,
            source_signal="score_direction_disagreement",
            owner_subsystem="mrs_scoring",
            estimated_effort="M" if severity == "high" else "S",
        )
