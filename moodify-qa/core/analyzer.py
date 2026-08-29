"""Audio analyzer - orchestrates all quality measurements.

Migrated from moodify.auditory modules with preserved algorithm logic.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from core.metrics import (
    LoudnessMetrics,
    PeakMetrics,
    DynamicMetrics,
    StereoMetrics,
    SpectralMetrics,
    IntegrityMetrics,
)


@dataclass
class AudioAnalysisResult:
    """Complete analysis result for a single audio file."""

    # File info
    filepath: str
    filename: str
    duration_seconds: float
    sample_rate: int
    channels: int
    bit_depth: int | None = None
    file_size_bytes: int = 0
    sha256: str = ""

    # Technical metrics
    loudness: LoudnessMetrics = field(default_factory=LoudnessMetrics)
    peaks: PeakMetrics = field(default_factory=PeakMetrics)
    dynamics: DynamicMetrics = field(default_factory=DynamicMetrics)
    stereo: StereoMetrics = field(default_factory=StereoMetrics)
    spectral: SpectralMetrics = field(default_factory=SpectralMetrics)
    integrity: IntegrityMetrics = field(default_factory=IntegrityMetrics)

    # Raw metrics dict for extensibility
    raw_metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file": {
                "path": self.filepath,
                "name": self.filename,
                "duration_seconds": round(self.duration_seconds, 3),
                "sample_rate_hz": self.sample_rate,
                "channels": self.channels,
                "bit_depth": self.bit_depth,
                "size_bytes": self.file_size_bytes,
                "sha256": self.sha256,
            },
            "loudness": self.loudness.to_dict(),
            "peaks": self.peaks.to_dict(),
            "dynamics": self.dynamics.to_dict(),
            "stereo": self.stereo.to_dict(),
            "spectral": self.spectral.to_dict(),
            "integrity": self.integrity.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class AudioAnalyzer:
    """Main audio quality analyzer.

    Aggregates all detection capabilities from Moodify Engine:
    - LUFS loudness analysis (ITU-R BS.1770-5)
    - Peak / True Peak detection (4x oversampling)
    - Dynamic Range analysis (crest factor, LRA)
    - LRA (Loudness Range) analysis (EBU Tech 3342)
    - Stereo Width analysis (correlation-based)
    - M/S analysis (mid/side energy ratios)
    - Frequency balance analysis (band energy distribution)
    - Clipping detection (sample-level)
    - Silence detection (windowed RMS)
    - Basic audio statistics (DC offset, noise floor)
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def analyze(self, filepath: str | Path) -> AudioAnalysisResult:
        """Analyze an audio file and return complete quality metrics."""
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Audio file not found: {filepath}")

        # Load audio
        samples, sr = sf.read(str(filepath), dtype=np.float64, always_2d=True)

        # File metadata
        file_info = sf.info(str(filepath))
        file_size = filepath.stat().st_size

        # Get bit depth if available
        bit_depth = None
        if hasattr(file_info, 'subtype') and isinstance(file_info.subtype, str):
            # Parse bit depth from subtype string like "PCM_16" -> 16
            subtype = file_info.subtype
            if "16" in subtype:
                bit_depth = 16
            elif "24" in subtype:
                bit_depth = 24
            elif "32" in subtype:
                bit_depth = 32

        # Compute SHA256
        sha256_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()

        # Initialize result
        result = AudioAnalysisResult(
            filepath=str(filepath.absolute()),
            filename=filepath.name,
            duration_seconds=len(samples) / sr,
            sample_rate=sr,
            channels=samples.shape[1],
            bit_depth=bit_depth,
            file_size_bytes=file_size,
            sha256=sha256_hash,
        )

        # Run all metric analyses
        result.loudness = LoudnessMetrics.from_samples(samples, sr)
        result.peaks = PeakMetrics.from_samples(samples, sr)
        result.dynamics = DynamicMetrics.from_samples(samples, sr)
        result.stereo = StereoMetrics.from_samples(samples)
        result.spectral = SpectralMetrics.from_samples(samples, sr)
        result.integrity = IntegrityMetrics.from_samples(samples, sr)

        # Store raw metrics for advanced use
        result.raw_metrics = self._collect_raw_metrics(result)

        return result

    def _collect_raw_metrics(self, result: AudioAnalysisResult) -> dict[str, Any]:
        """Collect all raw metrics into a flat dictionary."""
        return {
            # Loudness
            "integrated_lufs": result.loudness.integrated_lufs,
            "loudness_range_lu": result.loudness.loudness_range_lu,
            "momentary_max_lufs": result.loudness.momentary_max_lufs,
            "short_term_max_lufs": result.loudness.short_term_max_lufs,

            # Peaks
            "true_peak_dbfs": result.peaks.true_peak_dbfs,
            "sample_peak_dbfs": result.peaks.sample_peak_dbfs,
            "peak_to_loudness_ratio": result.peaks.peak_to_loudness_ratio,

            # Dynamics
            "crest_factor_db": result.dynamics.crest_factor_db,
            "rms_dbfs": result.dynamics.rms_dbfs,
            "dynamic_range_db": result.dynamics.dynamic_range_db,

            # Stereo
            "stereo_correlation": result.stereo.correlation if result.stereo.available else None,
            "mid_energy_ratio": result.stereo.mid_ratio if result.stereo.available else None,
            "side_energy_ratio": result.stereo.side_ratio if result.stereo.available else None,
            "side_to_mid_db": result.stereo.side_to_mid_db if result.stereo.available else None,
            "stereo_width_proxy": result.stereo.width_proxy if result.stereo.available else None,

            # Spectral
            "spectral_centroid_hz": result.spectral.centroid_hz,
            "spectral_rolloff_85_hz": result.spectral.rolloff_85_hz,
            "spectral_rolloff_95_hz": result.spectral.rolloff_95_hz,
            "spectral_flatness": result.spectral.flatness,
            "high_frequency_cutoff_hz": result.spectral.high_freq_cutoff_hz,

            # Integrity
            "clipping_sample_count": result.integrity.clipping_sample_count,
            "clipping_ratio": result.integrity.clipping_ratio,
            "silence_ratio": result.integrity.silence_ratio,
            "longest_silence_seconds": result.integrity.longest_silence_seconds,
            "dc_offset_left": result.integrity.dc_offset_left,
            "dc_offset_right": result.integrity.dc_offset_right,
            "estimated_noise_floor_dbfs": result.integrity.noise_floor_dbfs,
        }

    def batch_analyze(self, filepaths: list[str | Path]) -> list[AudioAnalysisResult]:
        """Analyze multiple files and return list of results."""
        results = []
        for fp in filepaths:
            try:
                result = self.analyze(fp)
                results.append(result)
                if self.verbose:
                    print(f"✓ Analyzed: {fp}")
            except Exception as e:
                if self.verbose:
                    print(f"✗ Failed: {fp} - {e}")
                raise
        return results
