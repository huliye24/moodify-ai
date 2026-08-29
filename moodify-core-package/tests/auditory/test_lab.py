"""Controlled auditory lab tests (MFY-PHASE1-DEPTH-005, Gates G2-G15).

The quick matrix exercises every mandatory operator at one ladder
strength: detection recall, measurement delta direction, evidence
completeness, false-positive safety, reproducibility, calibration
output and failure classification.
"""

from __future__ import annotations

import numpy as np

from moodify.auditory.lab.calibration import recommend_for_operator
from moodify.auditory.lab.ground_truth import build_ground_truth
from moodify.auditory.lab.models import PerturbationSpec
from moodify.auditory.lab.perturbations import LADDERS, PERTURBATION_VERSION
from moodify.auditory.lab.runner import run_experiment
from moodify.auditory.lab.sources import SOURCE_SPECS, generate_source

SR = 48000

# quick matrix: operator -> (source, ladder index)
QUICK_MATRIX = [
    ("C1", "HARD_CLIP", 1),
    ("C1", "NEAR_CLIP", 0),
    ("C1", "DC_OFFSET", 1),
    ("C3", "GAIN_STEP", 1),
    ("C1", "SILENCE_INSERT", 1),
    ("C3", "LOWPASS", 2),
    ("C2", "ANTIPHASE_REGION", 0),
    ("C3", "NOISE_INJECTION", 0),
    ("C1", "DYNAMIC_COMPRESSION", 0),
]


def _spec(operator: str, ladder_index: int) -> PerturbationSpec:
    params = dict(LADDERS[operator][ladder_index])
    region_start = int(params.pop("region_start_ms", 0))
    region_end = int(params.pop("region_end_ms", 0))
    return PerturbationSpec(operator, PERTURBATION_VERSION, params, region_start, region_end)


def _run_matrix(matrix: list[tuple[str, str, int]]) -> list[dict]:
    results = []
    for source_id, operator, level in matrix:
        ev = run_experiment(source_id, _spec(operator, level))["evaluation"]
        results.append(ev)
    return results


# ---------------------------------------------------------------------------
# G2/G3/G4 perturbation authority, ground truth, baseline controls
# ---------------------------------------------------------------------------

def test_perturbation_registry_complete():
    assert set(LADDERS) == {
        "HARD_CLIP", "NEAR_CLIP", "DC_OFFSET", "GAIN_STEP", "SILENCE_INSERT",
        "LOWPASS", "ANTIPHASE_REGION", "NOISE_INJECTION", "DYNAMIC_COMPRESSION",
    }
    assert PERTURBATION_VERSION == "lab-perturbation-v1"
    assert set(SOURCE_SPECS) == {"C1", "C2", "C3", "C4", "C5", "C6"}


def test_ground_truth_derived_from_construction():
    spec = _spec("SILENCE_INSERT", 1)
    truth = build_ground_truth("C1", spec)
    assert truth.expected_event_type == "SILENCE_GAP"
    assert truth.expected_start_ms == 4000
    assert truth.expected_end_ms == 4600
    assert truth.expected_measurement_delta["silence_ratio"] == "up"
    assert set(truth.allowed_secondary_event_types) == {
        "LEVEL_DROP", "HIGH_FREQUENCY_DROPOUT",
    }


def test_sources_have_unperturbed_controls():
    for source_id in SOURCE_SPECS:
        x = generate_source(source_id)
        assert x.size > 0
        assert np.isfinite(x).all()


# ---------------------------------------------------------------------------
# G6-G11 quick matrix: mandatory operators detect correctly
# ---------------------------------------------------------------------------

def test_quick_matrix_all_operators_behave():
    results = _run_matrix(QUICK_MATRIX)
    failures = []
    for result in results:
        operator = result["operator"]
        delta_ok = result.get("delta_all_correct") is not False
        detected = result.get("recall") != 0.0 or result.get("expected_event") is None
        if not (delta_ok and detected):
            failures.append(operator)
    assert not failures, f"operators failing: {failures}"
    # Event-detection operators must all be recalled.
    event_operators = [r for r in results if r["expected_event"] is not None]
    assert all(r["recall"] == 1.0 for r in event_operators), [
        r["operator"] for r in event_operators if r["recall"] != 1.0
    ]


def test_clipping_detection_and_localization():
    ev = run_experiment("C1", _spec("HARD_CLIP", 1))["evaluation"]
    assert ev["recall"] == 1.0
    assert ev["temporal_iou"] >= 0.5
    assert ev["delta_all_correct"] is True
    assert ev["evidence_complete"] is True


def test_silence_detection_localization():
    ev = run_experiment("C1", _spec("SILENCE_INSERT", 1))["evaluation"]
    assert ev["recall"] == 1.0
    assert ev["temporal_iou"] >= 0.8


def test_level_step_direction_and_event():
    ev = run_experiment("C3", _spec("GAIN_STEP", 1))["evaluation"]
    assert ev["recall"] == 1.0
    assert ev["delta_all_correct"] is True  # rms direction correct


def test_spectral_lowpass_response():
    ev = run_experiment("C3", _spec("LOWPASS", 2))["evaluation"]
    assert ev["recall"] == 1.0
    assert ev["delta_all_correct"] is True  # cutoff estimator decreases


def test_stereo_antiphase_detection():
    ev = run_experiment("C2", _spec("ANTIPHASE_REGION", 0))["evaluation"]
    assert ev["recall"] == 1.0
    assert ev["temporal_iou"] >= 0.7
    assert ev["delta_all_correct"] is True  # correlation decreases


def test_noise_and_dynamics_measurement_direction():
    noise_ev = run_experiment("C3", _spec("NOISE_INJECTION", 0))["evaluation"]
    assert noise_ev["delta_all_correct"] is True  # noise floor estimator rises
    dynamics_ev = run_experiment("C1", _spec("DYNAMIC_COMPRESSION", 0))["evaluation"]
    assert dynamics_ev["delta_all_correct"] is True  # crest factor falls


# ---------------------------------------------------------------------------
# G12 false-positive safety (single-domain perturbation)
# ---------------------------------------------------------------------------

def test_single_domain_perturbation_limited_cross_firing():
    # Silence perturbation on a mono source must not fire stereo-domain
    # detectors (NEGATIVE_CORRELATION_REGION / PHASE_RISK_REGION).
    payload = run_experiment("C1", _spec("SILENCE_INSERT", 1))
    unexpected = {
        event["event_type"] for event in payload["detected_events"]
        if event["event_type"] in {"NEGATIVE_CORRELATION_REGION", "PHASE_RISK_REGION"}
    }
    assert not unexpected, f"stereo detectors fired on mono source: {unexpected}"


def test_constructed_secondary_events_are_not_false_positives():
    # The allowance comes from operator physics in the ground-truth manifest,
    # never from observed detector output.
    for source_id, operator, level in QUICK_MATRIX:
        evaluation = run_experiment(source_id, _spec(operator, level))["evaluation"]
        assert evaluation["fp"] == 0, (operator, evaluation.get("unexpected_events"))


# ---------------------------------------------------------------------------
# G13 calibration output (evidence only, no auto mutation)
# ---------------------------------------------------------------------------

def test_calibration_never_auto_updates():
    results = _run_matrix(QUICK_MATRIX)
    for operator in LADDERS:
        recommendation = recommend_for_operator(operator, results)
        assert recommendation["recommendation"] in {
            "KEEP", "REVIEW_THRESHOLD", "REVIEW_DETECTOR", "INSUFFICIENT_DATA",
        }
        assert recommendation["auto_update"] is False
        assert "evidence" in recommendation


# ---------------------------------------------------------------------------
# G14 failure classification
# ---------------------------------------------------------------------------

def test_failures_are_classified():
    results = _run_matrix(QUICK_MATRIX)
    for result in results:
        failure = result.get("failure_class")
        assert failure in {
            "", "MEASUREMENT_FAILURE", "TEMPORAL_FAILURE", "RULE_FAILURE",
            "EVIDENCE_FAILURE",
        }, f"unclassified failure for {result['operator']}: {failure}"


# ---------------------------------------------------------------------------
# G5 reproducibility
# ---------------------------------------------------------------------------

def test_experiment_reproducible():
    first = run_experiment("C1", _spec("HARD_CLIP", 1))
    second = run_experiment("C1", _spec("HARD_CLIP", 1))
    assert first["evaluation"]["temporal_iou"] == second["evaluation"]["temporal_iou"]
    assert first["evaluation"]["delta_all_correct"] == second["evaluation"]["delta_all_correct"]


# ---------------------------------------------------------------------------
# G15 low-resource: quick matrix bounded
# ---------------------------------------------------------------------------

def test_quick_matrix_bounded():
    import time

    start = time.perf_counter()
    _run_matrix(QUICK_MATRIX)
    elapsed = time.perf_counter() - start
    assert elapsed < 120.0  # practical CI bound for 8 experiments
