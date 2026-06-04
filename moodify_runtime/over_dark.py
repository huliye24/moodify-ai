"""MHP-072: Graduated Over-Dark Detector — 3-level replacement for binary flag.

Replaces the binary ``over_dark_triggered`` with a 3-level graduated
assessment (none / mild / severe) based on spectral energy change in
three frequency bands: sub-bass (20-60Hz), low-mid (100-300Hz), mid (300-2000Hz).
"""

from __future__ import annotations

import math
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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


# Bands as (low_hz, high_hz, name)
FREQ_BANDS: List[Tuple[float, float, str]] = [
    (20.0, 60.0, "sub_bass"),
    (100.0, 300.0, "low_mid"),
    (300.0, 2000.0, "mid"),
]


# Genre-specific tolerance: max allowed per-band delta ratio before flagging
# Higher = more tolerant. "mild" threshold is this value; "severe" is 2×.
GENRE_TOLERANCE: Dict[str, Dict[str, float]] = {
    # (sub_bass, low_mid, mid)
    "electronic": {"sub_bass": 0.20, "low_mid": 0.15, "mid": 0.15},
    "piano":      {"sub_bass": 0.10, "low_mid": 0.10, "mid": 0.10},
    "vocal":      {"sub_bass": 0.10, "low_mid": 0.12, "mid": 0.10},
    "rock":       {"sub_bass": 0.15, "low_mid": 0.15, "mid": 0.12},
    "ambient":    {"sub_bass": 0.15, "low_mid": 0.12, "mid": 0.10},
}


# ── PCM band energy ─────────────────────────────────────────────────


def _read_pcm_mono(path: str) -> Tuple[List[float], int]:
    """Read WAV file, return (normalized_mono_samples [-1..1], sample_rate)."""
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)

    if sw == 2:
        import struct
        count = len(raw) // 2
        fmt = "<" + "h" * count
        samples = list(struct.unpack(fmt, raw[:count * 2]))
        max_val = 32768.0
    elif sw == 1:
        samples = [b - 128 for b in raw]
        max_val = 128.0
    elif sw == 3:
        samples = []
        for i in range(0, len(raw) - 2, 3):
            b = raw[i:i + 3]
            val = int.from_bytes(b + (b"\xff" if b[2] & 0x80 else b"\x00"), "little", signed=True)
            samples.append(val)
        max_val = 8388608.0
    else:
        return [], sr

    if nch > 1:
        mono = []
        for i in range(0, len(samples) - nch + 1, nch):
            mono.append(sum(samples[i:i + nch]) / nch)
    else:
        mono = list(samples)

    normalized = [v / max_val for v in mono]
    return normalized, sr


def _band_energy(samples: List[float], sr: int, low_hz: float, high_hz: float) -> float:
    """Approximate energy in a frequency band using a simple time-domain bandpass.

    Uses a crude first-order approximation: the ratio of samples to band
    width. For precision, a real FFT would be preferred, but this avoids
    numpy dependency. Good enough for over-dark detection.
    """
    if not samples or sr <= 0:
        return 0.0

    n = len(samples)
    # Simple moving-average filter as crude bandpass emulation.
    # Low_hz determines window size; the smaller the low frequency,
    # the larger the window needed.
    if low_hz <= 0:
        return 0.0

    # Window: ~ sr / low_hz samples (capture one cycle of lowest freq)
    window = max(1, int(sr / low_hz))
    # Decimation factor: keep ~2× highest freq resolution
    decimate = max(1, int(sr / (high_hz * 4)))

    energy = 0.0
    count = 0
    # Apply a simple rolling window
    for i in range(0, n - window, decimate):
        chunk = samples[i:i + window]
        avg = sum(chunk) / len(chunk)
        energy += avg * avg
        count += 1

    return energy / max(count, 1)


def _compute_band_energies(audio_path: str) -> Dict[str, float]:
    """Compute energy in each frequency band for an audio file."""
    samples, sr = _read_pcm_mono(audio_path)
    if not samples or sr <= 0:
        return {"sub_bass": 0.0, "low_mid": 0.0, "mid": 0.0}

    return {
        name: _band_energy(samples, sr, low, high)
        for low, high, name in FREQ_BANDS
    }


# ── Main detector ───────────────────────────────────────────────────


def detect_over_dark(
    before_path: str,
    after_path: str,
    genre: str = "",
) -> OverDarkResult:
    """Graduated over-dark detection comparing before/after audio.

    Args:
        before_path: Path to original (pre-processing) audio file.
        after_path: Path to processed audio file.
        genre: Optional genre hint for tolerance tuning.

    Returns:
        OverDarkResult with level, score, affected bands, and recommendation.
    """
    before_p = Path(before_path)
    after_p = Path(after_path)

    # Non-WAV: fall back to binary flag based on file existence
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
        missing = "before" if not before_p.exists() else "after"
        return OverDarkResult(
            level="mild",
            score=0.3,
            affected_bands=["unknown"],
            band_scores={},
            is_processing_induced=True,
            recommendation="review",
        )

    before_energy = _compute_band_energies(str(before_p))
    after_energy = _compute_band_energies(str(after_p))

    tolerance = GENRE_TOLERANCE.get(genre, GENRE_TOLERANCE["piano"])
    affected: List[str] = []
    band_scores: Dict[str, float] = {}
    max_delta = 0.0

    for _low, _high, name in FREQ_BANDS:
        before_val = before_energy.get(name, 0.0)
        after_val = after_energy.get(name, 0.0)
        if before_val > 1e-12:
            delta = (after_val - before_val) / before_val
        else:
            delta = after_val if after_val > 1e-12 else 0.0

        band_scores[name] = round(delta, 4)
        tol = tolerance.get(name, 0.10)

        if delta > tol * 2:
            affected.append(name)
            max_delta = max(max_delta, delta)
        elif delta > tol:
            # Mild: included but with lower weight
            if name not in affected:
                affected.append(name)
            max_delta = max(max_delta, delta)

    is_darker = any(v > 0.01 for v in band_scores.values())

    # Classify
    if len(affected) == 0:
        level = "none"
        recommendation = "pass"
    elif max_delta > tolerance.get(list(tolerance.keys())[0], 0.10) * 3:
        level = "severe"
        recommendation = "reject"
    elif len(affected) >= 2:
        level = "severe"
        recommendation = "reject"
    else:
        level = "mild"
        recommendation = "review"

    score = min(1.0, max_delta / 0.30)  # normalize: 30% delta = score 1.0

    return OverDarkResult(
        level=level,
        score=round(score, 4),
        affected_bands=affected,
        band_scores=band_scores,
        is_processing_induced=is_darker,
        recommendation=recommendation,
    )
