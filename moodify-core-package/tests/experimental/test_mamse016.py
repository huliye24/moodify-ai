"""MAMSE-016 synthetic gates — pitch / harmonicity evidence (Chapter II §10A).

Pitch is never a binary fact: candidates carry confidence, voicing and
harmonic evidence; polyphonic mixtures may legitimately carry several
concurrent candidates. Gates verify F0 localization, harmonic support,
multi-candidate honesty, silence, gain invariance (§11), determinism,
pitch-run events and serialization.
"""

from __future__ import annotations

import numpy as np
import pytest

from moodify_experimental.mamse016 import (
    DEFAULT_CONFIG,
    PitchConfig,
    build_pitch_sketch,
    compute_pitch_observation,
    geometry_evidence,
    load_case,
    save_case,
)

SR = 48000


def _sine(seconds: float, freq: float, gain: float = 0.3) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    return (gain * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _harmonics(seconds: float, f0: float = 220.0, gain: float = 0.25) -> np.ndarray:
    return sum(_sine(seconds, f0 * k, gain / k) for k in (1, 3, 5)).astype(np.float32)


def _mix(*signals: np.ndarray) -> np.ndarray:
    return np.sum(np.stack(signals), axis=0)


# ---------------------------------------------------------------------------
# A. F0 localization gates
# ---------------------------------------------------------------------------

def test_sine_f0_localized():
    obs = compute_pitch_observation(_sine(1.0, 440.0), SR)
    assert obs.voicing_fraction > 0.7
    voiced = obs.dominant_f0[obs.voiced]
    assert np.nanmedian(voiced) == pytest.approx(440.0, rel=0.03)


def test_harmonic_tone_has_support():
    obs = compute_pitch_observation(_harmonics(1.0, 220.0), SR)
    assert obs.harmonic_consistency_mean > 0.3
    voiced = obs.dominant_f0[obs.voiced]
    assert np.nanmedian(voiced) == pytest.approx(220.0, rel=0.03)


def test_pure_sine_has_low_harmonic_support():
    obs = compute_pitch_observation(_sine(1.0, 440.0), SR)
    assert obs.harmonic_consistency_mean < 0.3


def test_multiple_candidates_in_polyphony():
    # Two pitch structures over time (220 then 330): both are legitimate
    # candidates, never a single binary F0 claim.
    signal = np.concatenate([_sine(0.5, 220.0), _sine(0.5, 330.0)])
    obs = compute_pitch_observation(signal, SR)
    voiced = obs.dominant_f0[obs.voiced]
    assert voiced.size > 0
    low = voiced[voiced < 280.0]
    high = voiced[voiced >= 280.0]
    assert np.nanmedian(low) == pytest.approx(220.0, rel=0.03)
    assert np.nanmedian(high) == pytest.approx(330.0, rel=0.03)


def test_candidates_carry_confidence_and_support():
    obs = compute_pitch_observation(_harmonics(1.0, 220.0), SR)
    frame = next((c for c in obs.candidates if c), None)
    assert frame is not None
    for cand in frame:
        assert 0.0 < cand.confidence <= 1.0
        assert 0.0 <= cand.harmonic_support <= 1.0


def test_silence_honesty():
    obs = compute_pitch_observation(np.zeros(int(0.5 * SR), dtype=np.float32), SR)
    assert obs.status == "EMPTY"
    assert obs.voicing_fraction == 0.0
    assert not obs.events
    sketch = build_pitch_sketch(obs, DEFAULT_CONFIG)
    assert sketch.status == "EMPTY"


# ---------------------------------------------------------------------------
# B. Pitch-run events
# ---------------------------------------------------------------------------

def test_stable_pitch_run_event_with_scale():
    obs = compute_pitch_observation(_sine(1.0, 440.0), SR)
    runs = [e for e in obs.events if e.event_type == "STABLE_PITCH_RUN"]
    assert runs
    run = runs[0]
    assert run.frequency_hz == pytest.approx(440.0, rel=0.03)
    assert run.scale in {"PERCEPTUAL_FRAME", "SHORT_TERM", "MUSICAL_UNIT"}
    assert run.end_ms > run.start_ms


def test_short_blip_below_min_frames_no_run():
    config = PitchConfig(event_min_frames=30)
    blip = np.concatenate([np.zeros(int(0.2 * SR)), _sine(0.15, 440.0), np.zeros(int(0.2 * SR))])
    obs = compute_pitch_observation(blip, SR, config)
    assert not obs.events


# ---------------------------------------------------------------------------
# C. Invariance + boundaries
# ---------------------------------------------------------------------------

def test_gain_invariance_section_11():
    x = _mix(_sine(1.0, 440.0), _sine(1.0, 660.0))
    a = compute_pitch_observation(x, SR)
    b = compute_pitch_observation(2.0 * x, SR)
    assert np.array_equal(a.voiced, b.voiced)
    assert np.allclose(a.dominant_f0, b.dominant_f0, equal_nan=True)
    assert a.voicing_fraction == pytest.approx(b.voicing_fraction, abs=1e-9)


def test_deterministic_rerun():
    x = _mix(_sine(1.0, 440.0), _sine(1.0, 660.0))
    a = build_pitch_sketch(compute_pitch_observation(x, SR), DEFAULT_CONFIG)
    b = build_pitch_sketch(compute_pitch_observation(x, SR), DEFAULT_CONFIG)
    assert np.array_equal(a.values, b.values)
    assert a.track_features == b.track_features


def test_config_hash_and_geometry():
    assert DEFAULT_CONFIG.sha256() != PitchConfig(fmin_hz=80.0).sha256()
    assert DEFAULT_CONFIG.sha256() == DEFAULT_CONFIG.sha256()
    ev = geometry_evidence(DEFAULT_CONFIG, SR)
    assert ev["max_candidates"] == DEFAULT_CONFIG.max_candidates
    assert ev["lag_range_samples"][0] >= 1


def test_mono_only_enforced():
    stereo = np.stack([_sine(0.3, 440.0), _sine(0.3, 440.0)], axis=1)
    with pytest.raises(ValueError):
        compute_pitch_observation(stereo, SR)


def test_authority_all_estimator_or_descriptor():
    from moodify_experimental.mamse016 import FEATURE_AUTHORITY

    assert all(v.startswith(("ESTIMATOR", "DESCRIPTOR")) for v in FEATURE_AUTHORITY.values())


def test_save_load_round_trip(tmp_path):
    x = _harmonics(1.0, 220.0)
    obs = compute_pitch_observation(x, SR)
    sketch = build_pitch_sketch(obs, DEFAULT_CONFIG)
    paths = save_case(x, SR, DEFAULT_CONFIG, obs, sketch, tmp_path / "case")
    assert all(p.is_file() for p in paths.values())
    loaded = load_case(tmp_path / "case")
    assert loaded["manifest"]["operator_id"] == "MAMSE-016"
    assert loaded["manifest"]["implementation"]["model"] == "multi-candidate-f0-v0.1"
    assert loaded["manifest"]["feature_authority"]["dominant_frequency_hz"].startswith("ESTIMATOR")
    assert np.allclose(loaded["times_s"], sketch.times_s)
    assert np.array_equal(loaded["values"], sketch.values)
    assert np.array_equal(loaded["voiced"], obs.voiced)
    assert loaded["evidence"]["status"] == "VALID"
