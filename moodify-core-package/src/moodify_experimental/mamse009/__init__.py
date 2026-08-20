"""MAMSE-009 — Robust PCA / sparse anomaly separation (experimental).

X = L + S via IALM Principal Component Pursuit. L is low-rank structure
candidate, S is sparse structural-deviation candidate, dense residual is
kept separate. NaN/Inf fail closed. Candidates are anonymous
(EXPERIMENTAL_UNKNOWN) and never replace canonical P0 event rules.
"""

from .config import ALGORITHM_VERSION, MANIFEST_SCHEMA_VERSION, OPERATOR_ID, RPCAConfig
from .evidence import build_manifest, evidence_summary, event_overlap_report, load_result, save_result
from .rpca import (
    EPS,
    RPCAResult,
    RPCAUnavailableError,
    candidate_intervals,
    default_lambda,
    low_rank_similarity,
    principal_component_pursuit,
    robust_zscore,
    singular_value_threshold,
    soft_threshold,
    sparse_feature_score,
    sparse_frame_score,
    sparse_support_f1,
)

__all__ = [
    "OPERATOR_ID",
    "ALGORITHM_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "RPCAConfig",
    "RPCAResult",
    "RPCAUnavailableError",
    "principal_component_pursuit",
    "soft_threshold",
    "singular_value_threshold",
    "default_lambda",
    "sparse_frame_score",
    "sparse_feature_score",
    "robust_zscore",
    "candidate_intervals",
    "low_rank_similarity",
    "sparse_support_f1",
    "evidence_summary",
    "build_manifest",
    "save_result",
    "load_result",
    "event_overlap_report",
    "EPS",
]
