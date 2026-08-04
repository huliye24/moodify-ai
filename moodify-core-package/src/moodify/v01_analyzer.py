"""v01_analyzer.py — Spectrum analysis + basic audio metrics.

Produces an AudioMetrics dataclass and optionally a spectrum PNG.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from moodify.audio_io import load_audio
from moodify.bands import (
    get_band_edges,
)
from moodify.v01_types import AudioMetrics

if TYPE_CHECKING:
    from moodify.v01_types import FeatureVector


def analyze(input_path: str, output_dir: str = "outputs",
            label: str = "", band_spec: str = "7") -> AudioMetrics:
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

    rms = _compute_band_rms(mono, sr, band_edges=get_band_edges(band_spec))
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
        rms_presence=float(rms.get("presence", 0.0)),
        rms_brilliance=float(rms.get("brilliance", 0.0)),
        rms_air=float(rms.get("air", 0.0)),
        band_spec=band_spec,
        peak_db=round(peak, 1),
        crest_factor=round(crest, 2),
        dynamic_range_db=round(dyn_range, 1),
        correlation_lr=round(corr, 3),
    )

    _save_spectrum_png(metrics, output_dir, label=label)

    return metrics


# ── internal helpers ────────────────────────────────────

def _compute_band_rms(
    mono: np.ndarray,
    sr: int,
    band_edges: list[tuple[str, float, float]] | None = None,
) -> dict[str, float]:
    """Compute RMS energy per frequency band via FFT."""
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)

    total_energy = np.sum(fft ** 2) + 1e-12
    result = {"total": 20.0 * math.log10(np.sqrt(np.mean(fft ** 2)) + 1e-12)}

    for name, f1, f2 in band_edges or get_band_edges():
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


def spectrum_png_path(input_path: str, output_dir: str = "outputs",
                      label: str = "") -> str:
    """Return the expected spectrum PNG path for an analyzed file."""
    stem = Path(input_path).stem
    suffix = f"_{label}" if label else ""
    return os.path.join(output_dir, f"{stem}{suffix}_spectrum.png")


def _save_spectrum_png(metrics: AudioMetrics, output_dir: str,
                       label: str = "") -> None:
    """Save a simple bar-chart spectrum PNG."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    os.makedirs(output_dir, exist_ok=True)
    stem = Path(metrics.file_path).stem
    out_path = spectrum_png_path(metrics.file_path, output_dir, label=label)

    # Use band names matching the values we have
    if metrics.band_spec == "7":
        from moodify.bands import BAND_7_DISPLAYS, BAND_7_COLORS
        band_names = list(BAND_7_DISPLAYS)
        colors = list(BAND_7_COLORS)
    else:
        from moodify.bands import BAND_6_DISPLAYS, BAND_6_COLORS
        band_names = list(BAND_6_DISPLAYS)
        colors = list(BAND_6_COLORS)

    values = [
        metrics.rms_sub, metrics.rms_bass, metrics.rms_low_mid,
        metrics.rms_mid, metrics.rms_presence,
    ]
    if metrics.band_spec == "7":
        values.append(metrics.rms_brilliance)
    values.append(metrics.rms_air)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(band_names, values, color=colors, edgecolor="white", linewidth=0.5)
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_ylabel("dB (relative to total RMS)")
    title_label = f" ({label})" if label else ""
    ax.set_title(f"Spectrum — {stem}{title_label}")
    ax.set_ylim(max(-40, min(values) - 5), max(values) + 5)

    for bar, val in zip(bars, values):
        y = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, y + 0.5 if y >= 0 else y - 2,
                f"{val:.1f}", ha="center", fontsize=8)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# MAP v0.2 Feature Vector (MHP-852 / MHP-865)
# ═══════════════════════════════════════════════════════════════════════════


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def compute_feature_vector(metrics: AudioMetrics) -> "FeatureVector":
    """Derive the MAP 8-D feature vector from AudioMetrics.

    MHP-852 / MHP-865: All dimensions clamped to [0, 1].
    Uses only fields already present in AudioMetrics.
    """
    import math

    from moodify.v01_types import FeatureVector

    bass_balance = _clamp(math.tanh((metrics.rms_bass + 15.0) / 10.0))
    warmth = _clamp(math.tanh((metrics.rms_low_mid + 10.0) / 10.0))
    clarity = _clamp(math.tanh((metrics.rms_mid + 10.0) / 10.0))
    presence_energy = _clamp(math.tanh((metrics.rms_presence + 15.0) / 12.0))
    density = _clamp(1.0 - min(1.0, metrics.crest_factor / 12.0))
    stereo_width = _clamp(1.0 - abs(metrics.correlation_lr))
    rms_total = metrics.rms_total
    transient_energy = _clamp(
        math.tanh((metrics.peak_db - rms_total - 6.0) / 8.0)
    )
    reality_index = _clamp(1.0 - abs(metrics.dynamic_range_db - 12.0) / 18.0)

    return FeatureVector(
        bass_balance=round(bass_balance, 4),
        warmth=round(warmth, 4),
        clarity=round(clarity, 4),
        presence_energy=round(presence_energy, 4),
        density=round(density, 4),
        stereo_width=round(stereo_width, 4),
        transient_energy=round(transient_energy, 4),
        reality_index=round(reality_index, 4),
    )


def weighted_feature_distance(fv1: "FeatureVector", fv2: "FeatureVector",
                               genre: str = "default") -> float:
    """Compute genre-weighted Euclidean distance between two feature vectors.

    MHP-852: d(a,b) = sqrt(sum(w_g[i] * (a[i] - b[i])^2))
    """
    import math

    from moodify.v01_types import GENRE_WEIGHTS

    weights = GENRE_WEIGHTS.get(genre, GENRE_WEIGHTS["default"])
    v1 = fv1.to_list()
    v2 = fv2.to_list()
    sq = sum(weights[i] * (v1[i] - v2[i]) ** 2 for i in range(8))
    return round(math.sqrt(sq), 4)
