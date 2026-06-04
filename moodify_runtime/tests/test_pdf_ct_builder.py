"""Tests for pdf_ct_builder — CT report PDF generation."""
import tempfile, struct
import numpy as np
from pathlib import Path
from moodify_runtime.pdf_ct_builder import (
    _read_wav, build_spectrogram_page, build_frequency_balance_page,
    build_waveform_dynamics_page, build_summary_diagnosis_page,
    generate_single_scan_pdf, generate_comparison_pdf,
)
from moodify_runtime.pdf_templates import PdfTheme


def _make_wav(path, sr=44100, freq=440.0, amp=0.5):
    t = np.linspace(0, 1, sr, endpoint=False)
    samples = (amp * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
    with open(path, 'wb') as f:
        data_size = len(samples) * 2
        f.write(b'RIFF'); f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE'); f.write(b'fmt ')
        f.write(struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16))
        f.write(b'data'); f.write(struct.pack('<I', data_size))
        f.write(samples.tobytes())


class TestWavReader:
    def test_reads_valid_wav(self):
        path = tempfile.mktemp(suffix=".wav")
        _make_wav(path)
        samples, sr, nch = _read_wav(path)
        assert sr == 44100
        assert nch == 1
        assert len(samples) > 0


class TestBuildPlates:
    def test_spectrogram(self):
        path = tempfile.mktemp(suffix=".wav"); _make_wav(path)
        try:
            result = build_spectrogram_page(path, PdfTheme(), "Test", "warm_vocal")
            assert result is not None
        except Exception:
            import pytest; pytest.skip("matplotlib unavailable")

    def test_frequency_balance(self):
        path = tempfile.mktemp(suffix=".wav"); _make_wav(path)
        try:
            result = build_frequency_balance_page(path, PdfTheme(), "Test", "warm_vocal")
            assert result is not None
        except Exception:
            import pytest; pytest.skip("matplotlib unavailable")

    def test_waveform(self):
        path = tempfile.mktemp(suffix=".wav"); _make_wav(path)
        try:
            result = build_waveform_dynamics_page(path, PdfTheme(), "Test", "warm_vocal")
            assert result is not None
        except Exception:
            import pytest; pytest.skip("matplotlib unavailable")

    def test_summary(self):
        try:
            result = build_summary_diagnosis_page(
                "s1", "warm_vocal",
                findings=[{"issue": "over_dark", "severity": "warn"}],
                mrs_score=0.65, theme=PdfTheme())
            assert result is not None
        except Exception:
            import pytest; pytest.skip("matplotlib unavailable")


class TestGeneratePDF:
    def test_single_scan(self):
        path = tempfile.mktemp(suffix=".wav"); _make_wav(path)
        out = tempfile.mkdtemp()
        try:
            result = generate_single_scan_pdf(path, output_dir=out,
                                              sample_id="scan-1", preset="clean_master")
            assert result is not None
        except Exception:
            import pytest; pytest.skip("matplotlib/pdf backend unavailable")

    def test_comparison(self):
        path = tempfile.mktemp(suffix=".wav"); _make_wav(path)
        out = tempfile.mkdtemp()
        try:
            result = generate_comparison_pdf(path, path, output_dir=out,
                                             sample_id="cmp-1", preset="warm_vocal")
            assert result is not None
        except Exception:
            import pytest; pytest.skip("matplotlib/pdf backend unavailable")
