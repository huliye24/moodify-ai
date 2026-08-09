"""Experiment evaluation (MFY-PHASE1-DEPTH-005).

TP/FP/TN/FN raw counts, recall/precision, start/end error, temporal IoU,
measurement delta direction checks, first-detection level, cross-domain
false positives, evidence completeness and failure classification.
"""

from __future__ import annotations

from typing import Any

from moodify.auditory.lab.models import ExperimentResult, GroundTruth

FAILURE_CLASSES = {
    "MEASUREMENT_FAILURE", "TEMPORAL_FAILURE", "REPRESENTATION_FAILURE",
    "RULE_FAILURE", "EVIDENCE_FAILURE", "EXPECTATION_ERROR",
    "RESOURCE_FAILURE", "UNSUPPORTED_CASE",
}


def _temporal_iou(a0: int, a1: int, b0: int, b1: int) -> float:
    overlap = max(0, min(a1, b1) - max(a0, b0))
    union = max(1, max(a1, b1) - min(a0, b0))
    return overlap / union


def evaluate_experiment(result: ExperimentResult) -> dict[str, Any]:
    """Evaluate one experiment against its ground truth."""
    truth: GroundTruth = result.ground_truth
    expected_type = truth.expected_event_type
    detected = result.detected_events
    allowed_types = {expected_type, *truth.allowed_secondary_event_types}
    unexpected = [event for event in detected if event["event_type"] not in allowed_types]

    matched = None
    for event in detected:
        if event["event_type"] == expected_type:
            matched = event
            break

    summary: dict[str, Any] = {
        "experiment_id": result.experiment_id,
        "operator": truth.operator,
        "expected_event": expected_type,
        "failure_class": "",
    }
    if expected_type is None:
        # Measurement-only experiments: no event expected (e.g. DC_OFFSET).
        summary.update({
            "tp": 0, "fp": len(unexpected), "tn": 1, "fn": 0,
            "recall": None, "precision": 0.0 if unexpected else None,
            "unexpected_events": [e["event_type"] for e in unexpected],
        })
    elif matched is None:
        summary.update({
            "tp": 0, "fp": len(unexpected), "tn": 0, "fn": 1,
            "recall": 0.0, "precision": 0.0,
            "failure_class": _classify_failure(result, "missed"),
        })
    else:
        start_err = abs(matched["start_ms"] - (truth.expected_start_ms or 0))
        end_err = abs(matched["end_ms"] - (truth.expected_end_ms or matched["end_ms"]))
        iou = _temporal_iou(
            matched["start_ms"], matched["end_ms"],
            truth.expected_start_ms or matched["start_ms"],
            truth.expected_end_ms or matched["end_ms"],
        )
        summary.update({
            "tp": 1, "fp": len(unexpected), "tn": 0, "fn": 0,
            "recall": 1.0, "precision": 1.0 / (1 + len(unexpected)),
            "allowed_secondary_events": list(truth.allowed_secondary_event_types),
            "unexpected_events": [e["event_type"] for e in unexpected],
            "start_error_ms": start_err,
            "end_error_ms": end_err,
            "temporal_iou": round(iou, 4),
            "failure_class": _classify_failure(result, "localized") if iou < 0.3 else "",
        })

    # Measurement delta direction checks.
    delta_checks: dict[str, bool] = {}
    expected_delta = truth.expected_measurement_delta or {}
    for metric, direction in expected_delta.items():
        delta = result.measurement_delta.get(metric)
        if delta is None:
            delta_checks[metric] = False
            continue
        delta_checks[metric] = (delta > 0) if direction == "up" else (delta < 0)
    summary["delta_direction_checks"] = delta_checks
    summary["delta_all_correct"] = all(delta_checks.values()) if delta_checks else None
    summary["evidence_complete"] = result.evidence_complete

    if not summary.get("failure_class") and summary.get("delta_all_correct") is False:
        summary["failure_class"] = _classify_failure(result, "delta")
    if not summary.get("failure_class") and not result.evidence_complete:
        summary["failure_class"] = "EVIDENCE_FAILURE"
    return summary


def _classify_failure(result: ExperimentResult, kind: str) -> str:
    if result.failure_class in FAILURE_CLASSES:
        return result.failure_class
    if kind == "delta":
        return "MEASUREMENT_FAILURE"
    if kind == "localized":
        return "TEMPORAL_FAILURE"
    return "RULE_FAILURE"


def aggregate_matrix(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate TP/FP/TN/FN across the matrix."""
    tp = sum(1 for r in results if r["tp"])
    fp = sum(r["fp"] for r in results)
    fn = sum(1 for r in results if r["fn"])
    tn = sum(1 for r in results if r["tn"] and r["expected_event"] is None)
    recall = tp / (tp + fn) if (tp + fn) else None
    precision = tp / (tp + fp) if (tp + fp) else None
    return {
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "recall": round(recall, 4) if recall is not None else None,
        "precision": round(precision, 4) if precision is not None else None,
        "failures": {
            "MEASUREMENT_FAILURE": sum(1 for r in results if r.get("failure_class") == "MEASUREMENT_FAILURE"),
            "TEMPORAL_FAILURE": sum(1 for r in results if r.get("failure_class") == "TEMPORAL_FAILURE"),
            "RULE_FAILURE": sum(1 for r in results if r.get("failure_class") == "RULE_FAILURE"),
            "EVIDENCE_FAILURE": sum(1 for r in results if r.get("failure_class") == "EVIDENCE_FAILURE"),
        },
    }
