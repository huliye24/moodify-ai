"""Log-frequency auditory surface: STFT power -> log-frequency interpolation.

The surface is expressed in relative dB on the source sample clock; every
frame maps back to absolute time via `time_s`.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import stft

from .config import ModulationConfig


def rms_dbfs(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0:
        return float("-inf")
    rms = float(np.sqrt(np.mean(x * x)))
    return 20.0 * np.log10(rms + 1e-15)


def log_frequency_axis(cfg: ModulationConfig) -> np.ndarray:
    octaves = np.log2(cfg.fmax_hz / cfg.fmin_hz)
    n = int(np.floor(octaves * cfg.bands_per_octave)) + 1
    return cfg.fmin_hz * 2.0 ** (np.arange(n) / cfg.bands_per_octave)


def compute_log_frequency_surface(samples: np.ndarray, cfg: ModulationConfig):
    cfg.validate()
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 2:
        x = np.mean(x, axis=1)
    if x.ndim != 1:
        raise ValueError("samples must be mono or [samples, channels]")
    duration = x.size / cfg.sample_rate
    if duration < cfg.min_audio_seconds:
        return None, {"status": "UNAVAILABLE_TOO_SHORT", "duration_seconds": duration}
    level = rms_dbfs(x)
    if level < cfg.low_energy_rms_dbfs:
        return None, {"status": "UNAVAILABLE_LOW_ENERGY", "rms_dbfs": level}

    freqs, times, z = stft(
        x,
        fs=cfg.sample_rate,
        window="hann",
        nperseg=cfg.audio_n_fft,
        noverlap=cfg.audio_n_fft - cfg.audio_hop,
        nfft=cfg.audio_n_fft,
        boundary=None,
        padded=False,
    )
    power = np.abs(z) ** 2
    raw_db = 10.0 * np.log10(power + 1e-20)
    peak = float(np.max(raw_db))
    rel_db = np.maximum(raw_db - peak, cfg.log_floor_db)

    target = log_frequency_axis(cfg)
    valid = (freqs >= cfg.fmin_hz) & (freqs <= cfg.fmax_hz)
    src_f = freqs[valid]
    src = rel_db[valid]
    if src_f.size < 2:
        return None, {"status": "UNAVAILABLE_INVALID_CONFIG", "reason": "frequency support"}

    out = np.empty((target.size, times.size), dtype=np.float64)
    for i in range(times.size):
        out[:, i] = np.interp(target, src_f, src[:, i])
    return {
        "surface_db": out,
        "log_frequency_hz": target,
        "time_s": times,
        "frame_rate_hz": cfg.frame_rate_hz,
        "rms_dbfs": level,
    }, {"status": "OK"}
