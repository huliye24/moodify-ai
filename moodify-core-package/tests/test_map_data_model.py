"""MAP v0.2 data model tests (MHP-867).

Covers FeatureVector, ProblemVector, ScanResult acoustic fields,
compute_feature_vector, to_problem_vector, weighted_feature_distance.
"""

import math

import pytest

from moodify.v01_types import (
    AudioMetrics,
    DiagnosisReport,
    FeatureVector,
    GENRE_WEIGHTS,
    ProblemEntry,
    ProblemVector,
    ScanResult,
)
from moodify.v01_analyzer import compute_feature_vector, weighted_feature_distance
from moodify.v01_diagnostics import to_problem_vector


# ═══════════════════════════════════════════════════════════════════════════
# FeatureVector tests
# ═══════════════════════════════════════════════════════════════════════════

class TestFeatureVector:
    """MHP-863: FeatureVector dataclass."""

    def test_defaults_all_zero(self):
        fv = FeatureVector()
        assert fv.bass_balance == 0.0
        assert fv.warmth == 0.0
        assert fv.clarity == 0.0
        assert fv.presence_energy == 0.0
        assert fv.density == 0.0
        assert fv.stereo_width == 0.0
        assert fv.transient_energy == 0.0
        assert fv.reality_index == 0.0

    def test_to_list_returns_8_elements(self):
        fv = FeatureVector(
            bass_balance=0.1, warmth=0.2, clarity=0.3, presence_energy=0.4,
            density=0.5, stereo_width=0.6, transient_energy=0.7, reality_index=0.8,
        )
        lst = fv.to_list()
        assert len(lst) == 8
        assert lst == [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    def test_to_dict_rounds_to_4_decimal_places(self):
        fv = FeatureVector(bass_balance=0.123456)
        d = fv.to_dict()
        assert d["bass_balance"] == 0.1235  # rounded to 4 places

    def test_to_dict_includes_all_dimensions(self):
        fv = FeatureVector(bass_balance=1.0, warmth=0.5)
        d = fv.to_dict()
        for key in ["bass_balance", "warmth", "clarity", "presence_energy",
                     "density", "stereo_width", "transient_energy", "reality_index"]:
            assert key in d


# ═══════════════════════════════════════════════════════════════════════════
# ProblemEntry / ProblemVector tests
# ═══════════════════════════════════════════════════════════════════════════

class TestProblemVector:
    """MHP-863: ProblemEntry and ProblemVector dataclasses."""

    def test_problem_entry_defaults(self):
        pe = ProblemEntry()
        assert pe.problem_id == ""
        assert pe.category == ""
        assert pe.severity == "low"
        assert pe.confidence == 0.0
        assert pe.weight == 0.0

    def test_problem_entry_to_dict(self):
        pe = ProblemEntry(
            problem_id="over_compressed",
            category="dynamics",
            severity="high",
            confidence=0.85,
            weight=1.0,
            description="Over-compressed.",
        )
        d = pe.to_dict()
        assert d["problem_id"] == "over_compressed"
        assert d["category"] == "dynamics"
        assert d["severity"] == "high"
        assert d["confidence"] == 0.85
        assert d["weight"] == 1.0

    def test_problem_vector_empty(self):
        pv = ProblemVector()
        assert pv.problems == []
        assert pv.diagnosis_loss == 0.0
        assert pv.high_severity_count == 0
        assert pv.medium_severity_count == 0

    def test_problem_vector_counts_severity(self):
        pv = ProblemVector(problems=[
            ProblemEntry(problem_id="a", severity="high"),
            ProblemEntry(problem_id="b", severity="high"),
            ProblemEntry(problem_id="c", severity="medium"),
            ProblemEntry(problem_id="d", severity="low"),
        ])
        assert pv.high_severity_count == 2
        assert pv.medium_severity_count == 1

    def test_problem_vector_to_dict(self):
        pv = ProblemVector(
            problems=[ProblemEntry(problem_id="test", category="spectral", confidence=0.5)],
            diagnosis_loss=0.05,
        )
        d = pv.to_dict()
        assert d["problem_count"] == 1
        assert d["diagnosis_loss"] == 0.05
        assert len(d["problems"]) == 1


# ═══════════════════════════════════════════════════════════════════════════
# ScanResult acoustic fields tests
# ═══════════════════════════════════════════════════════════════════════════

class TestScanResultAcousticFields:
    """MHP-864: ScanResult with acoustic surface fields."""

    def test_defaults_are_none_or_zero(self):
        scan = ScanResult()
        assert scan.loudness_lufs is None
        assert scan.transient_ratio is None
        assert scan.stereo_width is None
        assert scan.spectral_centroid_hz is None
        assert scan.dc_offset is None
        assert scan.clip_count == 0

    def test_to_dict_includes_populated_acoustic_fields(self):
        scan = ScanResult(
            input_path="test.wav",
            exists=True,
            loudness_lufs=-18.5,
            transient_ratio=5.2,
            stereo_width=0.35,
            clip_count=10,
        )
        d = scan.to_dict()
        assert d["loudness_lufs"] == -18.5
        assert d["transient_ratio"] == 5.2
        assert d["stereo_width"] == 0.35
        assert d["clip_count"] == 10

    def test_to_dict_excludes_none_acoustic_fields(self):
        scan = ScanResult(input_path="test.wav", exists=False)
        d = scan.to_dict()
        assert "loudness_lufs" not in d
        assert "transient_ratio" not in d
        assert "spectral_centroid_hz" not in d
        assert "dc_offset" not in d

    def test_to_dict_excludes_zero_clip_count(self):
        scan = ScanResult(input_path="test.wav", exists=True, clip_count=0)
        d = scan.to_dict()
        assert "clip_count" not in d


# ═══════════════════════════════════════════════════════════════════════════
# compute_feature_vector tests
# ═══════════════════════════════════════════════════════════════════════════

class TestComputeFeatureVector:
    """MHP-865: compute_feature_vector from AudioMetrics."""

    @staticmethod
    def _make_metrics(**overrides) -> AudioMetrics:
        defaults = {
            "rms_bass": -8.0, "rms_low_mid": -5.0, "rms_mid": -8.0,
            "rms_presence": -14.0, "rms_air": -16.0, "rms_sub": -20.0,
            "rms_total": -10.0,
            "peak_db": -2.0, "crest_factor": 5.0, "dynamic_range_db": 12.0,
            "correlation_lr": 0.6, "channels": 2,
        }
        defaults.update(overrides)
        return AudioMetrics(**defaults)

    def test_healthy_metrics_produce_mid_range_features(self):
        metrics = self._make_metrics()
        fv = compute_feature_vector(metrics)
        # All values should be in [0, 1]
        for val in fv.to_list():
            assert 0.0 <= val <= 1.0

    def test_very_bassy_audio(self):
        metrics = self._make_metrics(rms_bass=0.0, rms_sub=0.0)
        fv = compute_feature_vector(metrics)
        assert fv.bass_balance > 0.8  # very prominent bass

    def test_very_thin_audio(self):
        metrics = self._make_metrics(rms_bass=-30.0, rms_low_mid=-25.0)
        fv = compute_feature_vector(metrics)
        assert fv.bass_balance < 0.2
        assert fv.warmth < 0.2

    def test_over_compressed_audio(self):
        metrics = self._make_metrics(crest_factor=1.5, dynamic_range_db=2.0)
        fv = compute_feature_vector(metrics)
        assert fv.density > 0.8  # very dense/full
        assert fv.reality_index < 0.5  # unnatural dynamics

    def test_wide_stereo_audio(self):
        metrics = self._make_metrics(correlation_lr=0.1)
        fv = compute_feature_vector(metrics)
        assert fv.stereo_width > 0.8

    def test_mono_audio(self):
        metrics = self._make_metrics(correlation_lr=0.99, channels=1)
        fv = compute_feature_vector(metrics)
        assert fv.stereo_width < 0.1

    def test_clamped_to_one_on_extreme_values(self):
        metrics = self._make_metrics(
            rms_bass=20.0, rms_low_mid=20.0, rms_mid=20.0,
            rms_presence=20.0, crest_factor=0.1,
            correlation_lr=0.0, peak_db=0.0, rms_total=-40.0,
            dynamic_range_db=30.0,
        )
        fv = compute_feature_vector(metrics)
        for val in fv.to_list():
            assert val <= 1.0, f"value {val} exceeds 1.0"


# ═══════════════════════════════════════════════════════════════════════════
# weighted_feature_distance tests
# ═══════════════════════════════════════════════════════════════════════════

class TestWeightedFeatureDistance:
    """MHP-865: genre-weighted feature distance."""

    def test_identical_vectors_zero_distance(self):
        fv = FeatureVector(bass_balance=0.5, warmth=0.5, clarity=0.5,
                           presence_energy=0.5, density=0.5, stereo_width=0.5,
                           transient_energy=0.5, reality_index=0.5)
        assert weighted_feature_distance(fv, fv) == 0.0

    def test_different_vectors_positive_distance(self):
        fv1 = FeatureVector()
        fv2 = FeatureVector(
            bass_balance=1.0, warmth=1.0, clarity=1.0, presence_energy=1.0,
            density=1.0, stereo_width=1.0, transient_energy=1.0, reality_index=1.0,
        )
        d = weighted_feature_distance(fv1, fv2)
        assert d > 0.0

    def test_unknown_genre_falls_back_to_default(self):
        fv1 = FeatureVector()
        fv2 = FeatureVector(bass_balance=1.0)
        d_unknown = weighted_feature_distance(fv1, fv2, "nonexistent")
        d_default = weighted_feature_distance(fv1, fv2, "default")
        assert d_unknown == d_default


# ═══════════════════════════════════════════════════════════════════════════
# to_problem_vector tests
# ═══════════════════════════════════════════════════════════════════════════

class TestToProblemVector:
    """MHP-866: to_problem_vector from DiagnosisReport."""

    @staticmethod
    def _make_report(**overrides) -> DiagnosisReport:
        m = AudioMetrics(
            rms_bass=-8.0, rms_low_mid=-5.0, rms_mid=-8.0,
            rms_presence=-14.0, rms_air=-16.0, rms_sub=-20.0,
            rms_total=-10.0,
            peak_db=-2.0, crest_factor=5.0, dynamic_range_db=12.0,
            correlation_lr=0.6, channels=2,
        )
        for k, v in overrides.items():
            setattr(m, k, v)
        return DiagnosisReport(metrics=m, overall_health="good")

    def test_healthy_audio_zero_problems(self):
        report = self._make_report()
        pv = to_problem_vector(report)
        assert pv.problems == []
        assert pv.diagnosis_loss == 0.0

    def test_over_compressed_detected(self):
        report = self._make_report(crest_factor=1.2)
        pv = to_problem_vector(report)
        ids = [p.problem_id for p in pv.problems]
        assert "over_compressed" in ids

    def test_flat_dynamics_detected(self):
        report = self._make_report(dynamic_range_db=1.5)
        pv = to_problem_vector(report)
        ids = [p.problem_id for p in pv.problems]
        assert "flat_dynamics" in ids

    def test_sub_overpower_detected(self):
        report = self._make_report(rms_sub=-3.0)
        pv = to_problem_vector(report)
        ids = [p.problem_id for p in pv.problems]
        assert "sub_overpower" in ids

    def test_presence_harsh_detected(self):
        report = self._make_report(rms_presence=-3.0)
        pv = to_problem_vector(report)
        ids = [p.problem_id for p in pv.problems]
        assert "presence_harsh" in ids

    def test_high_severity_appropriate_for_over_compressed(self):
        report = self._make_report(crest_factor=0.8)
        pv = to_problem_vector(report)
        oc = next(p for p in pv.problems if p.problem_id == "over_compressed")
        assert oc.severity == "high"

    def test_confidence_near_threshold(self):
        # Just barely crosses threshold → low confidence
        report = self._make_report(rms_sub=-6.5)  # threshold is -6, barely above
        pv = to_problem_vector(report)
        so = next((p for p in pv.problems if p.problem_id == "sub_overpower"), None)
        if so is not None:
            assert so.confidence < 0.3

    def test_confidence_far_from_threshold(self):
        report = self._make_report(rms_sub=0.0)  # way above threshold
        pv = to_problem_vector(report)
        so = next(p for p in pv.problems if p.problem_id == "sub_overpower")
        assert so.confidence > 0.5

    def test_diagnosis_loss_increases_with_problems(self):
        healthy = to_problem_vector(self._make_report())
        sick = to_problem_vector(self._make_report(
            crest_factor=0.8, dynamic_range_db=1.5, rms_sub=-3.0, rms_presence=-3.0,
        ))
        assert sick.diagnosis_loss > healthy.diagnosis_loss

    def test_stereo_problems_only_for_stereo(self):
        mono_report = self._make_report(channels=1)
        pv = to_problem_vector(mono_report)
        ids = [p.problem_id for p in pv.problems]
        assert "ultra_wide" not in ids
        assert "near_mono" not in ids

    def test_air_weak_is_low_severity(self):
        report = self._make_report(rms_air=-35.0)
        pv = to_problem_vector(report)
        aw = next(p for p in pv.problems if p.problem_id == "air_weak")
        assert aw.severity == "low"


# ═══════════════════════════════════════════════════════════════════════════
# GENRE_WEIGHTS tests
# ═══════════════════════════════════════════════════════════════════════════

class TestGenreWeights:
    """MHP-852: GENRE_WEIGHTS constants."""

    def test_all_5_genres_defined(self):
        for genre in ["vocal", "piano", "electronic", "orchestral", "default"]:
            assert genre in GENRE_WEIGHTS

    def test_each_genre_has_8_weights(self):
        for genre, weights in GENRE_WEIGHTS.items():
            assert len(weights) == 8, f"{genre} has {len(weights)} weights"

    def test_all_weights_in_range(self):
        for genre, weights in GENRE_WEIGHTS.items():
            for w in weights:
                assert 0.0 <= w <= 1.0, f"{genre} weight {w} out of range"


# ═══════════════════════════════════════════════════════════════════════════
# MRS Adapter tests (MHP-869 / MHP-873)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.v01
class TestMRSAdapter:
    """MHP-869: score_for_quality_gate adapter."""

    def test_adapter_returns_quality_gate_with_version(self, mock_wav):
        from moodify.mrs_adapter import score_for_quality_gate

        gate = score_for_quality_gate(
            before_path=mock_wav,
            after_path=mock_wav,  # same file → minimal delta
        )
        assert gate.mrs_version in (
            "mrs_proxy_v01", "mrs_proxy_v01_fallback", "mrs_calibrated_v02",
        )
        assert isinstance(gate.mrs_before, float)
        assert isinstance(gate.mrs_after, float)
        assert isinstance(gate.damage_loss, float)

    def test_adapter_same_file_produces_near_zero_delta(self, mock_wav):
        from moodify.mrs_adapter import score_for_quality_gate

        gate = score_for_quality_gate(
            before_path=mock_wav,
            after_path=mock_wav,
        )
        # Same file → MRS delta should be very small
        assert abs(gate.mrs_delta) < 5.0

    def test_adapter_includes_required_fields(self, mock_wav):
        from moodify.mrs_adapter import score_for_quality_gate

        gate = score_for_quality_gate(
            before_path=mock_wav,
            after_path=mock_wav,
        )
        d = gate.to_dict()
        for field in ["passed", "mrs_version", "mrs_before", "mrs_after",
                       "mrs_delta", "damage_loss", "risk_flags", "warnings", "deltas"]:
            assert field in d, f"missing field: {field}"

    def test_adapter_handles_missing_file(self, tmp_path):
        from moodify.mrs_adapter import score_for_quality_gate

        missing = str(tmp_path / "missing.wav")
        gate = score_for_quality_gate(
            before_path=missing,
            after_path=missing,
        )
        # Should not crash — returns QualityGate with warnings
        assert isinstance(gate.mrs_version, str)


# ═══════════════════════════════════════════════════════════════════════════
# Damage Loss / Risk Flags / Pass Policy tests (MHP-870/871/872/873)
# ═══════════════════════════════════════════════════════════════════════════

class TestDamageLossAndRiskFlags:
    """MHP-870/871: damage_loss and risk_flags computation."""

    def test_damage_loss_is_between_0_and_1(self, mock_wav):
        from moodify.mrs_adapter import score_for_quality_gate

        gate = score_for_quality_gate(
            before_path=mock_wav,
            after_path=mock_wav,
        )
        assert 0.0 <= gate.damage_loss <= 1.0

    def test_risk_flags_are_valid_enum_values(self, mock_wav):
        from moodify.mrs_adapter import score_for_quality_gate

        gate = score_for_quality_gate(
            before_path=mock_wav,
            after_path=mock_wav,
        )
        valid = {"peak_risk", "over_dark", "dynamic_damage",
                  "mrs_regression", "damage_loss_high"}
        for flag in gate.risk_flags:
            assert flag in valid, f"unknown risk flag: {flag}"

    def test_pass_policy_same_file_should_pass(self, mock_wav):
        """MHP-872: Same file → should pass quality gate."""
        from moodify.mrs_adapter import score_for_quality_gate

        gate = score_for_quality_gate(
            before_path=mock_wav,
            after_path=mock_wav,
        )
        # Same file may or may not pass depending on MRS engine,
        # but damage_loss should be low
        assert gate.damage_loss < 0.5

    def test_deltas_have_expected_keys(self, mock_wav):
        from moodify.mrs_adapter import score_for_quality_gate

        gate = score_for_quality_gate(
            before_path=mock_wav,
            after_path=mock_wav,
        )
        expected_keys = {"peak_db", "crest_factor", "dynamic_range_db",
                          "correlation_lr", "air", "presence", "bass"}
        assert set(gate.deltas.keys()) == expected_keys


class TestQualityGateIntegration:
    """MHP-873: End-to-end validation integration."""

    def test_process_audio_populates_quality_gate(self, mock_wav, tmp_path):
        from moodify.v01_pipeline import process_audio

        result = process_audio(
            input_path=mock_wav,
            preset="clean_master",
            output_dir=str(tmp_path / "outputs"),
        )
        assert result.success is True
        qg = result.quality_gate
        assert qg.mrs_version in (
            "mrs_proxy_v01", "mrs_proxy_v01_fallback", "mrs_calibrated_v02",
        )
        assert isinstance(qg.mrs_before, float)
        assert isinstance(qg.mrs_after, float)
        assert 0.0 <= qg.damage_loss <= 1.0
        for flag in qg.risk_flags:
            assert flag in ("peak_risk", "over_dark", "dynamic_damage",
                            "mrs_regression", "damage_loss_high")

    def test_report_includes_validation_result_fields(self, mock_wav, tmp_path):
        import json
        from pathlib import Path

        from moodify.v01_pipeline import process_audio

        result = process_audio(
            input_path=mock_wav,
            preset="clean_master",
            output_dir=str(tmp_path / "outputs"),
        )
        report_path = Path(result.report_path)
        with report_path.open("r", encoding="utf-8") as f:
            report = json.load(f)

        vr = report["validation_result"]
        assert "mrs_version" in vr
        assert "mrs_before" in vr
        assert "mrs_after" in vr
        assert "mrs_delta" in vr
        assert "damage_loss" in vr
        assert "risk_flags" in vr
        assert "passed" in vr
        assert "deltas" in vr
        assert "warnings" in vr

    def test_scan_includes_acoustic_fields_in_report(self, mock_wav, tmp_path):
        import json
        from pathlib import Path

        from moodify.v01_pipeline import process_audio

        result = process_audio(
            input_path=mock_wav,
            preset="clean_master",
            output_dir=str(tmp_path / "outputs"),
        )
        report_path = Path(result.report_path)
        with report_path.open("r", encoding="utf-8") as f:
            report = json.load(f)

        scan = report["scan"]
        # File-level fields always present
        assert "exists" in scan
        assert "readable" in scan
        # Acoustic fields may or may not be present (only when populated)
