"""Test suite for Moodify QA.

Tests for all core analysis modules.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

from core.metrics import (
    LoudnessMetrics,
    PeakMetrics,
    DynamicMetrics,
    StereoMetrics,
    SpectralMetrics,
    IntegrityMetrics,
)
from core.analyzer import AudioAnalyzer, AudioAnalysisResult
from core.scoring import QAScorer, IssueSeverity


class TestLoudnessMetrics(unittest.TestCase):
    """Test loudness measurement module."""

    def test_silence_returns_abs_gate(self):
        """Silence should return absolute gate value."""
        samples = np.zeros(48000, dtype=np.float64)  # 1 second silence
        metrics = LoudnessMetrics.from_samples(samples, 48000)
        self.assertEqual(metrics.integrated_lufs, -70.0)

    def test_sine_wave_loudness(self):
        """Test loudness of a sine wave."""
        t = np.linspace(0, 1, 48000)
        samples = 0.5 * np.sin(2 * np.pi * 1000 * t)
        metrics = LoudnessMetrics.from_samples(samples, 48000)
        # Should be above silence
        self.assertGreater(metrics.integrated_lufs, -60.0)


class TestPeakMetrics(unittest.TestCase):
    """Test peak measurement module."""

    def test_silence_peak(self):
        """Silence should have very low peak."""
        samples = np.zeros(48000, dtype=np.float64)
        metrics = PeakMetrics.from_samples(samples, 48000)
        self.assertLess(metrics.sample_peak_dbfs, -100.0)

    def test_full_scale_peak(self):
        """Full scale sine should have peak near 0 dBFS."""
        t = np.linspace(0, 1, 48000)
        samples = np.sin(2 * np.pi * 1000 * t)
        metrics = PeakMetrics.from_samples(samples, 48000)
        self.assertGreater(metrics.sample_peak_dbfs, -3.0)


class TestStereoMetrics(unittest.TestCase):
    """Test stereo analysis module."""

    def test_mono_returns_not_available(self):
        """Mono input should return available=False."""
        samples = np.random.randn(48000)
        metrics = StereoMetrics.from_samples(samples)
        self.assertFalse(metrics.available)

    def test_stereo_returns_available(self):
        """Stereo input should return available=True."""
        left = np.random.randn(48000)
        right = np.random.randn(48000)
        samples = np.column_stack([left, right])
        metrics = StereoMetrics.from_samples(samples)
        self.assertTrue(metrics.available)


class TestSpectralMetrics(unittest.TestCase):
    """Test spectral analysis module."""

    def test_silence_centroid(self):
        """Silence should have zero centroid."""
        samples = np.zeros(48000, dtype=np.float64)
        metrics = SpectralMetrics.from_samples(samples, 48000)
        self.assertEqual(metrics.centroid_hz, 0.0)

    def test_sine_centroid(self):
        """Sine wave centroid should match frequency."""
        t = np.linspace(0, 1, 48000)
        freq = 1000
        samples = np.sin(2 * np.pi * freq * t)
        metrics = SpectralMetrics.from_samples(samples, 48000)
        # Should be close to the sine frequency
        self.assertGreater(metrics.centroid_hz, freq * 0.5)
        self.assertLess(metrics.centroid_hz, freq * 2)


class TestIntegrityMetrics(unittest.TestCase):
    """Test signal integrity module."""

    def test_no_clipping_in_clean_signal(self):
        """Clean signal should have no clipping."""
        t = np.linspace(0, 1, 48000)
        samples = 0.5 * np.sin(2 * np.pi * 1000 * t)
        metrics = IntegrityMetrics.from_samples(samples, 48000)
        self.assertEqual(metrics.clipping_sample_count, 0)

    def test_detects_clipping(self):
        """Should detect clipped signal."""
        samples = np.ones(48000, dtype=np.float64)  # Full scale DC
        metrics = IntegrityMetrics.from_samples(samples, 48000)
        self.assertGreater(metrics.clipping_sample_count, 0)


class TestQAScorer(unittest.TestCase):
    """Test QA scoring module."""

    def test_score_returns_result(self):
        """Score should return a valid result."""
        # Create a minimal analysis result
        analysis = AudioAnalysisResult(
            filepath="/test.wav",
            filename="test.wav",
            duration_seconds=1.0,
            sample_rate=48000,
            channels=1,
        )

        scorer = QAScorer()
        result = scorer.score(analysis)

        self.assertIsNotNone(result)
        self.assertGreaterEqual(result.qa_score, 0)
        self.assertLessEqual(result.qa_score, 100)


if __name__ == "__main__":
    unittest.main()
