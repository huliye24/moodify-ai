"""Texture sketch and analyze_texture entry point.

Frame positions are mapped back to the original sample clock so texture
frames can overlay the existing S1/S2 windows. Descriptors are experimental
and never artistic quality scores.
"""

from __future__ import annotations

import hashlib
import math
import time
import tracemalloc
from dataclasses import dataclass

import numpy as np

from .config import TextureConfig
from .scattering import compute_scattering_like
from .wavelets import resample_deterministic


def _entropy(p: np.ndarray, eps: float) -> float:
    p = np.asarray(p, dtype=np.float64)
    p = p / (p.sum() + eps)
    nz = p[p > 0]
    if len(nz) == 0:
        return 0.0
    h = -float(np.sum(nz * np.log(nz + eps)))
    return h / max(math.log(len(p)), eps)


def _sparsity(p: np.ndarray, eps: float) -> float:
    p = np.asarray(p, dtype=np.float64)
    if len(p) == 0:
        return 0.0
    l1 = np.sum(np.abs(p))
    l2 = np.sqrt(np.sum(p ** 2))
    n = len(p)
    if n <= 1 or l2 < eps:
        return 0.0
    return float((np.sqrt(n) - l1 / (l2 + eps)) / (np.sqrt(n) - 1))


@dataclass
class TextureResult:
    source_sha256: str
    config: dict
    carrier_centers_hz: list[float]
    first_order_distribution: list[float]
    first_order_temporal_cv: list[float]
    modulation_rates_hz: list[float]
    modulation_distribution: list[float]
    high_modulation_ratio: float
    texture_entropy: float
    texture_sparsity: float
    stationarity_index: float
    order_ratio: float
    frame_starts_samples: list[int]
    frame_ends_samples: list[int]
    frame_texture_matrix: list[list[float]]
    runtime_seconds: float
    peak_memory_mb: float
    limitations: list[str]

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def analyze_texture(samples: np.ndarray, sample_rate: int, config: TextureConfig | None = None,
                    source_sha256: str | None = None) -> TextureResult:
    config = config or TextureConfig()
    config.validate()
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 2:
        x = x.mean(axis=1)
    if x.ndim != 1 or len(x) == 0:
        raise ValueError("samples must be non-empty mono/stereo array")
    if source_sha256 is None:
        source_sha256 = hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()

    tracemalloc.start()
    t0 = time.perf_counter()
    xa = resample_deterministic(x, sample_rate, config.analysis_sample_rate)
    raw = compute_scattering_like(xa, config.analysis_sample_rate, config)

    first = raw["first_global"]
    first_dist = first / (first.sum() + config.eps)
    mod = raw["mod_by_carrier"]
    if mod.size == 0:
        mod_dist: list[float] = []
        high_ratio = 0.0
    else:
        mod_rate = mod.sum(axis=0)
        mod_dist = list((mod_rate / (mod_rate.sum() + config.eps)).astype(float))
        high_mask = raw["modulation_rates_hz"] >= 8.0
        high_ratio = float(mod_rate[high_mask].sum() / (mod_rate.sum() + config.eps))
    cv = raw["first_cv"]
    finite_cv = cv[np.isfinite(cv)]
    stationarity = float(1.0 / (1.0 + np.mean(finite_cv))) if len(finite_cv) else 0.0
    order_ratio = float(mod.sum() / (first.sum() + config.eps))

    frames = raw["first_frames"]
    frame_rows = []
    for row in frames:
        p = row / (row.sum() + config.eps)
        centroid_idx = float(np.sum(np.arange(len(p)) * p) / max(len(p) - 1, 1))
        frame_rows.append([
            float(np.log10(row.sum() + config.eps)),
            _entropy(p, config.eps),
            _sparsity(p, config.eps),
            centroid_idx,
        ])

    runtime = time.perf_counter() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    scale = sample_rate / config.analysis_sample_rate
    starts = [int(round(int(v) * scale)) for v in raw["frame_starts_samples"]]
    ends = [int(round(int(v) * scale)) for v in raw["frame_ends_samples"]]

    return TextureResult(
        source_sha256=source_sha256,
        config=config.to_dict() | {"config_hash": config.config_hash},
        carrier_centers_hz=[float(v) for v in raw["carrier_centers_hz"]],
        first_order_distribution=[float(v) for v in first_dist],
        first_order_temporal_cv=[float(v) for v in cv],
        modulation_rates_hz=[float(v) for v in raw["modulation_rates_hz"]],
        modulation_distribution=[float(v) for v in mod_dist],
        high_modulation_ratio=high_ratio,
        texture_entropy=_entropy(first_dist, config.eps),
        texture_sparsity=_sparsity(first_dist, config.eps),
        stationarity_index=stationarity,
        order_ratio=order_ratio,
        frame_starts_samples=starts,
        frame_ends_samples=ends,
        frame_texture_matrix=frame_rows,
        runtime_seconds=float(runtime),
        peak_memory_mb=float(peak / 1024 / 1024),
        limitations=[
            "scattering-inspired prototype; not numerically equivalent to Kymatio/Mallat scattering",
            "analysis is downsampled to 24 kHz and carrier texture is limited to <=8 kHz",
            "texture descriptors are experimental and not artistic quality scores",
        ],
    )
