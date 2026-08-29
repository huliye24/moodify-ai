"""Experimental Moodify Reality Score research interfaces.

This package is intentionally separate from the legacy ``reality_metrics``
implementation. It defines a small, typed contract for future MRS research
without changing any processing or production decision path.
"""

from .benchmark import MRSBenchmark, MRSBenchmarkResult
from .config import DEFAULT_MRS_CONFIG, MRSConfig
from .metrics import MRSFeatures
from .scoring import MRSScore, RuleBasedMRSScorer

__all__ = [
    "DEFAULT_MRS_CONFIG",
    "MRSBenchmark",
    "MRSBenchmarkResult",
    "MRSConfig",
    "MRSFeatures",
    "MRSScore",
    "RuleBasedMRSScorer",
]
