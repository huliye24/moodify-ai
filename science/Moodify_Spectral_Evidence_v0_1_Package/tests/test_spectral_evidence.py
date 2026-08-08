from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import soundfile as sf
import yaml

from moodify_spectral_evidence.analyzer import AnalysisParams, TrackSpec, analyze_track
from moodify_spectral_evidence.cli import cmd_build, cmd_validate


def _tone(path: Path, *, sr: int = 22050, seconds: float = 0.25, gain: float = 0.2) -> None:
    time = np.arange(int(sr * seconds), dtype=np.float64) / sr
    sf.write(path, gain * np.sin(2 * np.pi * 440 * time), sr, subtype="FLOAT")


def _spec(path: Path, before: Path, after: Path, track_id: str = "full_mix") -> None:
    path.write_text(yaml.safe_dump({
        "case_id": "case_test",
        "title": "Synthetic test",
        "tracks": [{
            "track_id": track_id,
            "role": "full_mix",
            "before": {"path": str(before)},
            "after": {"path": str(after)},
        }],
    }), encoding="utf-8")


def test_common_reference_exposes_gain_change(tmp_path: Path) -> None:
    before = tmp_path / "before.wav"
    after = tmp_path / "after.wav"
    _tone(before, gain=0.1)
    _tone(after, gain=0.2)
    metrics = analyze_track(
        TrackSpec("mix", "full_mix", str(before), str(after)),
        AnalysisParams(), tmp_path / "assets",
    )
    assert not metrics.errors
    assert metrics.rms_delta_db == 6.02
    assert metrics.spectral_diff_mean_db is not None
    assert metrics.spectral_diff_mean_db > 5.5


def test_sample_rate_mismatch_is_rejected_without_images(tmp_path: Path) -> None:
    before = tmp_path / "before.wav"
    after = tmp_path / "after.wav"
    _tone(before, sr=22050)
    _tone(after, sr=44100)
    output = tmp_path / "assets"
    metrics = analyze_track(
        TrackSpec("mix", "full_mix", str(before), str(after)), AnalysisParams(), output,
    )
    assert "sample-rate mismatch" in metrics.errors[0]
    assert not list(output.glob("*.png"))


def test_timeline_mismatch_is_rejected_without_images(tmp_path: Path) -> None:
    before = tmp_path / "before.wav"
    after = tmp_path / "after.wav"
    _tone(before, seconds=0.25)
    _tone(after, seconds=0.3)
    output = tmp_path / "assets"
    metrics = analyze_track(
        TrackSpec("mix", "full_mix", str(before), str(after)), AnalysisParams(), output,
    )
    assert "Timeline mismatch" in metrics.errors[0]
    assert not list(output.glob("*.png"))


def test_build_generates_complete_bundle_and_validates(tmp_path: Path) -> None:
    before = tmp_path / "before.wav"
    after = tmp_path / "after.wav"
    spec = tmp_path / "case.yaml"
    output = tmp_path / "bundle"
    _tone(before, gain=0.1)
    _tone(after, gain=0.15)
    _spec(spec, before, after)
    before_hash = before.read_bytes()
    after_hash = after.read_bytes()

    assert cmd_build(Namespace(case_spec=str(spec), output_dir=str(output))) == 0
    assert cmd_validate(Namespace(bundle_dir=str(output))) == 0
    assert before.read_bytes() == before_hash
    assert after.read_bytes() == after_hash
    assert (output / "spectral_evidence.xlsx").is_file()
    with ZipFile(output / "spectral_evidence.xlsx") as workbook:
        assert workbook.testzip() is None
        workbook_xml = workbook.read("xl/workbook.xml").decode("utf-8")
        for sheet in ("README", "Track_Summary", "Band_Comparison", "Time_Sections",
                      "Decision_Log", "Human_Review", "Data_Quality"):
            assert f'name="{sheet}"' in workbook_xml
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["parquet_status"] == "NOT_AVAILABLE_NO_PYARROW"
    assert "spectral_evidence.xlsx" in manifest["artifact_hashes"]


def test_validate_detects_artifact_tamper(tmp_path: Path) -> None:
    before = tmp_path / "before.wav"
    after = tmp_path / "after.wav"
    spec = tmp_path / "case.yaml"
    output = tmp_path / "bundle"
    _tone(before)
    _tone(after, gain=0.3)
    _spec(spec, before, after)
    assert cmd_build(Namespace(case_spec=str(spec), output_dir=str(output))) == 0
    (output / "track_summary.csv").write_text("tampered", encoding="utf-8")
    assert cmd_validate(Namespace(bundle_dir=str(output))) == 1


def test_invalid_track_id_does_not_create_output(tmp_path: Path) -> None:
    before = tmp_path / "before.wav"
    after = tmp_path / "after.wav"
    spec = tmp_path / "case.yaml"
    output = tmp_path / "bundle"
    _tone(before)
    _tone(after)
    _spec(spec, before, after, "../escape")
    assert cmd_build(Namespace(case_spec=str(spec), output_dir=str(output))) == 2
    assert not output.exists()
