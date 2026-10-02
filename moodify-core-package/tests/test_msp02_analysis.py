"""MSP/0.2 analyze job, report trio, and display-screen renderers."""

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from moodify.auditory.protocol_report import (
    REPORT_SCHEMA_VERSION,
    ReportError,
    _absolute_flags,
    build_protocol_report,
    write_report_bundle,
)
from moodify.auditory.report_render import render_report_html, render_report_markdown
from moodify.sound_protocol import PROTOCOL_V02, ProtocolError, validate_job
from moodify import release_cli

pytestmark = pytest.mark.v01


def _write_wav(tmp_path: Path) -> Path:
    sr = 22050
    samples = (np.sin(2 * np.pi * 440 * np.arange(sr * 2) / sr) * 0.1).astype("float32")
    path = tmp_path / "source.wav"
    sf.write(path, samples, sr)
    return path


def _analyze_job(tmp_path: Path):
    return {"protocol": PROTOCOL_V02, "type": "analyze", "source": "source.wav",
            "output_dir": "out"}


def _ffmpeg_ok() -> bool:
    from moodify.auditory.decode import _which_ffmpeg, _which_ffprobe

    try:
        _which_ffmpeg()
        _which_ffprobe()
    except Exception:
        return False
    return True


def test_v02_analyze_job_validation_exact_fields(tmp_path):
    source = tmp_path / "source.wav"
    source.write_bytes(b"test input")
    with pytest.raises(ProtocolError, match="type must be one of"):
        validate_job({**_analyze_job(tmp_path), "type": "listen"}, tmp_path)
    with pytest.raises(ProtocolError, match="must contain exactly"):
        validate_job({**_analyze_job(tmp_path), "preset": "clean_master"}, tmp_path)
    with pytest.raises(ProtocolError, match="must contain exactly"):
        validate_job({"protocol": PROTOCOL_V02, "type": "analyze",
                      "source": "source.wav"}, tmp_path)
    with pytest.raises(ProtocolError, match="must contain exactly"):
        validate_job({"protocol": PROTOCOL_V02, "type": "process",
                      "source": "source.wav", "output_dir": "out"}, tmp_path)
    job = validate_job(_analyze_job(tmp_path), tmp_path)
    assert job["protocol"] == PROTOCOL_V02
    assert job["source"] == str(source)
    assert "expected_output" not in job


def test_v01_job_still_validates_after_v02_dispatch(tmp_path):
    source = tmp_path / "source.wav"
    source.write_bytes(b"test input")
    legacy = {"protocol": "moodify.sound/0.1", "source": "source.wav",
              "preset": "clean_master", "output_dir": "out"}
    job = validate_job(legacy, tmp_path)
    assert job["protocol"] == "moodify.sound/0.1"
    assert job["expected_output"] == str(tmp_path / "out" / "source_clean_master.wav")


@pytest.mark.skipif(not _ffmpeg_ok(), reason="ffmpeg not available")
def test_v02_analyze_end_to_end(tmp_path, capsys):
    _write_wav(tmp_path)
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(_analyze_job(tmp_path)), encoding="utf-8")
    assert release_cli.main(["protocol", "process", str(job_path)]) == 0
    result = json.loads(capsys.readouterr().out)

    assert result["status"] == "analyzed_review_required"
    assert result["review_required"] is True
    assert result["plan_status"] == "DRAFT_PLAN_NOT_EXECUTED"
    assert result["judgment_boundary"]["layer3_musical_judgment"] == "NOT_PROMISED"
    case_root = Path(result["case_root"])
    for name in ("report.json", "report.md", "report.html"):
        assert (case_root / name).is_file(), name

    report = json.loads((case_root / "report.json").read_text(encoding="utf-8"))
    assert report["report_schema_version"] == REPORT_SCHEMA_VERSION
    assert report["job"]["type"] == "analyze"
    assert report["source"]["duration_s"] == pytest.approx(2.0, abs=0.2)
    by_id = {row["id"]: row for row in report["measurements"]}
    assert by_id["integrated_lufs"]["visibility"]
    # a pure sine has crest ~3 dB, so a WARNING here is expected behavior,
    # never an invented BLOCKING finding
    assert report["technical_state"]["overall"] in {"OK", "RISK", "PARTIAL"}
    html_text = (case_root / "report.html").read_text(encoding="utf-8")
    assert "data:image/png;base64," in html_text
    markdown = (case_root / "report.md").read_text(encoding="utf-8")
    assert "判断边界" in markdown and "DRAFT_PLAN_NOT_EXECUTED" in markdown


@pytest.mark.skipif(not _ffmpeg_ok(), reason="ffmpeg not available")
def test_cli_report_rerenders_without_touching_json(tmp_path, capsys):
    source = _write_wav(tmp_path)
    case_root = _analyzed_case_root(tmp_path, source)
    before = (case_root / "report.json").read_text(encoding="utf-8")
    (case_root / "report.html").unlink()
    assert release_cli.main(["report", str(case_root / "report.json")]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "rendered"
    assert (case_root / "report.html").is_file()
    assert (case_root / "report.json").read_text(encoding="utf-8") == before


def test_report_render_is_deterministic():
    report = _sample_report()
    first_md = render_report_markdown(report)
    second_md = render_report_markdown(report)
    assert first_md == second_md
    first_html = render_report_html(report, {"scan/spectrum_linear.png": b"png"})
    second_html = render_report_html(report, {"scan/spectrum_linear.png": b"png"})
    assert first_html == second_html


def test_html_escapes_and_embeds_spectrogram():
    report = _sample_report()
    report["source"]["name"] = "<script>alert(1)</script>.wav"
    text = render_report_html(report, {"scan/spectrum_linear.png": b"png"})
    assert "<script>" not in text
    assert "&lt;script&gt;" in text
    assert "data:image/png;base64," in text


def test_absolute_flags_and_plan_mapping():
    metrics = {
        "clipping_sample_count": {"value": 12, "unit": "samples", "status": "VALID"},
        "true_peak_dbfs": {"value": -0.2, "unit": "dBFS", "status": "VALID"},
        "crest_factor_db": {"value": 9.0, "unit": "dB", "status": "VALID"},
    }
    codes = {flag["code"] for flag in _absolute_flags(metrics)}
    assert codes == {"CLIPPING_PRESENT", "TRUE_PEAK_MARGIN_EXCEEDED"}

    from moodify.auditory.protocol_report import _findings, _plan

    findings = _findings(metrics)
    plan = _plan(findings, "song.wav")
    ops = [node["op"] for node in plan["nodes"]]
    assert ops == ["limiter"]  # clipping maps to a note, never an auto node
    assert any("CLIPPING_PRESENT" in note for note in plan["notes"])
    assert plan["nodes"][0]["evidence_refs"] == ["TRUE_PEAK_MARGIN_EXCEEDED"]
    assert plan["status"] == "DRAFT_PLAN_NOT_EXECUTED"


def test_clean_metrics_yield_no_nodes():
    from moodify.auditory.protocol_report import _findings, _plan

    metrics = {
        "clipping_sample_count": {"value": 0, "unit": "samples", "status": "VALID"},
        "true_peak_dbfs": {"value": -3.0, "unit": "dBFS", "status": "VALID"},
    }
    findings = _findings(metrics)
    plan = _plan(findings, "song.wav")
    assert findings == []
    assert plan["nodes"] == []
    assert plan["notes"] == []


def test_unavailable_metric_is_kept_with_null_value():
    metrics = {
        "loudness_range_lu": {"value": None, "unit": "LU", "method": "EBU3342",
                              "status": "UNAVAILABLE",
                              "warnings": ["insufficient duration (<6 s)"]},
    }
    from moodify.auditory.protocol_report import _measurements

    rows = _measurements(metrics)
    assert len(rows) == 1
    assert rows[0]["value"] is None
    assert rows[0]["status"] == "UNAVAILABLE"
    assert rows[0]["warnings"] == ["insufficient duration (<6 s)"]


def test_build_report_fails_closed_on_incomplete_case(tmp_path):
    with pytest.raises(ReportError, match="missing"):
        build_protocol_report(tmp_path)


def _analyzed_case_root(tmp_path: Path, source: Path) -> Path:
    from moodify.release import analyze_to_case

    out = tmp_path / "out"
    case = analyze_to_case(source, out)
    case_root = out / case["case"]["case_id"]
    write_report_bundle(case_root)
    return case_root


def _sample_report() -> dict:
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
        "measurements": [
            {"id": "integrated_lufs", "value": -14.2, "unit": "LUFS",
             "method": "BS1770", "status": "VALID", "warnings": [],
             "visibility": "能看到整体响度", "group": "loudness"},
            {"id": "loudness_range_lu", "value": None, "unit": "LU",
             "method": "EBU3342", "status": "UNAVAILABLE",
             "warnings": ["insufficient duration (<6 s)"], "group": "loudness"},
        ],
        "findings": [
            {"code": "CREST_FACTOR_COLLAPSE", "severity": "WARNING",
             "message": "crest factor collapsed", "metric": "crest_factor_db",
             "observed_value": 3.1, "unit": "dB",
             "classification": "TECHNICAL_RISK", "confidence": 0.9,
             "evidence_refs": ["metrics.json"], "check": "delta_rule"},
        ],
        "plan": {"status": "DRAFT_PLAN_NOT_EXECUTED", "nodes": [],
                 "next_actions": ["moodify protocol process <job.json>"],
                 "notes": []},
        "judgment_boundary": {
            "layer1_measurement": "EXECUTED", "layer2_comparison": "NOT_RUN",
            "layer3_musical_judgment": "NOT_PROMISED",
            "layer4_production_judgment": "NOT_PROMISED",
            "layer5_cultural_judgment": "NOT_PROMISED",
        },
        "technical_state": {"overall": "RISK", "workflow_decision": "REVIEW_RECOMMENDED",
                            "reasons": ["warning: CREST_FACTOR_COLLAPSE"]},
        "provenance": {"core_version": "1.0.0-rc.1",
                       "profile_id": "MFY-WSE-SCAN-PROFILE-001",
                       "profile_parameters_sha256": "sha256:abc",
                       "judgment_rules_version": "1.0", "ffmpeg": "unknown"},
    }
