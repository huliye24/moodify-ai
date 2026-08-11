"""MAMSE-012 GSP operators: spectrum, GFT, energy, filters, localization.

Graph frequency is topology frequency, not acoustic Hz. High graph-frequency
energy is a structural variation candidate, not bad audio. Dense
eigendecomposition is guarded; large graphs use the sparse path.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from .contracts import EPS, GraphContractError

try:
    from scipy import sparse
    from scipy.sparse.linalg import eigsh
except Exception:  # pragma: no cover
    sparse = None
    eigsh = None

MAX_DENSE_NODES = 512


def spectral_decomposition(
    graph,
    *,
    normalized: bool = False,
    max_dense_nodes: int = MAX_DENSE_NODES,
    k: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    n = len(graph.nodes)
    L = graph.laplacian(normalized=normalized)
    if n <= max_dense_nodes:
        vals, vecs = np.linalg.eigh(L)
        order = np.argsort(vals)
        vals, vecs = vals[order], vecs[:, order]
        for col in range(vecs.shape[1]):
            i = int(np.argmax(np.abs(vecs[:, col])))
            if vecs[i, col] < 0:
                vecs[:, col] *= -1
        return (vals[:k], vecs[:, :k]) if k is not None else (vals, vecs)
    if k is None:
        raise GraphContractError("full dense graph Fourier basis blocked above max_dense_nodes")
    if sparse is None or eigsh is None:
        raise GraphContractError("scipy sparse eigensolver unavailable")
    if k >= n:
        raise ValueError("k must be < n")
    vals, vecs = eigsh(sparse.csr_matrix(L), k=k, which="SM")
    order = np.argsort(vals)
    vals, vecs = vals[order], vecs[:, order]
    for col in range(vecs.shape[1]):
        i = int(np.argmax(np.abs(vecs[:, col])))
        if vecs[i, col] < 0:
            vecs[:, col] *= -1
    return vals, vecs


def graph_fourier_transform(
    graph,
    signal: np.ndarray,
    *,
    normalized: bool = False,
    max_dense_nodes: int = MAX_DENSE_NODES,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = np.asarray(signal, dtype=float).reshape(-1)
    if len(x) != len(graph.nodes) or not np.all(np.isfinite(x)):
        raise GraphContractError("invalid complete graph signal")
    vals, U = spectral_decomposition(graph, normalized=normalized, max_dense_nodes=max_dense_nodes)
    return vals, U.T @ x, U


def inverse_graph_fourier(coefficients: np.ndarray, eigenvectors: np.ndarray) -> np.ndarray:
    c = np.asarray(coefficients, dtype=float).reshape(-1)
    U = np.asarray(eigenvectors, dtype=float)
    if U.ndim != 2 or U.shape[1] != len(c):
        raise ValueError("shape mismatch")
    return U @ c


def dirichlet_energy(graph, signal: np.ndarray, *, normalized: bool = False) -> float:
    x = np.asarray(signal, dtype=float).reshape(-1)
    if len(x) != len(graph.nodes) or not np.all(np.isfinite(x)):
        raise GraphContractError("invalid graph signal")
    L = graph.laplacian(normalized=normalized)
    return float(x @ L @ x)


def local_variation(graph, signal: np.ndarray) -> np.ndarray:
    x = np.asarray(signal, dtype=float).reshape(-1)
    if len(x) != len(graph.nodes) or not np.all(np.isfinite(x)):
        raise GraphContractError("invalid graph signal")
    W = graph.adjacency()
    return 0.5 * np.sum(W * (x[:, None] - x[None, :]) ** 2, axis=1)


def graph_spectral_energy(
    graph,
    signal: np.ndarray,
    *,
    high_fraction: float = 1 / 3,
    normalized: bool = False,
) -> dict[str, float]:
    if not 0 < high_fraction < 1:
        raise ValueError("high_fraction must be in (0,1)")
    vals, coeff, _ = graph_fourier_transform(graph, signal, normalized=normalized)
    e = coeff ** 2
    total = float(e.sum() + EPS)
    high_start = max(1, int(math.floor(len(e) * (1.0 - high_fraction))))
    return {
        "total_energy": total,
        "dc_energy_ratio": float(e[0] / total),
        "low_graph_frequency_ratio": float(e[:high_start].sum() / total),
        "high_graph_frequency_ratio": float(e[high_start:].sum() / total),
        "high_start_eigenvalue": float(vals[high_start]),
    }


def heat_kernel_filter(graph, signal: np.ndarray, tau: float, *, normalized: bool = False) -> np.ndarray:
    if tau < 0:
        raise ValueError("tau must be >= 0")
    vals, coeff, U = graph_fourier_transform(graph, signal, normalized=normalized)
    return U @ (np.exp(-tau * vals) * coeff)


def polynomial_graph_filter(
    graph,
    signal: np.ndarray,
    coefficients: Sequence[float],
    *,
    normalized: bool = False,
) -> np.ndarray:
    x = np.asarray(signal, dtype=float).reshape(-1)
    if len(x) != len(graph.nodes):
        raise GraphContractError("signal length mismatch")
    coeffs = [float(c) for c in coefficients]
    if not coeffs:
        raise ValueError("at least one coefficient required")
    L = graph.laplacian(normalized=normalized)
    y = coeffs[0] * x
    p = x.copy()
    for c in coeffs[1:]:
        p = L @ p
        y = y + c * p
    return y
