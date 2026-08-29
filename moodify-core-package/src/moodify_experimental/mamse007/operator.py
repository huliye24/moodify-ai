"""MAMSE-007 entry points: fit_pca / project_with_basis.

PCA is a representation/coordinate layer, not a judgment authority:
explained variance is not perceptual importance, CASE_LOCAL bases are not
cross-case comparable, and low-variance safety metrics stay outside PCA
gating.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from .config import PCAConfig
from .models import PCABasis, PCAResult
from .pca import fit_basis
from .preprocess import preprocess_fit, preprocess_project

INTERPRETATION_LIMITS = [
    "principal components are coordinate axes, not physical causes",
    "explained variance is not perceptual importance",
    "low-variance safety metrics must remain outside PCA gating",
    "CASE_LOCAL bases are not cross-case comparable",
]


def _reconstruct_standardized(scores: np.ndarray, components: np.ndarray) -> np.ndarray:
    return scores @ components


def fit_pca(
    matrix: np.ndarray,
    feature_names: tuple[str, ...],
    config: PCAConfig | None = None,
    *,
    source_meta: dict[str, Any] | None = None,
) -> PCAResult:
    cfg = config or PCAConfig()
    t0 = time.perf_counter()
    pre = preprocess_fit(matrix, feature_names, cfg)
    basis, scores = fit_basis(pre, cfg, tuple(feature_names))
    xz_hat = _reconstruct_standardized(scores, basis.components)
    xr_hat = xz_hat * basis.scale + basis.center
    residual = np.linalg.norm(pre.standardized - xz_hat, axis=1)
    evidence = {
        "operator": "MAMSE-007",
        "operator_version": "0.1.0",
        "config_hash": cfg.config_hash,
        "basis_id": basis.basis_id,
        "basis_version": basis.basis_version,
        "mode": basis.mode,
        "observations": int(pre.matrix.shape[0]),
        "input_features": len(feature_names),
        "retained_features": len(pre.retained_feature_names),
        "dropped_features": list(pre.dropped_features),
        "imputed_cells": int(np.sum(pre.imputation_mask)),
        "explained_variance_ratio": basis.explained_variance_ratio.tolist(),
        "cumulative_explained_variance": np.cumsum(basis.explained_variance_ratio).tolist(),
        "mean_reconstruction_residual_standardized": float(np.mean(residual)),
        "max_reconstruction_residual_standardized": float(np.max(residual)),
        "runtime_seconds": time.perf_counter() - t0,
        "interpretation_limits": INTERPRETATION_LIMITS,
        "source_meta": source_meta or {},
    }
    return PCAResult(
        basis=basis,
        scores=scores,
        reconstruction=xr_hat,
        residual_norm=residual,
        imputation_mask=pre.imputation_mask,
        retained_matrix=pre.matrix,
        standardized_matrix=pre.standardized,
        evidence=evidence,
    )


def project_with_basis(
    matrix: np.ndarray,
    feature_names: tuple[str, ...],
    basis: PCABasis,
    *,
    source_meta: dict[str, Any] | None = None,
) -> PCAResult:
    t0 = time.perf_counter()
    xr, xz, mask = preprocess_project(
        matrix,
        feature_names,
        basis.input_feature_names,
        basis.retained_feature_names,
        basis.center,
        basis.scale,
    )
    scores = xz @ basis.components.T
    xz_hat = _reconstruct_standardized(scores, basis.components)
    xr_hat = xz_hat * basis.scale + basis.center
    residual = np.linalg.norm(xz - xz_hat, axis=1)
    evidence = {
        "operator": "MAMSE-007",
        "operator_version": "0.1.0",
        "config_hash": None,
        "basis_id": basis.basis_id,
        "basis_version": basis.basis_version,
        "mode": "PROJECTION_ONLY",
        "basis_mode": basis.mode,
        "observations": int(xr.shape[0]),
        "retained_features": len(basis.retained_feature_names),
        "imputed_cells": int(np.sum(mask)),
        "mean_reconstruction_residual_standardized": float(np.mean(residual)),
        "max_reconstruction_residual_standardized": float(np.max(residual)),
        "runtime_seconds": time.perf_counter() - t0,
        "source_meta": source_meta or {},
    }
    return PCAResult(
        basis=basis,
        scores=scores,
        reconstruction=xr_hat,
        residual_norm=residual,
        imputation_mask=mask,
        retained_matrix=xr,
        standardized_matrix=xz,
        evidence=evidence,
    )
