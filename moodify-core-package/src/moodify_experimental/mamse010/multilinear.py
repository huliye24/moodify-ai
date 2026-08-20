"""MAMSE-010 multilinear research: unfold/fold, n-mode product, HOSVD/Tucker.

HOSVD is research-only, applies to fully-observed homogeneous tensors, and
never carries a quality interpretation (high residual != bad audio).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

from .contracts import EPS, SCHEMA_VERSION, TensorContractError


def unfold(x: np.ndarray, mode: int) -> np.ndarray:
    x = np.asarray(x)
    if mode < 0 or mode >= x.ndim:
        raise ValueError("invalid mode")
    return np.reshape(np.moveaxis(x, mode, 0), (x.shape[mode], -1))


def fold(mat: np.ndarray, mode: int, shape: tuple[int, ...]) -> np.ndarray:
    mat = np.asarray(mat)
    if mode < 0 or mode >= len(shape):
        raise ValueError("invalid mode")
    moved_shape = (shape[mode],) + tuple(shape[i] for i in range(len(shape)) if i != mode)
    x = np.reshape(mat, moved_shape)
    return np.moveaxis(x, 0, mode)


def mode_dot(x: np.ndarray, matrix: np.ndarray, mode: int) -> np.ndarray:
    """n-mode product: matrix shape (new_dim, old_dim)."""
    x = np.asarray(x, dtype=float)
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != x.shape[mode]:
        raise ValueError("matrix second dimension must match selected tensor mode")
    u = unfold(x, mode)
    return fold(matrix @ u, mode, tuple(
        matrix.shape[0] if i == mode else x.shape[i] for i in range(x.ndim)
    ))


@dataclass
class TuckerModel:
    factors: tuple[np.ndarray, ...]
    core: np.ndarray
    ranks: tuple[int, ...]
    source_shape: tuple[int, ...]
    model_id: str

    def reconstruct(self) -> np.ndarray:
        x = self.core
        for mode, factor in enumerate(self.factors):
            x = mode_dot(x, factor, mode)
        return x


def _fix_svd_signs(U: np.ndarray) -> np.ndarray:
    U = U.copy()
    for k in range(U.shape[1]):
        idx = int(np.argmax(np.abs(U[:, k])))
        if U[idx, k] < 0:
            U[:, k] *= -1
    return U


def hosvd(x: np.ndarray, ranks: tuple[int, ...]) -> TuckerModel:
    """Deterministic HOSVD/Tucker model for a fully observed tensor."""
    x = np.asarray(x, dtype=float)
    if not np.all(np.isfinite(x)):
        raise TensorContractError("HOSVD prototype requires a fully observed tensor")
    if len(ranks) != x.ndim:
        raise ValueError("ranks length must equal x.ndim")
    factors = []
    for mode, r in enumerate(ranks):
        if r < 1 or r > x.shape[mode]:
            raise ValueError(f"invalid rank for mode {mode}")
        U, _, _ = np.linalg.svd(unfold(x, mode), full_matrices=False)
        factors.append(_fix_svd_signs(U[:, :r]))
    core = x
    for mode, U in enumerate(factors):
        core = mode_dot(core, U.T, mode)
    h = hashlib.sha256()
    h.update(SCHEMA_VERSION.encode())
    h.update(str(tuple(x.shape)).encode())
    h.update(str(tuple(ranks)).encode())
    for U in factors:
        h.update(np.round(U, 12).tobytes())
    return TuckerModel(
        factors=tuple(factors),
        core=core,
        ranks=tuple(ranks),
        source_shape=tuple(x.shape),
        model_id="tucker-" + h.hexdigest()[:16],
    )


def project_tucker(x: np.ndarray, factors: tuple[np.ndarray, ...]) -> tuple[np.ndarray, np.ndarray]:
    """Project a tensor through a frozen multilinear basis and reconstruct it."""
    x = np.asarray(x, dtype=float)
    if len(factors) != x.ndim:
        raise ValueError("factor count must equal x.ndim")
    core = x
    for mode, U in enumerate(factors):
        if U.shape[0] != x.shape[mode]:
            raise ValueError(f"factor {mode} incompatible with input")
        core = mode_dot(core, U.T, mode)
    recon = core
    for mode, U in enumerate(factors):
        recon = mode_dot(recon, U, mode)
    return recon, x - recon


def relative_residual_by_time(x: np.ndarray, residual: np.ndarray, time_mode: int = 0) -> np.ndarray:
    """L2 relative residual for each time coordinate."""
    x = np.asarray(x, float)
    r = np.asarray(residual, float)
    if x.shape != r.shape:
        raise ValueError("shape mismatch")
    xm = np.moveaxis(x, time_mode, 0).reshape(x.shape[time_mode], -1)
    rm = np.moveaxis(r, time_mode, 0).reshape(r.shape[time_mode], -1)
    return np.linalg.norm(rm, axis=1) / (np.linalg.norm(xm, axis=1) + EPS)


def mode_singular_values(x: np.ndarray, mode: int) -> np.ndarray:
    return np.linalg.svd(unfold(np.asarray(x, float), mode), compute_uv=False)
