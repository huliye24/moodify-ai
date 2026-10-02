"""Moodify report window — view-model tests (pure, headless-safe).

tkinter itself is never instantiated here: ``build_report_view_model`` maps
report.json onto widget-ready data and is the part worth pinning. The window
code path is exercised by the real ``moodify demo`` run on a desktop.
"""

from __future__ import annotations

import pytest

from moodify.ui.report_window import build_report_view_model

pytestmark = pytest.mark.v01


def _report() -> dict:
    return {
        "protocol": "moodify.sound/0.2",
        "generated_at": "2026-10-02T00:00:00+00:00",
        "case": {"case_id": "case_abc"},
        "source": {"name": "北极星与黑夜_02.flac", "sha256": "sha256:ea3e",
                   "duration_s": 171.76, "channels": 2, "sample_rate": 48000},
        "technical_state": {"overall": "PARTIAL",
                            "workflow_decision": "NO_TECHNICAL_BLOCKERS"},
        "measurements": [
            {"id": "integrated_lufs", "value": -15.56, "unit": "LUFS",
             "status": "VALID", "group": "loudness"},
            {"id": "air_10000_16000_hz", "value": 0.00757277, "unit": "ratio",
             "status": "VALID", "group": "bands"},
        ],
        "findings": [
            {"severity": "WARN", "code": "TRUE_PEAK_MARGIN_EXCEEDED",
             "message": "真峰余量不足", "calibration_status": "DEFAULT_UNCALIBRATED"},
        ],
        "plan": {"status": "DRAFT_PLAN_NOT_EXECUTED",
                 "nodes": [{"operator": "limiter", "reason": "真峰余量草案"}],
                 "notes": ["削波不可自动修复"],
                 "next_actions": ["submit process job"]},
        "judgment_boundary": {
            "layer1_measurement": "EXECUTED",
            "layer2_comparison": "NOT_RUN",
            "layer3_musical_judgment": "NOT_PROMISED",
            "layer4_production_judgment": "NOT_PROMISED",
            "layer5_cultural_judgment": "NOT_PROMISED"},
        "provenance": {"judgment_calibration": {
            "calibrated": 0, "default_uncalibrated": 16, "note": "校准警示"}},
    }


def test_view_model_header_and_source():
    vm = build_report_view_model(_report())
    assert vm["title"].startswith("Moodify")
    assert vm["source_name"] == "北极星与黑夜_02.flac"
    assert vm["case_id"] == "case_abc"
    assert vm["overall"] == "PARTIAL"
    assert vm["workflow_decision"] == "NO_TECHNICAL_BLOCKERS"


def test_view_model_measurements_format_numbers():
    vm = build_report_view_model(_report())
    assert vm["measurements"][0] == {"id": "integrated_lufs", "value": "-15.56",
                                     "unit": "LUFS", "status": "VALID",
                                     "group": "loudness"}
    assert vm["measurements"][1]["value"] == "0.007573"


def test_view_model_findings_carry_calibration():
    vm = build_report_view_model(_report())
    assert vm["findings_empty_text"] == ""
    assert vm["findings"][0]["calibration_status"] == "DEFAULT_UNCALIBRATED"


def test_view_model_findings_empty_honest_text():
    report = _report()
    report["findings"] = []
    vm = build_report_view_model(report)
    assert vm["findings"] == []
    assert vm["findings_empty_text"] == "无（未触发阈值）"


def test_view_model_plan_is_draft_and_boundary_complete():
    vm = build_report_view_model(_report())
    assert vm["plan_status"] == "DRAFT_PLAN_NOT_EXECUTED"
    assert vm["plan_nodes"][0]["operator"] == "limiter"
    assert len(vm["boundary"]) == 5
    states = {layer["layer"]: layer["state"] for layer in vm["boundary"]}
    assert states["L1 测量"] == "EXECUTED"
    assert states["L5 文化判断"] == "NOT_PROMISED"


def test_view_model_calibration_summary_passthrough():
    vm = build_report_view_model(_report())
    assert vm["calibration_summary"]["calibrated"] == 0
    assert vm["calibration_summary"]["default_uncalibrated"] == 16


def test_view_model_tolerates_missing_optional_sections():
    vm = build_report_view_model({"source": None, "technical_state": None,
                                  "case": None, "plan": None,
                                  "judgment_boundary": None,
                                  "provenance": None})
    assert vm["source_name"] == "?"
    assert vm["measurements"] == []
    assert vm["findings_empty_text"] == "无（未触发阈值）"
    assert vm["plan_status"] == "?"
    assert all(layer["state"] == "?" for layer in vm["boundary"])
