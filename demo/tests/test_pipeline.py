"""End-to-end demo pipeline test on synthetic audio (no bundled assets needed)."""

import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from demo.analyzer.pipeline import run_analysis          # noqa: E402
from demo.report.generator import (                      # noqa: E402
    render_markdown,
    render_terminal,
    write_json,
    write_markdown,
)
from engine.report_schema.schema import validate_report_dict  # noqa: E402


@pytest.fixture(scope="module")
def synthetic_track(tmp_path_factory) -> Path:
    """Music-like synthetic stereo track with real dynamics."""
    out = tmp_path_factory.mktemp("audio") / "synthetic_demo.wav"
    sr = 44100
    t = np.linspace(0, 12, sr * 12, endpoint=False)
    rng = np.random.default_rng(7)
    sig = (0.25 * np.sin(2 * np.pi * 98 * t)
           + 0.18 * np.sin(2 * np.pi * 196 * t)
           + 0.10 * np.sin(2 * np.pi * 392 * t)
           + 0.03 * rng.standard_normal(len(t)))
    dyn = 1 + 0.5 * np.sin(2 * np.pi * 0.15 * t)
    x = np.clip(sig * dyn, -0.9, 0.9)
    right = 0.92 * x + 0.05 * rng.standard_normal(len(t))
    stereo = np.column_stack([x, right]).astype(np.float32)
    sf.write(str(out), stereo, sr)
    return out


def test_pipeline_produces_valid_report(synthetic_track):
    report = run_analysis(synthetic_track)
    data = report.to_dict()
    assert validate_report_dict(data) == []
    assert 0 <= report.quality_score.overall <= 100
    assert report.track_info.file_name == "synthetic_demo.wav"
    assert report.audio_features.loudness["integrated_lufs"] is not None


def test_markdown_and_terminal_render(synthetic_track):
    report = run_analysis(synthetic_track)
    md = render_markdown(report)
    term = render_terminal(report)
    assert "# Moodify Intelligence Report" in md
    assert "Moodify Intelligence Report" in term
    assert "Overall Score" in term
    assert report.commercial_insight.summary[:30] in md


def test_writers_create_files(synthetic_track, tmp_path):
    report = run_analysis(synthetic_track)
    json_path = write_json(report, tmp_path)
    md_path = write_markdown(report, tmp_path)
    assert json_path.exists() and md_path.exists()
    assert json_path.stat().st_size > 500
    assert md_path.stat().st_size > 500
