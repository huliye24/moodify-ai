"""Configuration for the experimental rule-based MRS baseline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MRSConfig:
    """Weights for normalized, task-specific MRS feature inputs.

    Each weight applies to a factor in the inclusive range [0.0, 1.0]. The
    weights are a transparent research baseline, not perceptual calibration.
    """

    loudness_weight: float = 0.20
    dynamic_weight: float = 0.20
    spectral_weight: float = 0.25
    spatial_weight: float = 0.15
    artifact_weight: float = 0.20

    def __post_init__(self) -> None:
        weights = (
            self.loudness_weight,
            self.dynamic_weight,
            self.spectral_weight,
            self.spatial_weight,
            self.artifact_weight,
        )
        if any(weight < 0.0 for weight in weights):
            raise ValueError("MRS weights must be non-negative")
        if not weights or sum(weights) <= 0.0:
            raise ValueError("MRS weights must have a positive total")


DEFAULT_MRS_CONFIG = MRSConfig()
