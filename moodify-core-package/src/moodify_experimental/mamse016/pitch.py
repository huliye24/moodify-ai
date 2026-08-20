"""MAMSE-016 pitch-evidence operator (YIN-lite, multi-candidate).

Per-frame difference-function candidates (YIN-style cumulative mean
normalized difference), up to K candidates with confidence, harmonic
support from STFT, voicing gate, and stable-pitch-run events. All
values are ESTIMATOR: pitch is never a binary fact, and polyphonic
mixtures may legitimately carry several concurrent candidates.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import stft

from moodify.auditory.evidence.scale import scale_for_duration_ms

from .config import PitchConfig

MIN_ENERGY = 1e-12


@dataclass(frozen=True)
class PitchCandidate:
    frequency_hz: float
    confidence: float  # 1 - cmndf, ESTIMATOR
    harmonic_support: float  # 0..1, energy fraction at 2..5x harmonics

    def to_dict(self) -> dict:
        return {
            "frequency_hz": self.frequency_hz,
            "confidence": self.confidence,
            "harmonic_support": self.harmonic_support,
        }


@dataclass(frozen=True)
class PitchRunEvent:
    event_type: str
    start_ms: int
    end_ms: int
    frequency_hz: float
    scale: str

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "frequency_hz": self.frequency_hz,
            "scale": self.scale,
        }


@dataclass
class PitchObservation:
    status: str  # VALID | EMPTY | DEGRADED
    notes: tuple[str, ...]
    times_s: np.ndarray
    candidates: tuple[tuple[PitchCandidate, ...], ...]  # per frame
    voiced: np.ndarray  # bool per frame
    dominant_f0: np.ndarray  # Hz per frame, NaN when unvoiced
    confidence: np.ndarray  # per frame
    harmonic_support: np.ndarray  # per frame
    events: tuple[PitchRunEvent, ...]
    sr: int
    config_hash: str

    @property
    def voicing_fraction(self) -> float:
        return float(np.mean(self.voiced)) if self.voiced.size else 0.0

    @property
    def harmonic_consistency_mean(self) -> float:
        return float(np.nanmean(self.harmonic_support[self.voiced])) \
            if np.any(self.voiced) else 0.0

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "notes": list(self.notes),
            "n_frames": int(self.times_s.size),
            "voicing_fraction": self.voicing_fraction,
            "harmonic_consistency_mean": self.harmonic_consistency_mean,
            "n_events": len(self.events),
            "config_hash": self.config_hash,
        }


def _frame_candidates(
    frame: np.ndarray, sr: int, config: PitchConfig, spectrum: np.ndarray, freqs: np.ndarray
) -> tuple[PitchCandidate, ...]:
    """YIN-lite candidates for one frame + harmonic support."""
    n = len(frame)
    acf = np.correlate(frame, frame, mode="full")[n - 1:]
    if acf[0] <= MIN_ENERGY:
        return ()
    d = 2.0 * acf[0] - 2.0 * acf  # difference function, d(0) = 0
    lo, hi = config.lag_range(sr)
    cmndf = np.zeros(hi + 1)
    for tau in range(1, hi + 1):
        denom = np.sum(d[1:tau + 1])
        cmndf[tau] = d[tau] * tau / denom if denom > MIN_ENERGY else 1.0

    best: list[tuple[float, int]] = []  # (cmndf, tau)
    for tau in range(lo, hi + 1):
        if cmndf[tau] < config.cmndf_threshold:
            left = cmndf[tau - 1] if tau > lo else 1.0
            right = cmndf[tau + 1] if tau < hi else 1.0
            if cmndf[tau] <= left and cmndf[tau] <= right:
                best.append((cmndf[tau], tau))
    best.sort(key=lambda p: p[0])

    out: list[PitchCandidate] = []
    for cmndf_val, tau in best[: config.max_candidates]:
        f0 = sr / tau
        out.append(PitchCandidate(
            frequency_hz=float(f0),
            confidence=float(1.0 - cmndf_val),
            harmonic_support=_harmonic_support(f0, spectrum, freqs),
        ))
    return tuple(out)


def _harmonic_support(f0: float, spectrum: np.ndarray, freqs: np.ndarray) -> float:
    """Fraction of harmonic-stack energy (2..5x) over fundamental+stack."""
    if f0 <= 0:
        return 0.0
    m = np.maximum(spectrum, 0.0)
    total = float(np.sum(m))
    if total <= MIN_ENERGY:
        return 0.0
    stack = 0.0
    fund = 0.0
    for k in range(1, 6):
        idx = int(round(k * f0 / freqs[1])) if len(freqs) > 1 else 0
        if 0 <= idx < len(freqs) and freqs[idx] <= 5 * f0 * 1.05:
            val = float(m[idx])
            if k == 1:
                fund = val
            else:
                stack += val
    return float(stack / max(fund + stack, MIN_ENERGY))


def compute_pitch_observation(
    samples: np.ndarray,
    sr: int,
    config: PitchConfig | None = None,
) -> PitchObservation:
    config = config or PitchConfig()
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1:
        raise ValueError("MAMSE-016 v0.1 is mono-only; stereo input rejected")
    if np.all(~np.isfinite(x)):
        raise ValueError("signal contains no finite samples")

    notes: list[str] = []
    if x.size < config.frame_samples:
        notes.append("signal shorter than analysis window")

    _, times_s, Z = stft(
        x, fs=sr, nperseg=config.frame_samples,
        noverlap=config.frame_samples - config.hop_length,
        window="hann", boundary=None,
    )
    freqs = np.fft.rfftfreq(config.frame_samples, 1.0 / sr)
    spec = np.abs(Z)

    candidates: list[tuple[PitchCandidate, ...]] = []
    voiced = np.zeros(spec.shape[1], dtype=bool)
    dominant = np.full(spec.shape[1], np.nan)
    confidence = np.zeros(spec.shape[1])
    support = np.zeros(spec.shape[1])

    hop = config.hop_length
    for i in range(spec.shape[1]):
        start = i * hop
        if start >= len(x):
            break
        frame = x[start:start + config.frame_samples]
        if len(frame) < config.frame_samples:
            frame = np.pad(frame, (0, config.frame_samples - len(frame)))
        rms = float(np.sqrt(np.mean(frame ** 2)))
        if rms < 1e-4:
            candidates.append(())
            continue
        cands = _frame_candidates(frame, sr, config, spec[:, i], freqs)
        candidates.append(cands)
        if cands:
            best = max(cands, key=lambda c: c.confidence)
            voiced[i] = True
            dominant[i] = best.frequency_hz
            confidence[i] = best.confidence
            support[i] = best.harmonic_support

    n_frames = len(candidates)
    times_s = np.arange(n_frames, dtype=np.float64) * hop / sr
    events = _detect_runs(voiced[:n_frames], dominant[:n_frames], times_s, sr, config)

    raw_energy = float(np.sum(np.abs(x) ** 2))
    status = "EMPTY" if raw_energy < MIN_ENERGY else "VALID"
    if notes:
        status = "DEGRADED" if status != "EMPTY" else status

    return PitchObservation(
        status=status,
        notes=tuple(notes),
        times_s=times_s,
        candidates=tuple(candidates),
        voiced=voiced[:n_frames],
        dominant_f0=dominant[:n_frames],
        confidence=confidence[:n_frames],
        harmonic_support=support[:n_frames],
        events=tuple(events),
        sr=sr,
        config_hash=config.sha256(),
    )


def _cents(a: float, b: float) -> float:
    return 1200.0 * np.log2(a / b)


def _detect_runs(
    voiced: np.ndarray, dominant: np.ndarray, times_s: np.ndarray, sr: int, config: PitchConfig
) -> list[PitchRunEvent]:
    """Sustained voiced regions with a stable dominant candidate."""
    events: list[PitchRunEvent] = []
    start: int | None = None
    ref_f0 = 0.0
    for i, v in enumerate(voiced):
        if v:
            if start is None:
                start, ref_f0 = i, dominant[i]
            elif abs(_cents(dominant[i], ref_f0)) > config.event_stability_cents:
                _close_run(events, voiced, dominant, times_s, sr, config, start, i, ref_f0)
                start, ref_f0 = i, dominant[i]
        elif start is not None:
            _close_run(events, voiced, dominant, times_s, sr, config, start, i, ref_f0)
            start = None
    if start is not None:
        _close_run(events, voiced, dominant, times_s, sr, config, start, len(voiced), ref_f0)
    return events


def _close_run(events, voiced, dominant, times_s, sr, config, start, end, ref_f0):
    if end - start < config.event_min_frames:
        return
    events.append(PitchRunEvent(
        event_type="STABLE_PITCH_RUN",
        start_ms=int(start * config.hop_length * 1000 / sr),
        end_ms=int((end - 1) * config.hop_length * 1000 / sr),
        frequency_hz=float(ref_f0),
        scale=scale_for_duration_ms((end - start) * config.hop_length * 1000 / sr),
    ))
