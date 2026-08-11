"""MAMSE-011 covariance model: schema gate, scaling, shrinkage, eigenspace.

Covariance models relations between auditory variables, not causality.
Window samples are temporally dependent (lag1/neff recorded). Mahalanobis
distance is a distance to a reference model, never an automatic quality
score. Near-degenerate eigenvectors are compared via subspaces.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np

from .config import ALGORITHM_VERSION, CovarianceConfig

EPS = 1e-12


class CovarianceContractError(ValueError):
    pass


@dataclass
class CovarianceModel:
    feature_names: tuple[str, ...]
    feature_units: tuple[str, ...]
    center: np.ndarray
    scale: np.ndarray
    covariance: np.ndarray
    correlation: np.ndarray
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    precision: np.ndarray
    whitening: np.ndarray
    shrinkage_alpha: float
    reference_distance_quantiles: dict[str, float]
    complete_rows: int
    total_rows: int
    lag1_by_feature: np.ndarray
    effective_sample_size_by_feature: np.ndarray
    config: CovarianceConfig
    model_id: str
    runtime_seconds: float = 0.0

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or X.shape[1] != len(self.feature_names):
            raise CovarianceContractError("input feature dimension mismatch")
        Z = (X - self.center[None, :]) / self.scale[None, :]
        if self.config.winsor_z is not None:
            z = float(self.config.winsor_z)
            Z = np.clip(Z, -z, z)
        return Z

    def mahalanobis_squared(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or X.shape[1] != len(self.feature_names):
            raise CovarianceContractError("input feature dimension mismatch")
        out = np.full(X.shape[0], np.nan, dtype=float)
        valid = np.all(np.isfinite(X), axis=1)
        if np.any(valid):
            Z = self.transform(X[valid])
            out[valid] = np.einsum("ni,ij,nj->n", Z, self.precision, Z)
        return out

    def whiten(self, X: np.ndarray) -> np.ndarray:
        Z = self.transform(X)
        if not np.all(np.isfinite(Z)):
            raise CovarianceContractError("whitening requires complete rows")
        return Z @ self.whitening.T

    def top_subspace(self, k: int) -> np.ndarray:
        if k < 1 or k > len(self.eigenvalues):
            raise ValueError("invalid k")
        return self.eigenvectors[:, :k]


def _validate_schema(
    X: np.ndarray,
    feature_names: Iterable[str],
    feature_units: Iterable[str] | None,
    config: CovarianceConfig,
) -> tuple[np.ndarray, tuple[str, ...], tuple[str, ...], np.ndarray]:
    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise CovarianceContractError("X must be rows x features")
    names = tuple(feature_names)
    if len(names) != X.shape[1]:
        raise CovarianceContractError("feature_names length mismatch")
    if len(set(names)) != len(names):
        raise CovarianceContractError("feature_names must be unique")
    units = tuple(feature_units) if feature_units is not None else tuple("unknown" for _ in names)
    if len(units) != len(names):
        raise CovarianceContractError("feature_units length mismatch")
    if X.shape[0] < config.min_complete_rows:
        raise CovarianceContractError("too few total rows")

    finite = np.isfinite(X)
    missing_fraction = 1.0 - float(np.mean(finite))
    if missing_fraction > config.max_missing_fraction:
        raise CovarianceContractError(
            f"missing fraction {missing_fraction:.3f} exceeds configured maximum"
        )
    complete = np.all(finite, axis=1)
    if int(np.sum(complete)) < config.min_complete_rows:
        raise CovarianceContractError("too few complete rows for PSD covariance model")
    return X, names, units, complete


def robust_location_scale(
    X: np.ndarray,
    *,
    center_method: str = "median",
    scale_method: str = "mad",
) -> tuple[np.ndarray, np.ndarray]:
    X = np.asarray(X, dtype=float)
    if not np.all(np.isfinite(X)):
        raise CovarianceContractError("robust_location_scale requires complete rows")

    if center_method == "median":
        center = np.median(X, axis=0)
    elif center_method == "mean":
        center = np.mean(X, axis=0)
    else:
        raise ValueError("center_method must be median or mean")

    if scale_method == "mad":
        mad = np.median(np.abs(X - np.median(X, axis=0)), axis=0)
        scale = 1.4826 * mad
        sd = np.std(X, axis=0, ddof=1)
        scale = np.where(scale > 1e-10, scale, sd)
    elif scale_method == "std":
        scale = np.std(X, axis=0, ddof=1)
    else:
        raise ValueError("scale_method must be mad or std")

    scale = np.where(np.isfinite(scale) & (scale > 1e-10), scale, 1.0)
    return center.astype(float), scale.astype(float)


def empirical_covariance(Z: np.ndarray) -> np.ndarray:
    Z = np.asarray(Z, dtype=float)
    Zc = Z - np.mean(Z, axis=0, keepdims=True)
    return (Zc.T @ Zc) / max(len(Zc), 1)


def oas_covariance(Z: np.ndarray) -> tuple[np.ndarray, float]:
    """Oracle Approximating Shrinkage toward mu * I (standard OAS closed form)."""
    Z = np.asarray(Z, dtype=float)
    Zc = Z - np.mean(Z, axis=0, keepdims=True)
    n, p = Zc.shape
    emp = (Zc.T @ Zc) / max(n, 1)
    mu = float(np.trace(emp) / p)
    alpha = float(np.mean(emp ** 2))
    num = alpha + mu ** 2
    den = (n + 1.0) * (alpha - (mu ** 2) / p)
    shrink = 1.0 if den <= EPS else min(max(num / den, 0.0), 1.0)
    cov = (1.0 - shrink) * emp + shrink * mu * np.eye(p)
    return _symmetrize(cov), float(shrink)


def fixed_shrinkage_covariance(Z: np.ndarray, alpha: float) -> tuple[np.ndarray, float]:
    if not (0 <= alpha <= 1):
        raise ValueError("shrinkage_alpha must be in [0,1]")
    emp = empirical_covariance(Z)
    mu = float(np.trace(emp) / emp.shape[0])
    cov = (1 - alpha) * emp + alpha * mu * np.eye(emp.shape[0])
    return _symmetrize(cov), float(alpha)


def _symmetrize(A: np.ndarray) -> np.ndarray:
    return (A + A.T) / 2.0


def covariance_to_correlation(cov: np.ndarray) -> np.ndarray:
    cov = np.asarray(cov, dtype=float)
    d = np.sqrt(np.maximum(np.diag(cov), 0.0))
    den = d[:, None] * d[None, :]
    corr = np.divide(cov, den, out=np.zeros_like(cov), where=den > EPS)
    for i, di in enumerate(d):
        corr[i, i] = 1.0 if di > EPS else 0.0
    return _symmetrize(corr)


def _canonical_eigh(cov: np.ndarray, floor: float) -> tuple[np.ndarray, np.ndarray]:
    vals, vecs = np.linalg.eigh(_symmetrize(cov))
    order = np.argsort(vals)[::-1]
    vals = np.maximum(vals[order], floor)
    vecs = vecs[:, order]
    for k in range(vecs.shape[1]):
        idx = int(np.argmax(np.abs(vecs[:, k])))
        if vecs[idx, k] < 0:
            vecs[:, k] *= -1
    return vals, vecs


def whitening_and_precision(eigenvalues: np.ndarray, eigenvectors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    inv_sqrt = eigenvectors @ np.diag(1.0 / np.sqrt(eigenvalues)) @ eigenvectors.T
    precision = eigenvectors @ np.diag(1.0 / eigenvalues) @ eigenvectors.T
    return _symmetrize(inv_sqrt), _symmetrize(precision)


def effective_rank(eigenvalues: np.ndarray) -> float:
    vals = np.maximum(np.asarray(eigenvalues, float), 0)
    p = vals / (np.sum(vals) + EPS)
    h = -np.sum(np.where(p > 0, p * np.log(p + EPS), 0.0))
    return float(np.exp(h))


def lag1_autocorrelation(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 3 or np.std(x[:-1]) <= EPS or np.std(x[1:]) <= EPS:
        return 0.0
    return float(np.clip(np.corrcoef(x[:-1], x[1:])[0, 1], -0.99, 0.99))


def effective_sample_size_ar1(x: np.ndarray) -> float:
    n = int(np.sum(np.isfinite(x)))
    if n <= 1:
        return float(n)
    rho = lag1_autocorrelation(x)
    neff = n * (1.0 - rho) / (1.0 + rho)
    return float(np.clip(neff, 1.0, float(n)))


def eigengap_stability(eigenvalues: np.ndarray, relative_tol: float = 1e-3) -> list[dict[str, Any]]:
    vals = np.asarray(eigenvalues, float)
    out = []
    for i in range(len(vals) - 1):
        gap = float(vals[i] - vals[i + 1])
        rel = gap / max(abs(float(vals[i])), EPS)
        out.append({
            "between": [i, i + 1],
            "gap": gap,
            "relative_gap": rel,
            "individual_vectors_stable_candidate": bool(rel >= relative_tol),
        })
    return out


def principal_angles(U: np.ndarray, V: np.ndarray) -> np.ndarray:
    """Principal angles in radians between two equal-dimensional subspaces."""
    U = np.asarray(U, float)
    V = np.asarray(V, float)
    if U.ndim != 2 or V.ndim != 2 or U.shape[0] != V.shape[0]:
        raise ValueError("subspaces must have same ambient dimension")
    if U.shape[1] != V.shape[1]:
        raise ValueError("subspaces must have same dimension")
    s = np.linalg.svd(U.T @ V, compute_uv=False)
    s = np.clip(s, -1.0, 1.0)
    return np.arccos(s)


def projector_distance(U: np.ndarray, V: np.ndarray) -> float:
    U = np.asarray(U, float)
    V = np.asarray(V, float)
    return float(np.linalg.norm(U @ U.T - V @ V.T, ord="fro"))


def fit_covariance_model(
    X: np.ndarray,
    feature_names: Iterable[str],
    *,
    feature_units: Iterable[str] | None = None,
    config: CovarianceConfig = CovarianceConfig(),
) -> CovarianceModel:
    config.validate()
    t0 = time.perf_counter()
    X, names, units, complete_mask = _validate_schema(X, feature_names, feature_units, config)
    Xc = X[complete_mask]

    center, scale = robust_location_scale(
        Xc, center_method=config.center_method, scale_method=config.scale_method
    )
    Z = (Xc - center[None, :]) / scale[None, :]
    if config.winsor_z is not None:
        zmax = float(config.winsor_z)
        Z = np.clip(Z, -zmax, zmax)

    if config.estimator == "oas":
        cov, shrink = oas_covariance(Z)
    elif config.estimator == "empirical":
        cov = empirical_covariance(Z)
        shrink = 0.0
    elif config.estimator == "fixed_shrinkage":
        cov, shrink = fixed_shrinkage_covariance(Z, config.shrinkage_alpha)
    else:
        raise ValueError("estimator must be oas, empirical, or fixed_shrinkage")

    eigenvalues, eigenvectors = _canonical_eigh(cov, config.eigen_floor)
    whitening, precision = whitening_and_precision(eigenvalues, eigenvectors)
    correlation = covariance_to_correlation(cov)

    d2 = np.einsum("ni,ij,nj->n", Z, precision, Z)
    quantiles = {
        "q50": float(np.quantile(d2, 0.50)),
        "q90": float(np.quantile(d2, 0.90)),
        "q95": float(np.quantile(d2, 0.95)),
        "q99": float(np.quantile(d2, 0.99)),
    }

    lag1 = np.array([lag1_autocorrelation(Xc[:, j]) for j in range(Xc.shape[1])])
    neff = np.array([effective_sample_size_ar1(Xc[:, j]) for j in range(Xc.shape[1])])

    h = hashlib.sha256()
    h.update(ALGORITHM_VERSION.encode())
    h.update(json.dumps(config.to_dict(), sort_keys=True).encode())
    h.update(json.dumps(names, ensure_ascii=False).encode())
    h.update(json.dumps(units, ensure_ascii=False).encode())
    h.update(np.round(center, 12).tobytes())
    h.update(np.round(scale, 12).tobytes())
    h.update(np.round(cov, 12).tobytes())
    model_id = "covmodel-" + h.hexdigest()[:16]

    return CovarianceModel(
        feature_names=names,
        feature_units=units,
        center=center,
        scale=scale,
        covariance=cov,
        correlation=correlation,
        eigenvalues=eigenvalues,
        eigenvectors=eigenvectors,
        precision=precision,
        whitening=whitening,
        shrinkage_alpha=shrink,
        reference_distance_quantiles=quantiles,
        complete_rows=int(np.sum(complete_mask)),
        total_rows=int(len(X)),
        lag1_by_feature=lag1,
        effective_sample_size_by_feature=neff,
        config=config,
        model_id=model_id,
        runtime_seconds=time.perf_counter() - t0,
    )


def covariance_drift(
    reference: CovarianceModel,
    current: CovarianceModel,
    *,
    top_k: int = 3,
) -> dict[str, Any]:
    if reference.feature_names != current.feature_names:
        raise CovarianceContractError("feature schema mismatch")
    k = min(top_k, len(reference.feature_names))
    U = reference.top_subspace(k)
    V = current.top_subspace(k)
    angles = principal_angles(U, V)
    cov_norm = np.linalg.norm(reference.covariance, ord="fro") + EPS
    corr_norm = np.linalg.norm(reference.correlation, ord="fro") + EPS
    return {
        "reference_model_id": reference.model_id,
        "current_model_id": current.model_id,
        "top_k": k,
        "covariance_relative_frobenius": float(
            np.linalg.norm(current.covariance - reference.covariance, ord="fro") / cov_norm
        ),
        "correlation_relative_frobenius": float(
            np.linalg.norm(current.correlation - reference.correlation, ord="fro") / corr_norm
        ),
        "principal_angles_deg": np.degrees(angles).tolist(),
        "projector_distance": projector_distance(U, V),
    }
