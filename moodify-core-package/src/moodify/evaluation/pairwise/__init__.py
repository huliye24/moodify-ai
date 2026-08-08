"""Pairwise Auditory Judge (DSK-MFY-PAIRWISE-JUDGE-001).

Compares two candidate audio files under a shared context using canonical
Moodify auditory analysis, produces exactly one of A_WINS / B_WINS /
INCONCLUSIVE with confidence bands and evidence-backed reasons, and persists
preference data for future learning. Machine-only judgments are never ground
truth.
"""

from moodify.evaluation.pairwise.dimensions import compare_dimensions
from moodify.evaluation.pairwise.models import (
    DimensionResult,
    HumanPairwiseDecision,
    PairwiseComparison,
    PairwiseJudgment,
    PreferenceRecord,
)
from moodify.evaluation.pairwise.policy import DecisionPolicy, decide
from moodify.evaluation.pairwise.service import record_human_decision, run_pairwise_judge

__all__ = [
    "DecisionPolicy",
    "DimensionResult",
    "HumanPairwiseDecision",
    "PairwiseComparison",
    "PairwiseJudgment",
    "PreferenceRecord",
    "compare_dimensions",
    "decide",
    "record_human_decision",
    "run_pairwise_judge",
]
