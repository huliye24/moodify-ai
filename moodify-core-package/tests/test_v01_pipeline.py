"""End-to-end tests for Moodify v0.1.0 pipeline."""

import json
from pathlib import Path

import pytest
import soundfile as sf

from moodify.v01_pipeline import process_audio
from moodify.v01_presets import list_presets


@pytest.mark.v01
def test_v01_pipeline_processes_mock_wav_end_to_end(mock_wav, tmp_path):
    output_dir = tmp_path / "outputs"

    result = process_audio(
        input_path=mock_wav,
        preset="clean_master",
        output_dir=str(output_dir),
    )

    assert result.success is True
    assert result.error == ""
    assert result.preset == "clean_master"

    output_path = Path(result.output_path)
    assert output_path.exists()
    assert output_path.suffix == ".wav"

    audio, sr = sf.read(str(output_path), always_2d=True)
    assert sr == 44100
    assert audio.shape[0] > 0
    assert audio.shape[1] == 2

    spectrum_path = output_dir / "test_spectrum.png"
    assert spectrum_path.exists()
    assert spectrum_path.stat().st_size > 0

    report_path = Path(str(output_path).replace(".wav", "_report.json"))
    assert report_path.exists()

    with report_path.open("r", encoding="utf-8") as f:
        report = json.load(f)

    assert report["preset"] == "clean_master"
    assert "overall_health" in report
    assert "issues" in report
    assert "strengths" in report
    assert "suggested_presets" in report
    assert "metrics" in report


@pytest.mark.v01
@pytest.mark.parametrize("preset", list_presets())
def test_v01_pipeline_supports_all_presets(mock_wav, tmp_path, preset):
    output_dir = tmp_path / f"outputs_{preset}"

    result = process_audio(
        input_path=mock_wav,
        preset=preset,
        output_dir=str(output_dir),
    )

    assert result.success is True
    assert result.preset == preset
    assert Path(result.output_path).exists()
    assert Path(result.output_path).name == f"test_{preset}.wav"


@pytest.mark.v01
def test_v01_pipeline_rejects_missing_file(tmp_path):
    missing = tmp_path / "missing.wav"

    result = process_audio(
        input_path=str(missing),
        preset="clean_master",
        output_dir=str(tmp_path / "outputs"),
    )

    assert result.success is False
    assert "File not found" in result.error


@pytest.mark.v01
def test_v01_pipeline_rejects_unknown_preset(mock_wav, tmp_path):
    result = process_audio(
        input_path=mock_wav,
        preset="not_a_real_preset",
        output_dir=str(tmp_path / "outputs"),
    )

    assert result.success is False
    assert "Unknown preset" in result.error
    assert "warm_vocal" in result.error
    assert "clean_master" in result.error
    assert "wide_space" in result.error
