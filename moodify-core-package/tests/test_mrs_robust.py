import numpy as np

from moodify.mrs_robust import (
    bootstrap_ci,
    build_reference_by_genre,
    build_robust_reference_stats,
    select_reference_stats,
)


def _feature(value):
    return {"spectrum": {"centroid_norm": float(value)}}


def test_mad_reference_is_less_sensitive_to_outlier_than_mean():
    clean = [_feature(value) for value in [0.40, 0.41, 0.42, 0.43, 0.44]]
    contaminated = clean + [_feature(10.0)]
    clean_stats = build_robust_reference_stats(clean)
    contaminated_stats = build_robust_reference_stats(contaminated)
    key = "spectrum__centroid_norm"
    mean_shift = abs(contaminated_stats["mu"][key] - clean_stats["mu"][key])
    median_shift = abs(contaminated_stats["median"][key] - clean_stats["median"][key])
    assert median_shift < mean_shift


def test_genre_references_are_isolated_and_case_insensitive():
    references = build_reference_by_genre(
        [_feature(0.2), _feature(0.3), _feature(0.8), _feature(0.9)],
        ["Classical", "Classical", "Electronic", "Electronic"],
    )
    fallback = build_robust_reference_stats([_feature(0.5)])
    selected = select_reference_stats(fallback, references, "electronic")
    assert selected["n"] == 2
    assert np.isclose(selected["median"]["spectrum__centroid_norm"], 0.85)
    assert select_reference_stats(fallback, references, "Jazz") is fallback


def test_bootstrap_ci_is_reproducible_and_contains_sample_mean():
    values = np.arange(1.0, 11.0)
    first = bootstrap_ci(values, n_resamples=500, seed=7)
    second = bootstrap_ci(values, n_resamples=500, seed=7)
    assert first == second
    assert first[0] < np.mean(values) < first[1]


def test_bootstrap_singleton_has_zero_width():
    assert bootstrap_ci([75.0]) == (75.0, 75.0)
