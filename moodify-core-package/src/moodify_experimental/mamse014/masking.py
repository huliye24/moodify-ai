"""MAMSE-014 masking-inference operator.

Per-frame ERB channel powers (FFT bin nearest-center assignment; a
masking-inference channelization, not a cochlear model) -> dB ->
spreading-masked thresholds -> soft audibility weights -> masking depth.
Events flag sustained regions where the masked-channel ratio exceeds the
gate. Everything is ESTIMATOR: masking here is spectral-competition
inference, not a hearing test. A channel is masked only when its
measured content sits below the spreading threshold of a louder channel;
a loud tone's own skirt keeps its neighbors audible by construction.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import stft

from moodify.auditory.evidence.scale import scale_for_duration_ms

from .config import MaskConfig

MIN_ENERGY = 1e-12


@dataclass
class MaskingEvent:
    event_type: str
    start_ms: int
    end_ms: int
    peak_depth: float
    scale: str

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "peak_depth": self.peak_depth,
            "scale": self.scale,
        }


@dataclass
class MaskingObservation:
    status: str  # VALID | EMPTY | DEGRADED
    notes: tuple[str, ...]
    center_frequencies_hz: np.ndarray
    times_s: np.ndarray
    channel_power_db: np.ndarray  # n_channels x n_frames
    masked_threshold_db: np.ndarray  # n_channels x n_frames
    audibility: np.ndarray  # n_channels x n_frames, soft 0..1
    masking_depth: np.ndarray  # n_frames, fraction of spectral mass masked
    masked_channel_ratio: np.ndarray  # n_frames, fraction of channels audibility < 0.5
    events: tuple[MaskingEvent, ...]
    sr: int
    config_hash: str

    @property
    def depth_mean(self) -> float:
        return float(np.mean(self.masking_depth)) if self.masking_depth.size else 0.0

    @property
    def depth_p95(self) -> float:
        return float(np.percentile(self.masking_depth, 95)) if self.masking_depth.size else 0.0

    @property
    def masked_channel_ratio_mean(self) -> float:
        return float(np.mean(self.masked_channel_ratio)) if self.masked_channel_ratio.size else 0.0

    @property
    def strongest_masker_frequency_hz(self) -> float:
        mean_power = np.mean(self.channel_power_db, axis=1)
        k = int(np.argmax(mean_power))
        return float(self.center_frequencies_hz[k])

    def audibility_at(self, frequency_hz: float) -> float:
        """Mean soft audibility of the channel nearest to a frequency (0..1)."""
        k = int(np.argmin(np.abs(self.center_frequencies_hz - frequency_hz)))
        return float(np.mean(self.audibility[k]))

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "notes": list(self.notes),
            "n_channels": len(self.center_frequencies_hz),
            "n_frames": int(self.times_s.size),
            "depth_mean": self.depth_mean,
            "depth_p95": self.depth_p95,
            "masked_channel_ratio_mean": self.masked_channel_ratio_mean,
            "strongest_masker_frequency_hz": self.strongest_masker_frequency_hz,
            "n_events": len(self.events),
            "config_hash": self.config_hash,
        }


def _channel_power_db(
    x: np.ndarray, sr: int, config: MaskConfig
) -> tuple[np.ndarray, np.ndarray]:
    """ERB channel powers via nearest-center FFT bin assignment.

    Returns (times_s, power_db). Each FFT bin belongs to exactly one
    channel (nearest ERB center), so a tone's main lobe lands in its own
    channel while far channels see only the window sidelobe floor.
    """
    if x.size < config.window_samples:
        x = np.pad(x, (0, config.window_samples - x.size))
    f, t, Z = stft(
        x, fs=sr, nperseg=config.window_samples,
        noverlap=config.window_samples - config.hop_length,
        window="hann", boundary=None,
    )
    power = np.abs(Z) ** 2  # n_bins x n_frames
    centers = config.center_frequencies()
    assign = np.argmin(np.abs(f[:, None] - centers[None, :]), axis=1)
    channel_power = np.zeros((config.n_channels, power.shape[1]), dtype=np.float64)
    for k in range(config.n_channels):
        channel_power[k] = np.sum(power[assign == k], axis=0)
    raw_total = float(np.sum(power))
    return t, 10.0 * np.log10(np.maximum(channel_power, MIN_ENERGY)), raw_total


def _masked_thresholds(power_db: np.ndarray, config: MaskConfig) -> np.ndarray:
    """Spreading-mask threshold per channel per frame.

    threshold_k = max_j ( P_j - slope * |erb_k - erb_j| - offset )
    """
    erbs = np.asarray(hz_to_erb_vec(config), dtype=np.float64)
    dist = np.abs(erbs[:, None] - erbs[None, :])  # n x n
    spread = config.slope_db_per_erb * dist + config.offset_db
    # A channel must not mask itself (its own P - offset always dominates);
    # only competing channels contribute to the masked threshold.
    np.fill_diagonal(spread, np.inf)
    # threshold for channel k from masker j: P_j - spread[j, k]
    contribution = power_db[:, None, :] - spread[:, :, None]
    return np.max(contribution, axis=0)  # n_channels x n_frames


def hz_to_erb_vec(config: MaskConfig) -> np.ndarray:
    from .config import hz_to_erb

    return hz_to_erb(config.center_frequencies())


def compute_masking_observation(
    samples: np.ndarray,
    sr: int,
    config: MaskConfig | None = None,
) -> MaskingObservation:
    config = config or MaskConfig()
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1:
        raise ValueError("MAMSE-014 v0.1 is mono-only; stereo input rejected")
    if np.all(~np.isfinite(x)):
        raise ValueError("signal contains no finite samples")

    notes: list[str] = []
    if x.size < config.window_samples:
        notes.append("signal shorter than analysis window")

    times_s, power_db, raw_total = _channel_power_db(x, sr, config)
    thresholds = _masked_thresholds(power_db, config)

    # Soft audibility: full at audible_db >= soft_range, zero at <= 0.
    audible_db = power_db - thresholds
    audibility = np.clip(audible_db / config.soft_range_db, 0.0, 1.0)
    power_lin = 10.0 ** (power_db / 10.0)
    audible_power = audibility * power_lin
    total = np.sum(power_lin, axis=0)
    depth = np.zeros_like(total)
    np.divide(np.maximum(total - np.sum(audible_power, axis=0), 0.0),
              np.maximum(total, MIN_ENERGY), out=depth)
    loudest_db = np.max(power_db, axis=0, keepdims=True)
    content = power_db > (loudest_db - config.content_floor_db)
    content_count = np.maximum(np.sum(content, axis=0), 1)
    masked_channel_ratio = np.sum((audibility < 0.5) & content, axis=0) / content_count

    events = _detect_events(masked_channel_ratio, sr, config)

    status = "EMPTY" if raw_total < MIN_ENERGY else "VALID"
    if notes:
        status = "DEGRADED" if status != "EMPTY" else status

    return MaskingObservation(
        status=status,
        notes=tuple(notes),
        center_frequencies_hz=config.center_frequencies(),
        times_s=times_s,
        channel_power_db=power_db,
        masked_threshold_db=thresholds,
        audibility=audibility,
        masking_depth=depth,
        masked_channel_ratio=masked_channel_ratio,
        events=tuple(events),
        sr=sr,
        config_hash=config.sha256(),
    )


def _detect_events(
    ratio: np.ndarray, sr: int, config: MaskConfig
) -> list[MaskingEvent]:
    """Sustained regions where the masked-channel ratio exceeds the gate."""
    hot = ratio > config.event_ratio_threshold
    events: list[MaskingEvent] = []
    start: int | None = None
    peak = 0.0
    for i, flag in enumerate(hot):
        if flag:
            if start is None:
                start = i
            peak = max(peak, float(ratio[i]))
        elif start is not None:
            if i - start >= config.event_min_frames:
                events.append(MaskingEvent(
                    event_type="STRONG_MASKING_REGION",
                    start_ms=int(start * config.hop_length * 1000 / sr),
                    end_ms=int((i - 1) * config.hop_length * 1000 / sr),
                    peak_depth=peak,
                    scale=scale_for_duration_ms((i - start) * config.hop_length * 1000 / sr),
                ))
            start = None
            peak = 0.0
    if start is not None and len(ratio) - start >= config.event_min_frames:
        events.append(MaskingEvent(
            event_type="STRONG_MASKING_REGION",
            start_ms=int(start * config.hop_length * 1000 / sr),
            end_ms=int((len(ratio) - 1) * config.hop_length * 1000 / sr),
            peak_depth=peak,
            scale=scale_for_duration_ms((len(ratio) - start) * config.hop_length * 1000 / sr),
        ))
    return events
