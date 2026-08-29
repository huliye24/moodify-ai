"""Fixed-width soft-object sketch from a soft-object observation.

All probabilities are ESTIMATOR: acoustic-role indicators, not source
identities and not classifier posteriors.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import HYPOTHESES, SoftObjectConfig
from .objects import SoftObjectObservation

TRACK_FEATURE_NAMES: tuple[str, ...] = (
    "n_objects",
    "mean_confidence",
    "unresolved_fraction",
    "tonal_fraction",
    "texture_fraction",
    "percussive_fraction",
    "unresolved_object_fraction",
)

FRAME_FEATURE_NAMES: tuple[str, ...] = (
    "frame_dominant_label",
    "frame_confidence",
    "frame_unresolved",
)

FEATURE_NAMES: tuple[str, ...] = TRACK_FEATURE_NAMES + FRAME_FEATURE_NAMES

FEATURE_AUTHORITY: dict[str, str] = {
    "n_objects": "DESCRIPTOR",
    "mean_confidence": "ESTIMATOR — acoustic-role cue, not classifier posterior",
    "unresolved_fraction": "ESTIMATOR — weak-evidence honesty",
    "tonal_fraction": "ESTIMATOR — acoustic-role cue",
    "texture_fraction": "ESTIMATOR — acoustic-role cue",
    "percussive_fraction": "ESTIMATOR — acoustic-role cue",
    "unresolved_object_fraction": "ESTIMATOR",
    "frame_dominant_label": "DESCRIPTOR",
    "frame_confidence": "ESTIMATOR",
    "frame_unresolved": "ESTIMATOR",
}


@dataclass
class SoftObjectSketch:
    feature_names: tuple[str, ...]
    times_s: np.ndarray
    values: np.ndarray  # frames x features; NaN = unavailable
    status: str
    geometry_id: str
    config_hash: str
    track_features: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "feature_schema": "mamse-015-soft-object-features-v1",
            "status": self.status,
            "geometry_id": self.geometry_id,
            "config_hash": self.config_hash,
            "n_frames": int(self.times_s.size),
            "track_features": self.track_features,
        }


def build_soft_object_sketch(
    obs: SoftObjectObservation, config: SoftObjectConfig
) -> SoftObjectSketch:
    """Decimate a soft-object observation into a fixed-width sketch."""
    objects = obs.objects
    label_counts = {name: 0.0 for name in HYPOTHESES}
    for obj in objects:
        label_counts[obj.label] += 1.0
    n_objects = max(len(objects), 1)

    track = {
        "n_objects": float(len(objects)),
        "mean_confidence": obs.mean_confidence,
        "unresolved_fraction": obs.unresolved_fraction,
        "tonal_fraction": label_counts["TONAL_CORE"] / n_objects,
        "texture_fraction": label_counts["NOISE_TEXTURE"] / n_objects,
        "percussive_fraction": label_counts["PERCUSSIVE"] / n_objects,
        "unresolved_object_fraction": label_counts["UNRESOLVED"] / n_objects,
    }

    values = np.column_stack([
        obs.frame_labels.astype(np.float64),
        np.max(obs.frame_probabilities, axis=1),
        obs.frame_unresolved,
    ])
    values[~np.isfinite(values)] = np.nan

    return SoftObjectSketch(
        feature_names=FEATURE_NAMES,
        times_s=obs.times_s,
        values=values,
        status=obs.status,
        geometry_id=config.geometry_id,
        config_hash=config.sha256(),
        track_features=track,
    )
