import numpy as np

from moodify_bridge.metrics import comparison_metrics, left_right_correlation, level_metrics


def test_level_metrics_are_deterministic() -> None:
    result = level_metrics(np.array([1.0, -1.0, 1.0, -1.0]))
    assert result.values == {"peak": 1.0, "rms": 1.0, "crest_factor": 1.0}


def test_comparison_fitted_gain() -> None:
    reference = np.array([1.0, -2.0, 3.0])
    result = comparison_metrics(reference, reference * 0.5)
    assert result.values["fitted_scalar_gain"] == pytest.approx(0.5)
    assert result.values["relative_residual"] == pytest.approx(0.0)


def test_stereo_correlation() -> None:
    mono = np.array([1.0, -1.0, 0.5, -0.5])
    assert left_right_correlation(np.column_stack([mono, mono])).values["left_right_correlation"] == pytest.approx(1.0)


import pytest

