"""Tests for mrs_surface — multi-dimension MRS quality surface."""
from moodify_runtime.mrs_surface import (
    compute_mrs_surface,
    MRSSurface,
    MRSDimension,
    _spectral_fidelity,
    _dynamic_preservation,
    _artifact_penalty_score,
)


class TestDimensionFunctions:
    def test_spectral_fidelity_perfect(self):
        s = _spectral_fidelity(-18.0, -18.0, 12.0, 12.0)
        assert s == 100.0

    def test_spectral_fidelity_diverged(self):
        s = _spectral_fidelity(-18.0, -9.0, 12.0, 6.0)
        assert s < 80.0

    def test_dynamic_preservation_perfect(self):
        s = _dynamic_preservation(30.0, 30.0)
        assert s == 100.0

    def test_dynamic_preservation_crushed(self):
        s = _dynamic_preservation(30.0, 10.0)
        assert s < 50.0

    def test_artifact_penalty_clean(self):
        s = _artifact_penalty_score("none", 0.0)
        assert s == 100.0

    def test_artifact_penalty_severe(self):
        s = _artifact_penalty_score("severe", 0.8)
        assert s < 30.0


class TestComputeMRSSurface:
    def test_full_surface(self):
        before = {"rms_db": -18.0, "crest_factor_db": 12.0, "dynamic_range_db": 30.0,
                   "lr_balance": 0.0, "eds": -18.0}
        after = {"rms_db": -16.0, "crest_factor_db": 11.0, "dynamic_range_db": 28.0,
                  "lr_balance": 0.05, "eds": -17.0}
        surface = compute_mrs_surface(
            sample_id="S1", genre="piano", preset="warm",
            before_metrics=before, after_metrics=after,
            over_dark_level="none", over_dark_score=0.0,
        )
        assert len(surface.dimensions) == 5
        assert surface.composite > 0.0
        assert surface.gate in ("ADOPT", "HOLD", "REJECT")
        assert surface.confidence >= 80.0

    def test_overdark_triggers_flags(self):
        before = {"rms_db": -18.0, "crest_factor_db": 12.0, "dynamic_range_db": 30.0,
                   "lr_balance": 0.0, "eds": -18.0}
        after = {"rms_db": -18.0, "crest_factor_db": 12.0, "dynamic_range_db": 30.0,
                  "lr_balance": 0.0, "eds": -18.0}
        surface = compute_mrs_surface(
            sample_id="S2", before_metrics=before, after_metrics=after,
            over_dark_level="severe", over_dark_score=0.9,
        )
        assert any("artifact_penalty" in f for f in surface.flags)

    def test_dimension_statuses(self):
        before = {"rms_db": -18.0, "crest_factor_db": 12.0, "dynamic_range_db": 30.0,
                   "lr_balance": 0.0, "eds": -18.0}
        after = {"rms_db": -18.0, "crest_factor_db": 12.0, "dynamic_range_db": 30.0,
                  "lr_balance": 0.0, "eds": -18.0}
        surface = compute_mrs_surface(
            before_metrics=before, after_metrics=after,
            over_dark_level="none", over_dark_score=0.0,
        )
        for d in surface.dimensions:
            assert d.status in ("ok", "warn", "fail")

    def test_to_dict(self):
        surface = compute_mrs_surface(sample_id="S1")
        d = surface.to_dict()
        assert d["sample_id"] == "S1"
        assert len(d["dimensions"]) == 5
        assert "composite" in d
