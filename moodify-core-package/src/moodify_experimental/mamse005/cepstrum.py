"""Real cepstrum, quefrency axis and low/high liftering.

log|X(f)| = log|E(f)| + log|H(f)| becomes additive in the cepstrum;
low quefrency carries the spectral envelope, high quefrency the periodic
fine structure. The log floor is explicit and versioned; silence/too-short
inputs never reach this layer (handled at the entry point).
"""

from __future__ import annotations

import numpy as np
from scipy.signal import get_window

EPS = 1e-12


def frame_signal(x: np.ndarray, n_fft: int, hop: int) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    if len(x) < n_fft:
        return np.empty((0, n_fft), dtype=np.float64)
    n = 1 + (len(x) - n_fft) // hop
    shape = (n, n_fft)
    strides = (x.strides[0] * hop, x.strides[0])
    return np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides).copy()


def real_cepstrum_frame(frame: np.ndarray, n_fft: int, window: str, magnitude_floor: float):
    frame = np.asarray(frame, dtype=np.float64)
    win = get_window(window, len(frame), fftbins=True)
    spectrum = np.fft.rfft(frame * win, n=n_fft)
    mag = np.abs(spectrum)
    logmag = np.log(np.maximum(mag, magnitude_floor))
    # Even log-magnitude spectrum before real IFFT: quefrency samples follow
    # the real-cepstrum convention for a real signal.
    if n_fft % 2 == 0:
        full = np.concatenate([logmag, logmag[-2:0:-1]])
    else:
        full = np.concatenate([logmag, logmag[-1:0:-1]])
    cep = np.fft.ifft(full).real
    return cep[:n_fft], logmag, mag


def low_quefrency_lifter(cep: np.ndarray, sr: int, cutoff_ms: float) -> np.ndarray:
    cep = np.asarray(cep, dtype=np.float64)
    cutoff = max(1, int(round(cutoff_ms * 1e-3 * sr)))
    cutoff = min(cutoff, len(cep) // 2 - 1)
    out = np.zeros_like(cep)
    out[:cutoff + 1] = cep[:cutoff + 1]
    out[-cutoff:] = cep[-cutoff:]
    return out


def reconstruct_logmag_from_cepstrum(cep: np.ndarray, n_fft: int) -> np.ndarray:
    spec = np.fft.fft(np.asarray(cep, dtype=np.float64), n=n_fft).real
    return spec[:n_fft // 2 + 1]


def cepstral_decompose_frame(frame: np.ndarray, sr: int, n_fft: int, window: str,
                             magnitude_floor: float, lifter_cutoff_ms: float) -> dict:
    cep, logmag, mag = real_cepstrum_frame(frame, n_fft, window, magnitude_floor)
    low = low_quefrency_lifter(cep, sr, lifter_cutoff_ms)
    envelope = reconstruct_logmag_from_cepstrum(low, n_fft)
    fine = logmag - envelope
    return {
        "cepstrum": cep,
        "logmag": logmag,
        "magnitude": mag,
        "envelope_logmag": envelope,
        "fine_logmag": fine,
        "low_cepstrum": low,
        "high_cepstrum": cep - low,
    }
