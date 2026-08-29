"""Issue → recommendation mapping (engine-level, shared by QA/Master/demo).

Deterministic mapping from detected issues to actionable recommendations.
The demo and future product modules must not invent their own fixes.
"""

from __future__ import annotations

from typing import Any

_RULES: dict[str, dict[str, str]] = {
    "high_frequency_harshness": {
        "action": "Apply a gentle high-shelf cut (1–3 dB) or a dynamic EQ on 2–5 kHz",
        "target": "presence band",
        "rationale": "Reduces listening fatigue on commercial playback systems.",
        "priority": "medium",
    },
    "low_dynamic_contrast": {
        "action": "Increase dynamic range: relax bus compression / limiting",
        "target": "master bus",
        "rationale": "Restores musical contrast and perceived openness.",
        "priority": "high",
    },
    "possible_over_compression": {
        "action": "Reduce limiter gain reduction to <= 2–3 dB and re-check crest factor",
        "target": "limiter",
        "rationale": "Recovers punch and transient detail before distribution.",
        "priority": "high",
    },
    "clipping_risk": {
        "action": "Lower output ceiling to -1.0 dBTP before encoding",
        "target": "output ceiling",
        "rationale": "Prevents inter-sample clipping on lossy playback.",
        "priority": "high",
    },
    "loudness_off_target": {
        "action": "Normalize integrated loudness toward -14 LUFS for streaming release",
        "target": "master loudness",
        "rationale": "Avoids platform gain-riding and preserves intended balance.",
        "priority": "low",
    },
    "thin_low_end": {
        "action": "Reinforce 60–250 Hz with EQ or re-balance the low-mid arrangement",
        "target": "bass band",
        "rationale": "Restores weight and fullness on full-range systems.",
        "priority": "medium",
    },
    "narrow_stereo_image": {
        "action": "Widen stereo image (mid/side processing, width 5–15%)",
        "target": "stereo bus",
        "rationale": "Creates space and depth without collapsing mono compatibility.",
        "priority": "low",
    },
}


def build_recommendations(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map engine issue records to prioritized recommendations."""
    recommendations: list[dict[str, str]] = []
    seen: set[str] = set()
    for issue in issues:
        rule = _RULES.get(issue["id"])
        if rule is None or issue["id"] in seen:
            continue
        seen.add(issue["id"])
        recommendations.append(dict(rule))
    # Order: high → medium → low, then by original issue order.
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda r: priority_rank[r["priority"]])
    return recommendations


def mastering_preset_suggestion(issues: list[dict[str, Any]]) -> str:
    """Suggest a Moodify Master preset name from the detected issue mix."""
    ids = {issue["id"] for issue in issues}
    if "possible_over_compression" in ids or "low_dynamic_contrast" in ids:
        return "dynamic_restore"
    if "high_frequency_harshness" in ids:
        return "smooth_presence"
    if "thin_low_end" in ids:
        return "warm_low_end"
    return "clean_master"
