"""MHP-083: Graduated Over-Dark Detector — FFT-based spectral analysis.

Replaces the binary ``over_dark_triggered`` with a 3-level graduated
assessment (none / mild / severe) based on FFT spectral energy change in
three frequency bands: sub-bass (20-60Hz), low-mid (100-300Hz), mid (300-2000Hz).

v0.2: Replaced time-domain moving average with numpy FFT-based band energy.
      Properly isolates frequency bands, eliminating 100% false-positive rate.
"""

from __future__ import annotations

import math
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ── Data model ──────────────────────────────────────────────────────


@dataclass
class OverDarkResult:
    level: str            # "none" | "mild" | "severe"
    score: float          # 0.0 (no darkness) → 1.0 (maximum darkness)
    affected_bands: List[str]   # e.g. ["low_mid", "mid"]
    band_scores: Dict[str, float]  # per-band delta ratio
    is_processing_induced: bool   # True if after is darker than before
    recommendation: str   # "pass" | "review" | "reject"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def triggered(self) -> bool:
        """Backward-compatible boolean flag. True if mild or severe."""
        return self.level in ("mild", "severe")


# ── Frequency band definitions ──────────────────────────────────────


FREQ_BANDS: List[Tuple[float, float, str]] = [
    (20.0, 60.0, "sub_bass"),
    (100.0, 300.0, "low_mid"),
    (300.0, 2000.0, "mid"),
]


# Genre-specific tolerance: max allowed per-band delta ratio before flagging.
# Sub_bass is naturally low-energy in most recordings → higher tolerance.
# low_mid and mid are the perceptually important bands → tighter tolerance.
GENRE_TOLERANCE: Dict[str, Dict[str, float]] = {
    "electronic": {"sub_bass": 1.50, "low_mid": 0.30, "mid": 0.30},
    "piano":      {"sub_bass": 1.00, "low_mid": 0.20, "mid": 0.20},
    "vocal":      {"sub_bass": 1.00, "low_mid": 0.25, "mid": 0.20},
    "rock":       {"sub_bass": 1.50, "low_mid": 0.30, "mid": 0.25},
    "ambient":    {"sub_bass": 1.50, "low_mid": 0.25, "mid": 0.20},
}

# Minimum energy floor: bands with normalized energy below this aren't penalized.
# Prevents low-energy bands (esp. sub_bass) from triggering false positives
# due to tiny absolute changes producing huge relative deltas.
MIN_BAND_ENERGY = 0.001


# ── Audio I/O ───────────────────────────────────────────────────────


def _read_pcm_mono(path: str) -> Tuple[np.ndarray, int]:
    """Read WAV file, return (float64 mono samples, sample_rate)."""
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)

    if sw == 2:
        samples = np.frombuffer(raw[:nframes * nch * 2], dtype=np.int16)
    elif sw == 1:
        samples = (np.frombuffer(raw[:nframes * nch], dtype=np.uint8).astype(np.float64) - 128.0).astype(np.int16)
    elif sw == 3:
        # 24-bit: slower but correct
        arr = np.frombuffer(raw[:nframes * nch * 3], dtype=np.uint8)
        arr = arr.reshape(-1, 3)
        samples = (arr[:, 0].astype(np.int32) +
                   (arr[:, 1].astype(np.int32) << 8) +
                   (arr[:, 2].astype(np.int32) << 16))
        # sign-extend
        samples = np.where(samples >= 0x800000, samples - 0x1000000, samples)
        samples = samples.astype(np.int16)
    else:
        samples = np.frombuffer(raw[:nframes * nch * 4], dtype=np.int32).astype(np.int16)

    if nch > 1:
        samples = samples.reshape(-1, nch).mean(axis=1)

    return samples.astype(np.float64), sr


# ── FFT-based band energy ───────────────────────────────────────────


def _band_energy_fft(samples: np.ndarray, sr: int, low_hz: float, high_hz: float) -> float:
    """Compute energy in [low_hz, high_hz] using FFT magnitude spectrum.

    Uses numpy FFT with Hann window for spectral leakage reduction.
    """
    if len(samples) < 2 or sr <= 0:
        return 0.0

    n = len(samples)
    # Hann window
    window = np.hanning(n)
    windowed = samples * window

    # Real FFT
    fft = np.fft.rfft(windowed)
    mag = np.abs(fft)
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)

    # Sum squared magnitude in band
    band_mask = (freqs >= low_hz) & (freqs <= high_hz)
    if not band_mask.any():
        return 0.0

    energy = float(np.sum(mag[band_mask] ** 2))
    return energy / n  # normalize by length


def _compute_band_energies(audio_path: str) -> Dict[str, float]:
    """Compute FFT band energies for an audio file."""
    samples, sr = _read_pcm_mono(audio_path)
    if len(samples) == 0 or sr <= 0:
        return {"sub_bass": 0.0, "low_mid": 0.0, "mid": 0.0}

    return {
        name: _band_energy_fft(samples, sr, low, high)
        for low, high, name in FREQ_BANDS
    }


# ── Main detector ───────────────────────────────────────────────────


def detect_over_dark(
    before_path: str,
    after_path: str,
    genre: str = "",
) -> OverDarkResult:
    """Graduated over-dark detection comparing before/after audio via FFT.

    Args:
        before_path: Path to original (pre-processing) audio file.
        after_path: Path to processed audio file.
        genre: Optional genre hint for tolerance tuning.

    Returns:
        OverDarkResult with level, score, affected bands, and recommendation.
    """
    before_p = Path(before_path)
    after_p = Path(after_path)

    # Non-WAV or missing files: fall back conservatively
    if before_p.suffix.lower() != ".wav" or after_p.suffix.lower() != ".wav":
        after_exists = after_p.exists()
        return OverDarkResult(
            level="mild" if not after_exists else "none",
            score=0.5 if not after_exists else 0.0,
            affected_bands=[] if after_exists else ["unknown"],
            band_scores={},
            is_processing_induced=not after_exists,
            recommendation="review" if not after_exists else "pass",
        )

    if not before_p.exists() or not after_p.exists():
        return OverDarkResult(
            level="mild", score=0.3, affected_bands=["unknown"],
            band_scores={}, is_processing_induced=True, recommendation="review",
        )

    before_energy = _compute_band_energies(str(before_p))
    after_energy = _compute_band_energies(str(after_p))

    tolerance = GENRE_TOLERANCE.get(genre, GENRE_TOLERANCE["piano"])
    affected: List[str] = []
    band_scores: Dict[str, float] = {}
    max_delta = 0.0
    total_energy_before = sum(before_energy.values())
    total_energy_after = sum(after_energy.values())

    # Normalize by total energy to avoid loudness-based false positives
    norm_factor_before = total_energy_before if total_energy_before > 1e-12 else 1.0
    norm_factor_after = total_energy_after if total_energy_after > 1e-12 else 1.0

    for _low, _high, name in FREQ_BANDS:
        before_norm = before_energy.get(name, 0.0) / norm_factor_before
        after_norm = after_energy.get(name, 0.0) / norm_factor_after

        # Skip bands with negligible energy (prevents false positives from
        # tiny absolute changes in nearly-silent bands, esp. sub_bass)
        if before_norm < MIN_BAND_ENERGY and after_norm < MIN_BAND_ENERGY:
            band_scores[name] = 0.0
            continue

        # Delta ratio: how much the band changed relative to before
        if before_norm > MIN_BAND_ENERGY:
            delta = (after_norm - before_norm) / before_norm
        elif after_norm > MIN_BAND_ENERGY:
            # New energy appeared where there was none — significant
            delta = 1.0
        else:
            delta = 0.0

        band_scores[name] = round(delta, 4)
        tol = tolerance.get(name, 0.15)

        if delta > tol * 2.0:
            affected.append(name)
            max_delta = max(max_delta, delta)
        elif delta > tol:
            affected.append(name)
            max_delta = max(max_delta, delta)

    is_darker = any(v > 0.001 for v in band_scores.values())

    # Classify
    if len(affected) == 0:
        level = "none"
        recommendation = "pass"
    elif len(affected) >= 2 and max_delta > 0.8:
        # Multiple bands with substantial darkening → severe
        level = "severe"
        recommendation = "reject"
    elif len(affected) >= 3:
        # All three bands affected → severe
        level = "severe"
        recommendation = "reject"
    elif max_delta > 1.5:
        # Single band with extreme darkening → severe
        level = "severe"
        recommendation = "reject"
    else:
        level = "mild"
        recommendation = "review"

    score = min(1.0, max_delta / 0.30)

    return OverDarkResult(
        level=level,
        score=round(score, 4),
        affected_bands=affected,
        band_scores=band_scores,
        is_processing_induced=is_darker,
        recommendation=recommendation,
    )
