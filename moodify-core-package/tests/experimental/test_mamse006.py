"""MAMSE-006 synthetic gates (G1-G13 + extras).

Silence/short unavailability, AM recovery (2/5/9 Hz), gain invariance,
static ripple, dynamic ripple rate/scale, orientation reversal, distribution
integrity, determinism, serialization, bounded resource growth, and
steady-vs-modulated dynamic energy separation.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from moodify_experimental.mamse006 import (
    ModulationConfig,
    analyze_surface,
    am_signal,
    harmonic_broadband,
    load_evidence,
    normalized_entropy,
    normalize_distribution,
    ripple_surface,
    run_mamse006,
    save_evidence,
    static_ripple_surface,
    summarize_modulation,
)

SR = 48_000
CFG = ModulationConfig(sample_rate=SR)


def test_short_input_unavailable():
    x = np.zeros(int(0.5 * SR))
    summary, arrays = run_mamse006(x, CFG)
    assert summary["status"] == "UNAVAILABLE_TOO_SHORT"
    assert arrays is None


def test_silence_unavailable():
    x = np.zeros(int(4.0 * SR))
    summary, arrays = run_mamse006(x, CFG)
    assert summary["status"] == "UNAVAILABLE_LOW_ENERGY"
    assert arrays is None


def _assert_peak(rate: float, tol: float = 0.5):
    x = am_signal(8.0, SR, rate)
    summary, arrays = run_mamse006(x, CFG)
    assert summary["status"] == "OK"
    assert arrays is not None
    assert summary["temporal_peak_hz"] is not None
    assert abs(summary["temporal_peak_hz"] - rate) <= tol


def test_am_2hz_recovered():
    _assert_peak(2.0)


def test_am_5hz_recovered():
    _assert_peak(5.0)


def test_am_9hz_recovered():
    _assert_peak(9.0)


def test_gain_invariance_of_peak():
    x = am_signal(8.0, SR, 5.0)
    a, _ = run_mamse006(x * 0.2, CFG)
    b, _ = run_mamse006(x * 0.8, CFG)
    assert abs(a["temporal_peak_hz"] - b["temporal_peak_hz"]) < 1e-9
    assert abs(a["temporal_centroid_hz"] - b["temporal_centroid_hz"]) < 0.1


def test_static_ripple_spectral_peak():
    surface = static_ripple_surface(96, 256, 12, 2.0)
    mod = analyze_surface(surface, frame_rate_hz=64, bands_per_octave=12,
                          modulation_window_seconds=4.0, modulation_hop_seconds=2.0)
    s = summarize_modulation(mod, temporal_min_hz=0.25, temporal_max_hz=30, spectral_max_cpo=4)
    assert s["spectral_peak_cpo"] is not None
    assert abs(s["spectral_peak_cpo"] - 2.0) <= 0.2


def test_dynamic_ripple_known_rate_scale():
    surface = ripple_surface(96, 512, 64, 12, temporal_hz=4.0, spectral_cpo=1.5, direction=1)
    mod = analyze_surface(surface, 64, 12, 4.0, 2.0)
    s = summarize_modulation(mod, temporal_min_hz=0.25, temporal_max_hz=20, spectral_max_cpo=4)
    assert s["ridge"] is not None
    assert abs(s["ridge"]["temporal_rate_hz"] - 4.0) <= 0.3
    assert abs(abs(s["ridge"]["spectral_rate_cpo"]) - 1.5) <= 0.15


def test_reversed_ripple_flips_orientation():
    a = ripple_surface(96, 512, 64, 12, 4.0, 1.5, direction=1)
    b = ripple_surface(96, 512, 64, 12, 4.0, 1.5, direction=-1)
    sa = summarize_modulation(analyze_surface(a, 64, 12, 4.0, 2.0), 0.25, 20, 4)
    sb = summarize_modulation(analyze_surface(b, 64, 12, 4.0, 2.0), 0.25, 20, 4)
    assert sa["diagonal_orientation_index"] * sb["diagonal_orientation_index"] < 0
    assert abs(abs(sa["diagonal_orientation_index"]) - abs(sb["diagonal_orientation_index"])) < 0.05


def test_distribution_normalization_and_entropy():
    x = np.array([0.0, 1.0, 2.0, 3.0])
    p = normalize_distribution(x)
    assert np.all(p >= 0)
    assert abs(p.sum() - 1.0) < 1e-12
    h = normalized_entropy(x)
    assert 0.0 <= h <= 1.0


def test_steady_carrier_has_lower_dynamic_energy_than_modulated():
    steady = harmonic_broadband(8.0, SR)
    modded = am_signal(8.0, SR, 5.0)
    _, a = run_mamse006(steady, CFG)
    _, b = run_mamse006(modded, CFG)
    assert a is not None and b is not None
    ea = float(np.sum(a["dynamic_joint_power"]))
    eb = float(np.sum(b["dynamic_joint_power"]))
    assert eb > ea * 1.2


def test_deterministic_rerun():
    x = am_signal(6.0, SR, 5.0)
    a, aa = run_mamse006(x, CFG)
    b, bb = run_mamse006(x, CFG)
    for key in ("operator_id", "operator_version", "profile_hash", "source_sha256", "temporal_peak_hz"):
        assert a[key] == b[key]
    for key in ("temporal_marginal", "spectral_marginal", "joint_power", "dynamic_joint_power"):
        assert np.allclose(aa[key], bb[key])


def test_serialization_roundtrip(tmp_path: Path):
    x = am_signal(6.0, SR, 5.0)
    summary, arrays = run_mamse006(x, CFG)
    j, n = save_evidence(summary, arrays, tmp_path)
    raw = json.loads(j.read_text(encoding="utf-8"))
    assert raw["operator_id"] == "MAMSE-006"
    assert n is not None
    assert (tmp_path / "mamse006_manifest.json").exists()
    loaded = np.load(n)
    assert "dynamic_joint_power" in loaded
    assert np.allclose(loaded["temporal_rates_hz"], arrays["temporal_rates_hz"])
    back = load_evidence(j, n)
    assert back["summary"]["profile_hash"] == raw["profile_hash"]


def test_resource_shape_growth_bounded():
    a, aa = run_mamse006(am_signal(5.0, SR, 5.0), CFG)
    b, bb = run_mamse006(am_signal(10.0, SR, 5.0), CFG)
    assert a["status"] == b["status"] == "OK"
    assert aa["joint_power"].shape == bb["joint_power"].shape
    assert b["modulation_segments"] <= a["modulation_segments"] * 4
