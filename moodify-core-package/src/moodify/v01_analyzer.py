"""v01_analyzer.py — Spectrum analysis + basic audio metrics.

Produces an AudioMetrics dataclass and optionally a spectrum PNG.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np

from moodify.audio_io import load_audio
from moodify.v01_types import AudioMetrics


def analyze(input_path: str, output_dir: str = "outputs") -> AudioMetrics:
    """Load audio and compute basic metrics.

    Args:
        input_path: path to WAV/MP3/FLAC file
        output_dir: directory for spectrum PNG

    Returns:
        AudioMetrics dataclass
    """
    audio, sr = load_audio(input_path, always_2d=False)

    if audio.ndim > 1 and audio.shape[1] >= 2:
        channels = 2
        mono = audio.mean(axis=1)
    else:
        channels = 1
        mono = audio if audio.ndim == 1 else audio[:, 0]

    mono = mono.astype(np.float32)
    duration_s = len(mono) / sr

    rms = _compute_band_rms(mono, sr)
    peak = float(20.0 * math.log10(np.max(np.abs(mono)) + 1e-12))
    crest = float(np.max(np.abs(mono)) / (np.sqrt(np.mean(mono ** 2)) + 1e-12))

    # Dynamic range: P95 – P05 RMS in 100ms windows
    dyn_range = _compute_dynamic_range(mono, sr)

    # Stereo correlation
    corr = _compute_correlation(audio) if channels == 2 else 1.0

    metrics = AudioMetrics(
        file_path=input_path,
        duration_s=duration_s,
        sample_rate=sr,
        channels=channels,
        rms_total=float(rms["total"]),
        rms_sub=float(rms["sub"]),
        rms_bass=float(rms["bass"]),
        rms_low_mid=float(rms["low_mid"]),
        rms_mid=float(rms["mid"]),
        rms_presence=float(rms["presence"]),
        rms_air=float(rms["air"]),
        peak_db=round(peak, 1),
        crest_factor=round(crest, 2),
        dynamic_range_db=round(dyn_range, 1),
        correlation_lr=round(corr, 3),
    )

    _save_spectrum_png(metrics, output_dir)

    return metrics


# ── internal helpers ────────────────────────────────────

from moodify.bands import BAND_6_EDGES as BAND_EDGES, BAND_6_COLORS as BAND_COLORS


def _compute_band_rms(mono: np.ndarray, sr: int) -> dict[str, float]:
    """Compute RMS energy per frequency band via FFT."""
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)

    total_energy = np.sum(fft ** 2) + 1e-12
    result = {"total": 20.0 * math.log10(np.sqrt(np.mean(fft ** 2)) + 1e-12)}

    for name, f1, f2 in BAND_EDGES:
        mask = (freqs >= f1) & (freqs <= f2)
        band_energy = np.sum(fft[mask] ** 2)
        ratio = band_energy / total_energy
        result[name] = 20.0 * math.log10(np.sqrt(ratio + 1e-12))

    return result


def _compute_dynamic_range(mono: np.ndarray, sr: int) -> float:
    """Estimate dynamic range as P95–P05 RMS in 100ms windows."""
    win_len = int(0.1 * sr)
    hop = win_len // 2
    if len(mono) < win_len:
        return 0.0

    rms_vals = []
    for i in range(0, len(mono) - win_len, hop):
        win = mono[i : i + win_len]
        rms = 20.0 * math.log10(np.sqrt(np.mean(win ** 2)) + 1e-12)
        rms_vals.append(rms)

    if len(rms_vals) < 3:
        return 0.0

    rms_arr = np.array(rms_vals)
    return float(np.percentile(rms_arr, 95) - np.percentile(rms_arr, 5))


def _compute_correlation(audio: np.ndarray) -> float:
    """Pearson correlation between left and right channels."""
    left = audio[:, 0]
    right = audio[:, 1]
    std_l, std_r = np.std(left), np.std(right)
    if std_l < 1e-12 or std_r < 1e-12:
        return 1.0
    return float(np.corrcoef(left, right)[0, 1])


def _save_spectrum_png(metrics: AudioMetrics, output_dir: str) -> None:
    """Save a simple bar-chart spectrum PNG."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    os.makedirs(output_dir, exist_ok=True)
    stem = Path(metrics.file_path).stem
    out_path = os.path.join(output_dir, f"{stem}_spectrum.png")

    from moodify.bands import BAND_6_DISPLAYS; bands = list(BAND_6_DISPLAYS)
    values = [
        metrics.rms_sub, metrics.rms_bass, metrics.rms_low_mid,
        metrics.rms_mid, metrics.rms_presence, metrics.rms_air,
    ]
    colors = list(BAND_COLORS)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(bands, values, color=colors, edgecolor="white", linewidth=0.5)
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_ylabel("dB (relative to total RMS)")
    ax.set_title(f"Spectrum — {stem}")
    ax.set_ylim(max(-40, min(values) - 5), max(values) + 5)

    for bar, val in zip(bars, values):
        y = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, y + 0.5 if y >= 0 else y - 2,
                f"{val:.1f}", ha="center", fontsize=8)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
