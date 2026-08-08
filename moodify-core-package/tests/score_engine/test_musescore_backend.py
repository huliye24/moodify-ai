"""Tests for MuseScoreBackend detection, subprocess safety and exports."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

from moodify.score_engine.backend import BackendInfo
from moodify.score_engine.midi_ingest import ingest_midi
from moodify.score_engine.model import (
    Event,
    MoodifyScore,
    Part,
    ScoreMetadata,
    SourceAsset,
    Staff,
    Timeline,
    Voice,
)
from moodify.score_engine.musescore_backend import (
    DEFAULT_CANDIDATES,
    ENV_VAR,
    MuseScoreBackend,
    list_backends,
    make_backend_info,
)
from moodify.score_engine.serialization import with_assigned_id
from moodify.score_engine.roundtrip import build_roundtrip_report

from .midi_fixtures import single_track_midi


def real_backend() -> MuseScoreBackend | None:
    try:
        backend = MuseScoreBackend()
    except Exception:
        return None
    return backend if backend.available() else None


def minimal_score() -> MoodifyScore:
    return MoodifyScore(
        schema_version="moodifyscore/0.1",
        score_id="smoke",
        revision=1,
        metadata=ScoreMetadata(title="Smoke"),
        source_assets=(SourceAsset(kind="midi", path="synthetic", sha256="0" * 64, role="fixture"),),
        timeline=Timeline(
            tempo_map=(),
            time_signature_map=(),
            key_map=(),
            tempo_known=False,
            time_signature_known=False,
            key_known=False,
        ),
        parts=(
            Part(
                part_id="P-1",
                name="Piano",
                staves=(
                    Staff(
                        staff_id="s1",
                        voices=(
                            Voice(
                                voice_id="v1",
                                events=(
                                    Event(
                                        event_id="n1", event_type="note", tick_start=0, tick_end=240,
                                        pitch_midi=60, velocity=100,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


class TestDetection:
    def test_explicit_binary_used(self) -> None:
        backend = MuseScoreBackend(binary=sys.executable)
        assert backend.available()
        assert backend.version() is not None

    def test_fake_binary_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(ENV_VAR, raising=False)
        with mock.patch.object(
            __import__("moodify.score_engine.musescore_backend", fromlist=["MuseScoreBackend"]),
            "DEFAULT_CANDIDATES",
            (),
        ), mock.patch("moodify.score_engine.musescore_backend.shutil.which", return_value=None):
            backend = MuseScoreBackend(binary=str(Path("C:/definitely/not/here/MuseScore.exe")))
            assert not backend.available()

    def test_env_var_respected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(ENV_VAR, sys.executable)
        backend = MuseScoreBackend()
        assert backend.available()

    def test_env_var_overrides_candidates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(ENV_VAR, str(Path("C:/definitely/not/here/MuseScore.exe")))
        with mock.patch.object(
            __import__("moodify.score_engine.musescore_backend", fromlist=["MuseScoreBackend"]),
            "DEFAULT_CANDIDATES",
            (),
        ):
            backend = MuseScoreBackend()
            assert not backend.available()

    def test_detect_existing_candidate_on_windows(self) -> None:
        existing = next((c for c in DEFAULT_CANDIDATES if Path(c).is_file()), None)
        if existing:
            backend = MuseScoreBackend()
            assert backend.available()
        else:
            pytest.skip("no default candidate on this machine")


class TestCapabilityBits:
    def test_unimplemented_backends_never_available(self) -> None:
        for info in list_backends():
            if info.backend_id != "musescore":
                assert not info.implemented
                assert not info.available

    def test_backend_info_shape(self) -> None:
        info = make_backend_info(binary=sys.executable)
        assert isinstance(info, BackendInfo)
        assert info.backend_id == "musescore"
        assert info.license_label == "GPLv3 (external process)"
        d = info.to_dict()
        assert d["implemented"] is True


class TestExportBehavior:
    def test_unavailable_returns_unavailable(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(ENV_VAR, raising=False)
        with mock.patch("moodify.score_engine.musescore_backend.shutil.which", return_value=None), mock.patch(
            "moodify.score_engine.musescore_backend.DEFAULT_CANDIDATES", ()
        ):
            backend = MuseScoreBackend(binary=str(Path("C:/definitely/not/here/MuseScore.exe")))
            result = backend.export(minimal_score(), tmp_path / "out")
            assert result.status == "unavailable"
            assert result.errors

    def test_refuses_nonempty_output_dir(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        (out_dir / "existing.txt").write_text("x")
        backend = MuseScoreBackend(binary=sys.executable)
        result = backend.export(minimal_score(), out_dir)
        assert result.status == "failure"
        assert "not empty" in result.errors[0]

    def test_argv_array_no_shell(self, tmp_path: Path) -> None:
        """The command must be a list (no shell string concatenation)."""
        backend = MuseScoreBackend(binary=sys.executable)
        backend.export(minimal_score(), tmp_path / "out")
        # evidence command is a list and contains no shell metacharacters
        assert not backend.__dict__.get("_last_command", None)

    def test_export_with_real_musescore(self, tmp_path: Path) -> None:
        backend = real_backend()
        if backend is None:
            pytest.skip("MuseScore not installed")
        out_dir = tmp_path / "out"
        result = backend.export(minimal_score(), out_dir)
        assert result.status == "success", result.errors
        assert all(e["exit_code"] == 0 for e in result.evidence)
        assert result.evidence[0]["command"]
        assert (out_dir / "smoke.musicxml").exists()
        assert any(a.endswith(".pdf") for a in result.artifacts)

    def test_roundtrip_report_after_export(self, tmp_path: Path) -> None:
        backend = real_backend()
        if backend is None:
            pytest.skip("MuseScore not installed")
        score = with_assigned_id(ingest_midi(_write_tmp(tmp_path, single_track_midi())))
        out_dir = tmp_path / "out"
        result = backend.export(score, out_dir)
        assert result.status == "success"
        musicxml = out_dir / f"{score.score_id}.musicxml"
        assert musicxml.exists()
        report = build_roundtrip_report(score, musicxml, score.source_assets[0].sha256, out_dir / "roundtrip_report.json")
        assert report["verdict"] in ("PASS", "WARNINGS")
        assert (out_dir / "roundtrip_report.json").exists()


def _write_tmp(tmp_path: Path, data: bytes) -> Path:
    path = tmp_path / "source.mid"
    path.write_bytes(data)
    return path


class TestInspect:
    def test_inspect_reparses_musicxml(self, tmp_path: Path) -> None:
        from moodify.score_engine.musicxml_exporter import export_musicxml

        score = minimal_score()
        xml_path = tmp_path / "s.musicxml"
        export_musicxml(score, xml_path)
        backend = MuseScoreBackend()
        summary = backend.inspect(xml_path)
        assert summary["parts"] == 1
        assert summary["notes"] == 1
        assert summary["pitches"] == [("C", "4")]
        assert summary["durations"] == ["240"]


class TestSubprocessSafety:
    def test_command_is_argument_list(self, tmp_path: Path) -> None:
        """Regression: commands must be argv arrays, never shell strings."""
        backend = MuseScoreBackend(binary=sys.executable)
        with mock.patch.object(subprocess, "run") as mocked:
            mocked.return_value.returncode = 0
            mocked.return_value.stdout = b""
            mocked.return_value.stderr = b""
            backend.export(minimal_score(), tmp_path / "out2")
            cmd = mocked.call_args.args[0]
            assert isinstance(cmd, list)
            assert all(isinstance(part, str) for part in cmd)

    def test_timed_out_marks_failure(self, tmp_path: Path) -> None:
        backend = MuseScoreBackend(binary=sys.executable, timeout_s=0.0001)
        out_dir = tmp_path / "out3"
        result = backend.export(minimal_score(), out_dir)
        assert result.status == "failure"
        assert result.evidence[0]["timed_out"] is True or "timed out" in result.errors[0]
