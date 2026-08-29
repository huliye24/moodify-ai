"""Typed, normalized metric inputs for experimental MRS scoring.

This module defines an input contract only. Feature extraction remains owned by
existing analysis modules until a validated adapter is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


_FEATURE_NAMES = (
    "loudness",
    "dynamic",
    "spectral",
    "spatial",
    "artifact",
)


@dataclass(frozen=True)
class MRSFeatures:
    """Normalized quality factors for a scoped MRS evaluation.

    Values use ``0.0`` for the least favorable value in the selected task
    range and ``1.0`` for the most favorable value. They are not raw LUFS,
    RMS, or listener-preference values.
    """

    loudness: float
    dynamic: float
    spectral: float
    spatial: float
    artifact: float

    def __post_init__(self) -> None:
        for name, value in self.to_dict().items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in the range [0.0, 1.0]")

    @classmethod
    def from_mapping(cls, values: Mapping[str, float]) -> "MRSFeatures":
        """Create features from a complete mapping of normalized factors."""
        missing = set(_FEATURE_NAMES) - set(values)
        if missing:
            missing_names = ", ".join(sorted(missing))
            raise ValueError(f"Missing MRS feature values: {missing_names}")
        return cls(**{name: float(values[name]) for name in _FEATURE_NAMES})

    def to_dict(self) -> dict[str, float]:
        """Return a serializable representation of the feature contract."""
        return {name: getattr(self, name) for name in _FEATURE_NAMES}
