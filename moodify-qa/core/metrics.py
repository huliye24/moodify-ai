"""Individual metric calculators - migrated from Moodify Engine.

Each module preserves the original algorithm logic from:
- moodify.auditory.loudness
- moodify.auditory.true_peak
- moodify.auditory.stereo
- moodify.auditory.metrics
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import lfilter, resample_poly


# =============================================================================
# Constants (from BS.1770 / EBU Tech 3341)
# =============================================================================

_RLB_B = [1.53512485958697, -2.69169618940638, 1.19839281085285]
_RLB_A = [1.0, -1.69065929318241, 0.73248077421585]
_HS_B = [1.0, -2.0, 1.0]
_HS_A = [1.0, -1.99004745483398, 0.99007225036621]

_ABS_GATE_LUFS = -70.0
_REL_GATE_LU = -10.0
_BLOCK_S = 0.4
_SHORT_BLOCK_S = 3.0
_LOUDNESS_OFFSET = -0.691


def _k_weighted(x: np.ndarray, sr: int) -> np.ndarray:
    """K-weighting (RLB high-pass + high-shelf)."""
    if sr not in (44100, 48000):
        x = resample_poly(x, 48000, sr)
    y = lfilter(_RLB_B, _RLB_A, x)
    return lfilter(_HS_B, _HS_A, y)


def _block_loudness(y: np.ndarray, sr: int, block_s: float, overlap: float = 0.75) -> np.ndarray:
    """Per-block loudness with standard 75% overlap."""
    block = int(block_s * sr)
    hop = max(1, int(block * (1 - overlap)))
    n = len(y)
    if n < block:
        return np.array([])
    z = sliding_window_view(y, block)[::hop]
    return 10 * np.log10(np.mean(z ** 2, axis=1) + 1e-12) + _LOUDNESS_OFFSET


def _channel_weight(channels: int) -> list[float]:
    """BS.1770-5 channel weights."""
    if channels <= 1:
        return [1.0]
    return [1.0, 1.0]


# =============================================================================
# Loudness Metrics (ITU-R BS.1770-5 / EBU Tech 3341)
# =============================================================================

@dataclass
class LoudnessMetrics:
    """Loudness measurements per BS.1770-5."""

    integrated_lufs: float = -70.0
    loudness_range_lu: float | None = None
    momentary_max_lufs: float = -70.0
    short_term_max_lufs: float = -70.0

    @classmethod
    def from_samples(cls, samples: np.ndarray, sr: int) -> LoudnessMetrics:
        """Compute loudness metrics from audio samples."""
        if samples.ndim == 1:
            samples = samples[:, None]

        weights = _channel_weight(samples.shape[1])
        energies = []

        # Integrated loudness
        for channel, weight in zip(range(samples.shape[1]), weights):
            weighted = _k_weighted(samples[:, channel], sr)
            loudness = _block_loudness(weighted, sr, _BLOCK_S)
            if loudness.size == 0:
                return cls()
            energies.append(weight * 10 ** (loudness / 10))

        combined = np.sum(energies, axis=0) / sum(weights)
        block_loudness = 10 * np.log10(combined + 1e-12)

        # Gates
        abs_gate = block_loudness[block_loudness > _ABS_GATE_LUFS]
        if abs_gate.size == 0:
            integrated = _ABS_GATE_LUFS
        else:
            rel_threshold = np.mean(abs_gate) + _REL_GATE_LU
            final = abs_gate[abs_gate > rel_threshold]
            if final.size == 0:
                integrated = _ABS_GATE_LUFS
            else:
                integrated = float(10 * np.log10(np.mean(10 ** (final / 10)) + 1e-12))

        # Loudness Range (EBU Tech 3342)
        mono = samples.mean(axis=1) if samples.ndim > 1 else samples
        weighted = _k_weighted(mono, sr)
        short = _block_loudness(weighted, sr, _SHORT_BLOCK_S)
        if short.size < 2:
            lra = None
        else:
            lo, hi = np.percentile(short, [10, 95])
            lra = float(max(0.0, hi - lo))

        # Momentary (400ms) and Short-term (3s) max
        momentary = _block_loudness(weighted, sr, 0.4)
        short_term = _block_loudness(weighted, sr, 3.0)

        return cls(
            integrated_lufs=round(integrated, 2),
            loudness_range_lu=round(lra, 2) if lra is not None else None,
            momentary_max_lufs=round(float(momentary.max()), 2) if momentary.size > 0 else -70.0,
            short_term_max_lufs=round(float(short_term.max()), 2) if short_term.size > 0 else -70.0,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "integrated_lufs": self.integrated_lufs,
            "loudness_range_lu": self.loudness_range_lu,
            "momentary_max_lufs": self.momentary_max_lufs,
            "short_term_max_lufs": self.short_term_max_lufs,
        }


# =============================================================================
# Peak Metrics (ITU-R BS.1770-5 True Peak)
# =============================================================================

@dataclass
class PeakMetrics:
    """Peak measurements including true peak (4x oversampling)."""

    true_peak_dbfs: float = 0.0
    sample_peak_dbfs: float = 0.0
    peak_to_loudness_ratio: float = 0.0

    @classmethod
    def from_samples(cls, samples: np.ndarray, sr: int, loudness_lufs: float = -23.0) -> PeakMetrics:
        """Compute peak metrics from audio samples."""
        if samples.ndim == 1:
            samples = samples[:, None]

        # Sample peak
        sample_peak = float(np.max(np.abs(samples)))
        sample_peak_db = 20 * np.log10(sample_peak + 1e-12)

        # True peak (4x oversampling)
        peaks = []
        for channel in range(samples.shape[1]):
            upsampled = resample_poly(samples[:, channel], 4, 1)
            peaks.append(float(np.max(np.abs(upsampled))))
        true_peak = max(peaks)
        true_peak_db = 20 * np.log10(true_peak + 1e-12)

        # PLR (Peak to Loudness Ratio)
        plr = true_peak_db - loudness_lufs

        return cls(
            true_peak_dbfs=round(true_peak_db, 2),
            sample_peak_dbfs=round(sample_peak_db, 2),
            peak_to_loudness_ratio=round(plr, 2),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "true_peak_dbfs": self.true_peak_dbfs,
            "sample_peak_dbfs": self.sample_peak_dbfs,
            "peak_to_loudness_ratio": self.peak_to_loudness_ratio,
        }


# =============================================================================
# Dynamic Metrics
# =============================================================================

@dataclass
class DynamicMetrics:
    """Dynamic range and crest factor measurements."""

    crest_factor_db: float = 0.0
    rms_dbfs: float = -100.0
    dynamic_range_db: float = 0.0

    @classmethod
    def from_samples(cls, samples: np.ndarray, sr: int) -> DynamicMetrics:
        """Compute dynamic metrics from audio samples."""
        mono = samples.mean(axis=1) if samples.ndim > 1 else samples

        # RMS
        rms = np.sqrt(np.mean(mono ** 2))
        rms_db = 20 * np.log10(rms + 1e-12)

        # Sample peak
        peak = np.max(np.abs(mono))
        peak_db = 20 * np.log10(peak + 1e-12)

        # Crest factor
        crest = peak_db - rms_db

        # Dynamic range estimate (using percentile spread)
        # 95th percentile - 10th percentile of short-term loudness
        win = int(0.1 * sr)  # 100ms windows
        n_win = len(mono) // win
        if n_win > 10:
            rms_windows = np.array([
                np.sqrt(np.mean(mono[i*win:(i+1)*win] ** 2))
                for i in range(n_win)
            ])
            rms_windows_db = 20 * np.log10(rms_windows + 1e-12)
            dr = float(np.percentile(rms_windows_db, 95) - np.percentile(rms_windows_db, 10))
        else:
            dr = crest  # fallback

        return cls(
            crest_factor_db=round(crest, 2),
            rms_dbfs=round(rms_db, 2),
            dynamic_range_db=round(dr, 2),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "crest_factor_db": self.crest_factor_db,
            "rms_dbfs": self.rms_dbfs,
            "dynamic_range_db": self.dynamic_range_db,
        }


# =============================================================================
# Stereo Metrics (M/S Analysis)
# =============================================================================

@dataclass
class StereoMetrics:
    """Stereo and M/S analysis metrics."""

    available: bool = False
    correlation: float = 0.0
    mid_ratio: float = 0.0
    side_ratio: float = 0.0
    side_to_mid_db: float = 0.0
    width_proxy: float = 0.0
    negative_correlation_ratio: float = 0.0
    phase_risk_ratio: float = 0.0

    @classmethod
    def from_samples(cls, samples: np.ndarray) -> StereoMetrics:
        """Compute stereo metrics from audio samples."""
        if samples.ndim < 2 or samples.shape[1] < 2:
            return cls(available=False)

        left = samples[:, 0].astype(np.float64)
        right = samples[:, 1].astype(np.float64)
        mid = (left + right) / 2.0
        side = (left - right) / 2.0

        # Correlation
        if np.std(left) > 0 and np.std(right) > 0:
            corr = float(np.corrcoef(left, right)[0, 1])
        else:
            corr = 0.0

        # M/S energy
        mid_e = float(np.mean(mid ** 2))
        side_e = float(np.mean(side ** 2))
        total = mid_e + side_e + 1e-12

        # Width proxy
        width = 1.0 - abs(corr)

        # Side-to-mid ratio in dB
        side_to_mid = float(10 * np.log10((side_e + 1e-12) / (mid_e + 1e-12)))

        # Frame-wise analysis for phase risk
        win = 4096
        hop = 2048
        n = max(1, (len(left) - win) // hop + 1)

        neg_count = 0
        phase_risk = 0
        for i in range(n):
            lw = left[i * hop: i * hop + win]
            rw = right[i * hop: i * hop + win]
            if len(lw) < win:
                break
            if np.std(lw) > 0 and np.std(rw) > 0:
                c = float(np.corrcoef(lw, rw)[0, 1])
                if c < -0.7:
                    neg_count += 1

                # Phase risk: side energy exceeds mid
                m_e = float(np.mean(((lw + rw) / 2) ** 2))
                s_e = float(np.mean(((lw - rw) / 2) ** 2))
                if s_e > 3.0 * m_e + 1e-12:
                    phase_risk += 1

        return cls(
            available=True,
            correlation=round(corr, 4),
            mid_ratio=round(mid_e / total, 6),
            side_ratio=round(side_e / total, 6),
            side_to_mid_db=round(side_to_mid, 2),
            width_proxy=round(width, 4),
            negative_correlation_ratio=round(neg_count / max(n, 1), 6),
            phase_risk_ratio=round(phase_risk / max(n, 1), 6),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "correlation": self.correlation,
            "mid_energy_ratio": self.mid_ratio,
            "side_energy_ratio": self.side_ratio,
            "side_to_mid_db": self.side_to_mid_db,
            "width_proxy": self.width_proxy,
            "negative_correlation_ratio": self.negative_correlation_ratio,
            "phase_risk_ratio": self.phase_risk_ratio,
        }


# =============================================================================
# Spectral Metrics
# =============================================================================

@dataclass
class SpectralMetrics:
    """Spectral analysis metrics."""

    centroid_hz: float = 0.0
    rolloff_85_hz: float = 0.0
    rolloff_95_hz: float = 0.0
    flatness: float = 0.0
    flux: float = 0.0
    high_freq_cutoff_hz: float = 0.0

    # Band energy ratios
    band_ratios: dict[str, float] = None  # type: ignore

    def __post_init__(self):
        if self.band_ratios is None:
            self.band_ratios = {}

    @classmethod
    def from_samples(cls, samples: np.ndarray, sr: int) -> SpectralMetrics:
        """Compute spectral metrics from audio samples."""
        mono = samples.mean(axis=1) if samples.ndim > 1 else samples

        n_fft = 8192
        hop = 2048
        win_fn = np.hanning(n_fft)
        freqs = np.fft.rfftfreq(n_fft, 1 / sr)

        n_frames = max(1, (len(mono) - n_fft) // hop + 1)
        spec_sum = np.zeros(len(freqs), dtype=np.float64)
        flux_acc = 0.0
        prev = None

        for i in range(n_frames):
            seg = mono[i * hop: i * hop + n_fft]
            if len(seg) < n_fft:
                seg = np.pad(seg, (0, n_fft - len(seg)))
            frame = np.abs(np.fft.rfft(seg * win_fn))
            spec_sum += frame ** 2
            if prev is not None:
                flux_acc += float(np.sum(np.maximum(frame - prev, 0)))
            prev = frame

        avg_spec = np.sqrt(spec_sum / n_frames)
        power = avg_spec ** 2
        total = power.sum()

        if total < 1e-12:
            return cls()

        # Centroid
        centroid = float(np.sum(freqs * power) / total)

        # Rolloff
        cum = np.cumsum(power)
        def rolloff(pct):
            idx = np.searchsorted(cum, total * pct)
            return float(freqs[min(idx, len(freqs) - 1)])

        # High frequency cutoff (99.5%)
        cutoff_idx = np.searchsorted(cum, total * 0.995)
        cutoff = float(freqs[min(cutoff_idx, len(freqs) - 1)])

        # Flatness
        flatness = float(np.exp(np.mean(np.log(power + 1e-12))) / np.mean(power))

        # Band ratios
        bands = {
            "sub_20_60_hz": (20, 60),
            "bass_60_120_hz": (60, 120),
            "low_mid_120_250_hz": (120, 250),
            "mid_250_500_hz": (250, 500),
            "core_mid_500_2000_hz": (500, 2000),
            "presence_2000_5000_hz": (2000, 5000),
            "brilliance_5000_10000_hz": (5000, 10000),
            "air_10000_16000_hz": (10000, 16000),
            "ultrasonic_16000_24000_hz": (16000, 24000),
        }
        band_ratios = {}
        for name, (lo, hi) in bands.items():
            mask = (freqs >= lo) & (freqs < hi)
            band_ratios[name] = round(float(np.sum(power[mask])) / total, 8)

        return cls(
            centroid_hz=round(centroid, 1),
            rolloff_85_hz=round(rolloff(0.85), 1),
            rolloff_95_hz=round(rolloff(0.95), 1),
            flatness=round(flatness, 5),
            flux=round(flux_acc / n_frames, 4),
            high_freq_cutoff_hz=round(cutoff, 1),
            band_ratios=band_ratios,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "centroid_hz": self.centroid_hz,
            "rolloff_85_hz": self.rolloff_85_hz,
            "rolloff_95_hz": self.rolloff_95_hz,
            "flatness": self.flatness,
            "flux": self.flux,
            "high_freq_cutoff_hz": self.high_freq_cutoff_hz,
            "band_ratios": self.band_ratios,
        }


# =============================================================================
# Integrity Metrics (Clipping, Silence, DC Offset)
# =============================================================================

@dataclass
class IntegrityMetrics:
    """Signal integrity measurements."""

    clipping_sample_count: int = 0
    clipping_ratio: float = 0.0
    near_clipping_count: int = 0
    silence_ratio: float = 0.0
    longest_silence_seconds: float = 0.0
    dc_offset_left: float = 0.0
    dc_offset_right: float | None = None
    noise_floor_dbfs: float = -100.0
    invalid_sample_count: int = 0

    @classmethod
    def from_samples(cls, samples: np.ndarray, sr: int) -> IntegrityMetrics:
        """Compute integrity metrics from audio samples."""
        mono = samples.mean(axis=1) if samples.ndim > 1 else samples
        channels = samples.shape[1] if samples.ndim > 1 else 1

        # Clipping detection
        absx = np.abs(mono)
        clip_count = int(np.sum(absx >= 0.999))
        clip_ratio = clip_count / max(len(mono), 1)
        near_clip = int(np.sum((absx >= 0.95) & (absx < 0.999)))

        # DC offset
        dc_left = float(np.mean(samples[:, 0] if samples.ndim > 1 else mono))
        dc_right = float(np.mean(samples[:, 1])) if channels >= 2 else None

        # Silence analysis (100ms windows, -60 dBFS threshold)
        win = int(0.1 * sr)
        n_win = len(mono) // win
        silence_ratio = 0.0
        longest_silence = 0.0

        if n_win > 0:
            z = mono[:n_win * win].reshape(n_win, win)
            rms_w = np.sqrt(np.mean(z ** 2, axis=1) + 1e-12)
            silent = rms_w < 10 ** (-60 / 20)
            silence_ratio = float(silent.mean())

            longest = 0
            cur = 0
            for s in silent:
                cur = cur + 1 if s else 0
                longest = max(longest, cur)
            longest_silence = longest * 0.1

        # Noise floor (10th percentile of frame RMS)
        n_fft = 8192
        hop = 2048
        n_frames = max(1, (len(mono) - n_fft) // hop + 1)
        frame_rms = np.array([
            np.sqrt(np.mean(mono[i * hop: i * hop + n_fft] ** 2) + 1e-12)
            for i in range(n_frames)
        ])
        noise_floor = float(20 * np.log10(np.percentile(frame_rms, 10) + 1e-12))

        # Invalid samples
        invalid = int(np.sum(~np.isfinite(mono)))

        return cls(
            clipping_sample_count=clip_count,
            clipping_ratio=round(clip_ratio, 8),
            near_clipping_count=near_clip,
            silence_ratio=round(silence_ratio, 6),
            longest_silence_seconds=round(longest_silence, 2),
            dc_offset_left=round(dc_left, 7),
            dc_offset_right=round(dc_right, 7) if dc_right is not None else None,
            noise_floor_dbfs=round(noise_floor, 1),
            invalid_sample_count=invalid,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "clipping_sample_count": self.clipping_sample_count,
            "clipping_ratio": self.clipping_ratio,
            "near_clipping_count": self.near_clipping_count,
            "silence_ratio": self.silence_ratio,
            "longest_silence_seconds": self.longest_silence_seconds,
            "dc_offset_left": self.dc_offset_left,
            "dc_offset_right": self.dc_offset_right,
            "noise_floor_dbfs": self.noise_floor_dbfs,
            "invalid_sample_count": self.invalid_sample_count,
        }
