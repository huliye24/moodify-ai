"""Primitive contract + counterfactual tests (MFY_PRESERVE_IDENTITY_INTERVENTION_001)."""

from __future__ import annotations

import numpy as np
import pytest

from moodify.intervention.primitives import (
    PRIMITIVES,
    apply_clip_peak_repair,
    apply_dc_offset_fix,
    apply_tonal_balance_conservative,
    detect_clip_segments,
    detect_dc_offset,
    detect_tonal_imbalance,
)

SR = 44100


@pytest.fixture
def clean_audio():
    """Well-balanced mix: low (60 Hz), mid (440/3000 Hz) and high (12 kHz) content."""
    t = np.arange(SR) / SR
    return (
        0.2 * np.sin(2 * np.pi * 60 * t)
        + 0.3 * np.sin(2 * np.pi * 440 * t)
        + 0.2 * np.sin(2 * np.pi * 3000 * t)
        + 0.1 * np.sin(2 * np.pi * 12000 * t)
    ).astype(np.float32)


def test_registry_contracts_complete():
    assert len(PRIMITIVES) == 3
    for pid, p in PRIMITIVES.items():
        c = p.contract
        assert c.scope, f"{pid} scope missing"
        assert c.max_strength, f"{pid} max_strength missing"
        assert c.identity_risk in ("NONE", "LOW", "MEDIUM"), f"{pid} risk"
        assert c.failure_state, f"{pid} failure_state missing"
        assert c.identity_risk != "NONE" or True  # NONE allowed


def test_dc_detect_and_fix_counterfactual(clean_audio):
    dc_audio = clean_audio + 0.05
    m = detect_dc_offset(dc_audio, SR)
    assert m["active"] == 1.0
    assert abs(m["dc"] - 0.05) < 1e-6

    fixed = apply_dc_offset_fix(dc_audio, SR, {})
    m2 = detect_dc_offset(fixed, SR)
    assert m2["active"] == 0.0
    assert abs(m2["dc"]) < 1e-5
    # identity-safe: only constant offset changed
    assert np.max(np.abs((fixed - clean_audio))) < 1e-4


def test_dc_does_not_fire_on_clean(clean_audio):
    assert detect_dc_offset(clean_audio, SR)["active"] == 0.0


def test_clip_detect_and_repair_counterfactual(clean_audio):
    clipped = clean_audio.copy()
    clipped[1000:1010] = 1.0  # 10-sample flat clip
    m = detect_clip_segments(clipped, SR)
    assert m["active"] == 1.0
    assert m["clip_segments"] == 1.0
    assert m["clip_repairable"] == 1.0

    repaired = apply_clip_peak_repair(clipped, SR, {})
    assert float(np.abs(repaired).max()) < 0.999
    assert detect_clip_segments(repaired, SR)["clip_segments"] == 0.0
    # untouched elsewhere
    assert np.array_equal(repaired[:995], clipped[:995])
    assert np.array_equal(repaired[1015:], clipped[1015:])


def test_clip_long_segment_reported_not_repaired(clean_audio):
    clipped = clean_audio.copy()
    clipped[1000:1030] = -1.0  # 30 samples > max repair 16
    m = detect_clip_segments(clipped, SR)
    assert m["clip_repairable"] == 0.0
    assert m["clip_longest_segment"] == 30.0
    repaired = apply_clip_peak_repair(clipped, SR, {})
    assert np.array_equal(repaired, clipped)  # untouched


def test_tonal_imbalance_detect_and_cap(clean_audio):
    # build a low-band-deficient signal (highpass) -> detector fires
    from scipy.signal import butter, sosfilt

    sos = butter(4, 150, btype="highpass", fs=SR, output="sos")
    hp = sosfilt(sos, clean_audio).astype(np.float32)
    m = detect_tonal_imbalance(hp, SR)
    assert m["active"] == 1.0

    out = apply_tonal_balance_conservative(hp, SR, {"low_gain_db": 3.0})
    # strength hard-capped at ±0.5 dB
    assert np.max(np.abs(out - hp)) < 0.1  # tiny change from 0.5 dB shelf

    balanced = apply_tonal_balance_conservative(clean_audio, SR, {"low_gain_db": 0.0, "high_gain_db": 0.0})
    assert np.array_equal(balanced, clean_audio)


def test_tonal_does_not_fire_on_balanced(clean_audio):
    assert detect_tonal_imbalance(clean_audio, SR)["active"] == 0.0


def test_nan_input_raises_never_silent(clean_audio):
    bad = clean_audio.copy()
    bad[100] = np.nan
    with pytest.raises(ValueError):
        apply_dc_offset_fix(bad, SR, {})
    with pytest.raises(ValueError):
        apply_clip_peak_repair(bad, SR, {})
    with pytest.raises(ValueError):
        apply_tonal_balance_conservative(bad, SR, {})


def test_stereo_and_mono_shapes_preserved():
    t = np.arange(SR // 2) / SR
    stereo = np.stack([0.2 * np.sin(2 * np.pi * 440 * t), 0.2 * np.sin(2 * np.pi * 554 * t)], axis=1)
    stereo_dc = stereo + 0.02
    out = apply_dc_offset_fix(stereo_dc, SR, {})
    assert out.shape == stereo.shape
    assert np.max(np.abs(detect_dc_offset(out, SR)["dc"])) < 1e-5

    mono = 0.2 * np.sin(2 * np.pi * 440 * t)
    out_mono = apply_clip_peak_repair(mono, SR, {})
    assert out_mono.shape == mono.shape
