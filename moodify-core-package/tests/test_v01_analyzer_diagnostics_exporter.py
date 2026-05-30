"""Tests for Moodify v0.1.0 analyzer, diagnostics, and exporter."""

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from moodify.v01_analyzer import analyze
from moodify.v01_diagnostics import diagnose
from moodify.v01_exporter import export
from moodify.v01_types import AudioMetrics, DiagnosisReport


@pytest.mark.v01
def test_v01_analyzer_returns_metrics_and_writes_spectrum_png(mock_wav, tmp_path):
    output_dir = tmp_path / "outputs"

    metrics = analyze(mock_wav, str(output_dir))

    assert isinstance(metrics, AudioMetrics)
    assert metrics.file_path == mock_wav
    assert metrics.sample_rate == 44100
    assert metrics.channels == 2
    assert metrics.duration_s == pytest.approx(10.0, rel=0.01)

    assert np.isfinite(metrics.rms_total)
    assert np.isfinite(metrics.rms_sub)
    assert np.isfinite(metrics.rms_bass)
    assert np.isfinite(metrics.rms_low_mid)
    assert np.isfinite(metrics.rms_mid)
    assert np.isfinite(metrics.rms_presence)
    assert np.isfinite(metrics.rms_air)
    assert np.isfinite(metrics.peak_db)
    assert np.isfinite(metrics.crest_factor)
    assert np.isfinite(metrics.dynamic_range_db)
    assert np.isfinite(metrics.correlation_lr)

    spectrum_path = output_dir / "test_spectrum.png"
    assert spectrum_path.exists()
    assert spectrum_path.stat().st_size > 0


@pytest.mark.v01
def test_v01_diagnostics_flags_weak_bass_and_presence():
    metrics = AudioMetrics(
        rms_sub=-35.0,
        rms_bass=-22.0,
        rms_presence=-22.0,
        rms_air=-35.0,
        crest_factor=4.0,
        dynamic_range_db=8.0,
        correlation_lr=0.5,
        channels=2,
    )

    report = diagnose(metrics)

    assert isinstance(report, DiagnosisReport)
    assert report.overall_health in {"good", "fair", "poor"}
    assert any("Sub-bass is very weak" in item for item in report.issues)
    assert any("Bass is very recessed" in item for item in report.issues)
    assert any("Presence band is weak" in item for item in report.issues)
    assert "warm_vocal" in report.suggested_presets


@pytest.mark.v01
def test_v01_diagnostics_flags_low_dynamic_range_and_suggests_clean_master():
    metrics = AudioMetrics(
        rms_sub=-12.0,
        rms_bass=-10.0,
        rms_presence=-10.0,
        rms_air=-20.0,
        crest_factor=1.5,
        dynamic_range_db=2.0,
        correlation_lr=0.5,
        channels=2,
    )

    report = diagnose(metrics)

    assert any("Very low crest factor" in item for item in report.issues)
    assert any("Dynamic range is very narrow" in item for item in report.issues)
    assert "clean_master" in report.suggested_presets


@pytest.mark.v01
def test_v01_diagnostics_flags_mono_like_stereo_and_suggests_wide_space():
    metrics = AudioMetrics(
        rms_sub=-12.0,
        rms_bass=-10.0,
        rms_presence=-10.0,
        rms_air=-20.0,
        crest_factor=4.0,
        dynamic_range_db=8.0,
        correlation_lr=0.99,
        channels=2,
    )

    report = diagnose(metrics)

    assert any("Almost mono stereo field" in item for item in report.issues)
    assert "wide_space" in report.suggested_presets


@pytest.mark.v01
def test_v01_diagnostics_good_case_has_clean_master_fallback():
    metrics = AudioMetrics(
        rms_sub=-12.0,
        rms_bass=-10.0,
        rms_presence=-10.0,
        rms_air=-18.0,
        crest_factor=4.0,
        dynamic_range_db=8.0,
        correlation_lr=0.5,
        channels=2,
    )

    report = diagnose(metrics)

    assert report.overall_health == "good"
    assert "clean_master" in report.suggested_presets
    assert any("Healthy crest factor" in item for item in report.strengths)
    assert any("Well-balanced stereo image" in item for item in report.strengths)


@pytest.mark.v01
def test_v01_exporter_writes_pcm16_wav_and_clamps_peak(tmp_path):
    sr = 44100
    t = np.arange(sr) / sr

    # Deliberately exceed 1.0 to verify peak clamp.
    audio = np.stack([
        1.5 * np.sin(2 * np.pi * 440 * t),
        1.5 * np.sin(2 * np.pi * 554 * t),
    ], axis=1).astype(np.float32)

    input_path = tmp_path / "source.wav"
    output_dir = tmp_path / "outputs"

    output_path = export(
        input_audio=audio,
        sr=sr,
        input_path=str(input_path),
        preset_key="clean_master",
        output_dir=str(output_dir),
    )

    output_path = Path(output_path)
    assert output_path.exists()
    assert output_path.name == "source_clean_master.wav"

    written, written_sr = sf.read(str(output_path), always_2d=True)
    assert written_sr == sr
    assert written.shape[1] == 2
    assert np.max(np.abs(written)) <= 1.0
