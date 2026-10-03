"""MSP 0.2 Layer C — threshold provenance and calibration tests.

Layer C discipline: provenance only. These tests pin the exact threshold
values (anti-recalibration guard: any value change must surface here as a
deliberate test change backed by a human decision record), enforce the
consistency invariants of THRESHOLD_PROVENANCE, and verify the sensitivity
sweep against the production judgment path.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from moodify.auditory.judgment import (
    CALIBRATION_DEFAULT,
    CALIBRATION_EXPERIMENTAL,
    CALIBRATION_STANDARD,
    JUDGMENT_RULES_VERSION,
    STATUS_CALIBRATED,
    STATUS_DEFAULT_UNCALIBRATED,
    THRESHOLD_PROVENANCE,
    UNIVERSAL_THRESHOLDS,
    calibration_summary,
    evaluate_risk_flags,
    write_judgment_rules,
)
from moodify.auditory.sensitivity import (
    _sweep_table,
    build_sensitivity_report,
)

pytestmark = pytest.mark.v01

# --- A. Anti-recalibration pin ---------------------------------------------
# Exact table, byte-identical since 5452ff44 (2026-08-02). Changing a value
# here without a calibration experiment + human decision record is a
# integrity violation this test makes visible.


def _expected_thresholds() -> dict:
    return {
        "true_peak_margin_reduced": {"metric": "true_peak_dbfs", "min_margin_db": 0.5},
        "excessive_loudness_increase": {"metric": "integrated_lufs", "max_increase_db": 4.0},
        "excessive_dynamic_compression": {"metric": "crest_factor_db", "max_reduction_db": 4.0},
        "crest_factor_collapse": {"metric": "crest_factor_db", "min_crest_db": 4.0},
        "new_clipping": {"metric": "clipping_sample_count", "max_count": 0},
        "low_frequency_overaccumulation": {"metric": "bass_60_120_hz", "max_increase_ratio": 0.03},
        "high_frequency_overaccumulation": {"metric": "brilliance_5000_10000_hz", "max_increase_ratio": 0.05},
        "new_high_frequency_cutoff": {"metric": "estimated_high_frequency_cutoff_hz", "max_reduction_hz": 3000.0},
        "stereo_phase_risk_increased": {"metric": "phase_risk_ratio", "max_increase": 0.02},
        "negative_correlation_increased": {"metric": "negative_correlation_ratio", "max_increase": 0.02},
        "duration_changed": {"metric": "duration", "max_abs_delta_s": 0.050},
        "channel_layout_changed": {"metric": "channels", "max_delta": 0},
        "sample_rate_changed": {"metric": "sample_rate", "max_delta": 0},
        "silence_structure_changed": {"metric": "silence_ratio", "max_abs_delta": 0.05},
        "invalid_audio_samples": {"metric": "invalid_sample_count", "max_count": 0},
        "analysis_confidence_low": {"metric": "finite_sample_ratio", "min_ratio": 0.999},
    }


def test_threshold_values_are_frozen():
    assert UNIVERSAL_THRESHOLDS == _expected_thresholds()


# --- B. Provenance registry -------------------------------------------------


def test_provenance_covers_every_threshold_exactly():
    assert set(THRESHOLD_PROVENANCE) == set(UNIVERSAL_THRESHOLDS)


def test_provenance_entries_complete_and_consistent():
    for key, prov in THRESHOLD_PROVENANCE.items():
        assert prov["source_class"] in {
            CALIBRATION_STANDARD, CALIBRATION_EXPERIMENTAL, CALIBRATION_DEFAULT,
        }, key
        assert prov["calibration_status"] in {
            STATUS_CALIBRATED, STATUS_DEFAULT_UNCALIBRATED,
        }, key
        assert isinstance(prov["calibratable"], bool), key
        assert len(prov["source"]) > 20, key
        # dates are ISO and trace to the table's introduction commit
        assert prov["date"] == "2026-08-02", key
        assert prov["introduced_in"] == "5452ff44", key
        # consistency invariants: unclassified provenance is a bug
        if prov["source_class"] == CALIBRATION_DEFAULT:
            assert prov["calibration_status"] == STATUS_DEFAULT_UNCALIBRATED, key
        else:
            assert prov["calibration_status"] == STATUS_CALIBRATED, key
        if not prov["calibratable"]:
            assert "not applicable" in prov["source"], key


def test_current_calibration_state_is_honest_zero():
    """2026-10-02 fact: no threshold has been through the calibration line."""
    summary = calibration_summary()
    assert summary["rules_total"] == len(UNIVERSAL_THRESHOLDS) == 16
    assert summary["by_source_class"] == {
        CALIBRATION_STANDARD: 0,
        CALIBRATION_EXPERIMENTAL: 0,
        CALIBRATION_DEFAULT: 16,
    }
    assert summary["calibrated"] == 0
    assert summary["default_uncalibrated"] == 16
    assert sorted(summary["uncalibrated_rules"]) == sorted(THRESHOLD_PROVENANCE)


def test_judgment_rules_json_carries_provenance(tmp_path):
    path = tmp_path / "judgment_rules.json"
    write_judgment_rules(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["judgment_rules_version"] == JUDGMENT_RULES_VERSION
    assert data["universal_thresholds"] == UNIVERSAL_THRESHOLDS
    assert data["threshold_provenance_version"]
    assert data["threshold_provenance"] == THRESHOLD_PROVENANCE
    assert data["calibration_summary"]["rules_total"] == 16


# --- C. Threshold wiring -----------------------------------------------------


def test_true_peak_rule_follows_threshold_table(monkeypatch):
    """The rule reads the declared value, not a hardcoded constant."""
    monkeypatch.setitem(
        UNIVERSAL_THRESHOLDS["true_peak_margin_reduced"], "min_margin_db", 0.9,
    )
    delta = {"true_peak_dbfs": {"absolute_delta": -0.2}}
    before = {"true_peak_dbfs": {"value": -0.6}}
    after = {"true_peak_dbfs": {"value": -0.8}}
    codes = {f.code for f in evaluate_risk_flags(delta, before, after)}
    assert "TRUE_PEAK_MARGIN_REDUCED" in codes  # -0.8 > -0.9
    monkeypatch.setitem(
        UNIVERSAL_THRESHOLDS["true_peak_margin_reduced"], "min_margin_db", 0.5,
    )
    codes = {f.code for f in evaluate_risk_flags(delta, before, after)}
    assert "TRUE_PEAK_MARGIN_REDUCED" not in codes  # -0.8 <= -0.5


def test_absolute_flags_carry_calibration_fields():
    from moodify.auditory.protocol_report import _absolute_flags

    metrics = {
        "clipping_sample_count": {"value": 100},
        "true_peak_dbfs": {"value": -0.2},
    }
    by_code = {f["code"]: f for f in _absolute_flags(metrics)}
    clip = by_code["CLIPPING_PRESENT"]
    assert clip["reference_basis"] == "new_clipping"
    assert clip["calibration_status"] == STATUS_DEFAULT_UNCALIBRATED
    assert clip["threshold_source_class"] == CALIBRATION_DEFAULT
    peak = by_code["TRUE_PEAK_MARGIN_EXCEEDED"]
    assert peak["reference_basis"] == "true_peak_margin_reduced"
    assert peak["calibration_status"] == STATUS_DEFAULT_UNCALIBRATED
    assert "0.5" in peak["message"]


# --- D. Sensitivity sweep ----------------------------------------------------


def test_sweep_table_tracks_threshold_registry():
    assert set(_sweep_table()) == set(UNIVERSAL_THRESHOLDS)


def test_sensitivity_all_flip_points_match():
    report = build_sensitivity_report()
    assert report["summary"]["rules_total"] == len(UNIVERSAL_THRESHOLDS)
    assert report["summary"]["all_match"] is True
    for entry in report["rules"]:
        assert entry["match"] is True, entry["rule"]


def test_sensitivity_report_is_deterministic():
    first = json.dumps(build_sensitivity_report(), ensure_ascii=False, sort_keys=True)
    second = json.dumps(build_sensitivity_report(), ensure_ascii=False, sort_keys=True)
    assert first == second


def test_lab_bridge_is_complete_and_honest():
    report = build_sensitivity_report()
    bridge = report["lab_calibration_bridge"]["rules"]
    assert set(bridge) == set(THRESHOLD_PROVENANCE)
    for key, prov in THRESHOLD_PROVENANCE.items():
        entry = bridge[key]
        assert isinstance(entry["comparable"], bool), key
        assert entry["note"], key
        if prov["calibratable"] and entry["operator"] is None:
            # a calibratable rule without a lab operator must say so plainly
            assert "尚无" in entry["note"] or "后续" in entry["note"], key


# --- E. Report integration ---------------------------------------------------


def _write_case_bundle(root: Path, metrics: dict) -> Path:
    (root / "scan").mkdir(parents=True)
    (root / "case.json").write_text(
        json.dumps({"case_id": "case_calib000000"}), encoding="utf-8")
    (root / "scan" / "metrics.json").write_text(
        json.dumps(metrics), encoding="utf-8")
    (root / "auditory_report.json").write_text(json.dumps({
        "source_name": "fixture.wav",
        "source_sha256": "sha256:" + "ab" * 32,
        "overall_status": "OK",
    }), encoding="utf-8")
    return root


def _calibration_metrics() -> dict:
    return {
        "clipping_sample_count": {"value": 500, "unit": "count",
                                  "method": "full-scale count", "status": "VALID"},
        "true_peak_dbfs": {"value": 0.3, "unit": "dBTP",
                           "method": "BS.1770-4 4x oversampling", "status": "VALID"},
        "duration": {"value": 12.0, "unit": "s", "method": "container", "status": "VALID"},
        "channels": {"value": 2, "unit": "count", "method": "container", "status": "VALID"},
        "sample_rate": {"value": 48000, "unit": "Hz", "method": "container", "status": "VALID"},
    }


def test_report_carries_calibration_provenance_and_validates(tmp_path):
    from moodify.auditory.protocol_report import _assemble_report

    root = _write_case_bundle(tmp_path / "case_calib000000", _calibration_metrics())
    report = _assemble_report(root, job_type="analyze")  # raises on schema failure
    calib = report["provenance"]["judgment_calibration"]
    assert calib["rules_total"] == 16
    assert calib["calibrated"] == 0
    assert calib["default_uncalibrated"] == 16
    assert len(calib["uncalibrated_rules"]) == 16
    assert report["provenance"]["judgment_rules_version"] == JUDGMENT_RULES_VERSION
    # findings inside the report carry their threshold's trust level
    clip = next(f for f in report["findings"] if f["code"] == "CLIPPING_PRESENT")
    assert clip["calibration_status"] == STATUS_DEFAULT_UNCALIBRATED
    assert clip["reference_basis"] == "new_clipping"


def test_render_surfaces_calibration_state(tmp_path):
    from moodify.auditory.protocol_report import _assemble_report
    from moodify.auditory.report_render import render_report_markdown

    root = _write_case_bundle(tmp_path / "case_calib000000", _calibration_metrics())
    report = _assemble_report(root, job_type="analyze")
    md = render_report_markdown(report)
    assert "0/16 已校准" in md
    assert "16 条 DEFAULT_UNCALIBRATED" in md
    assert "阈值来源 DEFAULT · DEFAULT_UNCALIBRATED" in md
    assert "不得当作经过听感校准" in md
