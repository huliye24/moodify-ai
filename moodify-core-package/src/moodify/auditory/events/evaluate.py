"""Event localization evaluation metrics (MFY-PHASE1-DEPTH-002).

Presence recall, unexpected false positives, start/end boundary error
and temporal IoU. Matching is by event type and maximum temporal
overlap. Deterministic given identical inputs.
"""

from __future__ import annotations

from moodify.auditory.events.models import TemporalEvent


def evaluate_events(predicted: list[TemporalEvent], ground_truth: list[dict]) -> dict:
    """Compare predicted events against ground-truth intervals.

    ground_truth: list of {"event_type", "start_ms", "end_ms"}.
    """
    results: dict[str, dict] = {}
    for event_type in {e["event_type"] for e in ground_truth} | {e.event_type for e in predicted}:
        gt = [g for g in ground_truth if g["event_type"] == event_type]
        pred = [p for p in predicted if p.event_type == event_type]
        matched_gt: set[int] = set()
        matched_pred: set[int] = set()
        start_errors: list[float] = []
        end_errors: list[float] = []
        ious: list[float] = []
        for i, p in enumerate(pred):
            best_j, best_iou = None, 0.0
            for j, g in enumerate(gt):
                if j in matched_gt:
                    continue
                iou = _temporal_iou(p.start_ms, p.end_ms, g["start_ms"], g["end_ms"])
                if iou > best_iou:
                    best_iou, best_j = iou, j
            if best_j is not None and best_iou > 0:
                matched_gt.add(best_j)
                matched_pred.add(i)
                g = gt[best_j]
                start_errors.append(abs(p.start_ms - g["start_ms"]))
                end_errors.append(abs(p.end_ms - g["end_ms"]))
                ious.append(best_iou)
        results[event_type] = {
            "expected": len(gt),
            "detected": len(matched_gt),
            "recall": round(len(matched_gt) / len(gt), 4) if gt else 1.0,
            "false_positives": len(pred) - len(matched_pred),
            "start_error_ms": round(sum(start_errors) / len(start_errors), 1) if start_errors else None,
            "end_error_ms": round(sum(end_errors) / len(end_errors), 1) if end_errors else None,
            "mean_iou": round(sum(ious) / len(ious), 4) if ious else None,
        }
    return results


def _temporal_iou(a0: int, a1: int, b0: int, b1: int) -> float:
    overlap = max(0, min(a1, b1) - max(a0, b0))
    union = max(1, max(a1, b1) - min(a0, b0))
    return overlap / union
