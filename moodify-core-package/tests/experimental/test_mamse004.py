"""MAMSE-004 synthetic gates (G1-G10 + extras).

Pure-delay constant group delay, 2π wrap invariance, linear-phase curvature,
low-magnitude masking, stereo delayed broadband recovery (sign and
magnitude), GCC-PHAT cross-check, mono UNAVAILABLE, determinism,
serialization roundtrip, roughly linear runtime, silence honesty.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from moodify_experimental.mamse004 import (
    PhaseGeometryConfig,
    analyze_phase_geometry,
    gcc_phat_delay,
    group_delay_from_phase,
    load_result,
    logical_json,
    magnitude_mask,
    phase_curvature_from_group_delay,
    save_result,
)

SR = 48000


def test_g1_pure_delay_constant_group_delay():
    f = np.linspace(80, 18000, 4000)
    w = 2 * np.pi * f
    delay = 0.00175
    phase = np.angle(np.exp(-1j * w * delay))
    gd = group_delay_from_phase(phase, w)
    assert abs(float(np.median(gd)) - delay) < 2e-6


def test_g2_wrap_invariance():
    f = np.linspace(100, 15000, 2500)
    w = 2 * np.pi * f
    delay = 0.00082
    p1 = np.angle(np.exp(-1j * w * delay))
    p2 = p1.copy()
    p2[700:1400] += 2 * np.pi
    g1 = group_delay_from_phase(p1, w)
    g2 = group_delay_from_phase(p2, w)
    assert np.allclose(g1, g2, atol=1e-9)


def test_g3_linear_phase_curvature_near_zero():
    f = np.linspace(100, 18000, 3000)
    w = 2 * np.pi * f
    delay = 0.002
    gd = group_delay_from_phase(-w * delay, w)
    c = phase_curvature_from_group_delay(gd, w)
    assert np.percentile(np.abs(c), 99) < 1e-12


def test_g4_low_magnitude_mask():
    mag = np.ones((2, 100))
    mag[:, 50:] = 1e-5
    m = magnitude_mask(mag, -45, axis=1)
    assert m[:, :50].all() and not m[:, 50:].any()


def _delayed_noise(delay_samples=24, seconds=2.0):
    rng = np.random.default_rng(7)
    n = int(seconds * SR)
    left = rng.standard_normal(n) * 0.15
    right = np.concatenate([np.zeros(delay_samples), left[:-delay_samples]])
    return left, right


def test_g5_stereo_delay_recovers_sign_and_magnitude():
    d = 24
    left, right = _delayed_noise(d)
    stereo = np.stack([left, right], axis=1)
    cfg = PhaseGeometryConfig(n_fft=4096, hop_length=1024, f_min_hz=200, f_max_hz=12000,
                              magnitude_floor_db=-35, gcc_max_delay_ms=3)
    r = analyze_phase_geometry(stereo, SR, cfg)
    est = r["summary"]["stereo"]["interchannel_delay_median_ms"]
    expected = d / SR * 1000
    assert est is not None and est > 0 and abs(est - expected) < 0.12


def test_g5b_larger_delay_magnitude_scales():
    d = 120  # 2.5 ms
    left, right = _delayed_noise(d)
    stereo = np.stack([left, right], axis=1)
    cfg = PhaseGeometryConfig(n_fft=4096, hop_length=1024, f_min_hz=200, f_max_hz=12000,
                              magnitude_floor_db=-35, gcc_max_delay_ms=5)
    r = analyze_phase_geometry(stereo, SR, cfg)
    est = r["summary"]["stereo"]["interchannel_delay_median_ms"]
    expected = d / SR * 1000
    assert est is not None and abs(est - expected) < 0.3


def test_g6_gcc_phat_known_delay():
    d = 31
    left, right = _delayed_noise(d)
    est = gcc_phat_delay(left, right, SR, 3.0)
    assert abs(est - d / SR) <= 1 / SR


def test_g7_mono_unavailable_stereo():
    t = np.arange(SR) / SR
    x = 0.2 * np.sin(2 * np.pi * 440 * t)
    r = analyze_phase_geometry(x, SR, PhaseGeometryConfig(n_fft=4096, hop_length=1024))
    assert r["summary"]["stereo"]["ipd_available"] is False
    assert r["summary"]["stereo"]["interchannel_delay_median_ms"] is None
    assert r["summary"]["stereo"]["gcc_phat_delay_ms"] is None


def test_g8_deterministic():
    left, right = _delayed_noise(12, 1.0)
    x = np.stack([left, right], axis=1)
    cfg = PhaseGeometryConfig(n_fft=2048, hop_length=512, f_max_hz=10000)
    a = analyze_phase_geometry(x, SR, cfg)
    b = analyze_phase_geometry(x, SR, cfg)
    assert logical_json(a) == logical_json(b)
    assert np.allclose(a["mono_raw"]["group_delay_s"], b["mono_raw"]["group_delay_s"], equal_nan=True)


def test_g9_serialization_roundtrip(tmp_path):
    left, right = _delayed_noise(16, 1.0)
    x = np.stack([left, right], axis=1)
    r = analyze_phase_geometry(x, SR, PhaseGeometryConfig(n_fft=2048, hop_length=512, f_max_hz=10000))
    e, n, m = save_result(r, tmp_path)
    js = json.loads(Path(e).read_text(encoding="utf-8"))
    z = np.load(n)
    assert js["operator_version"].startswith("mamse004")
    assert "group_delay_s" in z and "interchannel_delay_s" in z
    assert m.exists()
    loaded = load_result(e, n)
    assert loaded["summary"]["config_hash"] == js["config_hash"]
    assert loaded["summary"]["source_sha256"] == js["source_sha256"]
    assert np.allclose(loaded["npz"]["group_delay_s"], z["group_delay_s"], equal_nan=True)


def test_g10_runtime_roughly_bounded_linear():
    rng = np.random.default_rng(10)
    cfg = PhaseGeometryConfig(n_fft=2048, hop_length=512, f_max_hz=10000)

    def run(sec):
        x = rng.standard_normal((int(sec * SR), 2)) * 0.05
        t = time.perf_counter()
        analyze_phase_geometry(x, SR, cfg)
        return time.perf_counter() - t

    t1 = run(0.7)
    t2 = run(1.4)
    assert t2 < max(6 * t1, 1.5)


def test_silence_honesty():
    x = np.zeros(int(1.0 * SR))
    r = analyze_phase_geometry(x, SR, PhaseGeometryConfig(n_fft=2048, hop_length=512))
    mono = r["summary"]["mono"]
    assert mono["valid_bin_ratio"] < 1e-9
    assert mono["group_delay_median_ms"] is None
    assert mono["phase_curvature_median_s2"] is None


def test_short_signal_behavior():
    x = 0.2 * np.random.default_rng(3).standard_normal(int(0.02 * SR))
    r = analyze_phase_geometry(x, SR, PhaseGeometryConfig(n_fft=4096, hop_length=2048))
    assert r["summary"]["mono"]["group_delay_median_ms"] is not None or r["summary"]["mono"]["valid_bin_ratio"] < 1.0
