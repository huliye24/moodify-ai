"""T8 B 矩阵非线性检验测试 (SPEC-011 批次 8)."""

import numpy as np


class TestBMatrixLinearity:
    def test_check_returns_dict(self):
        from moodify.optimizer.search import check_b_matrix_linearity
        actual = np.random.randn(10, 5) * 0.1
        predicted = actual + np.random.randn(10, 5) * 0.02
        result = check_b_matrix_linearity("GA", actual, predicted)
        assert isinstance(result, dict)
        assert "residual_mean" in result
        assert "linearity_warning" in result

    def test_perfect_linearity_no_warning(self):
        from moodify.optimizer.search import check_b_matrix_linearity
        actual = np.array([[0.1, 0.2, 0.3, 0.4, 0.5]] * 10)
        predicted = actual.copy()
        result = check_b_matrix_linearity("GA", actual, predicted)
        assert result["linearity_warning"] is False
        assert result["residual_std"] < 1e-6

    def test_large_residual_triggers_warning(self):
        from moodify.optimizer.search import check_b_matrix_linearity
        actual = np.array([[0.5, 0.5, 0.5, 0.5, 0.5]] * 10)
        predicted = np.array([[0.0, 0.0, 0.0, 0.0, 0.0]] * 10)
        result = check_b_matrix_linearity("GA", actual, predicted)
        assert result["linearity_warning"] is True

    def test_dim_residuals_length(self):
        from moodify.optimizer.search import check_b_matrix_linearity
        actual = np.random.randn(10, 5) * 0.1
        predicted = np.random.randn(10, 5) * 0.1
        result = check_b_matrix_linearity("GA", actual, predicted)
        assert len(result["dim_residuals"]) == 5

    def test_validate_returns_string(self):
        from moodify.optimizer.search import validate_b_matrix_health
        actual = np.random.randn(10, 5) * 0.3
        predicted = np.random.randn(10, 5) * 0.1
        msg = validate_b_matrix_health("GA", actual, predicted)
        assert isinstance(msg, str)
        assert len(msg) > 20
