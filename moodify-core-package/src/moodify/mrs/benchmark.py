"""Benchmark interface for future MRS evaluation protocols."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .metrics import MRSFeatures
from .scoring import MRSScore, MRSScorer, RuleBasedMRSScorer


@dataclass(frozen=True)
class MRSBenchmarkResult:
    """Stable benchmark output without claiming a human listening result."""

    sample_id: str
    quality_score: float | None
    technical_score: float | None
    listening_score: float | None
    status: str
    method: str | None = None

    def to_dict(self) -> dict[str, float | str | None]:
        """Return the future benchmark contract in a serializable form."""
        return {
            "sample_id": self.sample_id,
            "quality_score": self.quality_score,
            "technical_score": self.technical_score,
            "listening_score": self.listening_score,
            "status": self.status,
            "method": self.method,
        }


class MRSBenchmark:
    """Evaluate a sample only when normalized features are supplied.

    Audio-to-feature extraction and human listening evaluation are intentionally
    outside this research interface. This avoids silently treating a file path
    as evidence of its quality.
    """

    def __init__(self, scorer: MRSScorer | None = None) -> None:
        self._scorer = scorer or RuleBasedMRSScorer()

    def evaluate(
        self,
        audio_sample: str | Path,
        features: MRSFeatures | None = None,
    ) -> MRSBenchmarkResult:
        """Return an unevaluated or rule-based benchmark result for a sample."""
        sample_id = str(audio_sample)
        if features is None:
            return MRSBenchmarkResult(
                sample_id=sample_id,
                quality_score=None,
                technical_score=None,
                listening_score=None,
                status="FEATURES_REQUIRED",
            )

        score: MRSScore = self._scorer.calculate(features)
        return MRSBenchmarkResult(
            sample_id=sample_id,
            quality_score=score.quality_score,
            technical_score=score.technical_score,
            listening_score=score.listening_score,
            status="EXPERIMENTAL_RULE_BASED",
            method=score.method,
        )
