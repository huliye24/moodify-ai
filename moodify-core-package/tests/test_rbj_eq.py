"""Tests for AEP-ACU-002: RBJ Biquad EQ (pytest)."""
from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.signal import freqz

from moodify.processing.rbj_eq import (
    COEFF_FUNCTIONS,
    apply_rbj_eq,
    cascade_freq_response,
    compute_freq_response,
    rbj_high_shelf_coeffs,
    rbj_highpass_coeffs,
    rbj_low_shelf_coeffs,
    rbj_lowpass_coeffs,
    rbj_peaking_coeffs,
)

SR = 44100.0


# ── Helper ─────────────────────────────────────────────────────


def make_sine(freq_hz, duration_s=1.0, sr=SR):
    """Generate a sine wave."""
    t = np.arange(int(sr * duration_s)) / sr
    return np.sin(2 * math.pi * freq_hz * t).astype(np.float64)


def rms_db(x):
    return float(20 * math.log10(np.sqrt(np.mean(x ** 2)) + 1e-15))


# ── Coefficient sanity ──────────────────────────────────────────


@pytest.mark.parametrize("ftype", list(COEFF_FUNCTIONS.keys()))
def test_coeffs_no_nan_normal_params(ftype):
    """All coefficient functions produce finite values with normal params."""
    coeff_fn = COEFF_FUNCTIONS[ftype]
    if ftype in ("high_pass", "low_pass"):
        b, a = coeff_fn(1000.0, 0.707, SR)
    else:
        b, a = coeff_fn(1000.0, 0.707, 6.0, SR)
    assert np.all(np.isfinite(b)), f"{ftype}: non-finite b coefficients"
    assert np.all(np.isfinite(a)), f"{ftype}: non-finite a coefficients"


@pytest.mark.parametrize("ftype", list(COEFF_FUNCTIONS.keys()))
def test_coeffs_no_nan_extreme_params(ftype):
    """All coefficient functions survive extreme parameters."""
    coeff_fn = COEFF_FUNCTIONS[ftype]
    for freq in [1.0, 20.0, 5000.0, 20000.0]:
        for q in [0.025, 40.0]:
            if ftype in ("high_pass", "low_pass"):
                b, a = coeff_fn(freq, q, SR)
            else:
                for gain in [-48.0, 0.0, 48.0]:
                    b, a = coeff_fn(freq, q, gain, SR)
                    assert np.all(np.isfinite(b)), f"{ftype} f={freq} q={q} g={gain}: NaN in b"
                    assert np.all(np.isfinite(a)), f"{ftype} f={freq} q={q} g={gain}: NaN in a"


# ── Zero-gain identity ──────────────────────────────────────────


def test_peaking_zero_db_identity():
    """Peaking filter with 0 dB gain should pass signal unchanged (b == a)."""
    b, a = rbj_peaking_coeffs(1000.0, 1.0, 0.0, SR)
    # Coefficients should be identical after normalisation
    np.testing.assert_allclose(b, a, atol=1e-12, rtol=0,
                               err_msg="0dB peaking should have b == a")


def test_low_shelf_zero_db_identity():
    """Low shelf with 0 dB gain should be identity."""
    b, a = rbj_low_shelf_coeffs(200.0, 0.707, 0.0, SR)
    np.testing.assert_allclose(b, a, atol=1e-12, rtol=0)


def test_high_shelf_zero_db_identity():
    """High shelf with 0 dB gain should be identity."""
    b, a = rbj_high_shelf_coeffs(6000.0, 0.707, 0.0, SR)
    np.testing.assert_allclose(b, a, atol=1e-12, rtol=0)


@pytest.mark.parametrize("ftype", ["low_shelf", "high_shelf", "peaking"])
def test_zero_db_passes_through(ftype):
    """0 dB EQ should not alter signal beyond floating-point precision."""
    x = make_sine(440, 0.5, SR)
    y = apply_rbj_eq(x, SR, [{"type": ftype, "freq_hz": 1000, "gain_db": 0.0, "q": 1.0}])
    # Skip first 100 samples to avoid lfilter transient
    diff_rms = rms_db(y[100:] - x[100:])
    assert diff_rms < -60, f"{ftype} 0dB: diff RMS = {diff_rms:.1f} dB, expected < -60 dB"


# ── Mono / stereo ───────────────────────────────────────────────


def test_mono_shape_preserved():
    x = np.random.randn(44100).astype(np.float32)
    y = apply_rbj_eq(x, SR, [{"type": "low_shelf", "freq_hz": 200, "gain_db": 3.0, "q": 0.707}])
    assert y.shape == x.shape
    assert y.ndim == 1


def test_stereo_shape_preserved():
    x = np.random.randn(44100, 2).astype(np.float32)
    y = apply_rbj_eq(x, SR, [{"type": "high_shelf", "freq_hz": 8000, "gain_db": -2.0, "q": 0.707}])
    assert y.shape == x.shape


def test_empty_filter_chain_identity():
    x = np.random.randn(1000).astype(np.float32)
    y = apply_rbj_eq(x, SR, [])
    assert np.array_equal(x, y)


# ── No NaN / no clip ────────────────────────────────────────────


@pytest.mark.parametrize("ftype", list(COEFF_FUNCTIONS.keys()))
def test_no_nan_in_output(ftype):
    x = np.random.randn(44100).astype(np.float32) * 0.5
    params = {"type": ftype, "freq_hz": 500, "gain_db": 12.0, "q": 0.5}
    y = apply_rbj_eq(x, SR, [params])
    assert not np.any(np.isnan(y)), f"NaN in {ftype} output"


@pytest.mark.parametrize("ftype", list(COEFF_FUNCTIONS.keys()))
def test_output_not_clipped(ftype):
    """Output should not exceed ±1.0 for reasonable input levels."""
    x = make_sine(440, 0.2, SR) * 0.8
    params = {"type": ftype, "freq_hz": 500, "gain_db": 12.0, "q": 0.5}
    y = apply_rbj_eq(x, SR, [params])
    assert np.max(np.abs(y)) <= 1.0 + 1e-10, f"{ftype}: output exceeds ±1.0"


# ── Filter type validation ──────────────────────────────────────


def test_invalid_filter_type_raises():
    x = np.random.randn(100).astype(np.float32)
    with pytest.raises(ValueError, match="Unknown filter type"):
        apply_rbj_eq(x, SR, [{"type": "not_a_filter", "freq_hz": 1000}])


# ── Frequency response verification ─────────────────────────────


def test_low_shelf_dc_gain():
    """Low shelf at DC should amplify by the specified gain."""
    b, a = rbj_low_shelf_coeffs(200.0, 0.707, 6.0, SR)
    _, h = freqz(b, a, worN=[1], fs=SR)  # freq=1 Hz ~ DC
    gain_db = float(20 * np.log10(np.abs(h[0]) + 1e-15))
    assert abs(gain_db - 6.0) < 0.5, f"DC gain should be ~6 dB, got {gain_db:.2f}"


def test_low_shelf_nq_gain():
    """Low shelf at Nyquist should be ~0 dB."""
    b, a = rbj_low_shelf_coeffs(200.0, 0.707, 6.0, SR)
    _, h = freqz(b, a, worN=[SR / 2 - 1], fs=SR)
    gain_db = float(20 * np.log10(np.abs(h[0]) + 1e-15))
    assert abs(gain_db) < 1.0, f"Nyquist gain should be ~0 dB, got {gain_db:.2f}"


def test_high_shelf_dc_gain():
    """High shelf at DC should be ~0 dB."""
    b, a = rbj_high_shelf_coeffs(6000.0, 0.707, -6.0, SR)
    _, h = freqz(b, a, worN=[1], fs=SR)
    gain_db = float(20 * np.log10(np.abs(h[0]) + 1e-15))
    assert abs(gain_db) < 1.0, f"DC gain should be ~0 dB, got {gain_db:.2f}"


def test_high_shelf_nq_gain():
    """High shelf at Nyquist should be ~the specified gain."""
    b, a = rbj_high_shelf_coeffs(6000.0, 0.707, -6.0, SR)
    _, h = freqz(b, a, worN=[SR / 2 - 1], fs=SR)
    gain_db = float(20 * np.log10(np.abs(h[0]) + 1e-15))
    assert abs(gain_db - (-6.0)) < 1.0, f"Nyquist gain should be ~-6 dB, got {gain_db:.2f}"


def test_peaking_center_freq_gain():
    """Peaking filter at center frequency should achieve specified gain."""
    b, a = rbj_peaking_coeffs(1000.0, 1.0, 6.0, SR)
    _, h = freqz(b, a, worN=[1000], fs=SR)
    gain_db = float(20 * np.log10(np.abs(h[0]) + 1e-15))
    assert abs(gain_db - 6.0) < 0.5, f"Center gain should be ~6 dB, got {gain_db:.2f}"


def test_peaking_dc_gain():
    """Peaking filter at DC should be ~0 dB."""
    b, a = rbj_peaking_coeffs(1000.0, 1.0, 6.0, SR)
    _, h = freqz(b, a, worN=[1], fs=SR)
    gain_db = float(20 * np.log10(np.abs(h[0]) + 1e-15))
    assert abs(gain_db) < 0.1, f"DC gain should be ~0 dB, got {gain_db:.2f}"


def test_hpf_low_freq_attenuation():
    """HPF should attenuate below cutoff."""
    b, a = rbj_highpass_coeffs(200.0, 0.707, SR)
    # At 20 Hz (well below 200 Hz), gain should be well below 0 dB
    _, h = freqz(b, a, worN=[20], fs=SR)
    gain_db = float(20 * np.log10(np.abs(h[0]) + 1e-15))
    assert gain_db < -20, f"20 Hz through 200 Hz HPF should be < -20 dB, got {gain_db:.2f}"


def test_lpf_high_freq_attenuation():
    """LPF should attenuate above cutoff."""
    b, a = rbj_lowpass_coeffs(2000.0, 0.707, SR)
    # At 16000 Hz (well above 2000 Hz), gain should be well below 0 dB
    _, h = freqz(b, a, worN=[16000], fs=SR)
    gain_db = float(20 * np.log10(np.abs(h[0]) + 1e-15))
    assert gain_db < -20, f"16 kHz through 2 kHz LPF should be < -20 dB, got {gain_db:.2f}"


# ── Cascade ─────────────────────────────────────────────────────


def test_cascade_three_filters():
    """Three cascaded filters should produce valid output."""
    x = make_sine(440, 0.2, SR) * 0.5
    filters = [
        {"type": "low_shelf", "freq_hz": 200, "gain_db": 3.0, "q": 0.707},
        {"type": "peaking", "freq_hz": 1000, "gain_db": -2.0, "q": 1.5},
        {"type": "high_shelf", "freq_hz": 6000, "gain_db": -1.0, "q": 0.707},
    ]
    y = apply_rbj_eq(x, SR, filters)
    assert y.shape == x.shape
    assert not np.any(np.isnan(y))
    assert np.max(np.abs(y)) <= 1.0 + 1e-10


def test_cascade_freq_response():
    """cascade_freq_response should be the product of individual responses."""
    from moodify.processing.rbj_eq import COEFF_FUNCTIONS

    coeffs_list = [
        COEFF_FUNCTIONS["low_shelf"](200.0, 0.707, 6.0, SR),
        COEFF_FUNCTIONS["peaking"](1000.0, 1.0, -3.0, SR),
    ]
    freqs, mag_cascade = cascade_freq_response(coeffs_list, n_fft=1024, sr=SR)

    # Individual responses multiplied
    _, h1 = freqz(*coeffs_list[0], worN=1024, fs=SR)
    _, h2 = freqz(*coeffs_list[1], worN=1024, fs=SR)
    mag_product = 20 * np.log10(np.abs(h1) * np.abs(h2) + 1e-15)

    np.testing.assert_allclose(mag_cascade, mag_product, atol=0.01, rtol=0,
                               err_msg="Cascade should equal product of individual responses")


# ── Legacy EQ still accessible ──────────────────────────────────


def test_legacy_eq_accessible():
    from moodify.processing.operators import OPERATOR_REGISTRY
    assert "eq_legacy_fft" in OPERATOR_REGISTRY, "Legacy FFT EQ must remain accessible"
    assert "eq" in OPERATOR_REGISTRY


def test_apply_eq_default_is_rbj():
    from moodify.processing.operators import apply_eq
    x = make_sine(440, 0.2, SR) * 0.5
    y = apply_eq(x, int(SR), low_shelf_gain_db=3.0, low_shelf_freq=200,
                 high_shelf_gain_db=-2.0, high_shelf_freq=6000,
                 peak_freq=1000, peak_gain_db=0.0, peak_q=1.0)
    assert y.shape == x.shape
    assert not np.any(np.isnan(y))


def test_apply_eq_legacy_mode():
    import warnings
    from moodify.processing.operators import apply_eq

    x = make_sine(440, 0.2, SR) * 0.5
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        y = apply_eq(x, int(SR), low_shelf_gain_db=3.0, mode="legacy_fft")
    assert y.shape == x.shape
    assert not np.any(np.isnan(y))


def test_apply_eq_invalid_mode_raises():
    from moodify.processing.operators import apply_eq
    x = make_sine(440, 0.1, SR)
    with pytest.raises(ValueError, match="Unknown EQ mode"):
        apply_eq(x, int(SR), mode="invalid", low_shelf_gain_db=6.0)


# ── Regression: EQ does not alter length ────────────────────────


def test_length_preserved():
    for n in [100, 1000, 10000, 44100]:
        x = np.random.randn(n).astype(np.float32) * 0.5
        y = apply_rbj_eq(x, SR, [{"type": "peaking", "freq_hz": 2000, "gain_db": 3.0, "q": 0.5}])
        assert len(y) == n, f"Length changed: {len(y)} != {n}"
