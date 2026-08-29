"""Exact NumPy SVD basis fitting with deterministic sign canonicalization.

Scores = U_k @ diag(S_k), components = V_k, reconstruction = scores @
components, residual_t = ||Xz_t - reconstruction_t||_2. The SVD sign
ambiguity is resolved by forcing the largest absolute loading of each
component positive; basis_id is deterministic.
"""

from __future__ import annotations

import hashlib
import json

import numpy as np

from .config import BASIS_VERSION, PCAConfig
from .models import PCABasis
from .preprocess import Preprocessed


def _canonicalize_component_signs(components: np.ndarray, scores: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    c = components.copy()
    s = scores.copy()
    for i in range(c.shape[0]):
        pivot = int(np.argmax(np.abs(c[i])))
        if c[i, pivot] < 0:
            c[i] *= -1.0
            s[:, i] *= -1.0
    return c, s


def _basis_id(pre: Preprocessed, components: np.ndarray, config: PCAConfig) -> str:
    payload = {
        "version": BASIS_VERSION,
        "mode": config.mode,
        "schema": pre.feature_schema_hash,
        "retained": list(pre.retained_feature_names),
        "center": np.round(pre.center, 12).tolist(),
        "scale": np.round(pre.scale, 12).tolist(),
        "components": np.round(components, 12).tolist(),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "basis-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def fit_basis(pre: Preprocessed, config: PCAConfig, input_feature_names: tuple[str, ...]) -> tuple[PCABasis, np.ndarray]:
    xz = pre.standardized
    u, singular_values, vt = np.linalg.svd(xz, full_matrices=False)
    rank_max = min(xz.shape)
    k = min(config.n_components or rank_max, rank_max)
    scores_full = u[:, :k] * singular_values[:k]
    components, scores = _canonicalize_component_signs(vt[:k], scores_full)

    denom = max(xz.shape[0] - 1, 1)
    explained = singular_values[:k] ** 2 / denom
    all_explained = singular_values ** 2 / denom
    total = float(np.sum(all_explained))
    ratio = explained / total if total > 0 else np.zeros_like(explained)

    basis = PCABasis(
        basis_id=_basis_id(pre, components, config),
        basis_version=BASIS_VERSION,
        mode=config.mode,
        input_feature_names=tuple(input_feature_names),
        retained_feature_names=pre.retained_feature_names,
        dropped_features=pre.dropped_features,
        center=pre.center,
        scale=pre.scale,
        components=components,
        singular_values=singular_values[:k],
        explained_variance=explained,
        explained_variance_ratio=ratio,
        feature_schema_hash=pre.feature_schema_hash,
        preprocessing={
            "scaling": config.scaling,
            "max_missing_fraction": config.max_missing_fraction,
            "imputation": config.impute,
            "sign_rule": "largest_abs_loading_positive",
            "whitening": False,
        },
    )
    return basis, scores
