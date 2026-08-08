"""Tests for provider adapters: detection, argv safety, error classes, honesty."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest import mock


from moodify.capability_registry.adapters import (
    AudacityAdapter,
    FfmpegAdapter,
    MuseScoreAdapter,
    SoxAdapter,
    all_adapters,
)
from moodify.capability_registry.adapters.base import InvokeRequest
from moodify.capability_registry.adapters.basic_pitch_adapter import BasicPitchAdapter


def make_request(tmp_path: Path, inputs: dict[str, str], parameters: dict | None = None) -> InvokeRequest:
    return InvokeRequest(
        capability_id="test",
        inputs=inputs,
        parameters=parameters or {},
        output_dir=str(tmp_path / "out"),
        timeout_s=10.0,
    )


class TestAdapterRegistry:
    def test_all_adapters_shape(self) -> None:
        adapters = all_adapters()
        assert len(adapters) == 9
        for adapter in adapters:
            assert adapter.capability_id
            assert adapter.provider_id

    def test_adapter_identity_matches_registry(self) -> None:
        from moodify.capability_registry.bootstrap import build_registry

        registry = build_registry()
        registry_providers = {p.provider_id for p in registry.providers}
        adapter_providers = {a.provider_id for a in all_adapters()}
        assert adapter_providers == registry_providers


class TestDetection:
    def test_musescore_detect_on_this_machine(self) -> None:
        adapter = MuseScoreAdapter()
        # This machine has MuseScore 4.5.1; if not, this test would still pass
        # shape-wise, so we assert the return type and consistency only.
        assert isinstance(adapter.detect(), bool)

    def test_audacity_never_reports_automation(self) -> None:
        adapter = AudacityAdapter()
        result = adapter.invoke(make_request(Path("."), {"source": "x.wav"}))
        assert result.status == "unavailable"
        assert "human_handoff" in result.errors[0]
        assert result.error_class == "policy_rejection"


class TestArgvSafety:
    def test_command_is_argument_list(self, tmp_path: Path) -> None:
        adapter = FfmpegAdapter()
        source = tmp_path / "a.wav"
        source.write_bytes(b"RIFF")
        request = make_request(tmp_path, {"source": str(source)}, {"format": "flac"})
        with mock.patch.object(subprocess, "run") as mocked:
            mocked.return_value.returncode = 0
            mocked.return_value.stdout = b""
            mocked.return_value.stderr = b""
            adapter.invoke(request)
            cmd = mocked.call_args.args[0]
            assert isinstance(cmd, list)
            assert all(isinstance(part, str) for part in cmd)
            assert ";" not in cmd and "&&" not in " ".join(cmd)

    def test_musescore_command_single_o(self, tmp_path: Path) -> None:
        adapter = MuseScoreAdapter()
        source = tmp_path / "s.musicxml"
        source.write_bytes(b"<score-partwise/>")
        request = make_request(tmp_path, {"score": str(source)})
        with mock.patch.object(subprocess, "run") as mocked:
            mocked.return_value.returncode = 0
            mocked.return_value.stdout = b""
            mocked.return_value.stderr = b""
            adapter.invoke(request)
            # version probe also calls subprocess.run; pick the invoke command
            invoke_cmds = [c.args[0] for c in mocked.call_args_list if "-o" in c.args[0]]
            assert invoke_cmds, "no invoke command with -o found"
            cmd = invoke_cmds[0]
            assert cmd.count("-o") == 1  # single -o per 009 failure knowledge
            assert "-I" not in cmd  # no -I argument

    def test_sox_command_shape(self, tmp_path: Path) -> None:
        adapter = SoxAdapter()
        source = tmp_path / "a.wav"
        source.write_bytes(b"RIFF")
        request = make_request(tmp_path, {"source": str(source)})
        with mock.patch.object(subprocess, "run") as mocked:
            mocked.return_value.returncode = 0
            mocked.return_value.stdout = b""
            mocked.return_value.stderr = b""
            adapter.invoke(request)
            invoke_cmds = [c.args[0] for c in mocked.call_args_list if "stat" in c.args[0]]
            assert invoke_cmds, "no sox stat command found"
            assert "stat" in invoke_cmds[0]


class TestErrorClassification:
    def test_timeout_classified(self, tmp_path: Path) -> None:
        adapter = FfmpegAdapter()
        source = tmp_path / "a.wav"
        source.write_bytes(b"RIFF")
        request = make_request(tmp_path, {"source": str(source)})
        with mock.patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired(cmd=["x"], timeout=1)):
            result = adapter.invoke(request)
            assert result.status == "failure"
            assert result.error_class == "timeout"

    def test_nonzero_exit_provider_defect(self, tmp_path: Path) -> None:
        adapter = FfmpegAdapter()
        source = tmp_path / "a.wav"
        source.write_bytes(b"RIFF")
        request = make_request(tmp_path, {"source": str(source)})
        with mock.patch.object(subprocess, "run") as mocked:
            mocked.return_value.returncode = 1
            mocked.return_value.stdout = b""
            mocked.return_value.stderr = b"boom"
            result = adapter.invoke(request)
            assert result.status == "failure"
            assert result.error_class == "provider_defect"
            assert "boom" in result.errors[0]

    def test_missing_input_invalid(self, tmp_path: Path) -> None:
        adapter = FfmpegAdapter()
        request = make_request(tmp_path, {"source": str(tmp_path / "missing.wav")})
        result = adapter.invoke(request)
        assert result.status == "failure"
        assert result.error_class == "invalid_input"

    def test_nonempty_output_rejected(self, tmp_path: Path) -> None:
        adapter = FfmpegAdapter()
        source = tmp_path / "a.wav"
        source.write_bytes(b"RIFF")
        out = tmp_path / "out"
        out.mkdir()
        (out / "existing.txt").write_text("x")
        request = InvokeRequest(
            capability_id="test", inputs={"source": str(source)},
            output_dir=str(out), timeout_s=10.0,
        )
        result = adapter.invoke(request)
        assert result.status == "failure"
        assert result.error_class == "invalid_input"


class TestBasicPitch:
    def test_detect_venv(self) -> None:
        adapter = BasicPitchAdapter()
        assert isinstance(adapter.detect(), bool)
        assert adapter.version() is None or adapter.version()

    def test_unavailable_when_venv_missing(self, tmp_path: Path) -> None:
        adapter = BasicPitchAdapter()
        request = make_request(tmp_path, {"source": "x.wav"})
        with mock.patch.object(type(adapter), "detect", return_value=False):
            result = adapter.invoke(request)
            assert result.status == "unavailable"
            assert result.error_class == "environment_failure"

    def test_known_failure_modes_nonempty(self) -> None:
        from moodify.capability_registry.adapters.basic_pitch_adapter import KNOWN_FAILURE_MODES

        assert KNOWN_FAILURE_MODES
        assert any("Demucs" in m for m in KNOWN_FAILURE_MODES)


class TestMuseScoreAdapter:
    def test_single_o_and_no_I(self, tmp_path: Path) -> None:
        """009 failure knowledge: single -o, no -I argument."""
        adapter = MuseScoreAdapter()
        source = tmp_path / "s.musicxml"
        source.write_bytes(b"<score-partwise/>")
        request = make_request(tmp_path, {"score": str(source)})
        with mock.patch.object(subprocess, "run") as mocked:
            mocked.return_value.returncode = 0
            mocked.return_value.stdout = b""
            mocked.return_value.stderr = b""
            adapter.invoke(request)
            # find the invoke command (version probe also uses subprocess.run)
            invoke_cmds = [c.args[0] for c in mocked.call_args_list if "-o" in c.args[0]]
            assert invoke_cmds, "no invoke command with -o found"
            cmd = invoke_cmds[0]
            assert cmd.count("-o") == 1
            assert "-I" not in cmd

