"""Calibration recommendations (MFY-PHASE1-DEPTH-005).

Evidence-backed recommendations only: KEEP / REVIEW_THRESHOLD /
REVIEW_DETECTOR / INSUFFICIENT_DATA. Never auto-update rules.
"""

from __future__ import annotations

from typing import Any


def recommend_for_operator(operator: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    """Produce a calibration recommendation from matrix evidence."""
    operator_results = [r for r in results if r.get("operator") == operator]
    if not operator_results:
        return {"operator": operator, "recommendation": "INSUFFICIENT_DATA",
                "evidence": {"experiments": 0}, "auto_update": False}

    expected = [r for r in operator_results if r["expected_event"] is not None]
    missed = sum(1 for r in expected if r.get("recall") == 0.0)
    localized_weak = sum(1 for r in expected
                         if r.get("temporal_iou") is not None and r["temporal_iou"] < 0.3)
    delta_fail = sum(1 for r in operator_results if r.get("delta_all_correct") is False)
    fp = sum(r.get("fp", 0) for r in operator_results)

    if missed == 0 and delta_fail == 0 and fp == 0:
        recommendation = "KEEP"
    elif missed > 0:
        recommendation = "REVIEW_THRESHOLD"
    elif localized_weak > 0 or fp > 0:
        recommendation = "REVIEW_DETECTOR"
    else:
        recommendation = "INSUFFICIENT_DATA"

    return {
        "operator": operator,
        "recommendation": recommendation,
        "evidence": {
            "experiments": len(operator_results),
            "missed": missed,
            "weak_localization": localized_weak,
            "delta_failures": delta_fail,
            "false_positives": fp,
        },
        "auto_update": False,  # never mutate thresholds automatically
    }
