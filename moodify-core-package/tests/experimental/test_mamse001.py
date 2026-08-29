"""MAMSE-001 synthetic gates (T6) and engineering boundary tests.

Eight required gates: stationary sine, close-tone resolution, impulse
localization, chirp monotonicity, HF-cutoff ladder response, silence
sanitization, deterministic rerun, serialization round-trip. Plus the
A-section acceptance items (bin_hz traceability, frame-center clock
mapping, short-source honesty, zero-padding honesty).
"""

from __future__ import annotations

import numpy as np
import pytest

from moodify_experimental.mamse001 import (
    build_cross_resolution_evidence,
    compute_multiresolution_sketch,
    compute_resolution_sketch,
    get_resolution,
    load_case,
    registry_hash,
    run_case,
)

SR = 48000


def _sine(seconds: float, freq: float, gain: float = 0.3) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    return (gain * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _impulse(seconds: float, at_seconds: float, gain: float = 0.9) -> np.ndarray:
    x = np.zeros(int(seconds * SR), dtype=np.float32)
    x[int(at_seconds * SR)] = gain
    return x


def _chirp(seconds: float, f0: float, f1: float, gain: float = 0.3) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    inst = f0 + (f1 - f0) * t / (seconds + 1e-9)
    return (gain * np.sin(2 * np.pi * np.cumsum(inst) / SR)).astype(np.float32)


def _lowpass_cutoff(x: np.ndarray, cutoff_hz: float) -> np.ndarray:
    from scipy.signal import butter, lfilter

    b, a = butter(6, cutoff_hz / (SR / 2))
    return lfilter(b, a, x).astype(np.float32)


# ---------------------------------------------------------------------------
# A. Mathematical correctness
# ---------------------------------------------------------------------------

def test_bin_hz_traceable():
    spec = get_resolution("R3")
    assert spec.bin_hz(SR) == pytest.approx(SR / spec.n_fft)


def test_frame_center_maps_to_sample_clock():
    x = _sine(2.0, 1000.0)
    sk = compute_resolution_sketch(x, SR, get_resolution("R0"))
    centers = sk["frame_centers_ms"]
    spec = get_resolution("R0")
    assert len(centers) > 0
    expected_first = 1000.0 * (spec.n_fft / 2) / SR
    assert centers[0] == pytest.approx(expected_first)
    assert centers[1] - centers[0] == pytest.approx(spec.hop_ms(SR))


def test_short_source_does_not_fake_r3():
    x = _sine(0.3, 1000.0)  # 14400 samples < R3 n_fft 32768
    sk = compute_resolution_sketch(x, SR, get_resolution("R3"))
    assert sk["n_frames"] == 0
    assert sk["values"].shape == (0, len(sk["feature_names"]))
    assert not np.isnan(sk["values"]).any()


def test_zero_padding_not_sold_as_resolution():
    x = _sine(1.0, 1000.0)
    sk = compute_resolution_sketch(x, SR, get_resolution("R0"))
    assert sk["dense_spectrogram_retained"] is False


# ---------------------------------------------------------------------------
# B. Synthetic gates
# ---------------------------------------------------------------------------

def test_stationary_1000hz_localization_r3_better_than_r0():
    x = _sine(3.0, 1000.0)
    errs = {}
    for rid in ("R0", "R1", "R2", "R3"):
        sk = compute_resolution_sketch(x, SR, get_resolution(rid))
        dom = sk["values"][:, sk["feature_names"].index("dominant_frequency_hz")]
        errs[rid] = float(np.abs(np.median(dom) - 1000.0))
    assert errs["R3"] < errs["R0"]


def test_close_tone_peak_gap_r3_better_than_r0():
    x = _sine(4.0, 1000.0) + _sine(4.0, 1030.0)
    gaps = {}
    for rid in ("R0", "R1", "R2", "R3"):
        sk = compute_resolution_sketch(x, SR, get_resolution(rid))
        gap = sk["values"][:, sk["feature_names"].index("peak_gap_hz")]
        gaps[rid] = float(np.median(gap))
    # True gap is 30 Hz; R3 must be far closer than R0.
    assert abs(gaps["R3"] - 30.0) < abs(gaps["R0"] - 30.0)


def test_impulse_temporal_localization_r0_better_than_r3():
    x = _impulse(2.0, 1.0)
    errs = {}
    for rid in ("R0", "R3"):
        sk = compute_resolution_sketch(x, SR, get_resolution(rid))
        centers = sk["frame_centers_ms"]
        rms = sk["values"][:, sk["feature_names"].index("rms_dbfs")]
        if len(centers) == 0:
            errs[rid] = float("inf")
            continue
        idx = int(np.argmax(rms))
        errs[rid] = abs(centers[idx] - 1000.0)
    assert errs["R0"] < errs["R3"]


def test_chirp_monotonic_trajectory_consistent_across_r():
    x = _chirp(4.0, 200.0, 8000.0)
    for rid in ("R0", "R1", "R2", "R3"):
        sk = compute_resolution_sketch(x, SR, get_resolution(rid))
        if sk["n_frames"] < 4:
            continue
        dom = sk["values"][:, sk["feature_names"].index("dominant_frequency_hz")]
        finite = dom[np.isfinite(dom)]
        # dominant frequency should trend upward for a rising chirp
        half = len(finite) // 2
        assert np.median(finite[half:]) > np.median(finite[:half])


def test_hf_cutoff_ladder_r2_r3_stable_response():
    noise_rng = np.random.default_rng(42)
    noise = (0.2 * noise_rng.standard_normal(int(4 * SR))).astype(np.float32)
    base = _lowpass_cutoff(noise, 16000.0)
    half = _lowpass_cutoff(noise, 8000.0)
    responses = {}
    for label, sig in (("full", base), ("half", half)):
        responses[label] = {}
        for rid in ("R2", "R3"):
            sk = compute_resolution_sketch(sig, SR, get_resolution(rid))
            flat = sk["values"][:, sk["feature_names"].index("spectral_flatness")]
            responses[label][rid] = float(np.median(flat))
    for rid in ("R2", "R3"):
        # the sharper cutoff leaves more near-zero out-of-band bins, so the
        # geometric-mean flatness drops; both resolutions must respond in the
        # same direction
        assert responses["half"][rid] < responses["full"][rid]


def test_silence_no_nan_inf_contamination():
    x = np.zeros(int(2 * SR), dtype=np.float32)
    multi = compute_multiresolution_sketch(x, SR)
    for rid, sk in multi["resolutions"].items():
        if sk["n_frames"] == 0:
            continue
        v = sk["values"]
        assert not np.isnan(v).any()
        assert not np.isinf(v).any()


def test_deterministic_rerun():
    x = _sine(2.0, 1000.0) + _impulse(2.0, 1.0)
    a = compute_multiresolution_sketch(x, SR)
    b = compute_multiresolution_sketch(x, SR)
    for rid in a["resolutions"]:
        assert np.array_equal(a["resolutions"][rid]["values"], b["resolutions"][rid]["values"])
    assert registry_hash() == registry_hash()


def test_serialization_round_trip(tmp_path):
    x = _sine(2.0, 1000.0) + 0.1 * _sine(2.0, 1030.0)
    multi = compute_multiresolution_sketch(x, SR)
    result = run_case(x, SR, tmp_path)
    assert (tmp_path / "mamse001_manifest.json").exists()
    assert (tmp_path / "mamse001_planes.npz").exists()
    assert (tmp_path / "cross_resolution_evidence.json").exists()
    manifest = result["manifest"]
    assert manifest["operator_id"] == "MAMSE-001"
    assert manifest["git_commit"] and len(manifest["git_commit"]) == 40
    assert manifest["fft_backend"]["backend"] == "numpy.fft.rfft"
    assert manifest["resolution_registry"]["hash"] == registry_hash()

    loaded = load_case(tmp_path / "mamse001_manifest.json", tmp_path / "mamse001_planes.npz")
    for rid in multi["resolutions"]:
        assert loaded["resolutions"][rid]["values"].shape == multi["resolutions"][rid]["values"].shape
        assert np.array_equal(loaded["resolutions"][rid]["values"], multi["resolutions"][rid]["values"])


# ---------------------------------------------------------------------------
# Engineering boundaries
# ---------------------------------------------------------------------------

def test_no_dense_spectrogram_retained():
    x = _sine(3.0, 1000.0)
    multi = compute_multiresolution_sketch(x, SR)
    for rid, sk in multi["resolutions"].items():
        assert sk["dense_spectrogram_retained"] is False
        assert sk["payload_bytes"] < sk["n_frames"] * 100  # sketch is fixed-width


def test_cross_resolution_conflicts_preserved_not_averaged():
    # transient chirp burst creates fine/coarse disagreement at the burst
    x = np.zeros(int(4 * SR), dtype=np.float32)
    x[1 * SR: int(1.5 * SR)] = _chirp(0.5, 1000.0, 6000.0)
    multi = compute_multiresolution_sketch(x, SR)
    ev = build_cross_resolution_evidence(multi)
    assert ev["schema_version"].startswith("mamse-001-evidence")
    assert isinstance(ev["conflicts"], list)
    assert "interpretation_policy" in ev
    # band spread must be per-band, not a single number
    assert all(v["samples"] >= 0 for v in ev["band_cross_resolution_spread"].values())


def test_resolution_ids_and_feature_schema_versioned():
    x = _sine(1.0, 1000.0)
    multi = compute_multiresolution_sketch(x, SR)
    assert set(multi["resolutions"]) == {"R0", "R1", "R2", "R3"}
    for rid in ("R0", "R1", "R2", "R3"):
        assert multi["resolutions"][rid]["resolution_id"] == rid
    assert multi["schema_version"].startswith("mamse-001-sketch-features")
    # band source must be the canonical registry, not a copy
    assert "feature_registry.BANDS" in multi["band_source"]
