"""Scientific listening stack regression fixtures.

MFY_EAR_SCIENTIFIC_LISTENING_STACK_001: cross sample-rate / channels / length
stability, layer metric presence, cost tiers, Machine Finding mapping.
Synthetic signals only.
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np
import pytest

from moodify.auditory.measurement_layers import (
    CostTier,
    Layer,
    layer_metric_keys,
    map_comparison_to_findings,
    map_metrics_to_findings,
    resolve_tier_profile,
)
from moodify.auditory.profiles import get_profile
from moodify.auditory.service import load_scan_evidence, scan_audio
from moodify.contracts.machine_finding import FindingType, FORBIDDEN_CONCLUSIONS


def _write_sine(path: Path, sr: int, seconds: float, channels: int = 1, freq: float = 440.0, amp: float = 0.25) -> Path:
    t = np.arange(int(sr * seconds)) / sr
    samples = (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    if channels == 2:
        samples = np.stack([samples, samples], axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((samples * 32767).astype(np.int16).tobytes())
    return path


@pytest.fixture()
def fixtures_dir(tmp_path: Path) -> Path:
    d = tmp_path / "fixtures"
    d.mkdir()
    _write_sine(d / "mono_44k_1s.wav", 44100, 1.0, 1)
    _write_sine(d / "mono_48k_5s.wav", 48000, 5.0, 1)
    _write_sine(d / "stereo_48k_2s.wav", 48000, 2.0, 2)
    return d


def _scan(path: Path, profile_id: str, tmp: Path) -> dict:
    case_id = f"case_{np.random.randint(0, 10**8):08x}"
    scan_dir = tmp / f"scan_{path.stem}_{profile_id.split('-')[-1]}"
    scan_dir.mkdir(parents=True, exist_ok=True)
    out = scan_audio(case_id, "before", path, scan_dir, get_profile(profile_id))
    return out.metrics


def test_cross_sample_rate_stability(fixtures_dir: Path, tmp_path: Path):
    """Same tone at 44.1k vs 48k must yield near-identical loudness/peak."""
    m44 = _scan(fixtures_dir / "mono_44k_1s.wav", "MFY-WSE-SCAN-PROFILE-001", tmp_path)
    m48 = _scan(fixtures_dir / "mono_48k_5s.wav", "MFY-WSE-SCAN-PROFILE-001", tmp_path)
    for key in ("integrated_lufs", "sample_peak_dbfs", "crest_factor_db"):
        assert abs(m44[key]["value"] - m48[key]["value"]) < 1.5, f"{key} drifted"


def test_stereo_metrics_present(fixtures_dir: Path, tmp_path: Path):
    m = _scan(fixtures_dir / "stereo_48k_2s.wav", "MFY-WSE-SCAN-PROFILE-001", tmp_path)
    assert m["channels"]["value"] == 2
    assert "dc_offset_left" in m and "dc_offset_right" in m
    assert m["dc_offset_right"]["status"] != "UNAVAILABLE"


def test_layer_metric_keys_defined():
    for layer in Layer:
        keys = layer_metric_keys(layer)
        assert keys, f"layer {layer} has no metrics"
    # WSE core keys present
    wse = layer_metric_keys(Layer.WSE)
    assert "integrated_lufs" in wse and "true_peak_dbfs" in wse


def test_cost_tiers_resolve():
    assert resolve_tier_profile(CostTier.FAST).profile_id == "MFY-WSE-SCAN-FAST-001"
    assert resolve_tier_profile(CostTier.STANDARD).profile_id == "MFY-WSE-SCAN-PROFILE-001"
    assert resolve_tier_profile(CostTier.DEEP).profile_id == "MFY-WSE-SCAN-DEEP-001"


def test_finding_mapping_allowed_only():
    metrics = {
        "clipping_sample_ratio": {"value": 0.001},
        "true_peak_dbfs": {"value": 0.3},
        "silence_ratio": {"value": 0.0},
        "spectral_flatness": {"value": 0.1},
    }
    findings = map_metrics_to_findings(metrics, domain="wse/loudness")
    types = {f["finding_type"] for f in findings}
    assert FindingType.CLIPPING_EVENT in types
    assert FindingType.TRUE_PEAK_EVENT in types
    # forbidden conclusions never appear
    assert not (types & {f for f in FORBIDDEN_CONCLUSIONS})


def test_finding_mapping_insufficient_evidence():
    metrics = {"silence_ratio": {"value": 0.995}, "clipping_sample_ratio": {"value": 0.0}}
    findings = map_metrics_to_findings(metrics, domain="mse")
    assert any(f["finding_type"] == FindingType.INSUFFICIENT_EVIDENCE for f in findings)


def test_comparison_mapping_baseline_deviation():
    delta = {"integrated_lufs": 2.5, "crest_factor_db": 0.3}
    findings = map_comparison_to_findings(delta, domain="ppe/ab")
    loudness = [f for f in findings if f["metric"] == "integrated_lufs"]
    assert loudness and loudness[0]["finding_type"] == FindingType.BASELINE_DEVIATION
    assert all(f["metric"] != "crest_factor_db" for f in findings if abs(f["value"]) < 1.0)
