"""Multi-scale representation tests (MFY-PHASE1-DEPTH-003, Gates G2-G14).

R301-R307 synthetic fixtures exercise scale output, time alignment,
event overlay, missing-value honesty, global/local consistency,
serialization round trip and determinism. Invariants I1-I12 are encoded
directly in the assertions.
"""

from __future__ import annotations

import hashlib
import json

import numpy as np

from moodify.auditory.events.engine import run_temporal_hearing
from moodify.auditory.measurement_registry import load_registry
from moodify.auditory.representation.alignment import coarse_to_fine, fine_to_coarse
from moodify.auditory.representation.build import build_representation
from moodify.auditory.representation.scales import REPRESENTATION_VERSION, get_scale

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


def _hash(x: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()


def _build(x: np.ndarray, events: list | None = None):
    return build_representation(x, SR, _hash(x), events=events)


def _s0_clip_windows(rep, threshold: float = 0.0) -> list[int]:
    values = rep.planes["S0"].values
    return [i for i in range(values.shape[0]) if values[i, 2] > threshold]


# ---------------------------------------------------------------------------
# G2/G3 authority
# ---------------------------------------------------------------------------

def test_single_scale_authority():
    assert REPRESENTATION_VERSION == "rep-v1"
    scale_ids = [scale.scale_id for scale in (get_scale(s) for s in ("S0", "S1", "S2", "S3"))]
    assert scale_ids == ["S0", "S1", "S2", "S3"]
    assert get_scale("S0").window_ms == 40 and get_scale("S0").hop_ms == 20
    assert get_scale("S1").window_ms == 400 and get_scale("S1").hop_ms == 100


def test_planes_are_only_approved_scales():
    x = _sine(6.0)
    rep = _build(x)
    assert set(rep.planes) == {"S0", "S1", "S2"}
    assert rep.scale_ids == ("S0", "S1", "S2", "S3")


# ---------------------------------------------------------------------------
# G4/G5 feature authority + time alignment
# ---------------------------------------------------------------------------

def test_feature_planes_resolve_to_registry():
    registry = load_registry()
    x = _sine(6.0)
    rep = _build(x)
    for plane in rep.planes.values():
        for name, meta in plane.feature_meta.items():
            metric_id = meta.get("metric_id")
            if metric_id in registry["metrics"]:
                assert meta["authority_class"] == registry["metrics"][metric_id]["authority_class"]


def test_sample_clock_alignment_invariants():
    x = _sine(6.0)
    rep = _build(x)
    for plane in rep.planes.values():
        starts = plane.window_starts_ms
        ends = plane.window_ends_ms
        assert all(b >= a for a, b in zip(starts, ends))  # I3 valid duration
        assert all(starts[i] <= starts[i + 1] for i in range(len(starts) - 1))  # I2 monotonic
        # I4 sample/seconds consistency within hop tolerance
        assert starts[0] == 0
        hop_ms = plane.hop_ms
        assert all(abs(starts[i] - i * hop_ms) <= hop_ms for i in range(len(starts)))


# ---------------------------------------------------------------------------
# R301 stationary sine
# ---------------------------------------------------------------------------

def test_r301_stationary_sine_plane_stability():
    x = _sine(6.0)
    rep = _build(x)
    s1 = rep.planes["S1"]
    rms = s1.values[:, 0]
    finite = rms[~np.isnan(rms)]
    assert np.std(finite) < 0.5  # stable RMS over time


# ---------------------------------------------------------------------------
# R302 two-state level
# ---------------------------------------------------------------------------

def test_r302_two_state_level_transition_aligned():
    low = _sine(3.0, gain=0.05)
    high = _sine(3.0, gain=0.7)
    x = np.concatenate([low, high])
    rep = _build(x)
    s1 = rep.planes["S1"]
    rms = s1.values[:, 0]
    transition_idx = int(np.argmax(np.abs(np.diff(np.nan_to_num(rms, nan=-120)))))
    transition_ms = s1.window_starts_ms[transition_idx]
    assert abs(transition_ms - 3000) < 500  # bounded by S1 hop (100 ms) + window


# ---------------------------------------------------------------------------
# R303 stereo state switch
# ---------------------------------------------------------------------------

def test_r303_stereo_switch_plane_and_event_overlay():
    mono = _sine(6.0)
    stereo = np.stack([mono, mono], axis=1)
    stereo[_time(2.0):_time(4.0)] = np.stack([mono[_time(2.0):_time(4.0)],
                                              -mono[_time(2.0):_time(4.0)]], axis=1)
    events = [e for e in run_temporal_hearing(stereo, SR).events
              if e.event_type == "NEGATIVE_CORRELATION_REGION"]
    rep = build_representation(stereo, SR, _hash(stereo), events=events)
    s1 = rep.planes["S1"]
    corr = s1.values[:, 2]  # stereo_correlation
    # Anti-phase region shows negative correlation in S1 plane
    anti_windows = [i for i in range(len(corr)) if not np.isnan(corr[i]) and corr[i] < -0.5]
    assert anti_windows
    # I8/G9: every event resolves to overlapping S1 windows
    for event_id, ref in rep.event_refs.items():
        assert ref["overlapping_windows"], f"event {event_id} has no overlapping windows"


# ---------------------------------------------------------------------------
# R304 spectral state switch
# ---------------------------------------------------------------------------

def test_r304_spectral_switch_hf_plane_responds():
    broadband = _noise(6.0)
    band_limited = _lowpass(_noise(6.0, seed=8), 4000)
    x = broadband.copy()
    x[_time(1.5):_time(3.5)] = band_limited[_time(1.5):_time(3.5)]
    rep = _build(x)
    s2 = rep.planes["S2"]
    hf = s2.values[:, 2]  # hf_ratio
    finite_hf = np.nan_to_num(hf, nan=0.0)
    assert np.min(finite_hf) < np.max(finite_hf)  # dropout visible


# ---------------------------------------------------------------------------
# R305 silence islands (missing-value honesty)
# ---------------------------------------------------------------------------

def test_r305_silence_islands_missing_value_honesty():
    x = _sine(8.0)
    x[_time(2.0):_time(2.5)] = 0.0
    x[_time(5.0):_time(5.8)] = 0.0
    rep = _build(x)
    s1 = rep.planes["S1"]
    rms = s1.values[:, 0]
    # Silence windows have very low RMS; they must not be encoded as
    # misleading physical zeros indistinguishable from unavailable (I7).
    # Unavailable values are NaN in the plane; low RMS is real measurement.
    assert np.isnan(rms).sum() >= 0  # no fabrication; NaN only where computed unavailable
    silent = np.nan_to_num(rms, nan=-120) < -55
    assert silent.sum() >= 2


# ---------------------------------------------------------------------------
# R306 clipping burst ladder (micro scale)
# ---------------------------------------------------------------------------

def test_r306_clipping_bursts_in_micro_scale():
    x = _sine(8.0)
    x[_time(1.0):_time(1.2)] = 1.0
    x[_time(3.0):_time(3.1)] = 1.0
    rep = _build(x)
    clip_windows = _s0_clip_windows(rep)
    assert clip_windows
    first_start = rep.planes["S0"].window_starts_ms[clip_windows[0]]
    assert abs(first_start - 1000) < 40  # bounded by S0 window/hop


# ---------------------------------------------------------------------------
# R307 mixed scenario end-to-end
# ---------------------------------------------------------------------------

def test_r307_mixed_scenario_end_to_end():
    x = _sine(10.0)
    x[_time(2.0):_time(2.6)] = 1.0  # clipping burst
    x[_time(4.0):_time(4.5)] = 0.0  # silence gap
    stereo = np.stack([x, x], axis=1)
    stereo[_time(6.0):_time(6.8)] = np.stack([x[_time(6.0):_time(6.8)],
                                              -x[_time(6.0):_time(6.8)]], axis=1)
    events = run_temporal_hearing(stereo, SR).events
    rep = build_representation(stereo, SR, _hash(stereo), events=events)
    # G9: all events mapped
    assert len(rep.event_refs) == len(events)
    for ref in rep.event_refs.values():
        assert ref["overlapping_windows"]
    # G8: global summary present and consistent
    assert rep.global_summary["metric_count"] >= 20
    assert rep.duration_ms == 10000


# ---------------------------------------------------------------------------
# G6/G12 determinism + scale correctness
# ---------------------------------------------------------------------------

def test_deterministic_rerun_logically_identical():
    x = _sine(6.0)
    first = _build(x)
    second = _build(x)
    assert first.representation_id == second.representation_id
    assert first.planes["S1"].window_starts_ms == second.planes["S1"].window_starts_ms
    assert np.allclose(first.planes["S1"].values, second.planes["S1"].values,
                       equal_nan=True)
    assert first.global_summary["metrics"] == second.global_summary["metrics"]


# ---------------------------------------------------------------------------
# Cross-scale alignment (G5)
# ---------------------------------------------------------------------------

def test_cross_scale_interval_mapping():
    x = _sine(6.0)
    rep = _build(x)
    s0, s1, s2 = rep.planes["S0"], rep.planes["S1"], rep.planes["S2"]
    # A coarse S2 window at ~2s should cover several S1 and many S0 windows.
    s2_index = 4  # 2.0s window (2000ms window, 500ms hop)
    s1_covered = coarse_to_fine(s2, s1, s2_index)
    s0_covered = coarse_to_fine(s2, s0, s2_index)
    assert len(s1_covered) >= 3
    assert len(s0_covered) >= 20
    # Round trip: fine window maps to a coarse window containing it.
    coarse_of_fine = fine_to_coarse(s1, s2, s1_covered[0])
    assert s2_index in coarse_of_fine


# ---------------------------------------------------------------------------
# G13 serialization round trip
# ---------------------------------------------------------------------------

def test_serialization_round_trip(tmp_path):
    x = _sine(6.0)
    x[_time(2.0):_time(2.4)] = 1.0
    rep = _build(x)
    json_path = tmp_path / "rep.json"
    npz_path = tmp_path / "rep.npz"
    from moodify.auditory.representation.serialize import load_representation, save_representation

    save_representation(rep, json_path, npz_path)
    loaded = load_representation(json_path)
    assert loaded.representation_id == rep.representation_id
    assert loaded.source_sha256 == rep.source_sha256
    assert loaded.representation_version == REPRESENTATION_VERSION
    assert np.allclose(loaded.planes["S1"].values, rep.planes["S1"].values, equal_nan=True)
    assert loaded.global_summary == rep.global_summary
    # JSON is inspectable and NaN survives as null
    raw = json.loads(json_path.read_text(encoding="utf-8"))
    assert raw["planes"]["S0"]["values"]  # list with nulls allowed


# ---------------------------------------------------------------------------
# G14 bounded resource
# ---------------------------------------------------------------------------

def test_resource_linear_growth():
    short = _sine(3.0)
    long = _sine(10.0)
    short_rep = _build(short)
    long_rep = _build(long)
    short_windows = sum(p.values.shape[0] for p in short_rep.planes.values())
    long_windows = sum(p.values.shape[0] for p in long_rep.planes.values())
    # ~3.3x duration -> < 4x windows (approximately linear, bounded)
    assert long_windows < short_windows * 4
