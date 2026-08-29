"""Chunk iterators that preserve sample identity and overlap semantics."""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np


def iter_chunks(samples: np.ndarray, chunk_samples: int,
                overlap_samples: int = 0) -> Iterator[tuple[int, int, np.ndarray]]:
    if chunk_samples <= 0 or overlap_samples < 0 or overlap_samples >= chunk_samples:
        raise ValueError("invalid chunk/overlap size")
    start = 0
    while start < len(samples):
        end = min(len(samples), start + chunk_samples)
        yield start, end, samples[start:end]
        if end == len(samples):
            break
        start = end - overlap_samples


def chunked_peak_rms(samples: np.ndarray, chunk_samples: int) -> tuple[float, float]:
    """Exact streaming peak/RMS sufficient statistics, independent of chunk size."""
    peak = 0.0
    energy = 0.0
    count = 0
    for _, _, chunk in iter_chunks(samples, chunk_samples):
        values = np.asarray(chunk, dtype=np.float64)
        if values.size:
            peak = max(peak, float(np.max(np.abs(values))))
            energy += float(np.sum(values * values))
            count += values.size
    return peak, float(np.sqrt(energy / count)) if count else 0.0
