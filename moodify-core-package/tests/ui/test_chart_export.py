"""Chart-export bridge — headless PNGs for the Electron shell.

The Electron shell needs the same unit-honest charts the Tk window draws;
this bridge re-exports them from a persisted report via Agg. Pinned
headless: PNGs exist, are non-empty, and are real PNGs.
"""

from __future__ import annotations

import json

import pytest

from moodify.ui.chart_export import export_chart_pngs

pytestmark = pytest.mark.v01


def _report() -> dict:
    return {"measurements": [
        {"id": "sub_20_60_hz", "value": 0.399, "unit": "ratio", "group": "bands"},
        {"id": "air_10000_16000_hz", "value": 0.00757, "unit": "ratio", "group": "bands"},
        {"id": "integrated_lufs", "value": -15.56, "unit": "LUFS", "group": "loudness"},
        {"id": "true_peak_dbfs", "value": -1.17, "unit": "dBFS", "group": "loudness"},
        {"id": "stereo_correlation", "value": 0.7018, "unit": "ratio", "group": "stereo"},
    ]}


def test_export_chart_pngs_writes_nonempty_pngs(tmp_path):
    charts = export_chart_pngs(_report(), tmp_path)
    assert set(charts) == {"bands", "levels_db", "stereo_ratios"}
    for path in charts.values():
        data = open(path, "rb").read(8)
        assert data.startswith(b"\x89PNG")
        assert len(open(path, "rb").read()) > 0


def test_export_chart_pngs_skips_empty_series(tmp_path):
    charts = export_chart_pngs({"measurements": []}, tmp_path)
    assert charts == {}


def test_bridge_cli_roundtrip(tmp_path, capsys):
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(_report()), encoding="utf-8")

    from moodify.ui.chart_export import main

    assert main([str(report_path), "--out", str(tmp_path / "charts")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert len(payload["charts"]) == 3
