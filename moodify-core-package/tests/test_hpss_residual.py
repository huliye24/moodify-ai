"""Tests for AEP-ACU-003: Residual-Preserving HPSS Chain (pytest)."""
from __future__ import annotations

import math

import numpy as np
import pytest

from moodify.processing.spectral_chain import (
    HPSSAudit,
    HPSSComponents,
    SpectralDSPChain,
    _compute_reconstruction_error,
)

SR = 44100


# ── Helpers ─────────────────────────────────────────────────────


def make_sine(freq_hz, duration_s=1.0, sr=SR):
    t = np.arange(int(sr * duration_s)) / sr
    return np.sin(2 * math.pi * freq_hz * t).astype(np.float32)


def make_stereo(audio_mono):
    return np.column_stack([audio_mono, audio_mono * 0.9])


# ── G1: H/P/R 分量完整 ─────────────────────────────────────────


def test_three_components_present():
    """HPSS decomposition must produce harmonic, percussive, AND residual."""
    chain = SpectralDSPChain()
    audio = make_stereo(make_sine(440, 1.0)) * 0.5

    comps, D_l, D_r = chain._decompose(audio)

    assert comps.harmonic.shape == audio.shape
    assert comps.percussive.shape == audio.shape
    assert comps.residual.shape == audio.shape
    assert comps.residual_energy_ratio >= 0.0
    assert comps.margin == 2.0


def test_residual_not_all_zeros():
    """With margin > 1.0, residual should be non-zero for most audio."""
    chain = SpectralDSPChain(margin=2.0)
    audio = make_stereo(make_sine(440, 0.5)) * 0.5
    # Add transient content so HPSS splits
    audio[1000:1100] *= 5.0

    comps, _, _ = chain._decompose(audio)
    r_rms = float(np.sqrt(np.mean(comps.residual ** 2)))
    assert r_rms > 0, "Residual should have non-zero energy with margin=2.0"


def test_residual_near_zero_at_margin_1():
    """At margin=1.0, hard masks → residual should be near zero."""
    chain = SpectralDSPChain(margin=1.0)
    audio = make_stereo(make_sine(440, 0.5)) * 0.5
    audio[1000:1100] *= 5.0

    comps, _, _ = chain._decompose(audio)
    r_rms = float(np.sqrt(np.mean(comps.residual ** 2)))
    assert r_rms < 0.01, f"margin=1.0 residual RMS should be near zero, got {r_rms:.6f}"


# ── G2: No-op 重建误差 ─────────────────────────────────────────


def test_noop_reconstruction_error_low():
    """H+P+R should reconstruct original signal with very low error."""
    chain = SpectralDSPChain()
    audio = make_stereo(make_sine(440, 1.0)) * 0.5

    comps, _, _ = chain._decompose(audio)
    err = comps.reconstruction_error

    assert err < 1e-4, f"Reconstruction error {err:.2e} exceeds 1e-4 threshold"


def test_noop_reconstruction_stereo_independence():
    """Each channel's reconstruction should be independent and accurate."""
    chain = SpectralDSPChain()
    # Different signals on L and R
    left = make_sine(440, 0.5) * 0.5
    right = make_sine(880, 0.5) * 0.3
    audio = np.column_stack([left, right])

    comps, D_l, D_r = chain._decompose(audio)

    # Verify left channel reconstruction
    H_l = comps.harmonic[:, 0]
    P_l = comps.percussive[:, 0]
    R_l = comps.residual[:, 0]
    err_l = _compute_reconstruction_error(H_l, P_l, R_l, left)
    assert err_l < 1e-4, f"Left channel error {err_l:.2e} exceeds threshold"


def test_process_preserves_shape():
    """process() should preserve input shape."""
    chain = SpectralDSPChain()
    audio = make_stereo(make_sine(440, 0.3)) * 0.3

    params = {"P02_vocal_presence_gain": 1.0}
    result = chain.process(audio, SR, params)

    assert result.shape == audio.shape
    assert result.dtype == audio.dtype


def test_process_no_nan():
    """Output should never contain NaN."""
    chain = SpectralDSPChain()
    audio = np.random.randn(SR, 2).astype(np.float32) * 0.3

    params = {"P02_vocal_presence_gain": 5.0, "P11_reverb_dry_wet": 0.2,
              "P06_compression_ratio": 3.0}
    result = chain.process(audio, SR, params)

    assert not np.any(np.isnan(result)), "NaN in output"
    assert not np.any(np.isinf(result)), "Inf in output"


# ── G3: 能量审计 ───────────────────────────────────────────────


def test_audit_rms_fields():
    """Audit must contain RMS before/after/delta."""
    chain = SpectralDSPChain()
    audio = make_stereo(make_sine(440, 0.3)) * 0.5

    chain.process(audio, SR, {"P02_vocal_presence_gain": 1.0})
    audit = chain.last_audit

    assert audit is not None
    assert audit.rms_before_db > -100
    assert audit.rms_after_db > -100
    assert isinstance(audit.rms_delta_db, float)


def test_audit_lufs_fields():
    """Audit must contain LUFS before/after/delta (best-effort)."""
    chain = SpectralDSPChain()
    audio = make_stereo(make_sine(440, 0.3)) * 0.5

    chain.process(audio, SR, {})
    audit = chain.last_audit

    assert isinstance(audit.lufs_before, float)
    assert isinstance(audit.lufs_after, float)
    assert isinstance(audit.lufs_delta, float)


def test_audit_spectral_residual_ratio():
    """Audit must contain spectral residual ratio."""
    chain = SpectralDSPChain()
    audio = make_stereo(make_sine(440, 0.3)) * 0.5

    chain.process(audio, SR, {"P02_vocal_presence_gain": 3.0})
    audit = chain.last_audit

    assert audit.spectral_residual_ratio >= 0.0


def test_audit_residual_ratio_field():
    """Audit must report residual_energy_ratio from decomposition."""
    chain = SpectralDSPChain()
    audio = make_stereo(make_sine(440, 0.3)) * 0.5
    audio[1000:1100] *= 5.0

    chain.process(audio, SR, {})
    audit = chain.last_audit

    assert audit.residual_energy_ratio >= 0.0


# ── Residual mode control ───────────────────────────────────────


def test_preserve_mode_keeps_residual():
    """preserve mode must set residual_preserved=True."""
    chain = SpectralDSPChain(residual_mode="preserve")
    audio = make_stereo(make_sine(440, 0.3)) * 0.5

    chain.process(audio, SR, {"P02_vocal_presence_gain": 2.0})
    assert chain.last_audit.residual_preserved is True


def test_discard_mode_flags_residual():
    """discard mode must set residual_preserved=False."""
    chain = SpectralDSPChain(residual_mode="discard")
    audio = make_stereo(make_sine(440, 0.3)) * 0.5

    chain.process(audio, SR, {"P02_vocal_presence_gain": 2.0})
    assert chain.last_audit.residual_preserved is False


def test_attenuate_mode_flags_residual():
    """attenuate mode sets residual_preserved=True (not discarded, just reduced)."""
    chain = SpectralDSPChain(residual_mode="attenuate")
    audio = make_stereo(make_sine(440, 0.3)) * 0.5

    chain.process(audio, SR, {"P02_vocal_presence_gain": 2.0})
    assert chain.last_audit.residual_preserved is True


def test_invalid_residual_mode_raises():
    with pytest.raises(ValueError, match="residual_mode"):
        SpectralDSPChain(residual_mode="invalid")


def test_discard_loses_residual_energy():
    """Decomposing then summing H+P (discarding R) must have lower energy
    than H+P+R at the component level (before pedalboard processing)."""
    audio = make_stereo(make_sine(440, 0.3)) * 0.5
    audio[1000:1100] *= 5.0  # Add transients

    chain = SpectralDSPChain(margin=2.0)
    comps, _, _ = chain._decompose(audio)

    # Energy of H+P only (old behaviour)
    hp_only = comps.harmonic + comps.percussive
    rms_hp = float(np.sqrt(np.mean(hp_only ** 2)))

    # Energy of H+P+R (new behaviour)
    hpr = hp_only + comps.residual
    rms_hpr = float(np.sqrt(np.mean(hpr ** 2)))

    assert rms_hp < rms_hpr, (
        f"H+P only should have lower RMS ({rms_hp:.6f}) "
        f"than H+P+R ({rms_hpr:.6f})"
    )
    # The difference should be measurable
    energy_loss_pct = (1.0 - rms_hp / rms_hpr) * 100
    assert energy_loss_pct > 0.1, (
        f"Energy loss from discarding residual too small: {energy_loss_pct:.2f}%"
    )


# ── Mono compatibility ──────────────────────────────────────────


def test_mono_process():
    chain = SpectralDSPChain()
    audio = make_sine(440, 0.5) * 0.3

    result = chain.process(audio, SR, {})
    assert result.ndim == 1
    assert len(result) == len(audio)
    assert not np.any(np.isnan(result))


def test_mono_audit():
    chain = SpectralDSPChain()
    audio = make_sine(440, 0.3) * 0.5

    chain.process(audio, SR, {"P02_vocal_presence_gain": 1.0})
    audit = chain.last_audit

    assert audit.residual_energy_ratio >= 0.0
    assert audit.reconstruction_error < 1e-4


# ── Backward compatibility ─────────────────────────────────────


def test_default_constructor_is_preserve():
    """Default SpectralDSPChain() should be residual-preserving."""
    chain = SpectralDSPChain()
    assert chain.residual_mode == "preserve"
    assert chain.margin == 2.0


def test_existing_callers_compatible():
    """SpectralDSPChain() with no args (existing callers) must work."""
    chain = SpectralDSPChain()  # No args like all existing callers
    audio = make_stereo(make_sine(440, 0.2)) * 0.3

    # This should not raise
    result = chain.process(audio, SR, {
        "P02_vocal_presence_gain": 1.0,
        "P06_compression_ratio": 2.0,
        "P11_reverb_dry_wet": 0.1,
    })
    assert result.shape == audio.shape


# ── HPSSAudit serializability ──────────────────────────────────


def test_audit_to_dict():
    from dataclasses import asdict
    audit = HPSSAudit(
        residual_energy_ratio=0.15,
        reconstruction_error=1e-6,
        rms_before_db=-12.0,
        rms_after_db=-11.5,
        rms_delta_db=0.5,
        residual_preserved=True,
        residual_mode="preserve",
    )
    d = asdict(audit)
    assert d["residual_energy_ratio"] == 0.15
    assert d["residual_preserved"] is True
    assert d["residual_mode"] == "preserve"


# ── HPSSComponents integrity ───────────────────────────────────


def test_components_residual_ratio_in_range():
    """residual_energy_ratio must be in [0, 1]."""
    chain = SpectralDSPChain()
    audio = make_stereo(make_sine(440, 0.3)) * 0.5
    audio[500:1500] *= 4.0

    comps, _, _ = chain._decompose(audio)
    assert 0.0 <= comps.residual_energy_ratio <= 1.0 + 1e-10
