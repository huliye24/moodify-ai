"""MAMSE-015 synthetic gates — soft auditory objects (Chapter II §10).

Soft objects carry independent probability profiles over acoustic-role
hypotheses; probabilities are ESTIMATORs, never source identities.
Weak evidence yields UNRESOLVED, never a confident label. Gates verify
role separation, object extraction, weak-evidence honesty, gain
invariance (§11), determinism and serialization.
"""

from __future__ import annotations

import numpy as np
import pytest

from moodify_experimental.mamse015 import (
    DEFAULT_CONFIG,
    SoftObjectConfig,
    build_soft_object_sketch,
    compute_soft_object_observation,
    geometry_evidence,
    load_case,
    save_case,
)

SR = 48000


def _sine(seconds: float, freq: float = 440.0, gain: float = 0.3) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    return (gain * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _noise(seconds: float, gain: float = 0.2) -> np.ndarray:
    rng = np.random.default_rng(42)
    return (gain * rng.standard_normal(int(seconds * SR))).astype(np.float32)


def _clicks(seconds: float, rate_hz: float = 40.0, gain: float = 0.8) -> np.ndarray:
    x = np.zeros(int(seconds * SR), dtype=np.float32)
    period = int(SR / rate_hz)
    for start in range(0, len(x), period):
        end = min(start + int(0.004 * SR), len(x))
        x[start:end] = gain
    return x


def _mix(*signals: np.ndarray) -> np.ndarray:
    return np.sum(np.stack(signals), axis=0)


# ---------------------------------------------------------------------------
# A. Role separation gates
# ---------------------------------------------------------------------------

def test_sine_is_tonal_core():
    obs = compute_soft_object_observation(_sine(1.0), SR)
    tonal = [obj for obj in obs.objects if obj.label == "TONAL_CORE"]
    assert tonal, "expected a TONAL_CORE object"
    assert tonal[0].probabilities["TONAL_CORE"] > 0.7
    assert obs.frame_probabilities[obs.frame_labels == 0][:, 0].mean() > 0.7


def test_noise_is_texture():
    obs = compute_soft_object_observation(_noise(1.0), SR)
    texture = [obj for obj in obs.objects if obj.label == "NOISE_TEXTURE"]
    assert texture, "expected a NOISE_TEXTURE object"
    assert texture[0].probabilities["NOISE_TEXTURE"] > 0.7


def test_click_train_is_percussive():
    obs = compute_soft_object_observation(_clicks(1.0), SR)
    percussive = [obj for obj in obs.objects if obj.label == "PERCUSSIVE"]
    assert percussive, "expected a PERCUSSIVE object"


def test_probabilities_are_independent_indicators():
    obs = compute_soft_object_observation(_sine(1.0), SR)
    tonal = [obj for obj in obs.objects if obj.label == "TONAL_CORE"][0]
    # Chapter style: "0.86 likely vocal AND 0.44 likely texture" — the
    # indicators are independent; the vector need not sum to one.
    assert 0.0 <= tonal.probabilities["TONAL_CORE"] <= 1.0
    assert 0.0 <= tonal.probabilities["NOISE_TEXTURE"] <= 1.0
    assert 0.0 <= tonal.probabilities["UNRESOLVED"] <= 1.0


# ---------------------------------------------------------------------------
# B. Temporal organization gates
# ---------------------------------------------------------------------------

def test_two_regions_produce_ordered_objects():
    signal = np.concatenate([_sine(0.5), np.zeros(int(0.05 * SR)), _noise(0.45)])
    obs = compute_soft_object_observation(signal, SR)
    labels = [obj.label for obj in obs.objects if obj.label != "UNRESOLVED"]
    assert labels
    assert labels[0] == "TONAL_CORE"
    assert any(label == "NOISE_TEXTURE" for label in labels)


def test_weak_evidence_is_unresolved_not_labeled():
    weak = np.concatenate([_sine(0.5), np.zeros(int(0.5 * SR))])
    obs = compute_soft_object_observation(weak, SR)
    assert obs.unresolved_fraction > 0.2
    assert not any(obj.label in {"TONAL_CORE", "NOISE_TEXTURE", "PERCUSSIVE"}
                   and obj.start_ms > 600 for obj in obs.objects)


def test_silence_honesty():
    obs = compute_soft_object_observation(np.zeros(int(0.5 * SR), dtype=np.float32), SR)
    assert obs.status == "EMPTY"
    assert not obs.objects
    assert obs.unresolved_fraction == pytest.approx(1.0)
    sketch = build_soft_object_sketch(obs, DEFAULT_CONFIG)
    assert sketch.status == "EMPTY"


def test_short_blip_below_min_frames_no_object():
    config = SoftObjectConfig(min_region_frames=30)
    blip = np.concatenate([np.zeros(int(0.2 * SR)), _sine(0.15), np.zeros(int(0.2 * SR))])
    obs = compute_soft_object_observation(blip, SR, config)
    assert not obs.objects


# ---------------------------------------------------------------------------
# C. Invariance + boundaries
# ---------------------------------------------------------------------------

def test_gain_invariance_section_11():
    x = _mix(_sine(0.5, 440.0, 0.3), _noise(0.5, 0.1))
    a = compute_soft_object_observation(x, SR)
    b = compute_soft_object_observation(2.0 * x, SR)
    assert np.array_equal(a.frame_labels, b.frame_labels)
    assert np.allclose(a.frame_probabilities, b.frame_probabilities, atol=1e-6)
    assert [(o.label, o.start_ms, o.end_ms) for o in a.objects] == \
        [(o.label, o.start_ms, o.end_ms) for o in b.objects]


def test_deterministic_rerun():
    x = _mix(_sine(0.5, 440.0, 0.3), _noise(0.5, 0.1))
    a = build_soft_object_sketch(compute_soft_object_observation(x, SR), DEFAULT_CONFIG)
    b = build_soft_object_sketch(compute_soft_object_observation(x, SR), DEFAULT_CONFIG)
    assert np.array_equal(a.values, b.values)
    assert a.track_features == b.track_features


def test_config_hash_and_geometry():
    assert DEFAULT_CONFIG.sha256() != SoftObjectConfig(label_confidence_gate=0.7).sha256()
    assert DEFAULT_CONFIG.sha256() == DEFAULT_CONFIG.sha256()
    ev = geometry_evidence(DEFAULT_CONFIG, SR)
    assert ev["hypotheses"] == ["TONAL_CORE", "NOISE_TEXTURE", "PERCUSSIVE", "UNRESOLVED"]


def test_mono_only_enforced():
    stereo = np.stack([_sine(0.3), _sine(0.3)], axis=1)
    with pytest.raises(ValueError):
        compute_soft_object_observation(stereo, SR)


def test_authority_all_estimator_or_descriptor():
    from moodify_experimental.mamse015 import FEATURE_AUTHORITY

    assert all(v.startswith(("ESTIMATOR", "DESCRIPTOR")) for v in FEATURE_AUTHORITY.values())


def test_save_load_round_trip(tmp_path):
    x = _mix(_sine(0.5, 440.0, 0.3), _noise(0.5, 0.1))
    obs = compute_soft_object_observation(x, SR)
    sketch = build_soft_object_sketch(obs, DEFAULT_CONFIG)
    paths = save_case(x, SR, DEFAULT_CONFIG, obs, sketch, tmp_path / "case")
    assert all(p.is_file() for p in paths.values())
    loaded = load_case(tmp_path / "case")
    assert loaded["manifest"]["operator_id"] == "MAMSE-015"
    assert loaded["manifest"]["implementation"]["model"] == "soft-role-cues-v0.1"
    assert np.allclose(loaded["times_s"], sketch.times_s)
    assert np.array_equal(loaded["values"], sketch.values)
    assert np.allclose(loaded["frame_probabilities"], obs.frame_probabilities)
    assert loaded["evidence"]["status"] == "VALID"
