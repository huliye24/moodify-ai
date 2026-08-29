"""Extensible scoring primitives for experimental Moodify Reality Score."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .config import DEFAULT_MRS_CONFIG, MRSConfig
from .metrics import MRSFeatures


@dataclass(frozen=True)
class MRSScore:
    """A transparent score returned by an experimental MRS evaluator."""

    quality_score: float
    technical_score: float
    listening_score: float | None
    method: str
    feature_contributions: dict[str, float]

    def to_dict(self) -> dict[str, float | str | None | dict[str, float]]:
        """Return the stable result shape used by benchmark consumers."""
        return {
            "quality_score": self.quality_score,
            "technical_score": self.technical_score,
            "listening_score": self.listening_score,
            "method": self.method,
            "feature_contributions": self.feature_contributions,
        }


class MRSScorer(Protocol):
    """Protocol for future rule-based, ML, reward, or feedback scorers."""

    def calculate(self, features: MRSFeatures) -> MRSScore:
        """Calculate an MRS result from normalized evaluation features."""


class RuleBasedMRSScorer:
    """Inspectable baseline scorer with no trained model dependency.

    The score is a weighted mean of normalized factors on a 0-100 scale.
    ``listening_score`` is deliberately ``None``: a rule-based technical
    baseline must not present itself as a measurement of human preference.
    """

    def __init__(self, config: MRSConfig = DEFAULT_MRS_CONFIG) -> None:
        self._config = config

    def calculate(self, features: MRSFeatures) -> MRSScore:
        """Calculate a deterministic baseline score for one feature record."""
        weights = {
            "loudness": self._config.loudness_weight,
            "dynamic": self._config.dynamic_weight,
            "spectral": self._config.spectral_weight,
            "spatial": self._config.spatial_weight,
            "artifact": self._config.artifact_weight,
        }
        total_weight = sum(weights.values())
        contributions = {
            name: value * weights[name] / total_weight
            for name, value in features.to_dict().items()
        }
        technical_score = round(sum(contributions.values()) * 100.0, 2)
        return MRSScore(
            quality_score=technical_score,
            technical_score=technical_score,
            listening_score=None,
            method="experimental_rule_based_v1",
            feature_contributions=contributions,
        )


def _example() -> None:
    """Run a minimal local smoke example without reading an audio file."""
    features = MRSFeatures(0.8, 0.7, 0.75, 0.65, 0.9)
    print(RuleBasedMRSScorer().calculate(features).to_dict())


if __name__ == "__main__":
    _example()
