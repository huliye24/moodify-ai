"""Frame streaming and RFFT primitives for MAMSE-001."""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np


def as_mono(samples: np.ndarray) -> np.ndarray:
    x = np.asarray(samples, dtype=np.float32)
    if x.ndim == 1:
        return x
    if x.ndim == 2:
        return x.mean(axis=1, dtype=np.float32)
    raise ValueError("samples must be 1D mono or 2D samples-by-channels")


def iter_frames(mono: np.ndarray, frame_length: int, hop_length: int) -> Iterator[tuple[int, np.ndarray]]:
    """Yield left-aligned frames without materializing a dense frame matrix.

    The last incomplete frame is not emitted: every emitted frame has exactly
    the declared support, so short sources never fabricate R3 results.
    """
    if frame_length <= 0 or hop_length <= 0:
        raise ValueError("invalid frame/hop")
    n = len(mono)
    if n < frame_length:
        return
    for start in range(0, n - frame_length + 1, hop_length):
        yield start, mono[start:start + frame_length]


def power_spectrum(frame: np.ndarray, n_fft: int, window: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(frame) != len(window):
        raise ValueError("frame/window mismatch")
    X = np.fft.rfft(frame * window, n=n_fft)
    mag = np.abs(X).astype(np.float64)
    return mag, mag * mag


def local_peak_frequencies(mag: np.ndarray, freqs: np.ndarray, top_k: int = 2) -> list[float]:
    """Strongest local-maximum frequencies excluding DC; deterministic, not a pitch tracker."""
    if len(mag) < 3:
        return []
    core = mag[1:-1]
    idx = np.where((core > mag[:-2]) & (core >= mag[2:]))[0] + 1
    if idx.size == 0:
        idx = np.array([int(np.argmax(mag[1:])) + 1])
    order = idx[np.argsort(mag[idx])[::-1]]
    return [float(freqs[i]) for i in order[:top_k]]
