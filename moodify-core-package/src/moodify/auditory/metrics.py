"""Numerical measurement layer (DSK-MFY-AUDITORY-SCAN-001).

Implements the full metric schema: loudness/level (BS.1770), signal
integrity, spectral descriptors, band energy ratios and stereo metrics.
Every metric carries value/unit/method/status/warnings.
"""

from __future__ import annotations

import numpy as np

from moodify.auditory.models import MetricValue

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rms_db(x: np.ndarray) -> float:
    return float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12))


def _peak_db(x: np.ndarray) -> float:
    return float(20 * np.log10(np.max(np.abs(x)) + 1e-12))


def true_peak_db(x: np.ndarray) -> float:
    """4x oversampled true peak (approximation)."""
    n = len(x)
    up = np.zeros(n * 4)
    up[::4] = x
    # simple 4x zero-stuff + Hann low-pass
    kernel = np.hanning(64)
    kernel /= kernel.sum()
    filtered = np.convolve(up, kernel, mode="same")
    return float(20 * np.log10(np.max(np.abs(filtered)) + 1e-12))


def spectral_centroid(spec: np.ndarray, freqs: np.ndarray) -> float:
    power = np.abs(spec) ** 2
    total = power.sum()
    if total < 1e-12:
        return 0.0
    return float(np.sum(freqs * power) / total)


def spectral_rolloff(spec: np.ndarray, freqs: np.ndarray, percentile: float) -> float:
    power = np.abs(spec) ** 2
    total = power.sum()
    if total < 1e-12:
        return 0.0
    cum = np.cumsum(power)
    idx = np.searchsorted(cum, total * percentile)
    return float(freqs[min(idx, len(freqs) - 1)])


def spectral_flatness(spec: np.ndarray) -> float:
    power = np.abs(spec) ** 2 + 1e-12
    return float(np.exp(np.mean(np.log(power))) / np.mean(power))


# ---------------------------------------------------------------------------
# Full scan metrics
# ---------------------------------------------------------------------------


def compute_metrics(
    samples: np.ndarray,
    sr: int,
    probe,
) -> dict:
    """Compute the complete metric record for one scan."""
    m: dict = {}
    mono = samples.mean(axis=1) if samples.ndim > 1 else samples
    channels = samples.shape[1] if samples.ndim > 1 else 1

    # loudness / level (MFY-PHASE1-DEPTH-001: standards-backed modules)
    from moodify.auditory.loudness import integrated_loudness_lufs, loudness_range_lu
    from moodify.auditory.true_peak import true_peak_db

    lufs = integrated_loudness_lufs(samples, sr)
    m["integrated_lufs"] = MetricValue(round(lufs, 2), "LUFS", "BS1770").to_dict()
    lra = loudness_range_lu(samples, sr)
    if lra is None:
        m["loudness_range_lu"] = MetricValue(
            None, "LU", "EBU3342", "UNAVAILABLE", ["insufficient duration (<6 s)"]
        ).to_dict()
    else:
        m["loudness_range_lu"] = MetricValue(round(lra, 2), "LU", "EBU3342").to_dict()
    tp = true_peak_db(samples, sr)
    m["true_peak_dbfs"] = MetricValue(round(tp, 2), "dBFS", "4x-oversample").to_dict()
    pk = _peak_db(mono)
    m["sample_peak_dbfs"] = MetricValue(round(pk, 2), "dBFS", "direct").to_dict()
    rms = _rms_db(mono)
    m["rms_dbfs"] = MetricValue(round(rms, 2), "dBFS", "direct").to_dict()
    crest = pk - rms
    m["crest_factor_db"] = MetricValue(round(crest, 2), "dB", "derived").to_dict()
    m["plr_db"] = MetricValue(round(tp - rms, 2), "dB", "peak-to-rms").to_dict()

    # signal integrity
    absx = np.abs(mono)
    clip_count = int(np.sum(absx >= 0.999))
    m["clipping_sample_count"] = MetricValue(clip_count, "samples", "direct").to_dict()
    m["clipping_sample_ratio"] = MetricValue(round(clip_count / max(len(mono), 1), 8), "ratio", "derived").to_dict()
    near_clip = int(np.sum((absx >= 0.95) & (absx < 0.999)))
    m["near_clipping_sample_count"] = MetricValue(near_clip, "samples", "direct").to_dict()

    def dc_of(ch: np.ndarray) -> float:
        return float(np.mean(ch))

    if channels >= 2:
        m["dc_offset_left"] = MetricValue(round(dc_of(samples[:, 0]), 7), "linear", "direct").to_dict()
        m["dc_offset_right"] = MetricValue(round(dc_of(samples[:, 1]), 7), "linear", "direct").to_dict()
    else:
        m["dc_offset_left"] = MetricValue(round(dc_of(mono), 7), "linear", "direct").to_dict()
        m["dc_offset_right"] = MetricValue(None, "linear", "mono", "UNAVAILABLE", ["mono input"]).to_dict()

    # silence analysis (100 ms windows, -60 dBFS threshold)
    win = int(0.1 * sr)
    n_win = len(mono) // win
    if n_win > 0:
        z = mono[: n_win * win].reshape(n_win, win)
        rms_w = np.sqrt(np.mean(z ** 2, axis=1) + 1e-12)
        silent = rms_w < 10 ** (-60 / 20)
        m["silence_ratio"] = MetricValue(round(float(silent.mean()), 6), "ratio", "derived").to_dict()
        longest = 0
        cur = 0
        for s in silent:
            cur = cur + 1 if s else 0
            longest = max(longest, cur)
        m["longest_silence_seconds"] = MetricValue(round(longest * 0.1, 2), "s", "derived").to_dict()
    else:
        m["silence_ratio"] = MetricValue(0.0, "ratio", "derived").to_dict()
        m["longest_silence_seconds"] = MetricValue(0.0, "s", "derived").to_dict()

    invalid = int(np.sum(~np.isfinite(mono)))
    m["invalid_sample_count"] = MetricValue(invalid, "samples", "direct").to_dict()
    m["finite_sample_ratio"] = MetricValue(round(1.0 - invalid / max(len(mono), 1), 8), "ratio", "derived").to_dict()

    # spectral metrics (STFT)
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
    m["spectral_centroid_hz"] = MetricValue(round(spectral_centroid(avg_spec, freqs), 1), "Hz", "stft").to_dict()
    m["spectral_rolloff_85_hz"] = MetricValue(round(spectral_rolloff(avg_spec, freqs, 0.85), 1), "Hz", "stft").to_dict()
    m["spectral_rolloff_95_hz"] = MetricValue(round(spectral_rolloff(avg_spec, freqs, 0.95), 1), "Hz", "stft").to_dict()
    m["spectral_flatness"] = MetricValue(round(spectral_flatness(avg_spec), 5), "ratio", "stft").to_dict()
    m["spectral_flux"] = MetricValue(round(flux_acc / n_frames, 4), "mag/frame", "stft").to_dict()

    # high-frequency cutoff: first bin where cumulative power >= 99.5%
    cum = np.cumsum(avg_spec ** 2)
    total_p = cum[-1] if cum[-1] > 0 else 1.0
    cutoff_idx = np.searchsorted(cum, total_p * 0.995)
    m["estimated_high_frequency_cutoff_hz"] = MetricValue(
        round(float(freqs[min(cutoff_idx, len(freqs) - 1)]), 1), "Hz", "cumulative-99.5%"
    ).to_dict()

    # noise floor: 10th percentile of frame RMS in dBFS
    frame_rms = np.array([
        np.sqrt(np.mean(mono[i * hop: i * hop + n_fft] ** 2) + 1e-12)
        for i in range(n_frames)
    ])
    m["estimated_noise_floor_dbfs"] = MetricValue(
        round(float(20 * np.log10(np.percentile(frame_rms, 10) + 1e-12)), 1), "dBFS", "p10-frame-rms"
    ).to_dict()

    # normalized band energy ratios
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
    band_energy = {}
    for name, (lo, hi) in bands.items():
        mask = (freqs >= lo) & (freqs < hi)
        band_energy[name] = float(np.sum(avg_spec[mask] ** 2))
    total_energy = sum(band_energy.values()) + 1e-12
    for name in bands:
        m[name] = MetricValue(round(band_energy[name] / total_energy, 8), "ratio", "normalized-band").to_dict()
        m[f"band_energy_{name}"] = MetricValue(
            round(float(band_energy[name]), 8), "linear-power", "stft"
        ).to_dict()

    return m
