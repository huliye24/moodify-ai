"""Scan-level tests (DSK-MFY-AUDITORY-SCAN-001)."""

from __future__ import annotations


import pytest

from moodify.auditory.errors import (
    AuditoryScanInputNotFound,
)
from moodify.auditory.profiles import MFY_WSE_SCAN_PROFILE_001, get_profile
from moodify.auditory.service import scan_audio
from moodify.auditory.spectrogram import generate_spectrogram


def _scan(path, case="MFY-TEST", stage="before", tmp_path=None):
    return scan_audio(case, stage, path, tmp_path / f"{stage}_scan")


def test_both_spectrograms_generated(fx_stereo_sine, tmp_path):
    out = _scan(fx_stereo_sine, tmp_path=tmp_path)
    assert out.spectrograms["linear"].validated
    assert out.spectrograms["log"].validated
    assert (tmp_path / "before_scan" / "spectrum_linear.png").is_file()
    assert (tmp_path / "before_scan" / "spectrum_log.png").is_file()


def test_spectrogram_images_valid_png(fx_stereo_sine, tmp_path):
    out = _scan(fx_stereo_sine, tmp_path=tmp_path)
    for view in ("linear", "log"):
        png = tmp_path / "before_scan" / f"spectrum_{view}.png"
        data = png.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert out.spectrograms[view].sha256  # hashed


def test_metrics_schema_valid(fx_stereo_sine, tmp_path):
    out = _scan(fx_stereo_sine, tmp_path=tmp_path)
    for key in ("integrated_lufs", "true_peak_dbfs", "spectral_centroid_hz",
                "sub_20_60_hz", "stereo_correlation"):
        entry = out.metrics[key]
        assert {"value", "unit", "method", "status", "warnings"} <= set(entry)


def test_profile_hash_stable():
    h1 = MFY_WSE_SCAN_PROFILE_001.hash()
    h2 = get_profile("MFY-WSE-SCAN-PROFILE-001").hash()
    assert h1 == h2
    assert len(h1) == 64


def test_source_audio_unchanged(fx_stereo_sine, tmp_path):
    import hashlib
    before = hashlib.sha256(fx_stereo_sine.read_bytes()).hexdigest()
    _scan(fx_stereo_sine, tmp_path=tmp_path)
    after = hashlib.sha256(fx_stereo_sine.read_bytes()).hexdigest()
    assert before == after


def test_rerun_deterministic(fx_stereo_sine, tmp_path):
    out1 = _scan(fx_stereo_sine, tmp_path=tmp_path)
    out2 = _scan(fx_stereo_sine, stage="before2", tmp_path=tmp_path)
    assert out1.metrics["integrated_lufs"] == out2.metrics["integrated_lufs"]
    assert out1.metrics["spectral_centroid_hz"] == out2.metrics["spectral_centroid_hz"]
    assert out1.profile_hash == out2.profile_hash


def test_clipping_detected(fx_clipped, tmp_path):
    out = _scan(fx_clipped, tmp_path=tmp_path)
    assert out.metrics["clipping_sample_count"]["value"] > 0


def test_dc_offset_detected(fx_dc_offset, tmp_path):
    out = _scan(fx_dc_offset, tmp_path=tmp_path)
    assert abs(out.metrics["dc_offset_left"]["value"]) > 0.01


def test_mono_stereo_fields_null(fx_mono_sine, tmp_path):
    out = _scan(fx_mono_sine, tmp_path=tmp_path)
    assert out.metrics["stereo_correlation"]["value"] is None
    assert out.metrics["stereo_correlation"]["status"] == "UNAVAILABLE"
    assert out.metrics["phase_risk_ratio"]["value"] is None


def test_antiphase_risk_detected(fx_antiphase, tmp_path):
    out = _scan(fx_antiphase, tmp_path=tmp_path)
    assert out.metrics["stereo_correlation"]["value"] < -0.9
    assert out.metrics["phase_risk_ratio"]["value"] > 0.5


def test_frequency_cutoff_detected(fx_band_limited, tmp_path):
    out = _scan(fx_band_limited, tmp_path=tmp_path)
    cutoff = out.metrics["estimated_high_frequency_cutoff_hz"]["value"]
    assert 2000 < cutoff < 5000  # band-limited to ~3 kHz


def test_input_not_found(tmp_path):
    with pytest.raises(AuditoryScanInputNotFound):
        scan_audio("MFY-TEST", "before", tmp_path / "missing.wav", tmp_path / "s")


def test_corrupt_audio_fails_closed(fx_corrupt, tmp_path):
    from moodify.auditory.errors import AuditoryError
    with pytest.raises(AuditoryError):  # decode or spectrogram must fail closed
        _scan(fx_corrupt, tmp_path=tmp_path)


def test_spectrogram_unknown_view(fx_stereo_sine, tmp_path):
    from moodify.auditory.errors import SpectrogramGenerationFailed
    with pytest.raises(SpectrogramGenerationFailed):
        generate_spectrogram(fx_stereo_sine, tmp_path / "x.png", MFY_WSE_SCAN_PROFILE_001, "bogus")
