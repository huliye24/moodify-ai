"""Preprocessing contract: scaling, missing handling, schema hashing.

NaN is never silently converted to 0: imputation is explicit with an
auditable mask; features above the missing threshold or with unresolvable
scale are dropped with a reason. Feature order is bound by schema hash and
projection fails closed on mismatch.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np

from .config import PCAConfig


@dataclass(frozen=True)
class Preprocessed:
    matrix: np.ndarray
    standardized: np.ndarray
    imputation_mask: np.ndarray
    retained_feature_names: tuple[str, ...]
    retained_indices: tuple[int, ...]
    dropped_features: tuple[dict, ...]
    center: np.ndarray
    scale: np.ndarray
    feature_schema_hash: str


def schema_hash(feature_names: tuple[str, ...]) -> str:
    raw = json.dumps(list(feature_names), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _finite_column_stats(col: np.ndarray, scaling: str, min_scale: float) -> tuple[float, float] | None:
    finite = col[np.isfinite(col)]
    if finite.size == 0:
        return None
    if scaling == "robust":
        center = float(np.median(finite))
        mad = float(np.median(np.abs(finite - center)))
        scale = 1.4826 * mad
        if scale <= min_scale:
            scale = float(np.std(finite, ddof=1)) if finite.size > 1 else 0.0
    else:
        center = float(np.mean(finite))
        scale = float(np.std(finite, ddof=1)) if finite.size > 1 else 0.0
    if not np.isfinite(scale) or scale <= min_scale:
        return None
    return center, scale


def preprocess_fit(
    matrix: np.ndarray,
    feature_names: tuple[str, ...],
    config: PCAConfig,
) -> Preprocessed:
    config.validate()
    x = np.asarray(matrix, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError("matrix must be 2D (observations x features)")
    if x.shape[0] < 2:
        raise ValueError("at least two observations are required")
    if x.shape[1] != len(feature_names):
        raise ValueError("feature_names length mismatch")

    retained: list[int] = []
    dropped: list[dict] = []
    centers: list[float] = []
    scales: list[float] = []
    for j, name in enumerate(feature_names):
        col = x[:, j]
        missing_fraction = float(np.mean(~np.isfinite(col)))
        if missing_fraction > config.max_missing_fraction:
            dropped.append({"feature": name, "reason": "TOO_MISSING", "missing_fraction": missing_fraction})
            continue
        stats = _finite_column_stats(col, config.scaling, config.min_scale)
        if stats is None:
            dropped.append({"feature": name, "reason": "ZERO_OR_UNRESOLVED_SCALE", "missing_fraction": missing_fraction})
            continue
        center, scale = stats
        retained.append(j)
        centers.append(center)
        scales.append(scale)

    if not retained:
        raise ValueError("no usable features remain after preprocessing")

    xr = x[:, retained].copy()
    mask = ~np.isfinite(xr)
    center_arr = np.asarray(centers, dtype=np.float64)
    scale_arr = np.asarray(scales, dtype=np.float64)
    # v0.1 median/mean center is also the imputation value; imputation remains explicit in evidence.
    for j in range(xr.shape[1]):
        xr[mask[:, j], j] = center_arr[j]
    xz = (xr - center_arr) / scale_arr
    names = tuple(feature_names[j] for j in retained)
    return Preprocessed(
        matrix=xr,
        standardized=xz,
        imputation_mask=mask,
        retained_feature_names=names,
        retained_indices=tuple(retained),
        dropped_features=tuple(dropped),
        center=center_arr,
        scale=scale_arr,
        feature_schema_hash=schema_hash(feature_names),
    )


def preprocess_project(
    matrix: np.ndarray,
    feature_names: tuple[str, ...],
    basis_input_feature_names: tuple[str, ...],
    retained_feature_names: tuple[str, ...],
    center: np.ndarray,
    scale: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if tuple(feature_names) != tuple(basis_input_feature_names):
        raise ValueError("FEATURE_SCHEMA_MISMATCH: projection requires exact input feature order")
    x = np.asarray(matrix, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != len(feature_names):
        raise ValueError("matrix shape mismatch")
    idx = [feature_names.index(name) for name in retained_feature_names]
    xr = x[:, idx].copy()
    mask = ~np.isfinite(xr)
    for j in range(xr.shape[1]):
        xr[mask[:, j], j] = center[j]
    return xr, (xr - center) / scale, mask
