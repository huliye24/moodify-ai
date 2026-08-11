"""MAMSE-008 NMF core: nonnegative factorization with deterministic identity.

V >= 0 (features x frames), V ≈ W @ H, W/H >= 0. Components are anonymous
mathematical factors, never automatic source labels. NaN/inf are masked,
never replaced by physical zeros. Scale/permutation ambiguities are
canonicalized deterministically; basis_id is stable per input/config.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass

import numpy as np

from .config import ALGORITHM_VERSION, NMFConfig

EPS = 1e-12


class NMFUnavailableError(ValueError):
    """Raised when a valid nonnegative decomposition cannot be supported."""


@dataclass
class NMFResult:
    W: np.ndarray
    H: np.ndarray
    mask: np.ndarray
    objective_history: list[float]
    iterations: int
    relative_error: float
    basis_id: str
    config: NMFConfig
    status: str = "OK"
    runtime_seconds: float = 0.0

    @property
    def reconstruction(self) -> np.ndarray:
        return self.W @ self.H

    @property
    def residual(self) -> np.ndarray:
        return self.mask * (self._V_for_residual - self.reconstruction)

    _V_for_residual: np.ndarray | None = None


def _validate_matrix(V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    V = np.asarray(V, dtype=np.float64)
    if V.ndim != 2:
        raise ValueError("V must be a 2-D nonnegative matrix (features x frames)")
    finite = np.isfinite(V)
    if not finite.any():
        raise NMFUnavailableError("all entries are unavailable")
    if np.any(V[finite] < 0):
        raise ValueError("NMF input must be nonnegative in physical linear coordinates")
    mask = finite.astype(np.float64)
    clean = np.where(finite, V, 0.0)
    if float(np.sum(clean)) <= EPS:
        raise NMFUnavailableError("matrix has no positive energy")
    return clean, mask


def beta_divergence(V: np.ndarray, Y: np.ndarray, beta: float, mask: np.ndarray | None = None) -> float:
    V = np.asarray(V, dtype=np.float64)
    Y = np.maximum(np.asarray(Y, dtype=np.float64), EPS)
    M = np.ones_like(V) if mask is None else np.asarray(mask, dtype=np.float64)
    if beta == 2:
        d = 0.5 * (V - Y) ** 2
    elif beta == 1:
        ratio_term = np.where(V > 0, V * np.log(np.maximum(V, EPS) / Y), 0.0)
        d = ratio_term - V + Y
    elif beta == 0:
        ratio = np.maximum(V, EPS) / Y
        d = ratio - np.log(ratio) - 1.0
    else:
        raise ValueError("v0.1 supports beta = 2 (Euclidean), 1 (KL), or 0 (IS)")
    return float(np.sum(M * d))


def _nndsvd(V: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic NNDSVD initialization (positive/negative SVD split)."""
    U, S, VT = np.linalg.svd(V, full_matrices=False)
    r = min(rank, len(S))
    W = np.zeros((V.shape[0], rank), dtype=np.float64)
    H = np.zeros((rank, V.shape[1]), dtype=np.float64)

    u0 = np.abs(U[:, 0])
    v0 = np.abs(VT[0, :])
    nu = np.linalg.norm(u0) + EPS
    nv = np.linalg.norm(v0) + EPS
    W[:, 0] = np.sqrt(S[0]) * u0 / nu
    H[0, :] = np.sqrt(S[0]) * v0 / nv

    for j in range(1, r):
        u = U[:, j]
        v = VT[j, :]
        up, un = np.maximum(u, 0), np.maximum(-u, 0)
        vp, vn = np.maximum(v, 0), np.maximum(-v, 0)
        nup, nun = np.linalg.norm(up), np.linalg.norm(un)
        nvp, nvn = np.linalg.norm(vp), np.linalg.norm(vn)
        mp, mn = nup * nvp, nun * nvn
        if mp >= mn:
            uu, vv, sigma = up, vp, mp
            nuj, nvj = nup, nvp
        else:
            uu, vv, sigma = un, vn, mn
            nuj, nvj = nun, nvn
        if sigma <= EPS or nuj <= EPS or nvj <= EPS:
            continue
        scale = math_sqrt(S[j] * sigma)
        W[:, j] = scale * uu / (nuj + EPS)
        H[j, :] = scale * vv / (nvj + EPS)

    mean_v = float(np.mean(V[V > 0])) if np.any(V > 0) else EPS
    W[W <= 0] = mean_v * 1e-6
    H[H <= 0] = mean_v * 1e-6
    return W, H


def math_sqrt(x: float) -> float:
    return float(np.sqrt(max(float(x), 0.0)))


def _random_init(V: np.ndarray, rank: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    scale = max(float(np.sqrt(np.mean(V) / max(rank, 1))), 1e-6)
    return (
        rng.random((V.shape[0], rank)) * scale + EPS,
        rng.random((rank, V.shape[1])) * scale + EPS,
    )


def _gamma(beta: float) -> float:
    if beta < 1:
        return 1.0 / (2.0 - beta)
    if beta > 2:
        return 1.0 / (beta - 1.0)
    return 1.0


def _normalize_columns(W: np.ndarray, H: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scales = np.sum(W, axis=0)
    scales = np.maximum(scales, EPS)
    W = W / scales[None, :]
    H = H * scales[:, None]
    return W, H


def canonicalize_factors(W: np.ndarray, H: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Resolve scale/permutation ambiguity deterministically."""
    Wc, Hc = _normalize_columns(np.asarray(W, float).copy(), np.asarray(H, float).copy())
    energy = np.sum(Hc, axis=1)
    centroids = np.sum(Wc * np.arange(Wc.shape[0])[:, None], axis=0)
    hashes = []
    for k in range(Wc.shape[1]):
        payload = np.round(Wc[:, k], 12).tobytes()
        hashes.append(hashlib.sha256(payload).hexdigest())
    keys = [(-energy[k], centroids[k], hashes[k], k) for k in range(Wc.shape[1])]
    perm = np.array([item[3] for item in sorted(keys)], dtype=int)
    return Wc[:, perm], Hc[perm, :], perm


def _basis_id(W: np.ndarray, config: NMFConfig, axis: np.ndarray | None) -> str:
    h = hashlib.sha256()
    h.update(ALGORITHM_VERSION.encode())
    h.update(json.dumps(config.to_dict(), sort_keys=True).encode())
    h.update(np.round(W, 12).tobytes())
    if axis is not None:
        h.update(np.round(np.asarray(axis, dtype=float), 9).tobytes())
    return "nmfbasis-" + h.hexdigest()[:16]


def fit_nmf(
    V: np.ndarray,
    config: NMFConfig = NMFConfig(),
    *,
    axis: np.ndarray | None = None,
) -> NMFResult:
    config.validate()
    t0 = time.perf_counter()
    Vc, M = _validate_matrix(V)
    if config.rank < 1 or config.rank > min(Vc.shape):
        raise ValueError("rank must be between 1 and min(V.shape)")
    if config.init == "nndsvd":
        W, H = _nndsvd(Vc, config.rank)
    elif config.init == "random":
        W, H = _random_init(Vc, config.rank, config.seed)
    else:
        raise ValueError("init must be 'nndsvd' or 'random'")

    if config.normalize_w:
        W, H = _normalize_columns(W, H)

    history: list[float] = []
    prev = None
    gamma = _gamma(config.beta)

    for it in range(config.max_iter):
        Y = np.maximum(W @ H, EPS)
        if config.beta == 2:
            num_h = W.T @ (M * Vc)
            den_h = W.T @ (M * Y) + config.l1_h + EPS
        else:
            num_h = W.T @ (M * Vc * (Y ** (config.beta - 2.0)))
            den_h = W.T @ (M * (Y ** (config.beta - 1.0))) + config.l1_h + EPS
        H *= np.maximum(num_h / den_h, EPS) ** gamma
        H = np.maximum(H, EPS)

        Y = np.maximum(W @ H, EPS)
        if config.beta == 2:
            num_w = (M * Vc) @ H.T
            den_w = (M * Y) @ H.T + config.l1_w + EPS
        else:
            num_w = (M * Vc * (Y ** (config.beta - 2.0))) @ H.T
            den_w = (M * (Y ** (config.beta - 1.0))) @ H.T + config.l1_w + EPS
        W *= np.maximum(num_w / den_w, EPS) ** gamma
        W = np.maximum(W, EPS)

        if config.normalize_w:
            W, H = _normalize_columns(W, H)

        if it == 0 or (it + 1) % 5 == 0 or it == config.max_iter - 1:
            obj = beta_divergence(Vc, W @ H, config.beta, M)
            history.append(obj)
            if prev is not None:
                rel = abs(prev - obj) / max(abs(prev), EPS)
                if rel < config.tol:
                    break
            prev = obj

    W, H, _ = canonicalize_factors(W, H)
    recon = W @ H
    num = np.linalg.norm(M * (Vc - recon))
    den = np.linalg.norm(M * Vc) + EPS
    result = NMFResult(
        W=W,
        H=H,
        mask=M,
        objective_history=history,
        iterations=it + 1,
        relative_error=float(num / den),
        basis_id=_basis_id(W, config, axis),
        config=config,
        runtime_seconds=time.perf_counter() - t0,
    )
    result._V_for_residual = Vc
    return result


def project_h(
    V: np.ndarray,
    W: np.ndarray,
    *,
    beta: float = 2.0,
    max_iter: int = 250,
    tol: float = 1e-7,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Project new nonnegative observations into a frozen basis W.

    Returns H, reconstruction, residual_ratio_per_frame.
    """
    Vc, M = _validate_matrix(V)
    W = np.asarray(W, dtype=np.float64)
    if W.ndim != 2 or W.shape[0] != Vc.shape[0]:
        raise ValueError("W feature dimension must match V")
    if np.any(W < 0):
        raise ValueError("W must be nonnegative")

    H = np.full((W.shape[1], Vc.shape[1]), max(float(np.mean(Vc)), 1e-6), dtype=np.float64)
    gamma = _gamma(beta)
    prev = None
    for _ in range(max_iter):
        Y = np.maximum(W @ H, EPS)
        if beta == 2:
            num = W.T @ (M * Vc)
            den = W.T @ (M * Y) + EPS
        else:
            num = W.T @ (M * Vc * Y ** (beta - 2))
            den = W.T @ (M * Y ** (beta - 1)) + EPS
        H *= np.maximum(num / den, EPS) ** gamma
        H = np.maximum(H, EPS)
        obj = beta_divergence(Vc, W @ H, beta, M)
        if prev is not None and abs(prev - obj) / max(abs(prev), EPS) < tol:
            break
        prev = obj

    recon = W @ H
    residual_l1 = np.sum(M * np.abs(Vc - recon), axis=0)
    signal_l1 = np.sum(M * np.abs(Vc), axis=0) + EPS
    ratio = residual_l1 / signal_l1
    return H, recon, ratio


def component_cosine_similarity(Wa: np.ndarray, Wb: np.ndarray) -> np.ndarray:
    Wa = np.asarray(Wa, float)
    Wb = np.asarray(Wb, float)
    na = np.linalg.norm(Wa, axis=0, keepdims=True) + EPS
    nb = np.linalg.norm(Wb, axis=0, keepdims=True) + EPS
    return (Wa / na).T @ (Wb / nb)


def activation_sparsity(h: np.ndarray) -> float:
    """Hoyer sparsity in [0,1] for one activation vector."""
    x = np.maximum(np.asarray(h, float), 0)
    n = x.size
    if n <= 1 or np.linalg.norm(x) <= EPS:
        return 0.0
    return float((np.sqrt(n) - np.sum(x) / (np.linalg.norm(x) + EPS)) / (np.sqrt(n) - 1))
