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
    assert vm["findings"][0]["calibration_status"] == "DEFAULT_UNCALIBRATED"


def test_view_model_findings_empty_stays_empty():
    report = _report()
    report["findings"] = []
    vm = build_report_view_model(report)
    assert vm["findings"] == []


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
    assert vm["findings"] == []
    assert vm["plan_status"] == "?"
    assert all(layer["state"] == "?" for layer in vm["boundary"])


# ——— 图表：选数与建图（Agg 无头安全；不启动任何窗口） ———

def _measurements() -> list[dict]:
    return [
        {"id": "sub_20_60_hz", "value": 0.399, "unit": "ratio", "group": "bands"},
        {"id": "air_10000_16000_hz", "value": 0.00757, "unit": "ratio", "group": "bands"},
        {"id": "integrated_lufs", "value": -15.56, "unit": "LUFS", "group": "loudness"},
        {"id": "true_peak_dbfs", "value": -1.17, "unit": "dBFS", "group": "loudness"},
        {"id": "crest_factor_db", "value": 13.13, "unit": "dB", "group": "loudness"},
        {"id": "loudness_range_lu", "value": 2.64, "unit": "LU", "group": "loudness"},
        {"id": "stereo_correlation", "value": 0.7018, "unit": "ratio", "group": "stereo"},
        {"id": "side_to_mid_db", "value": -7.55, "unit": "dB", "group": "stereo"},
        {"id": "duration", "value": 171.76, "unit": "s", "group": "format"},
    ]


def test_select_chart_measurements_keeps_units_on_their_own_axis():
    from moodify.ui.report_window import select_chart_measurements

    series = select_chart_measurements(_measurements())
    assert [name for name, _ in series["bands"]] == ["sub_20_60_hz", "air_10000_16000_hz"]
    # dB units only — the LU value is dB-family; the dB stereo value is not
    assert [name for name, _ in series["levels_db"]] == [
        "integrated_lufs", "true_peak_dbfs", "crest_factor_db", "loudness_range_lu"]
    assert series["stereo_ratios"] == [("stereo_correlation", 0.7018)]
    assert "format" not in {k: v for k, v in series.items() if v}


def test_uncomputable_measurements_are_skipped_not_defaulted():
    """A metric Core could not compute carries ``null``; it must not crash the chart."""
    from moodify.ui.report_window import select_chart_measurements

    measurements = _measurements() + [
        {"id": "spectral_flux", "value": None, "unit": "mag/frame", "group": "bands"},
        {"id": "loudness_range_lu", "value": None, "unit": "LU", "group": "loudness"},
    ]
    series = select_chart_measurements(measurements)
    # the null band is dropped; the *other* loudness_range_lu row is still plotted as before
    assert [name for name, _ in series["bands"]] == ["sub_20_60_hz", "air_10000_16000_hz"]
    assert "loudness_range_lu" in [name for name, _ in series["levels_db"]]
    # and a report made only of uncomputable values yields empty series, not zeros
    only_null = select_chart_measurements(
        [{"id": "x", "value": None, "unit": "ratio", "group": "bands"}])
    assert only_null == {"bands": [], "levels_db": [], "stereo_ratios": []}


def _save_png(fig) -> int:
    import io

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    return len(buffer.getvalue())


def test_chart_figures_render_headless():
    from moodify.ui.report_window import (
        build_band_figure,
        build_level_figure,
        build_stereo_figure,
        select_chart_measurements,
    )

    series = select_chart_measurements(_measurements())
    for rows, builder in ((series["bands"], build_band_figure),
                          (series["levels_db"], build_level_figure),
                          (series["stereo_ratios"], build_stereo_figure)):
        fig = builder(rows)
        assert len(fig.axes[0].patches) == len(rows)  # one bar per measurement
        assert _save_png(fig) > 0


def test_chart_figures_handle_empty_rows():
    from moodify.ui.report_window import build_band_figure

    fig = build_band_figure([])
    assert _save_png(fig) > 0
