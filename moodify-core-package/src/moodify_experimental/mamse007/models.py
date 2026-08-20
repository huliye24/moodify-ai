"""MAMSE-007 data models: basis and result containers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class PCABasis:
    basis_id: str
    basis_version: str
    mode: str
    input_feature_names: tuple[str, ...]
    retained_feature_names: tuple[str, ...]
    dropped_features: tuple[dict[str, Any], ...]
    center: np.ndarray
    scale: np.ndarray
    components: np.ndarray  # (k, d), rows are principal axes
    singular_values: np.ndarray
    explained_variance: np.ndarray
    explained_variance_ratio: np.ndarray
    feature_schema_hash: str
    preprocessing: dict[str, Any]

    @property
    def n_components(self) -> int:
        return int(self.components.shape[0])


@dataclass(frozen=True)
class PCAResult:
    basis: PCABasis
    scores: np.ndarray
    reconstruction: np.ndarray
    residual_norm: np.ndarray
    imputation_mask: np.ndarray
    retained_matrix: np.ndarray
    standardized_matrix: np.ndarray
    evidence: dict[str, Any]
