"""MAMSE-007 — PCA/SVD auditory state decomposition (experimental).

Turns a ScalePlane-like feature matrix into a versioned state space:
semantic preflight -> robust preprocessing -> exact NumPy SVD basis ->
state scores / reconstruction residual -> evidence. PCA is a coordinate
layer, not a judgment authority; CASE_LOCAL bases are not cross-case
comparable.
"""

from .config import (
    BASIS_VERSION,
    CONFIG_VERSION,
    MANIFEST_SCHEMA_VERSION,
    OPERATOR_ID,
    OPERATOR_VERSION,
    PCAConfig,
)
from .models import PCABasis, PCAResult
from .operator import fit_pca, project_with_basis
from .pca import fit_basis
from .preprocess import preprocess_fit, preprocess_project, schema_hash
from .semantic_preflight import (
    DEFAULT_SEMANTIC_RULES,
    FeatureSemanticRecord,
    basis_eligible_feature_names,
    preflight_features,
)
from .serialize import basis_from_dict, basis_to_dict, build_manifest, load_basis, load_result, save_result
from .synthetic import FEATURES, latent_auditory_matrix

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "CONFIG_VERSION",
    "BASIS_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "PCAConfig",
    "PCABasis",
    "PCAResult",
    "fit_pca",
    "project_with_basis",
    "fit_basis",
    "preprocess_fit",
    "preprocess_project",
    "schema_hash",
    "preflight_features",
    "basis_eligible_feature_names",
    "FeatureSemanticRecord",
    "DEFAULT_SEMANTIC_RULES",
    "basis_to_dict",
    "basis_from_dict",
    "build_manifest",
    "save_result",
    "load_result",
    "load_basis",
    "FEATURES",
    "latent_auditory_matrix",
]
