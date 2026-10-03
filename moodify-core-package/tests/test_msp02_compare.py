"""MSP/0.2 compare jobs: reference-vs-candidate comparison (Layer B, L2)."""

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf
from jsonschema import validate as jsonschema_validate

from moodify.auditory.comparison import (
    ScanEvidence,
    validate_compare_pair,
    validate_pair,
)
from moodify.auditory.protocol_report import (
    L2_VISIBILITY_NOTE,
    MSP_REPORT_SCHEMA,
    REPORT_SCHEMA_VERSION,
)
from moodify.sound_protocol import PROTOCOL_V02, ProtocolError, validate_job
from moodify import release_cli

pytestmark = pytest.mark.v01


def _write_wav(path: Path, seconds: float = 2.0, amplitude: float = 0.1,
               channels: int = 1) -> Path:
    sr = 22050
    t = np.arange(int(sr * seconds)) / sr
    wave = np.sin(2 * np.pi * 440 * t) * amplitude
    if channels == 2:
        wave = np.stack([wave, wave], axis=1)
    sf.write(path, wave.astype("float32"), sr)
    return path


def _compare_job(tmp_path: Path, *, candidate: str = "candidate.wav",
                 reference: str = "reference.wav") -> dict:
    return {"protocol": PROTOCOL_V02, "type": "compare", "source": candidate,
            "reference": reference, "output_dir": "out"}


def _ffmpeg_ok() -> bool:
    from moodify.auditory.decode import _which_ffmpeg, _which_ffprobe

    try:
        _which_ffmpeg()
        _which_ffprobe()
    except Exception:
        return False
    return True


def test_compare_job_validation_exact_fields(tmp_path):
    candidate = tmp_path / "candidate.wav"
    candidate.write_bytes(b"x")
    reference = tmp_path / "reference.wav"
    reference.write_bytes(b"x")
    with pytest.raises(ProtocolError, match="must contain exactly"):
        validate_job({**_compare_job(tmp_path), "preset": "clean_master"}, tmp_path)
    with pytest.raises(ProtocolError, match="must contain exactly"):
        validate_job({"protocol": PROTOCOL_V02, "type": "compare",
                      "source": "candidate.wav", "output_dir": "out"}, tmp_path)
    with pytest.raises(ProtocolError, match="reference is not a file"):
        validate_job(_compare_job(tmp_path, reference="missing.wav"), tmp_path)
    with pytest.raises(ProtocolError, match="must be different"):
        validate_job(_compare_job(tmp_path, reference="candidate.wav"), tmp_path)

    job = validate_job(_compare_job(tmp_path), tmp_path)
    assert job["type"] == "compare"
    assert job["reference"] == str(reference)
    assert job["source"] == str(candidate)


def test_validate_pair_semantics_unchanged():
    """Same-case validate_pair still enforces equal case IDs; the protocol
    compare check allows independent cases but keeps the protective checks."""
    def _ev(case_id: str, profile_hash: str = "p1", duration: float = 10.0,
            channels: int = 2) -> ScanEvidence:
        return ScanEvidence(
            case_id=case_id, profile=None, profile_hash=profile_hash,
            duration_s=duration, channels=channels, metrics={}, timeline=[],
            arrays={},
        )

    same_case_a = _ev("case_a")
    same_case_b = _ev("case_a")
    validate_pair(same_case_a, same_case_b)
    checks = validate_compare_pair(_ev("case_a"), _ev("case_b"))
    assert checks == {"profile_hash_match": True, "duration_within_tolerance": True,
                      "channels_match": True, "duration_tolerance_s": 0.05}

    with pytest.raises(Exception, match="case IDs differ"):
        validate_pair(_ev("case_a"), _ev("case_b"))
    from moodify.auditory.errors import (
        ComparisonChannelMismatch,
        ComparisonDurationMismatch,
        ScanProfileMismatch,
    )
    with pytest.raises(ComparisonDurationMismatch):
        validate_compare_pair(_ev("case_a", duration=10.0), _ev("case_b", duration=11.0))
    with pytest.raises(ComparisonChannelMismatch):
        validate_compare_pair(_ev("case_a", channels=2), _ev("case_b", channels=1))
    with pytest.raises(ScanProfileMismatch):
        validate_compare_pair(_ev("case_a", profile_hash="p1"),
                              _ev("case_b", profile_hash="p2"))


@pytest.mark.skipif(not _ffmpeg_ok(), reason="ffmpeg not available")
def test_compare_end_to_end_loudness_offset(tmp_path, capsys):
    _write_wav(tmp_path / "reference.wav", seconds=2.0, amplitude=0.1)
    _write_wav(tmp_path / "candidate.wav", seconds=2.0, amplitude=0.2)
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(_compare_job(tmp_path)), encoding="utf-8")
    assert release_cli.main(["protocol", "process", str(job_path)]) == 0
    result = json.loads(capsys.readouterr().out)

    assert result["status"] == "compared_review_required"
    assert result["judgment_boundary"]["layer2_comparison"] == "EXECUTED"
    assert result["judgment_boundary"]["layer3_musical_judgment"] == "NOT_PROMISED"
    assert result["loudness_normalization"]["valid"] is True

    compare_root = Path(result["compare_root"])
    for name in ("report.json", "report.md", "report.html",
                 "delta_spectrum_linear.png", "delta_spectrum_log.png"):
        assert (compare_root / name).is_file(), name

    report = json.loads((compare_root / "report.json").read_text(encoding="utf-8"))
    assert report["job"]["type"] == "compare"
    assert report["comparison"]["reference"]["case_id"] == result["reference_case_id"]
    deltas = {row["id"]: row for row in report["comparison"]["metric_deltas"]}
    lufs = deltas["integrated_lufs"]
    assert lufs["direction"] == "INCREASE"
    assert lufs["absolute_delta"] == pytest.approx(6.02, abs=0.15)
    assert report["comparison"]["loudness_normalization"]["gain_db"] == pytest.approx(
        -6.02, abs=0.15)
    assert deltas["integrated_lufs"]["visibility"]  # blind-spot declaration carried
    html_text = (compare_root / "report.html").read_text(encoding="utf-8")
    assert "对比层" in html_text
    assert html_text.count("data:image/png;base64,") >= 6  # 2 candidate + 2 reference + 2 delta
    assert "delta_spectrum" in (compare_root / "report.md").read_text(encoding="utf-8")


@pytest.mark.skipif(not _ffmpeg_ok(), reason="ffmpeg not available")
def test_compare_duration_mismatch_fails_closed(tmp_path, capsys):
    _write_wav(tmp_path / "reference.wav", seconds=2.0)
    _write_wav(tmp_path / "candidate.wav", seconds=2.5)
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(_compare_job(tmp_path)), encoding="utf-8")
    # the CLI converts ProtocolError to exit code 2 with JSON on stderr
    assert release_cli.main(["protocol", "process", str(job_path)]) == 2
    assert "duration mismatch" in capsys.readouterr().err


@pytest.mark.skipif(not _ffmpeg_ok(), reason="ffmpeg not available")
def test_compare_channel_mismatch_fails_closed(tmp_path, capsys):
    _write_wav(tmp_path / "reference.wav", seconds=2.0, channels=1)
    _write_wav(tmp_path / "candidate.wav", seconds=2.0, channels=2)
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(_compare_job(tmp_path)), encoding="utf-8")
    assert release_cli.main(["protocol", "process", str(job_path)]) == 2
    assert "channel mismatch" in capsys.readouterr().err


@pytest.mark.skipif(not _ffmpeg_ok(), reason="ffmpeg not available")
def test_compare_rerender_via_cli_byte_identical(tmp_path, capsys):
    _write_wav(tmp_path / "reference.wav", seconds=2.0, amplitude=0.1)
    _write_wav(tmp_path / "candidate.wav", seconds=2.0, amplitude=0.2)
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(_compare_job(tmp_path)), encoding="utf-8")
    assert release_cli.main(["protocol", "process", str(job_path)]) == 0
    capsys.readouterr()

    # locate the single compare dir under out/
    compare_roots = [p for p in (tmp_path / "out").iterdir() if p.name.startswith("compare_")]
    assert len(compare_roots) == 1
    compare_root = compare_roots[0]
    before_md = (compare_root / "report.md").read_text(encoding="utf-8")
    before_html = (compare_root / "report.html").read_bytes()
    (compare_root / "report.html").unlink()
    assert release_cli.main(["report", str(compare_root / "report.json")]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "rendered"
    assert (compare_root / "report.md").read_text(encoding="utf-8") == before_md
    assert (compare_root / "report.html").read_bytes() == before_html


def _sample_analyze_report() -> dict:
    return {
        "protocol": "moodify.sound/0.2",
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "generated_at": "2026-10-02T00:00:00+00:00",
        "job": {"type": "analyze", "source": "song.wav"},
        "case": {"case_id": "case-001"},
        "source": {"name": "song.wav", "sha256": "sha256:abc", "duration_s": 12.5,
                   "channels": 2, "sample_rate": 44100},
        "representation": {"profile": "MFY-WSE-SCAN-PROFILE-001",
                           "spectrograms": ["scan/spectrum_linear.png"],
                           "timeline_path": None, "timeline_windows": None,
                           "stft_arrays": None},
        "measurements": [],
        "findings": [],
        "plan": {"status": "DRAFT_PLAN_NOT_EXECUTED", "nodes": [],
                 "next_actions": [], "notes": []},
        "judgment_boundary": {
            "layer1_measurement": "EXECUTED", "layer2_comparison": "NOT_RUN",
            "layer3_musical_judgment": "NOT_PROMISED",
            "layer4_production_judgment": "NOT_PROMISED",
            "layer5_cultural_judgment": "NOT_PROMISED",
        },
        "technical_state": {"overall": "OK", "workflow_decision":
                            "NO_TECHNICAL_BLOCKERS", "reasons": []},
        "provenance": {"core_version": "1.0.0-rc.1",
                       "profile_id": "MFY-WSE-SCAN-PROFILE-001",
                       "profile_parameters_sha256": "sha256:abc",
                       "judgment_rules_version": "1.0", "ffmpeg": "unknown"},
    }


def _sample_comparison() -> dict:
    return {
        "reference": {"name": "ref.wav", "sha256": "sha256:def",
                      "case_id": "case-000", "case_root": "/tmp/case-000",
                      "duration_s": 12.5, "channels": 2, "sample_rate": 44100},
        "loudness_normalization": {"gain_db": -6.02, "valid": True,
                                   "method": "gain-to-before-LUFS"},
        "metric_deltas": [
            {"id": "integrated_lufs", "before": -20.1, "after": -14.08,
             "absolute_delta": 6.02, "relative_delta": 0.299, "unit": "LUFS",
             "direction": "INCREASE", "visibility": "能看到整体响度",
             "group": "loudness"},
        ],
        "band_deltas": {"raw": {"bass_60_120_hz": 0.01}, "normalized": {}},
        "delta_spectrograms": ["delta_spectrum_linear.png", "delta_spectrum_log.png"],
        "pair_checks": {"profile_hash_match": True, "duration_within_tolerance": True,
                        "channels_match": True, "duration_tolerance_s": 0.05},
        "visibility_note": L2_VISIBILITY_NOTE,
    }


def _compare_report_fixture() -> dict:
    report = _sample_analyze_report()
    report["job"]["type"] = "compare"
    report["case"]["case_root"] = "/tmp/case-001"
    report["comparison"] = _sample_comparison()
    report["judgment_boundary"]["layer2_comparison"] = "EXECUTED"
    return report


def test_schema_analyze_report_rejects_comparison_section():
    jsonschema_validate(_sample_analyze_report(), MSP_REPORT_SCHEMA)
    polluted = _sample_analyze_report()
    polluted["comparison"] = _sample_comparison()
    with pytest.raises(Exception):
        jsonschema_validate(polluted, MSP_REPORT_SCHEMA)


def test_schema_compare_report_requires_comparison_section():
    jsonschema_validate(_compare_report_fixture(), MSP_REPORT_SCHEMA)
    missing = _compare_report_fixture()
    missing.pop("comparison")
    with pytest.raises(Exception):
        jsonschema_validate(missing, MSP_REPORT_SCHEMA)


def test_compare_render_deterministic():
    from moodify.auditory.report_render import render_report_html, render_report_markdown

    report = _compare_report_fixture()
    images = {"delta_spectrum_linear.png": b"png",
              "delta_spectrum_log.png": b"png",
              "reference/scan/spectrum_linear.png": b"png",
              "reference/scan/spectrum_log.png": b"png"}
    assert render_report_markdown(report) == render_report_markdown(report)
    assert render_report_html(report, images) == render_report_html(report, images)
    markdown = render_report_markdown(report)
    assert "对比层（L2）" in markdown and "INCREASE" in markdown
    html_text = render_report_html(report, images)
    assert "参考频谱" in html_text and "Δ 频谱" in html_text
