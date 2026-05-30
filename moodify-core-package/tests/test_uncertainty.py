"""T0 基础设施模块测试 (SPEC-011 批次 0).

覆盖: UncertaintyResult, ConfidenceLevel, MeasurementRecord,
      ProcessorFingerprint, ConservationReport, audit_conservation,
      estimate_cr_eff, compute_icc
"""

import pytest
from moodify.uncertainty import UncertaintyResult, ConfidenceLevel
from moodify.protocol import MeasurementRecord, PROTOCOL_VERSION, STFT_CONFIG_STANDARD
from moodify.fingerprint import ProcessorFingerprint, estimate_cr_eff
from moodify.conservation import ConservationReport, audit_conservation
from moodify.icc import compute_icc


class TestUncertaintyResult:
    def test_from_bootstrap(self):
        samples = [1.0, 1.1, 0.9, 1.05, 0.95, 1.02, 0.98, 1.03, 0.97, 1.01]
        result = UncertaintyResult.from_bootstrap(samples)
        assert 0.9 < result.point_estimate < 1.1
        assert result.ci_lower is not None
        assert result.ci_upper is not None
        assert result.n_observations == 10
        assert result.method == "bootstrap"

    def test_from_rule_of_thumb(self):
        result = UncertaintyResult.from_rule_of_thumb(point=5.0, relative_uncertainty=0.1)
        assert result.point_estimate == 5.0
        assert result.standard_uncertainty == 0.5
        assert result.confidence_level == "low"
        assert result.method == "rule_of_thumb"

    def test_to_dict(self):
        u = UncertaintyResult(
            point_estimate=1.0, standard_uncertainty=0.1,
            ci_lower=0.8, ci_upper=1.2, n_observations=10,
        )
        d = u.to_dict()
        assert d["point_estimate"] == 1.0
        assert d["ci_95"] == [0.8, 1.2]
        assert d["n_observations"] == 10

    def test_str_representation(self):
        u = UncertaintyResult(
            point_estimate=3.14, standard_uncertainty=0.05,
            ci_lower=3.04, ci_upper=3.24,
        )
        s = str(u)
        assert "3.14" in s
        assert "±" in s


class TestConfidenceLevel:
    def test_high(self):
        level = ConfidenceLevel.classify(icc=0.8, relative_uncertainty=0.03)
        assert level == "high"

    def test_medium_icc(self):
        level = ConfidenceLevel.classify(icc=0.6, relative_uncertainty=0.03)
        assert level == "medium"

    def test_medium_uncertainty(self):
        level = ConfidenceLevel.classify(icc=0.8, relative_uncertainty=0.07)
        assert level == "medium"

    def test_low_no_icc(self):
        level = ConfidenceLevel.classify(icc=None, relative_uncertainty=0.15)
        assert level == "low"

    def test_low_both_fail(self):
        level = ConfidenceLevel.classify(icc=0.3, relative_uncertainty=0.20)
        assert level == "low"


class TestMeasurementRecord:
    def test_record_creation(self):
        rec = MeasurementRecord(parameter_name="D1_LRA", value=6.2, uncertainty=0.3)
        assert rec.protocol_version == PROTOCOL_VERSION
        assert rec.protocol_mode == "full"
        assert rec.stft_config == STFT_CONFIG_STANDARD
        assert rec.confidence_level == "medium"

    def test_fallback_flag(self):
        rec = MeasurementRecord(
            parameter_name="D1_LRA", value=6.0, uncertainty=0.5,
            is_fallback=True, fallback_note="pyloudnorm unavailable, used fallback"
        )
        assert rec.is_fallback is True
        assert "pyloudnorm" in rec.fallback_note

    def test_to_dict(self):
        rec = MeasurementRecord(parameter_name="S1_SubPresence", value=-12.0, uncertainty=0.5)
        d = rec.to_dict()
        assert d["parameter_name"] == "S1_SubPresence"
        assert d["value"] == -12.0
        assert d["protocol_version"] == PROTOCOL_VERSION


class TestConservation:
    def test_safe_conservation(self):
        report = audit_conservation(
            l_in=-14.0, l_out=-14.2,
            l_dynamics=-0.1, l_spectral=-0.1, sigma_noise=0.1,
        )
        assert report.energy_grade == "safe"
        assert abs(report.delta_e_residual) < 0.3

    def test_warning(self):
        report = audit_conservation(
            l_in=-14.0, l_out=-13.5,
            l_dynamics=0.0, l_spectral=0.0, sigma_noise=0.1,
        )
        assert report.energy_grade == "warning"
        assert report.warning_message != ""

    def test_violation_detected(self):
        report = audit_conservation(
            l_in=-14.0, l_out=-9.0,
            l_dynamics=0.0, l_spectral=0.0, sigma_noise=0.1,
        )
        assert report.energy_grade == "violation"
        assert "严重违反" in report.warning_message

    def test_to_dict(self):
        report = ConservationReport(delta_e_residual=-0.15, cm_energy=0.99)
        d = report.to_dict()
        assert d["delta_e_residual_db"] == -0.15
        assert d["cm_energy"] == 0.99


class TestCR_eff:
    def test_below_threshold(self):
        cr = estimate_cr_eff(nominal_ratio=4.0, threshold_db=-20.0, input_peak_dbfs=-30.0)
        assert cr == 1.0

    def test_above_threshold(self):
        cr = estimate_cr_eff(nominal_ratio=4.0, threshold_db=-20.0, input_peak_dbfs=-10.0)
        assert cr > 1.0

    def test_ratio_capped(self):
        cr = estimate_cr_eff(nominal_ratio=4.0, threshold_db=-20.0, input_peak_dbfs=10.0)
        assert cr <= 4.0


class TestICC:
    def test_perfect_agreement(self):
        ratings = [[5.0, 6.0, 7.0], [5.0, 6.0, 7.0]]
        result = compute_icc(ratings)
        assert result["icc"] > 0.99

    def test_no_agreement(self):
        ratings = [[1.0, 2.0, 3.0, 4.0], [4.0, 3.0, 2.0, 1.0]]
        result = compute_icc(ratings)
        assert result["icc"] < 0.0

    def test_low_sample(self):
        ratings = [[1.0], [2.0]]
        result = compute_icc(ratings)
        assert result["n_raters"] == 2
        assert result["n_targets"] == 1
        assert result["method"] == "anova_fallback"

    def test_moderate_agreement(self):
        ratings = [
            [3.0, 4.0, 5.0, 4.0, 3.0],
            [3.5, 4.5, 4.5, 3.5, 3.5],
            [2.5, 3.5, 5.5, 4.5, 2.5],
        ]
        result = compute_icc(ratings)
        assert -1.0 <= result["icc"] <= 1.0
        assert result["n_raters"] == 3
        assert result["n_targets"] == 5
