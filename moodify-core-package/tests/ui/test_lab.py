"""Moodify Lab — observation view model, catalog honesty, compare path.

Headless discipline: the pure parts are pinned (case provenance assembly,
compare view model, capability catalog honesty); the Tk frames are exercised
by the human on the desktop. The compare integration test walks the real
0.2 validate/execute path on tiny synthetic audio — no new DSP, no new
thresholds.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from moodify.ui.lab import (
    CAPABILITY_CATALOG,
    build_compare_view_model,
    load_case_provenance,
    run_compare,
)

pytestmark = pytest.mark.v01


def _write_case(tmp_path: Path) -> Path:
    case_root = tmp_path / "case_x1"
    (case_root / "scan").mkdir(parents=True)
    (case_root / "report.json").write_text(json.dumps({
        "protocol": "moodify.sound/0.2", "generated_at": "2026-10-02T00:00:00+00:00",
        "case": {"case_id": "case_x1"}, "job": {"type": "analyze"},
        "source": {"name": "song.flac"},
        "representation": {"timeline_windows": 344,
                           "stft_arrays": "scan/analysis_data.npz"},
    }, ensure_ascii=False), encoding="utf-8")
    (case_root / "scan" / "scan_manifest.json").write_text(json.dumps({
        "stage": "source", "input_sha256": "a" * 64,
        "scan_profile_id": "MFY-WSE-SCAN-PROFILE-001",
        "artifacts": {"metrics": {"path": "scan/metrics.json"}},
    }), encoding="utf-8")
    (case_root / "evidence.json").write_text(json.dumps([
        {"artifact_type": "metrics", "logical_path": "measurements.json",
         "content_hash": "sha256:" + "b" * 64, "created_at": "2026-10-02T00:00:00Z",
         "size_bytes": 1234},
    ]), encoding="utf-8")
    (case_root / "judgment_rules.json").write_text(json.dumps({
        "judgment_rules_version": "1.1",
        "universal_thresholds": {"new_clipping": {"metric": "clipping_sample_count",
                                                  "max_count": 0}},
    }), encoding="utf-8")
    return case_root


def test_load_case_provenance_assembles_persisted_facts(tmp_path):
    prov = load_case_provenance(_write_case(tmp_path))
    assert prov["exists"] is True
    assert prov["case_id"] == "case_x1"
    assert prov["job_type"] == "analyze"
    assert prov["profile_id"] == "MFY-WSE-SCAN-PROFILE-001"
    assert prov["input_sha256"] == "a" * 18
    assert prov["evidence"][0]["artifact_type"] == "metrics"
    assert prov["evidence"][0]["hash"] == ("sha256:" + "b" * 64)[:18]
    assert prov["artifacts"] == [{"name": "metrics", "path": "scan/metrics.json"}]
    assert prov["representation"]["timeline_windows"] == 344


def test_load_case_provenance_survives_damage(tmp_path):
    empty = tmp_path / "case_empty"
    empty.mkdir()
    prov = load_case_provenance(empty)
    assert prov["exists"] is False
    assert prov["evidence"] == [] and prov["rules"] == [] and prov["artifacts"] == []

    corrupt = tmp_path / "case_bad"
    corrupt.mkdir()
    (corrupt / "evidence.json").write_text("[broken", encoding="utf-8")
    assert load_case_provenance(corrupt)["evidence"] == []


def test_rules_render_metric_and_limit_text(tmp_path):
    prov = load_case_provenance(_write_case(tmp_path))
    assert prov["rules"] == [{"id": "new_clipping",
                              "text": "metric=clipping_sample_count max_count=0"}]


def test_capability_catalog_is_honest():
    allowed = {"CANONICAL", "EXPERIMENTAL", "EXPERIMENTAL_ACCEPTED", "READY",
               "LEGACY", "HISTORICAL", "ABSENT", "UNRESOLVED"}
    assert len(CAPABILITY_CATALOG) >= 5
    for cap in CAPABILITY_CATALOG:
        assert set(cap) == {"name", "domain", "status", "what", "entry"}
        assert cap["status"] in allowed
        assert cap["what"] and cap["entry"]
    # only the two surfaces reachable from this window may claim the lab
    lab_entries = [c for c in CAPABILITY_CATALOG if "本实验台" in c["entry"]]
    assert {c["name"] for c in lab_entries} <= {"0.2 analyze 作业", "0.2 compare 作业"}


def _compare_report() -> dict:
    return {
        "protocol": "moodify.sound/0.2",
        "source": {"name": "candidate.wav"},
        "comparison": {
            "reference": {"name": "reference.wav", "sha256": "sha256:" + "c" * 64},
            "loudness_normalization": {"gain_db": -0.65, "valid": True,
                                       "method": "integrated_lufs"},
            "metric_deltas": [
                {"id": "integrated_lufs", "before": -15.56, "after": -14.21,
                 "absolute_delta": 1.35, "relative_delta": None,
                 "unit": "LUFS", "direction": "up"},
                {"id": "true_peak_dbfs", "before": -1.17, "after": -0.4,
                 "absolute_delta": 0.77, "unit": "dBFS", "direction": "up"},
            ],
            "delta_spectrograms": ["delta_spectrum_linear.png"],
            "pair_checks": {"profile_hash_match": True,
                            "duration_within_tolerance": True,
                            "channels_match": True,
                            "duration_tolerance_s": 2.0},
            "visibility_note": "delta 只描述不评级",
        },
    }


def test_compare_view_model_maps_rows_checks_and_reference():
    model = build_compare_view_model(_compare_report())
    assert model["candidate"] == "candidate.wav"
    assert model["reference_name"] == "reference.wav"
    assert model["normalization"] == "-0.65 dB" and model["normalization_valid"]
    assert model["rows"][0] == {"id": "integrated_lufs", "before": "-15.56",
                                "after": "-14.21", "delta": "1.35", "unit": "LUFS",
                                "direction": "up"}
    passed = {c["check"]: c["passed"] for c in model["pair_checks"]}
    assert passed == {"profile_hash_match": True, "duration_within_tolerance": True,
                      "channels_match": True, "duration_tolerance_s": None}
    detail = {c["check"]: c["detail"] for c in model["pair_checks"]}
    assert detail["duration_tolerance_s"] == "2.0"
    assert model["visibility_note"] == "delta 只描述不评级"


def test_compare_view_model_tolerates_missing_comparison():
    model = build_compare_view_model({"source": {"name": "x.wav"}})
    assert model["rows"] == [] and model["pair_checks"] == []
    assert model["normalization"] == "无效/未对齐"


def test_run_compare_executes_the_protocol_path(tmp_path):
    sr = 8000
    t = np.linspace(0.0, 0.5, sr // 2, endpoint=False)
    reference = tmp_path / "ref.wav"
    sf.write(reference, (0.2 * np.sin(2 * np.pi * 440.0 * t)).astype("float32"), sr)
    candidate = tmp_path / "cand.wav"
    sf.write(candidate,
             (0.25 * np.sin(2 * np.pi * 440.0 * t)).astype("float32"), sr)
    cases = tmp_path / "archive"

    result = run_compare(reference, candidate, cases)
    compare_root = Path(result["compare_root"])
    assert compare_root.is_dir()
    report = json.loads((compare_root / "report.json").read_text(encoding="utf-8"))
    model = build_compare_view_model(report)
    assert model["reference_name"].endswith("ref.wav")
    checks = {c["check"]: c["passed"] for c in model["pair_checks"]}
    assert checks["profile_hash_match"] is True
    assert checks["channels_match"] is True
    assert (compare_root / "delta_spectrum_log.png").is_file()
