"""MAMSE-005 synthetic gates (G1-G8 + extras).

Cepstrum math, F0 ladder (100/250/400 Hz), gain invariance, lifter
reconstruction identity, envelope smoothness, controlled resonance
candidates, silence/short/noise honesty, determinism, shapes/quefrency
axis, serialization, roughly linear runtime.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from scipy.signal import iirpeak, lfilter

from moodify_experimental.mamse005 import (
    CepstrumConfig,
    analyze_cepstral_structure,
    cepstral_decompose_frame,
    load_result,
    logical_json,
    save_result,
)

SR = 48000
CFG = CepstrumConfig(n_fft=4096, hop_length=1024, lifter_cutoff_ms=2.5, f0_min_hz=60, f0_max_hz=500,
                     min_periodicity_score=0.85, resonance_prominence_db=0.7)


def harmonic(f0, seconds=2.0, gain=0.35, harmonics=25):
    t = np.arange(int(seconds * SR)) / SR
    x = np.zeros_like(t)
    for k in range(1, harmonics + 1):
        x += (gain / k) * np.sin(2 * np.pi * f0 * k * t)
    return x


def test_short_is_unavailable():
    r = analyze_cepstral_structure(np.zeros(1000), SR, CFG)
    assert r["summary"]["availability"] == "UNAVAILABLE_TOO_SHORT"


def test_silence_no_f0():
    r = analyze_cepstral_structure(np.zeros(SR), SR, CFG)
    assert r["summary"]["median_f0_candidate_hz"] is None
    assert r["summary"]["periodicity_available_ratio"] == 0.0


def test_200hz_candidate():
    r = analyze_cepstral_structure(harmonic(200), SR, CFG)
    f = r["summary"]["median_f0_candidate_hz"]
    assert f is not None and abs(f - 200) / 200 < 0.03


def test_f0_ladder():
    for target in (100, 250, 400):
        r = analyze_cepstral_structure(harmonic(target), SR, CFG)
        f = r["summary"]["median_f0_candidate_hz"]
        assert f is not None and abs(f - target) / target < 0.04, (target, f)


def test_gain_invariance_candidate():
    a = analyze_cepstral_structure(harmonic(220, gain=.1), SR, CFG)["summary"]["median_f0_candidate_hz"]
    b = analyze_cepstral_structure(harmonic(220, gain=.7), SR, CFG)["summary"]["median_f0_candidate_hz"]
    assert a and b and abs(a - b) < 3.0


def test_lifter_reconstruction_identity_log_domain():
    x = harmonic(180, seconds=.2)[:CFG.n_fft]
    d = cepstral_decompose_frame(x, SR, CFG.n_fft, CFG.window, CFG.magnitude_floor, CFG.lifter_cutoff_ms)
    assert np.max(np.abs((d["envelope_logmag"] + d["fine_logmag"]) - d["logmag"])) < 1e-10


def test_envelope_smoother_than_raw_log_spectrum():
    r = analyze_cepstral_structure(harmonic(180), SR, CFG)
    assert r["summary"]["spectral_envelope_roughness"] < r["summary"]["raw_log_spectrum_roughness"]


def test_controlled_resonance_candidates():
    x = harmonic(120, seconds=2.0, harmonics=80)
    y = x.copy()
    for f0, q in ((800, 8), (2200, 10)):
        b, a = iirpeak(f0 / (SR / 2), q)
        y = lfilter(b, a, y)
    r = analyze_cepstral_structure(y, SR, CFG)
    cand = []
    for row in r["raw"]["resonance_candidates"]:
        cand.extend([v["frequency_hz"] for v in row])
    assert any(500 < f < 1200 for f in cand)
    assert any(1500 < f < 3000 for f in cand)


def test_white_noise_not_forced_stable_f0():
    rng = np.random.default_rng(7)
    x = rng.standard_normal(SR * 2) * .1
    r = analyze_cepstral_structure(x, SR, CFG)
    assert r["summary"]["periodicity_available_ratio"] < 0.8


def test_deterministic_summary():
    x = harmonic(196, seconds=1.3)
    a = analyze_cepstral_structure(x, SR, CFG)
    b = analyze_cepstral_structure(x, SR, CFG)
    assert logical_json(a) == logical_json(b)


def test_shapes_and_quefrency_axis():
    r = analyze_cepstral_structure(harmonic(150, seconds=1), SR, CFG)
    raw = r["raw"]
    assert raw["cepstrum"].shape[0] == len(raw["frame_time_s"])
    assert raw["cepstrum"].shape[1] == CFG.n_fft // 2 + 1
    assert np.isclose(raw["quefrency_s"][1], 1 / SR)


def test_serialization_roundtrip(tmp_path):
    r = analyze_cepstral_structure(harmonic(196, seconds=1.0), SR, CFG)
    e, n, m = save_result(r, tmp_path)
    js = json.loads(Path(e).read_text(encoding="utf-8"))
    z = np.load(n)
    assert js["operator_version"].startswith("mamse005")
    assert js["availability"] == "AVAILABLE"
    assert "cepstrum" in z and "envelope_logmag" in z
    assert m.exists()
    loaded = load_result(e, n)
    assert loaded["summary"]["config_hash"] == js["config_hash"]
    assert loaded["summary"]["source_sha256"] == js["source_sha256"]
    assert np.allclose(loaded["npz"]["cepstrum"], z["cepstrum"])


def test_resource_growth_bounded():
    rng = np.random.default_rng(4)

    def run(sec):
        x = rng.standard_normal(int(sec * SR)) * .03
        t = time.perf_counter()
        analyze_cepstral_structure(x, SR, CFG)
        return time.perf_counter() - t

    a = run(.8)
    b = run(1.6)
    assert b < max(a * 5.5, 1.8)
