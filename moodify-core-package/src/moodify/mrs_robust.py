"""Robust, genre-aware reference statistics and bootstrap intervals for MRS."""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

import numpy as np

MAD_NORMAL_SCALE = 1.4826
_GROUPS = ("spectrum", "dynamic", "transient", "space", "texture", "temporal", "artifact")


def flatten_features(features: Mapping[str, Any]) -> dict[str, float]:
    """Flatten numeric MRS feature groups into ``group__feature`` keys."""
    flattened: dict[str, float] = {}
    for group in _GROUPS:
        values = features.get(group, {})
        if not isinstance(values, Mapping):
            continue
        for name, value in values.items():
            if isinstance(value, (int, float, np.integer, np.floating)):
                flattened[f"{group}__{name}"] = float(value)
    return flattened


def build_robust_reference_stats(features_list: Sequence[Mapping[str, Any]]) -> dict:
    """Build median/MAD statistics while retaining mean/SD for comparison."""
    rows = [flatten_features(features) for features in features_list]
    if not rows:
        return {"mu": {}, "sigma": {}, "median": {}, "mad": {}, "n": 0, "method": "mad"}
    keys = sorted(set.intersection(*(set(row) for row in rows)))
    mu: dict[str, float] = {}
    sigma: dict[str, float] = {}
    median: dict[str, float] = {}
    mad: dict[str, float] = {}
    for key in keys:
        values = np.asarray([row[key] for row in rows], dtype=np.float64)
        centre = float(np.median(values))
        robust_scale = float(MAD_NORMAL_SCALE * np.median(np.abs(values - centre)))
        fallback_scale = float(np.std(values))
        mu[key] = float(np.mean(values))
        sigma[key] = max(fallback_scale, 0.01)
        median[key] = centre
        mad[key] = max(robust_scale, 0.01)
    return {
        "mu": mu,
        "sigma": sigma,
        "median": median,
        "mad": mad,
        "n": len(rows),
        "method": "mad",
    }


def build_reference_by_genre(
    features_list: Sequence[Mapping[str, Any]],
    genres: Sequence[str],
) -> dict[str, dict]:
    """Build one robust reference distribution per genre."""
    if len(features_list) != len(genres):
        raise ValueError("features_list and genres must have equal length")
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for features, genre in zip(features_list, genres):
        label = str(genre).strip()
        if not label:
            raise ValueError("genre labels must not be empty")
        grouped.setdefault(label, []).append(features)
    return {
        genre: build_robust_reference_stats(items)
        for genre, items in sorted(grouped.items())
    }


def select_reference_stats(
    default_reference: Mapping[str, Any],
    reference_by_genre: Mapping[str, Mapping[str, Any]] | None,
    genre: str | None,
) -> Mapping[str, Any]:
    """Select a genre reference, falling back to the default distribution."""
    if genre and reference_by_genre:
        exact = reference_by_genre.get(genre)
        if exact is not None:
            return exact
        folded = {name.casefold(): stats for name, stats in reference_by_genre.items()}
        match = folded.get(genre.casefold())
        if match is not None:
            return match
    return default_reference


def bootstrap_ci(
    values: Sequence[float],
    statistic: Callable[[np.ndarray], float] = np.mean,
    confidence: float = 0.95,
    n_resamples: int = 1000,
    seed: int | None = 0,
) -> tuple[float, float]:
    """Percentile bootstrap confidence interval for a one-dimensional sample."""
    sample = np.asarray(values, dtype=np.float64)
    if sample.ndim != 1 or sample.size == 0:
        raise ValueError("values must be a non-empty one-dimensional sequence")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between 0 and 1")
    if n_resamples < 1:
        raise ValueError("n_resamples must be positive")
    if sample.size == 1:
        value = float(statistic(sample))
        return value, value
    rng = np.random.default_rng(seed)
    estimates = np.empty(n_resamples, dtype=np.float64)
    for index in range(n_resamples):
        resample = rng.choice(sample, size=sample.size, replace=True)
        estimates[index] = float(statistic(resample))
    alpha = (1.0 - confidence) / 2.0
    low, high = np.quantile(estimates, [alpha, 1.0 - alpha])
    return float(low), float(high)
