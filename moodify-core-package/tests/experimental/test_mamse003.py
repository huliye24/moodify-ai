"""MAMSE-003 synthetic gates (T4) — 9 required fixtures + two-state switch.

Carrier geometry, tone concentration, gain invariance, time-shift stability,
8 Hz AM enhancement, pulse-train high-modulation, seeded determinism,
serialization roundtrip, rerun determinism, two-state texture switch.
"""

from __future__ import annotations

import json

import numpy as np

from moodify_experimental.mamse003 import TextureConfig, analyze_texture, load_case, save_case

SR = 24000


def _sine(seconds: float = 4.0, freq: float = 1000.0, gain: float = 0.3) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    return gain * np.sin(2 * np.pi * freq * t)


def _am_sine(seconds: float = 4.0, carrier: float = 1000.0, mod: float = 8.0, depth: float = 0.9) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    env = 1.0 + depth * np.sin(2 * np.pi * mod * t)
    return 0.2 * env * np.sin(2 * np.pi * carrier * t)


def _pulse_train(seconds: float = 4.0, rate: float = 12.0) -> np.ndarray:
    n = int(seconds * SR)
    x = np.zeros(n)
    step = int(SR / rate)
    width = max(2, int(0.004 * SR))
    for i in range(0, n, step):
        x[i:i + width] = np.hanning(min(width, n - i))
    return 0.5 * x


def _cosine(a, b) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def test_carrier_geometry_monotonic_geometric():
    c = TextureConfig()
    centers = np.asarray(c.carrier_centers_hz)
    assert np.all(np.diff(centers) > 0)
    ratios = centers[1:] / centers[:-1]
    assert np.std(ratios) < 1e-10
    assert centers[0] == c.carrier_f_min
    assert centers[-1] <= c.carrier_f_max


def test_stationary_tone_concentrates_near_carrier():
    r = analyze_texture(_sine(freq=1000.0), SR)
    centers = np.asarray(r.carrier_centers_hz)
    p = np.asarray(r.first_order_distribution)
    fc = centers[np.argmax(p)]
    assert abs(np.log2(fc / 1000.0)) < 0.35
    assert p.max() > p.mean() * 2


def test_gain_scaled_signature_nearly_invariant():
    r1 = analyze_texture(_sine(gain=0.1), SR)
    r2 = analyze_texture(_sine(gain=0.7), SR)
    assert _cosine(r1.first_order_distribution, r2.first_order_distribution) > 0.995


def test_time_shifted_texture_global_signature_stable():
    x = _am_sine()
    y = np.roll(x, int(0.12 * SR))
    r1 = analyze_texture(x, SR)
    r2 = analyze_texture(y, SR)
    assert _cosine(r1.first_order_distribution, r2.first_order_distribution) > 0.98
    assert _cosine(r1.modulation_distribution, r2.modulation_distribution) > 0.90


def test_8hz_am_enhances_8hz_modulation():
    stable = analyze_texture(_sine(), SR)
    modded = analyze_texture(_am_sine(mod=8.0), SR)
    rates = np.asarray(modded.modulation_rates_hz)
    i8 = int(np.argmin(np.abs(rates - 8.0)))
    assert modded.modulation_distribution[i8] > stable.modulation_distribution[i8]


def test_pulse_train_has_more_high_modulation_than_stable_tone():
    a = analyze_texture(_sine(), SR)
    b = analyze_texture(_pulse_train(), SR)
    assert b.high_modulation_ratio > a.high_modulation_ratio


def test_seeded_noise_deterministic():
    rng = np.random.default_rng(7)
    x = 0.2 * rng.standard_normal(int(3.0 * SR))
    a = analyze_texture(x, SR)
    b = analyze_texture(x, SR)
    assert np.allclose(a.first_order_distribution, b.first_order_distribution, rtol=1e-10, atol=1e-12)
    assert np.allclose(a.modulation_distribution, b.modulation_distribution, rtol=1e-10, atol=1e-12)


def test_two_state_texture_switch_changes_frame_matrix():
    x = np.concatenate([_sine(2.0, freq=1000.0), _sine(2.0, freq=3000.0)])
    r = analyze_texture(x, SR)
    frames = np.asarray(r.frame_texture_matrix)
    assert frames.shape[0] >= 8
    # the frame texture matrix must show non-uniform structure across the switch
    centroid_col = frames[:, 3]
    assert np.std(centroid_col) > 1e-3


def test_serialization_roundtrip(tmp_path):
    r = analyze_texture(_am_sine(seconds=2.5), SR)
    paths = save_case(r, tmp_path)
    assert paths["manifest"].exists() and paths["npz"].exists() and paths["summary"].exists()
    loaded = load_case(paths["manifest"], paths["npz"])
    assert loaded["manifest"]["source_sha256"] == r.source_sha256
    assert loaded["manifest"]["config_hash"] == r.config["config_hash"]
    assert loaded["manifest"]["git_commit"] and len(loaded["manifest"]["git_commit"]) >= 7
    assert np.allclose(loaded["first_order_distribution"], r.first_order_distribution)
    assert loaded["frame_texture_matrix"].shape[1] == 4
    assert "scattering-inspired" in json.dumps(loaded["manifest"]["limitations"])


def test_rerun_logically_deterministic():
    x = _am_sine(seconds=2.0, mod=4.0)
    a = analyze_texture(x, SR)
    b = analyze_texture(x, SR)
    da, db = a.to_dict(), b.to_dict()
    for k in ("runtime_seconds", "peak_memory_mb"):
        da.pop(k)
        db.pop(k)
    assert json.dumps(da, sort_keys=True) == json.dumps(db, sort_keys=True)
