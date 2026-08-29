"""Experiment runner (MFY-PHASE1-DEPTH-005).

Canonical loop: source -> perturb -> ground truth -> Moodify analysis ->
evaluation -> evidence -> result. Runs the temporal hearing engine and
global measurement deltas; no audio analysis is duplicated beyond the
shared authorities.
"""

from __future__ import annotations

from typing import Any
from moodify.auditory.events.engine import run_temporal_hearing
from moodify.auditory.identity import logical_id
from moodify.auditory.lab.evaluate import evaluate_experiment
from moodify.auditory.lab.ground_truth import build_ground_truth
from moodify.auditory.lab.models import ExperimentResult, PerturbationSpec
from moodify.auditory.lab.perturbations import apply_perturbation
from moodify.auditory.lab.sources import generate_source, SR
from moodify.auditory.metrics import compute_metrics


class _Probe:
    def __init__(self, sha256: str = "lab"):
        self.sha256 = sha256


def _metric_value(metrics: dict, key: str) -> float | None:
    entry = metrics.get(key)
    if isinstance(entry, dict):
        value = entry.get("value")
        return float(value) if isinstance(value, (int, float)) else None
    return None


def run_experiment(source_id: str, spec: PerturbationSpec,
                   evaluate: bool = True) -> dict[str, Any]:
    """Run one controlled experiment."""
    original = generate_source(source_id)
    perturbed = apply_perturbation(original, SR, spec)
    ground_truth = build_ground_truth(source_id, spec)

    before_metrics = compute_metrics(original, SR, _Probe())
    after_metrics = compute_metrics(perturbed, SR, _Probe())
    from moodify.auditory.stereo import compute_stereo_metrics

    if original.ndim > 1:
        before_metrics.update(compute_stereo_metrics(original))
        after_metrics.update(compute_stereo_metrics(perturbed))
    delta = {}
    if ground_truth.expected_measurement_delta:
        for metric in ground_truth.expected_measurement_delta:
            before = _metric_value(before_metrics, metric)
            after = _metric_value(after_metrics, metric)
            if before is not None and after is not None:
                delta[metric] = round(after - before, 6)

    events = run_temporal_hearing(perturbed, SR).events
    detected = [
        {"event_type": event.event_type,
         "start_ms": event.start_ms, "end_ms": event.end_ms}
        for event in events
    ]

    result = ExperimentResult(
        experiment_id=logical_id("exp", {
            "source_id": source_id,
            "perturbation": spec.to_dict(),
        }, 10),
        source_id=source_id,
        perturbation=spec,
        ground_truth=ground_truth,
        detected_events=detected,
        measurement_delta=delta,
        evidence_complete=all(event.evidence_windows for event in events),
    )
    payload = result.to_dict()
    payload["evaluation"] = evaluate_experiment(result) if evaluate else None
    return payload
