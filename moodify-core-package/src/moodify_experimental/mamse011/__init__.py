"""MAMSE-011 — covariance & auditory eigenspace (experimental).

Models relations between auditory variables: schema gate -> robust scaling
-> shrinkage covariance -> eigenspace/whitening/precision -> Mahalanobis
geometry -> frozen-reference projection -> covariance drift. Covariance is
not causality; Mahalanobis is not a quality score; temporal dependence is
recorded (lag1/neff); near-degenerate eigenvectors compare subspaces.
"""

from .config import (
    ALGORITHM_VERSION,
    MANIFEST_SCHEMA_VERSION,
    OPERATOR_ID,
    SCHEMA_VERSION,
    CovarianceConfig,
)
from .covariance import (
    CovarianceContractError,
    CovarianceModel,
    covariance_drift,
    covariance_to_correlation,
    effective_rank,
    effective_sample_size_ar1,
    eigengap_stability,
    empirical_covariance,
    fit_covariance_model,
    fixed_shrinkage_covariance,
    lag1_autocorrelation,
    oas_covariance,
    principal_angles,
    projector_distance,
    robust_location_scale,
    whitening_and_precision,
)
from .evidence import load_model, model_evidence, save_model

__all__ = [
    "OPERATOR_ID",
    "ALGORITHM_VERSION",
    "SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "CovarianceConfig",
    "CovarianceModel",
    "CovarianceContractError",
    "fit_covariance_model",
    "robust_location_scale",
    "empirical_covariance",
    "oas_covariance",
    "fixed_shrinkage_covariance",
    "covariance_to_correlation",
    "whitening_and_precision",
    "effective_rank",
    "lag1_autocorrelation",
    "effective_sample_size_ar1",
    "eigengap_stability",
    "principal_angles",
    "projector_distance",
    "covariance_drift",
    "model_evidence",
    "save_model",
    "load_model",
]
