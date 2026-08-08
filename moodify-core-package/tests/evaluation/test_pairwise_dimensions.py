"""Pairwise dimension comparison tests."""
from __future__ import annotations

from moodify.evaluation.pairwise.dimensions import compare_dimensions
from moodify.evaluation.pairwise.models import DimensionResult


def _metrics(**overrides):
    base = {
        "channels": {"value": 2},
        "duration": {"value": 6.0},
        "clipping_sample_ratio": {"value": 0.0},
        "near_clipping_sample_count": {"value": 0},
        "invalid_sample_count": {"value": 0},
        "finite_sample_ratio": {"value": 1.0},
        "silence_ratio": {"value": 0.0},
        "integrated_lufs": {"value": -14.0},
        "true_peak_dbfs": {"value": -1.0},
        "crest_factor_db": {"value": 10.0},
        "loudness_range_lu": {"value": 8.0},
        "spectral_flatness": {"value": 0.001},
        "estimated_high_frequency_cutoff_hz": {"value": 18000.0},
        "estimated_noise_floor_dbfs": {"value": -90.0},
        "sub_20_60_hz": {"value": 0.1}, "bass_60_120_hz": {"value": 0.1},
        "low_mid_120_250_hz": {"value": 0.1}, "mid_250_500_hz": {"value": 0.1},
        "core_mid_500_2000_hz": {"value": 0.1}, "presence_2000_5000_hz": {"value": 0.1},
        "brilliance_5000_10000_hz": {"value": 0.1}, "air_10000_16000_hz": {"value": 0.1},
        "stereo_correlation": {"value": 0.7},
        "negative_correlation_ratio": {"value": 0.0},
        "phase_risk_ratio": {"value": 0.0},
    }
    for key, value in overrides.items():
        if value is None:
            base.pop(key, None)
        else:
            base[key] = {"value": value}
    return base


def _by_dimension(results: list[DimensionResult]) -> dict[str, str]:
    return {r.dimension: r.relative_result for r in results}


def test_clipping_difference_drives_signal_integrity():
    clean = _metrics()
    clipped = _metrics(clipping_sample_ratio=0.02, near_clipping_sample_count=500,
                       true_peak_dbfs=0.0, crest_factor_db=5.0)
    results = _by_dimension(compare_dimensions(clean, clipped))
    assert results["signal_integrity"] == "A_BETTER"


def test_loudness_compares_distance_to_target():
    clean = _metrics()
    loud = _metrics(integrated_lufs=-8.0, true_peak_dbfs=0.0)
    results = _by_dimension(compare_dimensions(clean, loud))
    assert results["loudness"] == "A_BETTER"


def test_near_identical_candidates_tie():
    a = _metrics()
    b = _metrics()
    results = _by_dimension(compare_dimensions(a, b))
    assert all(v == "TIE" for v in results.values())


def test_mono_input_abstains_stereo():
    a = _metrics(channels=1)
    b = _metrics(channels=1)
    results = _by_dimension(compare_dimensions(a, b))
    assert results["stereo_phase"] == "INSUFFICIENT_EVIDENCE"


def test_missing_metrics_produce_insufficient_evidence():
    a = _metrics()
    b = _metrics()
    b.pop("integrated_lufs", None)
    b.pop("crest_factor_db", None)
    results = _by_dimension(compare_dimensions(a, b))
    assert results["loudness"] == "INSUFFICIENT_EVIDENCE"
