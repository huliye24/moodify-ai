"""Characterization tests for craft_processes.execute_operation dispatch.

Freeze observable behavior of all 22 craft operations before the
temporal-texture restructure (DSK-MFY-TEMPORAL-TEXTURE-001 wave 1).
Uses synthetic audio; asserts success paths, output files, channel
counts and failure modes — not DSP coefficients.
"""

from __future__ import annotations

import wave

import numpy as np
import pytest

from moodify_runtime.craft_processes import (
    CRAFT_REGISTRY,
    OpResult,
    execute_operation,
)

SR = 44100


def _write_wav(path, stereo: np.ndarray, sr: int = SR) -> None:
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((stereo * 32767).astype(np.int16).tobytes())


@pytest.fixture
def audio_input(tmp_path):
    t = np.linspace(0, 2.0, SR * 2, endpoint=False)
    mono = 0.2 * np.sin(2 * np.pi * 220 * t) + 0.1 * np.sin(2 * np.pi * 440 * t)
    mono = mono / np.max(np.abs(mono)) * 0.2
    stereo = np.column_stack([mono, mono * 0.9])
    path = tmp_path / "input.wav"
    _write_wav(path, stereo)
    return path


def _frames(path) -> int:
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes()


def _channels(path) -> int:
    with wave.open(str(path), "rb") as wf:
        return wf.getnchannels()


class TestFailureModes:
    def test_unknown_operation(self, audio_input, tmp_path) -> None:
        result = execute_operation("does_not_exist", str(audio_input), str(tmp_path / "o.wav"))
        assert result.success is False
        assert "Unknown operation" in result.error

    def test_missing_input_file(self, tmp_path) -> None:
        result = execute_operation("input_normalize", str(tmp_path / "missing.wav"), str(tmp_path / "o.wav"))
        assert result.success is False
        assert "Failed to read input" in result.error

    def test_empty_audio_file(self, tmp_path) -> None:
        empty = tmp_path / "empty.wav"
        _write_wav(empty, np.zeros((0, 2)))
        result = execute_operation("input_normalize", str(empty), str(tmp_path / "o.wav"))
        assert result.success is False
        assert "Empty or unreadable" in result.error


class TestDispatch:
    @pytest.mark.parametrize("op_id", sorted(CRAFT_REGISTRY.keys()))
    def test_every_operation_succeeds_with_defaults(self, op_id, audio_input, tmp_path) -> None:
        out_path = tmp_path / f"out_{op_id}.wav"
        result = execute_operation(op_id, str(audio_input), str(out_path))
        assert result.success, f"{op_id}: {result.error}"
        assert isinstance(result, OpResult)
        assert result.metrics, f"{op_id}: expected metrics"
        assert out_path.exists(), f"{op_id}: output file missing"

    @pytest.mark.parametrize("op_id", sorted(CRAFT_REGISTRY.keys()))
    def test_output_is_readable_wav(self, op_id, audio_input, tmp_path) -> None:
        out_path = tmp_path / f"out_{op_id}.wav"
        execute_operation(op_id, str(audio_input), str(out_path))
        with wave.open(str(out_path), "rb") as wf:
            assert wf.getnframes() > 0
            assert wf.getsampwidth() == 2

    # KNOWN PRE-EXISTING BEHAVIOR: _write_wav flattens stereo and always
    # writes a single channel (nch is discarded). Frozen as current
    # behavior; fixing it is a behavior change requiring authority.
    def test_stereo_width_control_writes_flattened_audio(self, audio_input, tmp_path) -> None:
        out_path = tmp_path / "out_stereo.wav"
        result = execute_operation("stereo_width_control", str(audio_input), str(out_path))
        assert result.success
        assert _channels(out_path) == 1
        assert _frames(out_path) == _frames(audio_input) * 2

    def test_center_focus_writes_flattened_audio(self, audio_input, tmp_path) -> None:
        out_path = tmp_path / "out_center.wav"
        result = execute_operation("center_focus", str(audio_input), str(out_path))
        assert result.success
        assert _channels(out_path) == 1
        assert _frames(out_path) == _frames(audio_input) * 2

    def test_mono_ops_write_mono(self, audio_input, tmp_path) -> None:
        out_path = tmp_path / "out_mono.wav"
        result = execute_operation("dc_offset_repair", str(audio_input), str(out_path))
        assert result.success
        assert _channels(out_path) == 1
