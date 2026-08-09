"""Temporal hearing tests (MFY-PHASE1-DEPTH-002, Gates G3-G13).

Synthetic ground-truth fixtures with known start/end times plus clean
controls exercise every P0 detector, the merge/debounce layer, evidence
resolution and localization metrics.
"""

from __future__ import annotations

import numpy as np

from moodify.auditory.events.evaluate import evaluate_events
from moodify.auditory.events.engine import run_temporal_hearing
from moodify.auditory.events.models import FORBIDDEN_LABELS, P0_EVENT_TYPES
from moodify.auditory.events.temporal_profile import TemporalProfile

SR = 48000


def _time(seconds: float) -> int:
    return int(seconds * SR)


def _sine(seconds: float, gain: float = 0.3, freq: float = 440.0) -> np.ndarray:
    t = np.arange(_time(seconds)) / SR
    return gain * np.sin(2 * np.pi * freq * t)


def _noise(seconds: float, gain: float = 0.3, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return gain * rng.standard_normal(_time(seconds))


def _lowpass(x: np.ndarray, cutoff_hz: float) -> np.ndarray:
    from scipy.signal import butter, lfilter

    b, a = butter(6, cutoff_hz / (SR / 2))
    return lfilter(b, a, x)


def _as_stereo(mono: np.ndarray, invert: bool = False) -> np.ndarray:
    return np.stack([mono, -mono if invert else mono], axis=1)


def _detect(mono: np.ndarray, profile: TemporalProfile | None = None) -> list:
    result = run_temporal_hearing(mono, SR, profile)
    return result.events


# ---------------------------------------------------------------------------
# Profile authority (G2)
# ---------------------------------------------------------------------------

def test_profile_is_single_versioned_authority():
    profile = TemporalProfile.from_yaml()
    assert profile.profile_id == "temporal-hearing-v1"
    assert profile.domains["integrity"].window_ms == 100
    assert profile.domains["spectrum"].window_ms == 1000
    assert profile.gap_tolerance_ms == 150


# ---------------------------------------------------------------------------
# G5 Clipping localization
# ---------------------------------------------------------------------------

def test_clipping_cluster_localized():
    x = _sine(8.0)
    x[_time(2.0):_time(2.6)] = 1.0
    events = [e for e in _detect(x) if e.event_type == "CLIPPING_CLUSTER"]
    assert len(events) == 1
    event = events[0]
    assert abs(event.start_ms / 1000 - 2.0) < 0.2  # bounded by integrity hop (50 ms)
    assert abs(event.end_ms / 1000 - 2.6) < 0.2
    assert event.evidence_windows  # evidence resolution (G12)
    assert event.localization_precision_ms <= 50


# ---------------------------------------------------------------------------
# G6 Silence localization
# ---------------------------------------------------------------------------

def test_silence_gap_localized():
    x = _sine(8.0)
    x[_time(4.0):_time(5.0)] = 0.0
    events = [e for e in _detect(x) if e.event_type == "SILENCE_GAP"]
    assert len(events) == 1
    event = events[0]
    assert abs(event.start_ms / 1000 - 4.0) <= 0.15
    assert abs(event.end_ms / 1000 - 5.0) <= 0.15


# ---------------------------------------------------------------------------
# G7 Stereo/phase localization
# ---------------------------------------------------------------------------

def test_negative_correlation_region_detected():
    mono = _sine(8.0)
    stereo = np.stack([mono, mono], axis=1)
    stereo[_time(1.5):_time(2.5)] = _as_stereo(mono[_time(1.5):_time(2.5)], invert=True)
    events = [e for e in run_temporal_hearing(stereo, SR).events
              if e.event_type == "NEGATIVE_CORRELATION_REGION"]
    assert len(events) >= 1
    # Proxy semantics: confidence reported, never absolute phase failure.
    assert all(e.status in {"DETECTED", "ESTIMATOR_DERIVED"} for e in events)


def test_phase_risk_region_detected():
    mono = _sine(8.0)
    stereo = np.stack([mono, mono], axis=1)
    stereo[_time(3.0):_time(3.8)] = _as_stereo(mono[_time(3.0):_time(3.8)], invert=True)
    events = [e for e in run_temporal_hearing(stereo, SR).events
              if e.event_type == "PHASE_RISK_REGION"]
    assert len(events) >= 1


# ---------------------------------------------------------------------------
# G8 Spectral dropout (estimator-derived)
# ---------------------------------------------------------------------------

def test_hf_dropout_detected_as_estimator():
    broadband = _noise(8.0)
    band_limited = _lowpass(_noise(8.0, seed=8), 4000)
    x = broadband.copy()
    x[_time(2.0):_time(4.0)] = band_limited[_time(2.0):_time(4.0)]
    events = [e for e in _detect(x) if e.event_type == "HIGH_FREQUENCY_DROPOUT"]
    assert len(events) >= 1
    assert all(e.status == "ESTIMATOR_DERIVED" for e in events)
    assert all(e.confidence <= 0.6 for e in events)


# ---------------------------------------------------------------------------
# G9 Level events
# ---------------------------------------------------------------------------

def test_level_spike_detected():
    x = _sine(8.0, gain=0.05)
    x[_time(1.0):_time(1.4)] = _sine(0.4, gain=0.7)
    events = [e for e in _detect(x) if e.event_type == "LEVEL_SPIKE"]
    assert len(events) >= 1
    assert abs(events[0].start_ms / 1000 - 1.0) < 0.5  # bounded by level hop (100 ms)


def test_level_drop_detected():
    x = _sine(8.0, gain=0.7)
    x[_time(5.0):_time(5.6)] = _sine(0.6, gain=0.05)
    events = [e for e in _detect(x) if e.event_type == "LEVEL_DROP"]
    assert len(events) >= 1


# ---------------------------------------------------------------------------
# G10 Merge/debounce
# ---------------------------------------------------------------------------

def test_merge_joins_close_clusters():
    x = _sine(8.0)
    x[_time(2.0):_time(2.2)] = 1.0
    x[_time(2.25):_time(2.45)] = 1.0  # gap 50 ms < tolerance 150 ms
    events = [e for e in _detect(x) if e.event_type == "CLIPPING_CLUSTER"]
    assert len(events) == 1  # merged
    assert events[0].start_ms / 1000 < 2.1


def test_merge_keeps_distant_clusters_separate():
    x = _sine(8.0)
    x[_time(2.0):_time(2.2)] = 1.0
    x[_time(4.0):_time(4.2)] = 1.0
    events = [e for e in _detect(x) if e.event_type == "CLIPPING_CLUSTER"]
    assert len(events) == 2


# ---------------------------------------------------------------------------
# G11 False-positive safety
# ---------------------------------------------------------------------------

def test_clean_sine_no_false_positives():
    events = _detect(_sine(6.0))
    assert events == []


def test_clean_noise_no_false_positives():
    events = _detect(_noise(6.0))
    assert events == []


# ---------------------------------------------------------------------------
# G4 taxonomy integrity + forbidden labels
# ---------------------------------------------------------------------------

def test_events_use_only_approved_types():
    x = _sine(8.0)
    x[_time(2.0):_time(2.6)] = 1.0
    events = _detect(x)
    assert all(e.event_type in P0_EVENT_TYPES for e in events)
    assert not (P0_EVENT_TYPES & FORBIDDEN_LABELS)


# ---------------------------------------------------------------------------
# G3 reproducibility
# ---------------------------------------------------------------------------

def test_deterministic_same_input_same_events():
    x = _sine(8.0)
    x[_time(2.0):_time(2.6)] = 1.0
    first = [(e.event_type, e.start_ms, e.end_ms) for e in _detect(x)]
    second = [(e.event_type, e.start_ms, e.end_ms) for e in _detect(x)]
    assert first == second


# ---------------------------------------------------------------------------
# Evaluation metrics (07)
# ---------------------------------------------------------------------------

def test_evaluate_metrics_presence_and_iou():
    x = _sine(8.0)
    x[_time(2.0):_time(2.6)] = 1.0
    events = [e for e in _detect(x) if e.event_type == "CLIPPING_CLUSTER"]
    results = evaluate_events(events, [
        {"event_type": "CLIPPING_CLUSTER", "start_ms": 2000, "end_ms": 2600},
    ])
    clipping = results["CLIPPING_CLUSTER"]
    assert clipping["recall"] == 1.0
    assert clipping["false_positives"] == 0
    assert clipping["mean_iou"] >= 0.5
    assert clipping["start_error_ms"] is not None
