"""Fixed-width masking sketch from a masking observation.

All values are ESTIMATOR/DESCRIPTOR: masking depth is spectral-competition
inference, not a hearing test; a masked estimate never claims absence.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import MaskConfig, hz_to_erb
from .masking import MaskingObservation

TRACK_FEATURE_NAMES: tuple[str, ...] = (
    "masking_depth_mean",
    "masking_depth_p95",
    "masked_channel_ratio_mean",
    "audible_channel_ratio_mean",
    "strongest_masker_frequency_hz",
    "n_strong_masking_events",
)

FRAME_FEATURE_NAMES: tuple[str, ...] = (
    "frame_masked_channel_ratio",
    "frame_audible_centroid_erb",
)

FEATURE_NAMES: tuple[str, ...] = TRACK_FEATURE_NAMES + FRAME_FEATURE_NAMES

FEATURE_AUTHORITY: dict[str, str] = {
    "masking_depth_mean": "ESTIMATOR — spectral-competition inference, not a hearing test",
    "masking_depth_p95": "ESTIMATOR — spectral-competition inference, not a hearing test",
    "masked_channel_ratio_mean": "ESTIMATOR — masked does not mean absent",
    "audible_channel_ratio_mean": "ESTIMATOR — audible does not mean present",
    "strongest_masker_frequency_hz": "DESCRIPTOR",
    "n_strong_masking_events": "DESCRIPTOR",
    "frame_masked_channel_ratio": "ESTIMATOR",
    "frame_audible_centroid_erb": "DESCRIPTOR",
}


@dataclass
class MaskingSketch:
    feature_names: tuple[str, ...]
    times_s: np.ndarray
    values: np.ndarray  # frames x features; NaN = unavailable
    status: str
    geometry_id: str
    config_hash: str
    track_features: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "feature_schema": "mamse-014-masking-features-v1",
            "status": self.status,
            "geometry_id": self.geometry_id,
            "config_hash": self.config_hash,
            "n_frames": int(self.times_s.size),
            "track_features": self.track_features,
        }


def build_masking_sketch(obs: MaskingObservation, config: MaskConfig) -> MaskingSketch:
    """Decimate a masking observation into a fixed-width sketch."""
    ratio = obs.masked_channel_ratio
    depth_mean = float(np.mean(obs.masking_depth)) if obs.masking_depth.size else 0.0
    audible_channel_ratio = 1.0 - obs.masked_channel_ratio_mean

    erbs = hz_to_erb(obs.center_frequencies_hz)
    power = 10.0 ** (obs.channel_power_db / 10.0)
    frame_total = np.sum(power, axis=0)
    safe = np.where(frame_total > 0.0, frame_total, 1.0)
    audible_centroid = np.sum(erbs[:, None] * obs.audibility * power, axis=0) / safe

    track = {
        "masking_depth_mean": depth_mean,
        "masking_depth_p95": obs.depth_p95,
        "masked_channel_ratio_mean": obs.masked_channel_ratio_mean,
        "audible_channel_ratio_mean": audible_channel_ratio,
        "strongest_masker_frequency_hz": obs.strongest_masker_frequency_hz,
        "n_strong_masking_events": float(len(obs.events)),
    }

    values = np.column_stack([ratio, audible_centroid])
    values[~np.isfinite(values)] = np.nan

    return MaskingSketch(
        feature_names=FEATURE_NAMES,
        times_s=obs.times_s,
        values=values,
        status=obs.status,
        geometry_id=config.geometry_id,
        config_hash=config.sha256(),
        track_features=track,
    )
