"""MAMSE-013 synthetic gates — ERB geometry + gammatone filterbank.

Chapter II §4: human-inspired channels are a parallel perceptual view,
never adopted by ideology. Gates verify ERB math, filter localization,
energy organization, silence honesty, invariance (§11), determinism and
serialization.
"""

from __future__ import annotations

import numpy as np
import pytest

from moodify_experimental.mamse013 import (
    DEFAULT_CONFIG,
    ERBConfig,
    build_er_b_sketch,
    compute_er_b_observation,
    erb_bandwidth_hz,
    erb_to_hz,
    geometry_evidence,
    hz_to_erb,
    load_case,
    save_case,
)

SR = 48000


def _sine(seconds: float, freq: float, gain: float = 0.3) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    return (gain * np.sin(2 * np.pi * freq * t)).astype(np.float32)


# ---------------------------------------------------------------------------
# A. ERB geometry gates
# ---------------------------------------------------------------------------

def test_erb_bandwidth_formula_at_1khz():
    # Glasberg & Moore: ERB(1000) = 24.7 * (4.37*1 + 1) ≈ 132.64 Hz
    assert erb_bandwidth_hz(1000.0) == pytest.approx(132.64, abs=0.05)


def test_erb_rate_round_trip():
    f = np.array([50.0, 250.0, 1000.0, 8000.0])
    assert np.allclose(erb_to_hz(hz_to_erb(f)), f, rtol=1e-9)


def test_center_frequencies_monotonic_and_in_range():
    cfg = ERBConfig()
    freqs = cfg.center_frequencies()
    assert len(freqs) == cfg.n_channels
    assert np.all(np.diff(freqs) > 0)
    assert freqs[0] == pytest.approx(cfg.fmin_hz, abs=1e-6)
    assert freqs[-1] <= cfg.fmax_hz
    # ~41 ERB steps between 20 Hz and 20 kHz at 1 channel/ERB
    assert 38 <= cfg.n_channels <= 45


def test_channel_spacing_grows_with_frequency():
    freqs = ERBConfig().center_frequencies()
    spacing = np.diff(freqs)
    assert spacing[0] < spacing[-1]
    assert spacing[0] == pytest.approx(erb_bandwidth_hz(freqs[0]) / DEFAULT_CONFIG.channels_per_erb,
                                       rel=0.15)


def test_geometry_evidence_contract():
    ev = geometry_evidence(DEFAULT_CONFIG, SR)
    assert ev["n_channels"] == DEFAULT_CONFIG.n_channels
    assert ev["erb_bandwidth_high_hz"] > ev["erb_bandwidth_lowest_hz"]
    assert ev["filter_gain"] == "unit_peak_normalized"


def test_config_hash_changes_with_geometry():
    assert ERBConfig().sha256() != ERBConfig(fmin_hz=50.0).sha256()
    assert ERBConfig().sha256() == ERBConfig().sha256()


# ---------------------------------------------------------------------------
# B. Filterbank organization gates
# ---------------------------------------------------------------------------

def test_sine_localizes_to_nearby_channel():
    obs = compute_er_b_observation(_sine(0.5, 440.0), SR)
    assert obs.status == "VALID"
    assert abs(obs.dominant_frequency_hz - 440.0) <= 40.0


def test_low_vs_high_frequency_separation():
    low = compute_er_b_observation(_sine(0.5, 100.0), SR)
    high = compute_er_b_observation(_sine(0.5, 5000.0), SR)
    assert low.dominant_frequency_hz < 200.0
    assert high.dominant_frequency_hz > 2000.0
    assert high.dominant_channel - low.dominant_channel > 10


def test_far_channels_carry_fraction_of_peak_energy():
    obs = compute_er_b_observation(_sine(0.5, 440.0), SR)
    peak = float(np.max(obs.mean_channel_power))
    k = obs.dominant_channel
    band = obs.center_frequencies_hz
    far = obs.mean_channel_power[(band < band[k] - 2 * erb_bandwidth_hz(band[k])) |
                                 (band > band[k] + 2 * erb_bandwidth_hz(band[k]))]
    assert float(np.max(far)) < 0.2 * peak


def test_silence_honesty():
    obs = compute_er_b_observation(np.zeros(int(0.5 * SR), dtype=np.float32), SR)
    assert obs.status == "EMPTY"
    assert float(np.sum(obs.mean_channel_power)) < 1e-9
    sketch = build_er_b_sketch(obs, DEFAULT_CONFIG)
    assert sketch.status == "EMPTY"


def test_gain_invariance_section_11():
    x = _sine(0.5, 440.0)
    a = build_er_b_sketch(compute_er_b_observation(x, SR), DEFAULT_CONFIG)
    b = build_er_b_sketch(compute_er_b_observation(2.0 * x, SR), DEFAULT_CONFIG)
    assert a.track_features["dominant_frequency_hz"] == b.track_features["dominant_frequency_hz"]
    assert a.track_features["erb_centroid"] == pytest.approx(b.track_features["erb_centroid"])
    assert a.track_features["peak_to_floor_ratio_db"] == pytest.approx(
        b.track_features["peak_to_floor_ratio_db"])


def test_deterministic_rerun():
    x = _sine(0.5, 330.0)
    a = build_er_b_sketch(compute_er_b_observation(x, SR), DEFAULT_CONFIG)
    b = build_er_b_sketch(compute_er_b_observation(x, SR), DEFAULT_CONFIG)
    assert np.array_equal(a.values, b.values)
    assert a.track_features == b.track_features


def test_sketch_shape_and_descriptor_authority():
    obs = compute_er_b_observation(_sine(0.5, 440.0), SR)
    sketch = build_er_b_sketch(obs, DEFAULT_CONFIG)
    n_frames = obs.channel_energies.shape[1]
    assert sketch.values.shape == (n_frames, 3)
    assert sketch.times_s.shape == (n_frames,)
    from moodify_experimental.mamse013 import FEATURE_AUTHORITY

    assert all(v.startswith("DESCRIPTOR") for v in FEATURE_AUTHORITY.values())


def test_mono_only_enforced():
    stereo = np.stack([_sine(0.3, 440.0), _sine(0.3, 440.0)], axis=1)
    with pytest.raises(ValueError):
        compute_er_b_observation(stereo, SR)


# ---------------------------------------------------------------------------
# C. Serialization gates
# ---------------------------------------------------------------------------

def test_save_load_round_trip(tmp_path):
    x = _sine(0.4, 220.0)
    obs = compute_er_b_observation(x, SR)
    sketch = build_er_b_sketch(obs, DEFAULT_CONFIG)
    paths = save_case(x, SR, DEFAULT_CONFIG, obs, sketch, tmp_path / "case")
    assert all(p.is_file() for p in paths.values())
    loaded = load_case(tmp_path / "case")
    assert loaded["manifest"]["operator_id"] == "MAMSE-013"
    assert loaded["manifest"]["geometry_id"].startswith("glasberg-moore-erb")
    assert loaded["manifest"]["feature_authority"]["erb_centroid"].startswith("DESCRIPTOR")
    assert np.allclose(loaded["times_s"], sketch.times_s)
    assert np.array_equal(loaded["values"], sketch.values)
    assert np.allclose(loaded["center_frequencies_hz"], obs.center_frequencies_hz)
    assert loaded["evidence"]["status"] == "VALID"
