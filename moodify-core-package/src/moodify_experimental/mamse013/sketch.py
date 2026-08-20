"""Fixed-width ERB sketch from a gammatone observation.

All values are DESCRIPTOR: an ERB centroid is not loudness perception,
a dominant channel is not pitch understanding. Perceptual organization
assists organization; it never claims psychoacoustic truth.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import ERBConfig, hz_to_erb
from .gammatone import ErbObservation

TRACK_FEATURE_NAMES: tuple[str, ...] = (
    "dominant_channel_index",
    "dominant_frequency_hz",
    "erb_centroid",
    "erb_spread",
    "low_band_ratio",
    "mid_band_ratio",
    "high_band_ratio",
    "peak_to_floor_ratio_db",
    "channel_flatness",
)

FRAME_FEATURE_NAMES: tuple[str, ...] = (
    "frame_total_energy",
    "frame_erb_centroid",
    "frame_dominant_channel",
)

FEATURE_NAMES: tuple[str, ...] = TRACK_FEATURE_NAMES + FRAME_FEATURE_NAMES

FEATURE_AUTHORITY: dict[str, str] = {
    name: "DESCRIPTOR — perceptual organization view, not psychoacoustic truth"
    for name in FEATURE_NAMES
}


@dataclass
class ErbSketch:
    feature_names: tuple[str, ...]
    times_s: np.ndarray
    values: np.ndarray  # frames x features; NaN = unavailable
    status: str
    geometry_id: str
    config_hash: str
    track_features: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "feature_schema": "mamse-013-erb-features-v1",
            "status": self.status,
            "geometry_id": self.geometry_id,
            "config_hash": self.config_hash,
            "n_frames": int(self.times_s.size),
            "track_features": self.track_features,
        }


def _safe_flatness(power: np.ndarray) -> float:
    p = power[power > 0]
    if p.size == 0:
        return 0.0
    geometric = float(np.exp(np.mean(np.log(p))))
    return float(geometric / np.mean(p))


def build_er_b_sketch(obs: ErbObservation, config: ERBConfig) -> ErbSketch:
    """Decimate a gammatone observation into a fixed-width sketch."""
    power = np.maximum(obs.mean_channel_power, 0.0)
    total = float(np.sum(power)) or 1.0
    erbs = hz_to_erb(obs.center_frequencies_hz)

    centroid = float(np.sum(erbs * power) / total)
    spread = float(np.sqrt(np.sum(erbs ** 2 * power) / total - centroid ** 2))
    third = (hz_to_erb(config.fmax_hz) - hz_to_erb(config.fmin_hz)) / 3.0
    low_edge, mid_edge = hz_to_erb(config.fmin_hz) + third, hz_to_erb(config.fmin_hz) + 2 * third
    low = float(np.sum(power[erbs < low_edge]) / total)
    high = float(np.sum(power[erbs > mid_edge]) / total)
    mid = float(np.sum(power[(erbs >= low_edge) & (erbs <= mid_edge)]) / total)

    peak = float(np.max(power)) if power.size else 0.0
    floor = float(np.percentile(power, 10)) if power.size else 0.0
    peak_to_floor = 10.0 * np.log10(peak / max(floor, 1e-12)) if peak > 0.0 else 0.0

    track = {
        "dominant_channel_index": float(obs.dominant_channel),
        "dominant_frequency_hz": obs.dominant_frequency_hz,
        "erb_centroid": centroid,
        "erb_spread": spread,
        "low_band_ratio": low,
        "mid_band_ratio": mid,
        "high_band_ratio": high,
        "peak_to_floor_ratio_db": float(peak_to_floor),
        "channel_flatness": _safe_flatness(power),
    }

    energies = obs.channel_energies
    frame_total = np.sum(energies, axis=0)
    frame_total_safe = np.where(frame_total > 0.0, frame_total, 1.0)
    frame_centroid = np.sum(erbs[:, None] * energies, axis=0) / frame_total_safe
    frame_dominant = np.argmax(energies, axis=0)

    values = np.column_stack([
        frame_total,
        frame_centroid,
        frame_dominant.astype(np.float64),
    ])
    values[~np.isfinite(values)] = np.nan

    return ErbSketch(
        feature_names=FEATURE_NAMES,
        times_s=obs.times_s,
        values=values,
        status=obs.status,
        geometry_id=config.geometry_id,
        config_hash=config.sha256(),
        track_features=track,
    )
