"""Layer D — packaging/deployment readiness tests (private-delivery track).

Human adjudication 2026-10-02: GPL-3.0-only stays, pip is the only
distribution form, delivery is self-hosted, pricing deferred. These tests
pin the decision-free engineering prep: version unification and the
`moodify doctor` environment probe.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.v01

_PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def test_package_version_matches_runtime_version():
    """D-ENG-1: pyproject version and release.PRODUCT_VERSION are one fact."""
    from moodify.release import PRODUCT_VERSION

    text = _PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version = "(.+)"$', text, re.M)
    assert match, "pyproject.toml must declare a project version"
    assert match.group(1) == PRODUCT_VERSION


def test_package_name_and_license_are_stable():
    """LD-1 adjudication: GPL-3.0-only stays; the pip package name is moodify."""
    text = _PYPROJECT.read_text(encoding="utf-8")
    assert re.search(r'^name = "moodify"$', text, re.M)
    assert 'license = {text = "GPL-3.0-only"}' in text


def test_doctor_reports_ready_environment():
    from moodify.release_cli import main

    rc = main(["doctor"])
    assert rc == 0


def test_doctor_output_carries_probe_data(capsys):
    from moodify.release_cli import main

    assert main(["doctor"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "ok"
    # the machine-readable verdict, not an exit code
    assert report["ready"] is True
    assert report["core_version"]
    assert report["judgment_rules_version"]
    assert report["ffmpeg"]["found"] is True
    assert report["ffmpeg"]["path"]
    for name in ("numpy", "scipy", "librosa", "soundfile", "pyloudnorm",
                 "jsonschema", "pedalboard", "matplotlib"):
        assert report["packages"][name]["importable"] is True, name


def test_doctor_flags_missing_ffmpeg(monkeypatch, capsys):
    """A probe must degrade honestly when the runtime resolver finds nothing."""
    from moodify.auditory.decode import FfmpegNotFound

    def _missing():
        raise FfmpegNotFound("ffmpeg not found on PATH")

    monkeypatch.setattr("moodify.auditory.decode._which_ffmpeg", _missing)
    from moodify.release_cli import main

    assert main(["doctor"]) == 0  # diagnostic still succeeds
    report = json.loads(capsys.readouterr().out)
    assert report["ready"] is False
    assert report["ffmpeg"]["found"] is False
    assert "hint" in report
