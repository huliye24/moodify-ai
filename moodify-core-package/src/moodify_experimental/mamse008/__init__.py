"""MAMSE-008 — NMF auditory component structure (experimental).

V ≈ W @ H over nonnegative linear-energy matrices. Components are anonymous
mathematical factors, never automatic source stems; dB/mixed-unit/signed
inputs are rejected; NaN is masked, never replaced by physical zero; rank is
not the true source count; residuals are out-of-subspace candidates.
"""

from .config import ALGORITHM_VERSION, MANIFEST_SCHEMA_VERSION, OPERATOR_ID, NMFConfig
from .evidence import build_manifest, evidence_summary, load_result, save_result
from .nmf import (
    EPS,
    NMFResult,
    NMFUnavailableError,
    activation_sparsity,
    beta_divergence,
    canonicalize_factors,
    component_cosine_similarity,
    fit_nmf,
    project_h,
)

__all__ = [
    "OPERATOR_ID",
    "ALGORITHM_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "NMFConfig",
    "NMFResult",
    "NMFUnavailableError",
    "fit_nmf",
    "project_h",
    "beta_divergence",
    "canonicalize_factors",
    "component_cosine_similarity",
    "activation_sparsity",
    "evidence_summary",
    "build_manifest",
    "save_result",
    "load_result",
    "EPS",
]
