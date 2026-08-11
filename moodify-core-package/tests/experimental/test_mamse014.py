"""MAMSE-014 synthetic gates — masking inference (Chapter II §9).

Masking inference is probabilistic: energy present does not mean
perceptually available, and the correct output for weak evidence is
insufficient evidence, not an alarm. Gates verify the spreading-model
direction, level dependence, silence honesty, gain invariance (§11),
event gating, determinism and serialization.
"""

from __future__ import annotations

import numpy as np
import pytest

from moodify_experimental.mamse014 import (
    DEFAULT_CONFIG,
    MaskConfig,
    build_masking_sketch,
    compute_masking_observation,
    geometry_evidence,
    load_case,
    save_case,
)

SR = 48000

MASKER_LOUD = 0.9   # ~ -5 dBFS
MASKER_QUIET = 0.05  # ~ -26 dBFS, 21 dB below loud
MASKEE_FREQ = 676.0  # ch12 center, ~3.1 ERB above the 440 Hz masker
MASKEE_GAIN = 0.001  # ~ -60 dBFS: in the loud masker's shadow


def _sine(seconds: float, freq: float, gain: float = 0.3) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    return (gain * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _mix(*signals: np.ndarray) -> np.ndarray:
    return np.sum(np.stack(signals), axis=0)


# ---------------------------------------------------------------------------
# A. Spreading-model direction gates
# ---------------------------------------------------------------------------

def test_near_maskee_masked_far_maskee_audible():
    near = compute_masking_observation(
        _mix(_sine(1.0, 440.0, MASKER_LOUD), _sine(1.0, MASKEE_FREQ, MASKEE_GAIN)), SR)
    far = compute_masking_observation(
        _mix(_sine(1.0, 440.0, MASKER_LOUD), _sine(1.0, 2500.0, MASKEE_GAIN)), SR)
    assert near.audibility_at(MASKEE_FREQ) < 0.2
    assert far.audibility_at(2500.0) > 0.9
    assert near.masked_channel_ratio_mean > far.masked_channel_ratio_mean


def test_louder_masker_masks_more():
    loud = compute_masking_observation(
        _mix(_sine(1.0, 440.0, MASKER_LOUD), _sine(1.0, MASKEE_FREQ, MASKEE_GAIN)), SR)
    quiet = compute_masking_observation(
        _mix(_sine(1.0, 440.0, MASKER_QUIET), _sine(1.0, MASKEE_FREQ, MASKEE_GAIN)), SR)
    assert loud.audibility_at(MASKEE_FREQ) < 0.2
    assert quiet.audibility_at(MASKEE_FREQ) > 0.8
    assert loud.masked_channel_ratio_mean > quiet.masked_channel_ratio_mean


def test_silence_honesty():
    obs = compute_masking_observation(np.zeros(int(0.5 * SR), dtype=np.float32), SR)
    assert obs.status == "EMPTY"
    assert obs.masked_channel_ratio_mean == pytest.approx(0.0, abs=1e-6)
    assert not obs.events
    sketch = build_masking_sketch(obs, DEFAULT_CONFIG)
    assert sketch.status == "EMPTY"


def test_gain_invariance_section_11():
    x = _mix(_sine(1.0, 440.0, MASKER_LOUD), _sine(1.0, MASKEE_FREQ, MASKEE_GAIN))
    a = compute_masking_observation(x, SR)
    b = compute_masking_observation(2.0 * x, SR)
    assert a.masked_channel_ratio_mean == pytest.approx(b.masked_channel_ratio_mean, abs=1e-6)
    assert a.depth_mean == pytest.approx(b.depth_mean, abs=1e-6)


def test_deterministic_rerun():
    x = _mix(_sine(1.0, 300.0, 0.9), _sine(1.0, 400.0, 0.03))
    a = build_masking_sketch(compute_masking_observation(x, SR), DEFAULT_CONFIG)
    b = build_masking_sketch(compute_masking_observation(x, SR), DEFAULT_CONFIG)
    assert np.array_equal(a.values, b.values)
    assert a.track_features == b.track_features


def test_config_hash_and_geometry():
    assert DEFAULT_CONFIG.sha256() != MaskConfig(slope_db_per_erb=30.0).sha256()
    assert DEFAULT_CONFIG.sha256() == DEFAULT_CONFIG.sha256()
    ev = geometry_evidence(DEFAULT_CONFIG, SR)
    assert ev["n_channels"] == DEFAULT_CONFIG.n_channels
    assert ev["slope_db_per_erb"] == DEFAULT_CONFIG.slope_db_per_erb


# ---------------------------------------------------------------------------
# B. Event gates
# ---------------------------------------------------------------------------

def _masking_cluster() -> np.ndarray:
    # Dense loud low cluster -> channels between/around tones collapse.
    return _mix(*[_sine(0.6, f, 0.9) for f in (200.0, 230.0, 260.0, 290.0, 320.0, 350.0)])


def test_strong_masking_region_event_fires_with_scale():
    obs = compute_masking_observation(_masking_cluster(), SR)
    assert obs.events, "expected at least one STRONG_MASKING_REGION"
    event = obs.events[0]
    assert event.event_type == "STRONG_MASKING_REGION"
    assert event.scale in {"PERCEPTUAL_FRAME", "SHORT_TERM", "MUSICAL_UNIT"}
    assert event.end_ms > event.start_ms
    assert event.peak_depth > 0.1


def test_short_blip_below_min_frames_no_event():
    config = MaskConfig(event_min_frames=50)
    blip = _mix(*[_sine(0.2, f, 0.9) for f in (200.0, 230.0, 260.0, 290.0, 320.0, 350.0)])
    obs = compute_masking_observation(blip, SR, config)
    assert not obs.events


# ---------------------------------------------------------------------------
# C. Boundaries + serialization
# ---------------------------------------------------------------------------

def test_mono_only_enforced():
    stereo = np.stack([_sine(0.3, 440.0), _sine(0.3, 440.0)], axis=1)
    with pytest.raises(ValueError):
        compute_masking_observation(stereo, SR)


def test_authority_all_estimator_or_descriptor():
    from moodify_experimental.mamse014 import FEATURE_AUTHORITY

    assert all(v.startswith(("ESTIMATOR", "DESCRIPTOR")) for v in FEATURE_AUTHORITY.values())


def test_save_load_round_trip(tmp_path):
    x = _masking_cluster()
    obs = compute_masking_observation(x, SR)
    sketch = build_masking_sketch(obs, DEFAULT_CONFIG)
    paths = save_case(x, SR, DEFAULT_CONFIG, obs, sketch, tmp_path / "case")
    assert all(p.is_file() for p in paths.values())
    loaded = load_case(tmp_path / "case")
    assert loaded["manifest"]["operator_id"] == "MAMSE-014"
    assert loaded["manifest"]["implementation"]["model"] == "spreading-masking-v0.1"
    assert loaded["manifest"]["feature_authority"]["masked_channel_ratio_mean"].startswith("ESTIMATOR")
    assert np.allclose(loaded["times_s"], sketch.times_s)
    assert np.array_equal(loaded["values"], sketch.values)
    assert np.allclose(loaded["masked_channel_ratio"], obs.masked_channel_ratio)
    assert loaded["evidence"]["status"] == "VALID"
