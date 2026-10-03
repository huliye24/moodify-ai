"""Moodify desktop app hub — archive scan, protocol path, CLI spawn.

Headless discipline: only the pure parts are pinned here (archive scan,
run_analysis through the real 0.2 validate/execute path, CLI spawn data).
The Tk class itself is exercised by the human on the desktop; CI never
instantiates it.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from moodify.ui.app import DEFAULT_CASES_ROOT, run_analysis, scan_case_archive

pytestmark = pytest.mark.v01


def _write_report(case_dir: Path, payload: dict) -> None:
    case_dir.mkdir(parents=True)
    (case_dir / "report.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _case_payload(case_id: str, generated_at: str, source: str = "song.flac") -> dict:
    return {
        "protocol": "moodify.sound/0.2",
        "generated_at": generated_at,
        "case": {"case_id": case_id},
        "source": {"name": source},
        "technical_state": {"overall": "PARTIAL",
                            "workflow_decision": "NO_TECHNICAL_BLOCKERS"},
    }


def test_scan_case_archive_orders_newest_first_and_tolerates_damage(tmp_path):
    _write_report(tmp_path / "case_a", _case_payload("case_a", "2026-10-01T10:00:00+00:00"))
    _write_report(tmp_path / "case_b", _case_payload("case_b", "2026-10-02T09:00:00+00:00"))
    payload_c = _case_payload("case_c", "?")
    del payload_c["generated_at"]  # timestamp missing entirely
    _write_report(tmp_path / "case_c", payload_c)
    (tmp_path / "case_bad").mkdir()
    (tmp_path / "case_bad" / "report.json").write_text("{not json", encoding="utf-8")
    (tmp_path / "case_empty").mkdir()  # interrupted analysis, no report yet
    _write_report(tmp_path / "other", _case_payload("other", "2026-10-03T00:00:00+00:00"))

    rows = scan_case_archive(tmp_path)
    assert [row["case_id"] for row in rows] == ["case_b", "case_a", "case_c"]
    assert rows[0]["source_name"] == "song.flac"
    assert rows[0]["overall"] == "PARTIAL"
    assert rows[0]["report_path"].endswith(str(Path("case_b") / "report.json"))


def test_scan_case_archive_missing_root_is_empty(tmp_path):
    assert scan_case_archive(tmp_path / "nowhere") == []


def test_run_analysis_executes_the_protocol_path(tmp_path):
    sr = 8000
    t = np.linspace(0.0, 0.5, sr // 2, endpoint=False)
    src = tmp_path / "app_source.wav"
    sf.write(src, (0.2 * np.sin(2 * np.pi * 440.0 * t)).astype("float32"), sr)
    cases = tmp_path / "archive"

    result = run_analysis(src, cases)
    report_path = Path(result["reports"]["json"])
    assert report_path.is_file()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["plan"]["status"] == "DRAFT_PLAN_NOT_EXECUTED"
    assert report["case"]["case_id"].startswith("case_")


def test_cli_app_command_spawns_the_hub_detached(tmp_path, capsys, monkeypatch):
    spawned: list[tuple[str, tuple[str, ...]]] = []
    monkeypatch.setattr(
        "moodify.release_cli._spawn_ui_module",
        lambda module, *args: spawned.append((module, args)) or {"mode": "window", "pid": 7})

    from moodify.release_cli import main

    rc = main(["app", str(tmp_path)])
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert spawned == [("moodify.ui.app", (str(tmp_path),))]
    assert result == {"command": "app", "cases_root": str(tmp_path),
                      "display": {"mode": "window", "pid": 7}}


def test_cli_app_default_root_is_the_home_archive(capsys, monkeypatch):
    spawned: list[tuple[str, tuple[str, ...]]] = []
    monkeypatch.setattr(
        "moodify.release_cli._spawn_ui_module",
        lambda module, *args: spawned.append((module, args)) or None)

    from moodify.release_cli import main

    rc = main(["app"])
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert spawned == [("moodify.ui.app", (str(DEFAULT_CASES_ROOT),))]
    assert result["cases_root"] == str(DEFAULT_CASES_ROOT)
    assert result["display"] is None  # spawn failure is data, not a crash
