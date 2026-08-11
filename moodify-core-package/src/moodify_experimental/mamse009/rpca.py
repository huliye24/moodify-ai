"""MAMSE-009 — Robust PCA / Principal Component Pursuit (IALM).

Model: X = L + S with L low-rank, S sparse. Low-rank is a modeling
assumption, not "normal audio"; sparse is a structural deviation candidate,
not "bad audio". v0.1 fails closed on NaN/Inf (no imputation). The dense
residual X - L - S is kept separate from S.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from .config import ALGORITHM_VERSION, RPCAConfig

EPS = 1e-12


class RPCAUnavailableError(ValueError):
    pass


@dataclass
class RPCAResult:
    L: np.ndarray
    S: np.ndarray
    dense_residual: np.ndarray
    iterations: int
    converged: bool
    relative_constraint_error: float
    rank_L: int
    sparsity_S: float
    lambda_used: float
    model_id: str
    config: RPCAConfig
    objective_history: list[float]
    runtime_seconds: float = 0.0


def soft_threshold(X: np.ndarray, tau: float) -> np.ndarray:
    return np.sign(X) * np.maximum(np.abs(X) - tau, 0.0)


def singular_value_threshold(X: np.ndarray, tau: float) -> tuple[np.ndarray, np.ndarray]:
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    keep = s > tau
    if not np.any(keep):
        return np.zeros_like(X), np.array([], dtype=float)
    shr = s[keep] - tau
    return (U[:, keep] * shr) @ Vt[keep, :], shr


def _validate(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    if X.ndim != 2:
        raise ValueError("X must be 2-D")
    if min(X.shape) < 2:
        raise RPCAUnavailableError("matrix too small for low-rank/sparse decomposition")
    if not np.all(np.isfinite(X)):
        raise RPCAUnavailableError("v0.1 does not impute missing values; NaN/Inf must fail closed")
    if np.linalg.norm(X, "fro") <= EPS:
        raise RPCAUnavailableError("matrix contains no recoverable structure")
    return X


def default_lambda(shape: tuple[int, int]) -> float:
    return 1.0 / np.sqrt(max(shape))


def _model_id(X: np.ndarray, config: RPCAConfig, lam: float, space_id: str) -> str:
    h = hashlib.sha256()
    h.update(ALGORITHM_VERSION.encode())
    h.update(space_id.encode())
    h.update(json.dumps(config.to_dict(), sort_keys=True).encode())
    h.update(f"{lam:.17g}".encode())
    h.update(np.round(X, 12).tobytes())
    return "rpcamodel-" + h.hexdigest()[:16]


def principal_component_pursuit(X: np.ndarray, config: RPCAConfig = RPCAConfig(), *,
                                space_id: str = "UNSPECIFIED") -> RPCAResult:
    """Inexact Augmented Lagrange Multiplier solver for PCP.

    Solves approximately: min ||L||_* + lambda ||S||_1 subject to X = L + S.
    """
    config.validate()
    t0 = time.perf_counter()
    X = _validate(X)
    lam = float(config.lam if config.lam is not None else default_lambda(X.shape))
    norm2 = float(np.linalg.norm(X, 2))
    norm_inf = float(np.max(np.abs(X)) / max(lam, EPS))
    dual_norm = max(norm2, norm_inf, EPS)
    Y = X / dual_norm
    mu = config.mu_factor / max(norm2, EPS)
    mu_bar = mu * config.max_mu_factor
    L = np.zeros_like(X)
    S = np.zeros_like(X)
    normX = np.linalg.norm(X, "fro") + EPS
    hist: list[float] = []
    converged = False
    for it in range(1, config.max_iter + 1):
        L, _ = singular_value_threshold(X - S + Y / mu, 1.0 / mu)
        S = soft_threshold(X - L + Y / mu, lam / mu)
        Z = X - L - S
        Y = Y + mu * Z
        mu = min(mu * config.rho, mu_bar)
        err = float(np.linalg.norm(Z, "fro") / normX)
        if it == 1 or it % 5 == 0 or err < config.tol:
            nuclear = float(np.sum(np.linalg.svd(L, compute_uv=False)))
            l1 = float(np.sum(np.abs(S)))
            hist.append(nuclear + lam * l1)
        if err < config.tol:
            converged = True
            break
    dense = X - L - S
    svals = np.linalg.svd(L, compute_uv=False)
    rank = int(np.sum(svals > max(svals[0] if len(svals) else 0, 1.0) * 1e-8))
    sparsity = float(np.mean(np.abs(S) > 1e-10))
    return RPCAResult(
        L=L, S=S, dense_residual=dense, iterations=it, converged=converged,
        relative_constraint_error=float(np.linalg.norm(dense, "fro") / normX),
        rank_L=rank, sparsity_S=sparsity, lambda_used=lam,
        model_id=_model_id(X, config, lam, space_id), config=config,
        objective_history=hist, runtime_seconds=time.perf_counter() - t0,
    )


def sparse_frame_score(X: np.ndarray, S: np.ndarray) -> np.ndarray:
    X = np.asarray(X, float)
    S = np.asarray(S, float)
    return np.sum(np.abs(S), axis=0) / (np.sum(np.abs(X), axis=0) + EPS)


def sparse_feature_score(X: np.ndarray, S: np.ndarray) -> np.ndarray:
    X = np.asarray(X, float)
    S = np.asarray(S, float)
    return np.sum(np.abs(S), axis=1) / (np.sum(np.abs(X), axis=1) + EPS)


def robust_zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    med = float(np.median(x))
    mad = float(np.median(np.abs(x - med)))
    scale = 1.4826 * mad
    if scale <= EPS:
        fallback = float(np.mean(np.abs(x - med)))
        if fallback <= EPS:
            return np.zeros_like(x)
        scale = fallback
    return (x - med) / scale


def candidate_intervals(scores: np.ndarray, *, z_threshold: float = 6.0, min_frames: int = 2,
                        gap_tolerance: int = 1) -> list[dict[str, Any]]:
    """Anonymous sparse-structure candidate intervals (no quality semantic)."""
    scores = np.asarray(scores, float)
    z = robust_zscore(scores)
    active = np.where(z >= z_threshold)[0]
    if len(active) == 0:
        return []
    groups = []
    cur = [int(active[0])]
    for idx in active[1:]:
        idx = int(idx)
        if idx - cur[-1] <= gap_tolerance + 1:
            cur.append(idx)
        else:
            groups.append(cur)
            cur = [idx]
    groups.append(cur)
    out = []
    for g in groups:
        if len(g) < min_frames:
            continue
        out.append({"event_type": "SPARSE_STRUCTURE_CANDIDATE", "start_frame": g[0], "end_frame": g[-1],
                    "peak_z": float(np.max(z[g])), "peak_score": float(np.max(scores[g])),
                    "semantic_authority": "EXPERIMENTAL_UNKNOWN"})
    return out


def low_rank_similarity(L_true: np.ndarray, L_est: np.ndarray) -> float:
    a = np.asarray(L_true, float).ravel()
    b = np.asarray(L_est, float).ravel()
    return float(np.dot(a, b) / ((np.linalg.norm(a) + EPS) * (np.linalg.norm(b) + EPS)))


def sparse_support_f1(S_true: np.ndarray, S_est: np.ndarray, *, threshold: float | None = None) -> float:
    T = np.abs(np.asarray(S_true, float)) > 1e-10
    if threshold is None:
        nz = np.abs(S_est[np.abs(S_est) > 1e-12])
        threshold = float(np.percentile(nz, 25)) if nz.size else np.inf
    E = np.abs(S_est) >= threshold
    tp = np.sum(T & E)
    fp = np.sum((~T) & E)
    fn = np.sum(T & (~E))
    p = tp / (tp + fp + EPS)
    r = tp / (tp + fn + EPS)
    return float(2 * p * r / (p + r + EPS))
