"""
f0.py — F0 / Pitch Stability Analysis (AEP-ACU-008)
=====================================================

Diagnostic-only F0 extraction with stability metrics and AI vocal
artifact flags. Uses librosa.pyin (probabilistic YIN) as default.

What this does:
  - Extract F0 curve, voiced probability, confidence per frame
  - Compute stability: pitch MAD, long-term drift, vibrato rate/depth
  - Flag AI vocal artifacts: drift, unstable tail, fake vibrato,
    abrupt jumps, low confidence
  - Output JSON-serializable report

What this does NOT do:
  - Pitch correction / Auto-Tune
  - Multi-instrument transcription
  - GPU-accelerated CREPE (optional, not default dependency)

Reference:
  de Cheveigné, A. & Kawahara, H. (2002). YIN.
  Mauch, M. & Dixon, S. (2014). pYIN.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np


# ═══════════════════════════════════════════════════════════════════
# Output dataclass
# ═══════════════════════════════════════════════════════════════════


@dataclass
class F0Analysis:
    """Complete F0 / pitch stability analysis (AEP-ACU-008)."""
    feature_version: str = "f0_v0.1"
    sample_rate: int = 44100
    duration_s: float = 0.0
    algorithm: str = "pyin"

    # ── Core F0 output ──
    f0_hz: List[float] = field(default_factory=list)        # per-frame F0
    f0_times_s: List[float] = field(default_factory=list)    # per-frame time
    voiced_prob: List[float] = field(default_factory=list)   # 0-1 per frame
    voiced_ratio: float = 0.0                                 # fraction voiced

    # ── Stability metrics ──
    pitch_median_hz: float = 0.0
    pitch_mad_cents: float = 0.0       # local pitch variability
    long_drift_cents: float = 0.0       # drift over full duration
    vibrato_rate_hz: float = 0.0        # estimated vibrato rate
    vibrato_depth_cents: float = 0.0    # estimated vibrato depth
    jump_count: int = 0                 # abrupt F0 jumps
    unstable_tail_ratio: float = 0.0    # fraction of tail with high variability

    # ── Artifact flags ──
    flags: List[str] = field(default_factory=list)
    confidence: float = 0.0             # overall confidence 0-1

    # ── Limitations ──
    limitations: List[str] = field(default_factory=list)
    failure_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "feature_version": self.feature_version,
            "sample_rate": self.sample_rate,
            "duration_s": round(self.duration_s, 2),
            "algorithm": self.algorithm,
            "f0": {
                "median_hz": round(self.pitch_median_hz, 1),
                "mad_cents": round(self.pitch_mad_cents, 1),
                "long_drift_cents": round(self.long_drift_cents, 1),
                "voiced_ratio": round(self.voiced_ratio, 3),
                "jump_count": self.jump_count,
                "frame_count": len(self.f0_hz),
                "f0_hz_sample": [round(f, 1) for f in self.f0_hz[:50]],
                "voiced_prob_sample": [round(v, 3) for v in self.voiced_prob[:50]],
            },
            "vibrato": {
                "rate_hz": round(self.vibrato_rate_hz, 2),
                "depth_cents": round(self.vibrato_depth_cents, 1),
            },
            "stability": {
                "mad_cents": round(self.pitch_mad_cents, 1),
                "long_drift_cents": round(self.long_drift_cents, 1),
                "unstable_tail_ratio": round(self.unstable_tail_ratio, 3),
            },
            "flags": self.flags,
            "confidence": round(self.confidence, 3),
            "limitations": self.limitations,
            "failure_reason": self.failure_reason or "none",
        }

    def to_json(self, path: str = "") -> str:
        data = self.to_dict()
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return json.dumps(data, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════
# F0 extraction (YIN / pYIN via librosa)
# ═══════════════════════════════════════════════════════════════════


def _hz_to_cents(f0_hz: np.ndarray, ref_hz: float) -> np.ndarray:
    """Convert Hz to cents relative to reference."""
    return 1200.0 * np.log2(np.maximum(f0_hz, 1e-12) / max(ref_hz, 1e-12))


def _detect_jumps(f0_hz: np.ndarray, voiced: np.ndarray,
                  threshold_cents: float = 200.0) -> int:
    """Count abrupt F0 jumps between consecutive voiced frames."""
    if len(f0_hz) < 2:
        return 0
    jumps = 0
    for i in range(1, len(f0_hz)):
        if voiced[i] and voiced[i - 1]:
            if f0_hz[i] > 0 and f0_hz[i - 1] > 0:
                cents = abs(1200.0 * math.log2(f0_hz[i] / f0_hz[i - 1]))
                if cents > threshold_cents:
                    jumps += 1
    return jumps


def _estimate_vibrato(
    f0_hz: np.ndarray, voiced: np.ndarray, sr: int,
    hop_length: int,
) -> Tuple[float, float]:
    """Crude vibrato estimation: look for periodic modulation in F0.

    Returns (rate_hz, depth_cents).
    If no clear vibrato detected, both return 0.0.
    """
    # Extract voiced segments and look for ~4-8 Hz modulation
    f0_voiced = f0_hz[voiced]
    if len(f0_voiced) < 100:
        return 0.0, 0.0

    # Detrend
    from scipy.signal import detrend
    try:
        f0_detrended = detrend(f0_voiced.astype(np.float64))
    except Exception:
        return 0.0, 0.0

    # Simple autocorrelation-based period detection
    n = len(f0_detrended)
    if n < 50:
        return 0.0, 0.0

    # Look for peaks in autocorrelation corresponding to 4-8 Hz
    frame_period = hop_length / sr
    min_lag = int(1.0 / 8.0 / frame_period)   # 8 Hz
    max_lag = int(1.0 / 4.0 / frame_period)   # 4 Hz
    if max_lag >= n or min_lag >= max_lag:
        return 0.0, 0.0

    autocorr = np.correlate(f0_detrended, f0_detrended, mode="full")
    autocorr = autocorr[len(autocorr) // 2:]  # Positive lags only
    autocorr = autocorr / max(autocorr[0], 1e-15)

    if min_lag < len(autocorr) and max_lag < len(autocorr):
        segment = autocorr[min_lag:max_lag]
        peak_idx = np.argmax(segment) + min_lag
        peak_val = autocorr[peak_idx]
        if peak_val > 0.3:  # Significant periodicity
            rate_hz = 1.0 / (peak_idx * frame_period)
            # Depth: std of F0 in cents around median
            median_hz = float(np.median(f0_voiced))
            if median_hz > 0:
                depth = float(np.std(_hz_to_cents(f0_voiced, median_hz)))
                return rate_hz, depth

    return 0.0, 0.0


def _compute_unstable_tail_ratio(
    f0_hz: np.ndarray, voiced: np.ndarray,
    tail_fraction: float = 0.15, mad_threshold_cents: float = 50.0,
) -> float:
    """Compute fraction of tail segment with high pitch variability."""
    n = len(f0_hz)
    tail_start = int(n * (1.0 - tail_fraction))
    if tail_start >= n:
        return 0.0

    tail_f0 = f0_hz[tail_start:]
    tail_voiced = voiced[tail_start:]
    if not np.any(tail_voiced):
        return 0.0

    voiced_f0 = tail_f0[tail_voiced]
    if len(voiced_f0) < 5:
        return 0.0

    median = float(np.median(voiced_f0))
    if median < 1e-6:
        return 0.0
    mad = float(np.median(np.abs(voiced_f0 - median)))
    mad_cents = 1200.0 * math.log2(1.0 + mad / median)

    return 1.0 if mad_cents > mad_threshold_cents else 0.0


# ═══════════════════════════════════════════════════════════════════
# Main extraction function
# ═══════════════════════════════════════════════════════════════════


def analyze_f0(
    audio: np.ndarray,
    sr: int = 44100,
    fmin_hz: float = 65.0,
    fmax_hz: float = 1200.0,
    frame_length: int = 2048,
    hop_length: int = 512,
) -> F0Analysis:
    """Extract F0 curve and compute pitch stability metrics.

    Uses librosa.pyin (probabilistic YIN) for robust F0 estimation
    with built-in voiced/unvoiced detection.

    Args:
        audio: 1D or 2D audio array. Stereo is mixed to mono.
        sr: Sample rate.
        fmin_hz, fmax_hz: F0 search range.
        frame_length, hop_length: STFT frame parameters.

    Returns:
        F0Analysis dataclass with all metrics and flags.
    """
    if audio.ndim > 1:
        mono = audio.mean(axis=1).astype(np.float64)
    else:
        mono = audio.astype(np.float64)

    duration_s = len(mono) / sr

    result = F0Analysis(
        sample_rate=int(sr),
        duration_s=duration_s,
    )

    # ── F0 extraction via librosa.pyin ──
    try:
        import librosa
        f0, voiced_flag, voiced_prob = librosa.pyin(
            mono, fmin=fmin_hz, fmax=fmax_hz,
            sr=sr, frame_length=frame_length,
            hop_length=hop_length,
        )
    except Exception as e:
        result.failure_reason = f"librosa.pyin failed: {e}"
        result.limitations.append("F0 extraction failed — no metrics available")
        result.confidence = 0.0
        return result

    if f0 is None or len(f0) == 0:
        result.failure_reason = "librosa.pyin returned None"
        result.limitations.append("No F0 data produced")
        return result

    # Fill NaN with 0
    f0_nan = np.array(f0, dtype=np.float64)
    v_prob = np.array(voiced_prob, dtype=np.float64)
    v_flag = np.array(voiced_flag, dtype=bool)
    f0_nan = np.nan_to_num(f0_nan, nan=0.0)
    v_prob = np.nan_to_num(v_prob, nan=0.0)

    times = np.arange(len(f0_nan)) * hop_length / sr

    # ── Basic metrics ──
    voiced_mask = v_flag & (f0_nan > 0)
    voiced_f0 = f0_nan[voiced_mask]
    voiced_ratio = float(np.mean(voiced_mask)) if len(voiced_mask) > 0 else 0.0
    confidence = float(np.mean(v_prob[voiced_mask])) if np.any(voiced_mask) else 0.0

    if len(voiced_f0) < 3:
        result.voiced_ratio = voiced_ratio
        result.confidence = 0.0
        result.limitations.append("Too few voiced frames for stability analysis")
        result.failure_reason = "insufficient voiced frames"
        result.f0_hz = f0_nan.tolist()
        result.f0_times_s = times.tolist()
        result.voiced_prob = v_prob.tolist()
        return result

    median_hz = float(np.median(voiced_f0))

    # ── Stability: MAD in cents ──
    cents = _hz_to_cents(voiced_f0, median_hz)
    mad_cents = float(np.median(np.abs(cents - np.median(cents))))

    # ── Long-term drift ──
    if len(voiced_f0) >= 10:
        quarters = np.array_split(voiced_f0, 4)
        q_medians = [float(np.median(q)) for q in quarters if len(q) > 0]
        if len(q_medians) >= 2 and q_medians[0] > 0:
            drift = float(1200.0 * math.log2(
                max(q_medians[-1], 1e-12) / max(q_medians[0], 1e-12)
            ))
            long_drift = abs(drift)
        else:
            long_drift = 0.0
    else:
        long_drift = 0.0

    # ── Jumps ──
    jumps = _detect_jumps(f0_nan, voiced_mask.values if hasattr(voiced_mask, 'values') else voiced_mask)

    # ── Vibrato ──
    v_rate, v_depth = _estimate_vibrato(f0_nan,
                                          voiced_mask.values if hasattr(voiced_mask, 'values') else voiced_mask,
                                          sr, hop_length)

    # ── Unstable tail ──
    tail_ratio = _compute_unstable_tail_ratio(
        f0_nan,
        voiced_mask.values if hasattr(voiced_mask, 'values') else voiced_mask,
    )

    # ── Artifact flags ──
    flags: List[str] = []

    if mad_cents > 50:
        flags.append("pitch_instability")       # High local jitter
    if long_drift > 50:
        flags.append("pitch_drift")             # Long-term drift
    if jumps > 0:
        flags.append("abrupt_jump")             # Sudden F0 jumps
    if tail_ratio > 0.5:
        flags.append("unstable_tail")           # Tail-end instability
    if v_rate > 3.5 and v_depth > 20:
        flags.append("fake_vibrato")            # risk proxy / hypothesis — excessive vibrato
    if confidence < 0.5:
        flags.append("low_confidence")          # Overall low reliability

    # ── Limitations ──
    limitations: List[str] = []
    if voiced_ratio < 0.3:
        limitations.append("Low voiced ratio — may be instrumental or noisy mix")
    if confidence < 0.6:
        limitations.append("Low F0 confidence — pitch metrics may be unreliable")
    if sr < 22050:
        limitations.append("Low sample rate — reduced F0 accuracy")

    # ── Assemble result ──
    result.f0_hz = f0_nan.tolist()
    result.f0_times_s = times.tolist()
    result.voiced_prob = v_prob.tolist()
    result.voiced_ratio = round(voiced_ratio, 3)
    result.pitch_median_hz = round(median_hz, 1)
    result.pitch_mad_cents = round(mad_cents, 1)
    result.long_drift_cents = round(long_drift, 1)
    result.vibrato_rate_hz = round(v_rate, 2)
    result.vibrato_depth_cents = round(v_depth, 1)
    result.jump_count = jumps
    result.unstable_tail_ratio = round(tail_ratio, 3)
    result.flags = flags
    result.confidence = round(confidence, 3)
    result.limitations = limitations

    return result
