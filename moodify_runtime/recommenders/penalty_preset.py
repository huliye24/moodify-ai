"""Penalty-Driven Preset Recommender (Loop C).

MHP-816: Implement Penalty-Driven Preset Recommender.

Analyzes MRS Open penalty flags (over_dark, over_bright, etc.) and produces
craft/preset policy recommendations.
"""

from __future__ import annotations

from typing import Any

from moodify_runtime.recommenders.base import Recommendation


# Known penalty flag types and their default actions
FLAG_ACTIONS: dict[str, dict[str, str]] = {
    "over_dark": {
        "action": "Down-rank or block preset for this sample class; test brighter alternative",
        "owner": "craft_presets",
    },
    "over_bright": {
        "action": "Down-rank or block preset for this sample class; test warmer alternative",
        "owner": "craft_presets",
    },
    "loudness_penalty": {
        "action": "Check loudness compliance; may need limiter or gain adjustment",
        "owner": "craft_presets",
    },
    "hq_damage": {
        "action": "Preset caused quality degradation; review processing chain for artifacts",
        "owner": "craft_chain",
    },
}


class PenaltyPresetRecommender:
    """Produce craft/preset policy recommendations from MRS Open penalty flags.

    Usage:
        rec = PenaltyPresetRecommender()
        recommendations = rec.analyze(flagged_tasks)
    """

    def analyze(self, tasks: list[dict[str, Any]]) -> list[Recommendation]:
        """Analyze flagged tasks and return preset policy recommendations."""
        recommendations: list[Recommendation] = []
        for task in tasks:
            flags = task.get("mrs_open_flags", "")
            if not flags:
                continue
            rec = self._analyze_one(task, flags)
            recommendations.append(rec)
        return recommendations

    def _analyze_one(self, task: dict[str, Any], flag: str) -> Recommendation:
        task_id = task.get("task_id", "")
        sample_id = task.get("sample_id", "")
        preset = task.get("preset", "")
        open_delta = task.get("delta_mrs_open_v031") or 0

        flag_info = FLAG_ACTIONS.get(flag, {
            "action": f"Review {preset} for penalty flag: {flag}",
            "owner": "craft_presets",
        })

        # Severity: over_dark on a preset that also shows negative delta is higher severity
        abs_delta = abs(open_delta)
        if flag == "over_dark" and open_delta < -5:
            severity = "high"
            needs_review = True
        elif abs_delta > 20:
            severity = "medium"
            needs_review = False
        else:
            severity = "medium"
            needs_review = False

        reason = (
            f"{preset} on {sample_id} triggered {flag} flag. "
            f"MRS Open delta: {open_delta:+.1f}."
        )

        action = (
            f"{flag_info['action']}. "
            f"Sample: {sample_id}, Preset: {preset}, Flag: {flag}."
        )

        return Recommendation(
            task_id=f"{task_id}:craft",
            loop="craft_preset_selection",
            severity=severity,
            reason=reason[:180],
            next_action=action[:220],
            needs_human_review=needs_review,
            source_signal=f"mrs_open_flags:{flag}",
            owner_subsystem=flag_info["owner"],
            estimated_effort="M" if severity == "high" else "S",
        )
