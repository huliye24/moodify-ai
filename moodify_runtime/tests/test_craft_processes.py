"""Tests for craft_processes — DSP operations, registry, audio functions."""
import tempfile
from pathlib import Path

import numpy as np
import pytest

from moodify_runtime.craft_processes import (
    RiskLevel, OpCategory, CraftOperation, OpResult,
    get_registry, get_active_operations, get_operation, list_operation_ids,
    _compute_rms, _compute_peak, _mono, _apply_gain, _soft_clip,
    _read_wav, _write_wav,
)


def _make_sine_wav(path, sr=44100, freq=440.0, amplitude=0.5):
    import struct
    t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
    samples = (amplitude * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
    with open(path, 'wb') as f:
        data_size = len(samples) * 2
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write(struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16))
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        f.write(samples.tobytes())


class TestRegistry:
    def test_registry_populated(self):
        reg = get_registry()
        assert len(reg) > 10

    def test_get_operation_valid(self):
        ids = list_operation_ids()
        for oid in ids[:5]:
            op = get_operation(oid)
            assert op is not None

    def test_get_operation_missing(self):
        assert get_operation("nonexistent_v999") is None

    def test_active_operations_exist(self):
        active = get_active_operations()
        assert len(active) > 0

    def test_registry_has_risk_levels(self):
        reg = get_registry()
        risks = {op.risk for op in reg.values()}
        assert len(risks) >= 1

    def test_all_ids_non_empty(self):
        for oid in list_operation_ids():
            assert oid and " " not in oid


class TestDSPFunctions:
    def test_compute_rms_zero_returns_neg_inf(self):
        """RMS of silence in dB should be very negative."""
        samples = np.zeros(1000, dtype=np.float32)
        rms = _compute_rms(samples)
        assert rms < -50  # dB scale, silence → -∞ dB

    def test_compute_rms_sine_positive_dB(self):
        t = np.linspace(0, 1, 44100, endpoint=False)
        samples = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        rms = _compute_rms(samples)
        # RMS of sine wave in dB should be around -3dB
        assert -10 < rms < 0

    def test_compute_peak_sine(self):
        t = np.linspace(0, 1, 44100, endpoint=False)
        samples = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        peak = _compute_peak(samples)
        # Peak of sine in dB should be around 0dB
        assert -5 <= peak <= 5

    def test_compute_peak_low(self):
        samples = np.array([0.01, 0.02], dtype=np.float32)
        peak = _compute_peak(samples)
        assert peak < -20  # very low amplitude → very negative dB

    def test_mono_stereo_average(self):
        stereo = np.array([[0.5, 0.3], [0.2, 0.4]], dtype=np.float32)
        mono = _mono(stereo)
        assert mono.ndim == 1

    def test_mono_identity(self):
        mono_in = np.array([0.5, 0.3], dtype=np.float32)
        mono_out = _mono(mono_in)
        assert mono_out[0] == pytest.approx(0.5)

    def test_apply_gain_positive(self):
        samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        gained = _apply_gain(samples, 6.0)  # +6dB ≈ ×2
        assert gained[0] > samples[0]

    def test_apply_gain_negative(self):
        samples = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        gained = _apply_gain(samples, -6.0)  # -6dB ≈ ×0.5
        assert gained[0] < samples[0]

    def test_soft_clip_reduces_peaks(self):
        samples = np.array([2.0, -2.0, 0.5], dtype=np.float32)
        clipped = _soft_clip(samples, threshold=1.0)
        assert max(abs(clipped)) < 2.0

    def test_soft_clip_preserves_below_threshold(self):
        samples = np.array([0.3, -0.4, 0.5], dtype=np.float32)
        clipped = _soft_clip(samples, threshold=1.0)
        assert clipped[0] == pytest.approx(0.3, rel=0.01)


class TestWavIO:
    def test_write_read_roundtrip(self):
        path = tempfile.mktemp(suffix=".wav")
        sr = 44100
        t = np.linspace(0, 0.1, int(sr * 0.1), endpoint=False)
        original = (0.5 * np.sin(2 * np.pi * 1000 * t)).astype(np.float32)
        _write_wav(path, original, sr)
        samples, read_sr, nch = _read_wav(path)
        assert read_sr == sr
        assert len(samples) > 0
        # RMS should be similar
        assert abs(abs(_compute_rms(samples)) - abs(_compute_rms(original))) < 10


class TestCraftOperation:
    def test_operation_creation(self):
        # Use actual OpCategory value from the enum
        cats = list(OpCategory)
        op = CraftOperation(
            op_id="test_eq", name="Test EQ",
            category=cats[0], risk=RiskLevel.MEDIUM,
        )
        assert op.op_id == "test_eq"
        assert op.risk == RiskLevel.MEDIUM

    def test_op_result_success(self):
        r = OpResult(op_id="test", success=True, metrics={"rms": 0.5})
        assert r.success
        assert r.metrics["rms"] == 0.5

    def test_op_result_failure(self):
        r = OpResult(op_id="test", success=False, error="DSP crashed")
        assert not r.success
        assert "DSP" in r.error
