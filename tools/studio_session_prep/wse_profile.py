"""WSE profile generation — wave-spectral evolution analysis.

Produces a versioned WseProfile JSON with all available metrics, explicit
null entries for unavailable measurements, per-window evolution CSV, and
warnings index.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from .metrics_adapter import (
    FloatArray,
    MetricOutput,
    band_fractions,
    left_right_correlation,
    level_metrics,
    loudness_metrics,
    spectral_metrics,
)

WSE_PROFILE_VERSION = "1.0.0"


@dataclass
class WseProfile:
    """Complete WSE analysis profile for one audio file."""

    profile_version: str = WSE_PROFILE_VERSION
    tool_version: str = "0.1.0"
    source_path: str = ""
    source_sha256: str = ""
    sample_rate: int = 0
    channels: int = 0
    duration_s: float = 0.0
    num_samples: int = 0
    generated_at: str = ""

    # Level
    peak_linear: float | None = None
    rms_linear: float | None = None
    crest_factor: float | None = None

    # Loudness
    loudness_lufs: float | None = None  # null if pyloudnorm unavailable

    # Spectral
    spectral_entropy: float | None = None
    spectral_centroid_hz: float | None = None
    spectral_flux: float | None = None

    # Band fractions
    band_fractions: dict[str, float | None] = field(default_factory=dict)

    # Stereo
    left_right_correlation: float | None = None

    # Explicitly unavailable — always null
    lra_lu: None = None
    true_peak_dbtp: None = None
    phase_rotation_deg: None = None
    masking_index: None = None

    # Warnings index
    warnings: list[str] = field(default_factory=list)

    # Window evolution summary
    window_count: int = 0
    window_frame_size: int = 0
    window_hop_size: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_version": self.profile_version,
            "tool_version": self.tool_version,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "duration_s": self.duration_s,
            "num_samples": self.num_samples,
            "generated_at": self.generated_at,
            "level": {
                "peak_linear": self.peak_linear,
                "rms_linear": self.rms_linear,
                "crest_factor": self.crest_factor,
                "peak_dbfs": _linear_to_db(self.peak_linear) if self.peak_linear else None,
                "rms_db": _linear_to_db(self.rms_linear) if self.rms_linear else None,
            },
            "loudness": {
                "loudness_lufs": self.loudness_lufs,
                "lra_lu": self.lra_lu,
                "true_peak_dbtp": self.true_peak_dbtp,
            },
            "spectral": {
                "spectral_entropy": self.spectral_entropy,
                "spectral_centroid_hz": self.spectral_centroid_hz,
                "spectral_flux": self.spectral_flux,
            },
            "band_fractions": self.band_fractions,
            "stereo": {
                "left_right_correlation": self.left_right_correlation,
            },
            "unavailable": {
                "lra_lu": "null — pyloudnorm does not provide LRA output",
                "true_peak_dbtp": "null — no BS.1770 true peak meter available",
                "phase_rotation_deg": "null — no phase analysis backend",
                "masking_index": "null — experimental; no validated model",
            },
            "warnings": self.warnings,
            "window_evolution": {
                "window_count": self.window_count,
                "frame_size": self.window_frame_size,
                "hop_size": self.window_hop_size,
            },
        }


def _linear_to_db(value: float) -> float:
    return round(20.0 * np.log10(max(value, 1e-12)), 2)


def _load_audio(path: str) -> tuple[FloatArray, int, int, float, int]:
    """Load audio, return samples, sr, channels, duration_s, num_samples."""
    import soundfile as sf

    data, sr = sf.read(path, always_2d=False, dtype="float64")
    samples = np.asarray(data, dtype=np.float64)
    channels = 1 if samples.ndim == 1 else samples.shape[1]
    num_samples = samples.shape[0] if samples.ndim == 1 else samples.shape[0]
    duration = num_samples / sr if sr > 0 else 0.0
    return samples, sr, channels, duration, num_samples


def compute_wse_profile(
    audio_path: str,
    source_sha256: str = "",
    frame_size: int = 2048,
    hop_size: int = 1024,
) -> WseProfile:
    """Compute complete WSE profile for an audio file. Read-only."""
    profile = WseProfile()
    profile.generated_at = datetime.now(timezone.utc).isoformat()
    profile.source_path = str(Path(audio_path).resolve())
    profile.source_sha256 = source_sha256
    profile.window_frame_size = frame_size
    profile.window_hop_size = hop_size

    try:
        samples, sr, channels, duration, num_samples = _load_audio(audio_path)
    except Exception as exc:
        profile.warnings.append(f"Failed to load audio: {exc}")
        return profile

    profile.sample_rate = sr
    profile.channels = channels
    profile.duration_s = round(duration, 3)
    profile.num_samples = num_samples

    # Level
    lm = level_metrics(samples)
    profile.peak_linear = lm.values.get("peak")
    profile.rms_linear = lm.values.get("rms")
    profile.crest_factor = lm.values.get("crest_factor")
    profile.warnings.extend(lm.warnings)

    # Loudness
    lum = loudness_metrics(samples, sr)
    profile.loudness_lufs = lum.values.get("loudness_lufs")
    profile.warnings.extend(lum.warnings)

    # Spectral
    sm = spectral_metrics(samples, sr, frame_size, hop_size)
    profile.spectral_entropy = sm.values.get("spectral_entropy")
    profile.spectral_centroid_hz = sm.values.get("spectral_centroid_hz")
    profile.spectral_flux = sm.values.get("spectral_flux")
    profile.warnings.extend(sm.warnings)

    # Band fractions
    bm = band_fractions(samples, sr)
    profile.band_fractions = bm.values
    profile.warnings.extend(bm.warnings)

    # Stereo
    stm = left_right_correlation(samples)
    profile.left_right_correlation = stm.values.get("left_right_correlation")
    profile.warnings.extend(stm.warnings)

    return profile


def compute_window_evolution(
    audio_path: str,
    frame_size: int = 2048,
    hop_size: int = 1024,
) -> tuple[list[dict[str, Any]], int]:
    """Sliding-window evolution: per-window time, RMS, peak, centroid, band fractions.

    Returns (list of window dicts, number of windows).
    """
    try:
        samples, sr, _, _, _ = _load_audio(audio_path)
    except Exception:
        return [], 0

    mono = samples if samples.ndim == 1 else samples.mean(axis=1).astype(np.float64)
    n = len(mono)
    if n < frame_size:
        return [], 0

    bands = ((20, 250), (250, 2000), (2000, 8000), (8000, 20000))
    windows = []
    for i in range(0, n - frame_size + 1, hop_size):
        frame = mono[i : i + frame_size]
        time_s = round(i / sr, 3)
        peak = float(np.max(np.abs(frame)))
        rms = float(np.sqrt(np.mean(frame * frame)))

        win = frame * np.hanning(frame_size)
        mag = np.abs(np.fft.rfft(win))
        freq = np.fft.rfftfreq(frame_size, 1 / sr)
        total_mag = mag.sum()
        if total_mag > 0:
            centroid = float(np.sum(freq * mag) / total_mag)
        else:
            centroid = 0.0

        bf = {}
        total_power = float(np.sum(mag ** 2))
        if total_power > 0:
            for low, high in bands:
                bf[f"band_{low:g}_{high:g}_fraction"] = round(
                    float(np.sum(mag[(freq >= low) & (freq < high)] ** 2) / total_power), 6,
                )

        windows.append({
            "window_index": len(windows),
            "time_s": time_s,
            "rms_linear": round(rms, 6),
            "peak_linear": round(peak, 6),
            "centroid_hz": round(centroid, 1),
            **bf,
        })

    return windows, len(windows)


def write_wse_profile(profile: WseProfile, output_dir: Path) -> Path:
    """Write WseProfile as JSON to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "wse_profile.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)
    return path


def write_wse_warnings(profile: WseProfile, output_dir: Path) -> Path:
    """Write explicit warnings file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "wse_warnings.json"
    data = {
        "profile_version": profile.profile_version,
        "source_path": profile.source_path,
        "warnings": profile.warnings,
        "null_metrics": {
            "lra_lu": "pyloudnorm does not provide LRA",
            "true_peak_dbtp": "no BS.1770 true peak meter available",
            "phase_rotation_deg": "no phase analysis backend",
            "masking_index": "experimental; no validated model",
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def write_window_evolution_csv(
    windows: list[dict[str, Any]],
    output_dir: Path,
) -> Path:
    """Write window evolution data as CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "wse_evolution.csv"
    if not windows:
        path.write_text("No windows computed.\n", encoding="utf-8")
        return path

    fieldnames = list(windows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(windows)
    return path
