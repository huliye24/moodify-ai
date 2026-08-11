"""MAMSE-002 synthetic gates (T5) — 10 required + extras.

Frequency-grid constant ratio, octave/semitone bin spacing, window support
decrease, A4 localization (<= 35 cents), A3->A4 shift (24 bins), A1+A#1
close pair, silence honesty, deterministic rerun, serialization round trip,
plus tuning-offset ladder and low-register pair resolution.
"""

from __future__ import annotations

import numpy as np
import pytest

from moodify_experimental.mamse002 import (
    DEFAULT_CONFIG,
    build_log_frequency_sketch,
    compute_cqt_observation,
    dominant_frequency_from_mean,
    hz_to_midi,
    load_case,
    local_peaks_from_mean,
    save_case,
)

SR = 48000


def _sine(seconds: float, freq: float, gain: float = 0.3) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    return (gain * np.sin(2 * np.pi * freq * t)).astype(np.float32)


# ---------------------------------------------------------------------------
# A. Mathematical gates
# ---------------------------------------------------------------------------

def test_frequency_grid_constant_ratio():
    freqs = DEFAULT_CONFIG.frequencies()
    ratios = freqs[1:] / freqs[:-1]
    expected = 2 ** (1 / DEFAULT_CONFIG.bins_per_octave)
    assert np.allclose(ratios, expected, rtol=1e-9)


def test_octave_and_semitone_spacing():
    cfg = DEFAULT_CONFIG
    assert cfg.bins_per_octave == 24
    freqs = cfg.frequencies()
    octave_up = np.argmin(np.abs(freqs - 2 * cfg.fmin_hz))
    assert octave_up == 24
    semitone_up = np.argmin(np.abs(freqs - cfg.fmin_hz * 2 ** (1 / 12)))
    assert semitone_up == 2


def test_nominal_window_support_decreases_with_frequency():
    windows = DEFAULT_CONFIG.nominal_window_samples(SR)
    assert windows[0] > windows[-1]
    a4_idx = int(np.argmin(np.abs(DEFAULT_CONFIG.frequencies() - 440.0)))
    assert windows[0] > windows[a4_idx] > windows[-1]


# ---------------------------------------------------------------------------
# B. Synthetic gates
# ---------------------------------------------------------------------------

def test_a4_440hz_localization_within_35_cents():
    x = _sine(2.0, 440.0)
    obs = compute_cqt_observation(x, SR)
    assert obs.status == "OK"
    dom = dominant_frequency_from_mean(obs)
    assert dom is not None
    cents_err = abs(100 * (hz_to_midi(dom) - 69.0))
    assert cents_err <= 35.0


def test_a3_to_a4_octave_shift_24_bins():
    a3 = _sine(2.0, 220.0)
    a4 = _sine(2.0, 440.0)
    obs3 = compute_cqt_observation(a3, SR)
    obs4 = compute_cqt_observation(a4, SR)
    peaks3 = local_peaks_from_mean(obs3)
    peaks4 = local_peaks_from_mean(obs4)
    assert peaks3 and peaks4
    assert peaks4[0][0] - peaks3[0][0] == pytest.approx(24, abs=2)


def test_440_to_a_sharp_4_shift_2_bins():
    a4 = _sine(2.0, 440.0)
    ash4 = _sine(2.0, 466.1637615180899)
    obs_a = compute_cqt_observation(a4, SR)
    obs_ash = compute_cqt_observation(ash4, SR)
    p_a = local_peaks_from_mean(obs_a)[0]
    p_ash = local_peaks_from_mean(obs_ash)[0]
    assert p_ash[0] - p_a[0] == pytest.approx(2, abs=1)


def test_a1_a_sharp1_low_register_pair():
    a1 = _sine(3.0, 55.0)
    ash1 = _sine(3.0, 58.27047018976124)
    x = a1 + ash1
    obs = compute_cqt_observation(x, SR)
    peaks = local_peaks_from_mean(obs, min_relative=0.05)
    freqs = sorted(p[1] for p in peaks[:4])
    near_a1 = [f for f in freqs if 50.0 <= f <= 62.0]
    assert len(near_a1) >= 2, f"expected two low peaks near 55/58.3 Hz, got {freqs}"


def test_silence_honesty():
    x = np.zeros(int(2 * SR), dtype=np.float32)
    obs = compute_cqt_observation(x, SR)
    assert obs.status == "SILENCE"
    assert dominant_frequency_from_mean(obs) is None
    sketch = build_log_frequency_sketch(obs)
    assert sketch.status == "SILENCE"
    assert np.all(np.isnan(sketch.values))


def test_deterministic_rerun():
    x = _sine(2.0, 440.0) + 0.2 * _sine(2.0, 554.3652619543977)
    o1 = compute_cqt_observation(x, SR)
    o2 = compute_cqt_observation(x, SR)
    assert np.array_equal(o1.power, o2.power)
    assert DEFAULT_CONFIG.sha256() == DEFAULT_CONFIG.sha256()


def test_serialization_round_trip(tmp_path):
    x = _sine(2.0, 220.0) + 0.3 * _sine(2.0, 440.0)
    obs = compute_cqt_observation(x, SR)
    sketch = build_log_frequency_sketch(obs)
    paths = save_case(x, SR, DEFAULT_CONFIG, obs, sketch, tmp_path)
    assert paths["manifest"].exists() and paths["npz"].exists() and paths["evidence"].exists()

    loaded = load_case(paths["manifest"], paths["npz"])
    assert loaded["manifest"]["operator_id"] == "MAMSE-002"
    assert loaded["manifest"]["geometry_id"] == DEFAULT_CONFIG.geometry_id
    assert loaded["manifest"]["config_sha256"] == DEFAULT_CONFIG.sha256()
    assert loaded["manifest"]["runtime"]["librosa"]  # version recorded
    assert np.array_equal(loaded["values"], sketch.values)
    assert np.array_equal(loaded["times_s"], sketch.times_s)


def test_tuning_offset_ladder_consistent():
    # a 440 Hz tone with +10 cents offset must estimate closer to +10 than -10
    x_plus = _sine(3.0, 440.0 * 2 ** (10 / 1200))
    obs = compute_cqt_observation(x_plus, SR)
    sketch = build_log_frequency_sketch(obs)
    cents_col = sketch.values[:, sketch.feature_names.index("tuning_deviation_cents")]
    median_cents = float(np.nanmedian(cents_col))
    assert abs(median_cents - 10.0) < abs(median_cents + 10.0)


def test_low_register_resolution_beats_linear_bin():
    # 55.0 vs 58.27 Hz: linear 512-bin STFT at 48k has 93.75 Hz bins and
    # cannot separate them; CQT geometry must show two distinct peaks.
    a1 = _sine(3.0, 55.0)
    ash1 = _sine(3.0, 58.27047018976124)
    x = a1 + ash1
    obs = compute_cqt_observation(x, SR)
    peaks = local_peaks_from_mean(obs, min_relative=0.05)
    freqs = [p[1] for p in peaks[:4]]
    assert any(50.0 <= f <= 56.5 for f in freqs)
    assert any(56.5 < f <= 62.0 for f in freqs)
