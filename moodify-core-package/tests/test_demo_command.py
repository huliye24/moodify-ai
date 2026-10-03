"""`moodify demo` — the one-shot core moment: audio in, Moodify's own window.

A convenience wrapper over the 0.2 analyze job (same validate/execute path,
no new DSP): runs the analysis, renders report.json/md/html, and surfaces
the report in the Moodify report window (``moodify.ui``, detached process)
— the system browser is only an export-viewing fallback (``--browser``).
stdout stays JSON-first and the CLI returns immediately; the display action
is recorded as the machine-readable ``display`` field.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

pytestmark = pytest.mark.v01


def _write_wav(tmp_path: Path) -> Path:
    sr = 8000
    t = np.linspace(0.0, 0.5, sr // 2, endpoint=False)
    samples = (0.2 * np.sin(2 * np.pi * 440.0 * t)).astype("float32")
    path = tmp_path / "demo_source.wav"
    sf.write(path, samples, sr)
    return path


def test_demo_renders_report_and_opens_moodify_window(tmp_path, capsys, monkeypatch):
    src = _write_wav(tmp_path)
    out = tmp_path / "cases"
    spawned = []
    monkeypatch.setattr("moodify.release_cli._spawn_report_window",
                        lambda report_json: spawned.append(report_json) or {"mode": "window", "pid": 4242})

    from moodify.release_cli import main

    rc = main(["demo", str(src), "--cases-root", str(out)])
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "analyzed_review_required"
    assert result["review_required"] is True
    # the plan is a draft, never an execution
    assert result["plan_status"] == "DRAFT_PLAN_NOT_EXECUTED"
    html = Path(result["reports"]["html"])
    assert html.is_file()
    assert html.read_text(encoding="utf-8").lstrip().lower().startswith("<!doctype html")
    assert Path(result["reports"]["markdown"]).is_file()
    # the display action is data, not an exit code; the window got the persisted report
    assert result["display"] == {"mode": "window", "pid": 4242}
    assert spawned == [Path(result["reports"]["json"])]


def test_demo_browser_flag_uses_export_fallback(tmp_path, capsys, monkeypatch):
    src = _write_wav(tmp_path)
    out = tmp_path / "cases"
    opened: list[str] = []
    monkeypatch.setattr("webbrowser.open",
                        lambda url, *a, **k: opened.append(url) or True)

    from moodify.release_cli import main

    rc = main(["demo", str(src), "--cases-root", str(out), "--browser"])
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert result["display"] == {"mode": "browser"}
    assert len(opened) == 1 and opened[0].startswith("file:///")


def test_demo_no_open_renders_only(tmp_path, capsys, monkeypatch):
    src = _write_wav(tmp_path)
    out = tmp_path / "cases"
    monkeypatch.setattr("moodify.release_cli._spawn_report_window",
                        lambda report_json: pytest.fail("window must not spawn with --no-open"))

    from moodify.release_cli import main

    rc = main(["demo", str(src), "--cases-root", str(out), "--no-open"])
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert "display" not in result
    assert Path(result["reports"]["html"]).is_file()


def test_demo_missing_source_fails_closed(tmp_path, capsys):
    from moodify.release_cli import main

    rc = main(["demo", str(tmp_path / "nope.wav"),
               "--cases-root", str(tmp_path / "cases")])
    assert rc == 2
    payload = json.loads(capsys.readouterr().err)
    assert payload["status"] == "error"
    assert "nope.wav" in payload["error"]
