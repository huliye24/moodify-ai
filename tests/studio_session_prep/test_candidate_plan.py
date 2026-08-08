"""Tests for candidate plan generation — deterministic, threshold-based."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from tools.studio_session_prep.candidate_plan import (
    CandidatePlan,
    CandidatePlanSet,
    generate_candidate_plans,
    _pick_preset,
)


def _make_wse_profile_json(tmp_path: Path, **overrides) -> Path:
    """Create a minimal WSE profile JSON for testing."""
    data = {
        "profile_version": "1.0.0",
        "source_path": "/tmp/test.wav",
        "source_sha256": "a" * 64,
        "sample_rate": 48000,
        "channels": 2,
        "duration_s": 10.0,
        "level": {
            "peak_linear": 0.3,
            "rms_linear": 0.1,
            "crest_factor": 3.0,
            "peak_dbfs": -10.5,
            "rms_db": -20.0,
        },
        "loudness": {
            "loudness_lufs": -18.0,
            "lra_lu": None,
            "true_peak_dbtp": None,
        },
        "spectral": {
            "spectral_entropy": 0.6,
            "spectral_centroid_hz": 1500.0,
            "spectral_flux": 0.1,
        },
        "band_fractions": {
            "band_20_250_fraction": 0.1,
            "band_250_2000_fraction": 0.4,
            "band_2000_8000_fraction": 0.35,
            "band_8000_20000_fraction": 0.15,
        },
        "stereo": {
            "left_right_correlation": 0.6,
        },
        "unavailable": {},
        "warnings": [],
        "window_evolution": {
            "window_count": 10,
            "frame_size": 2048,
            "hop_size": 1024,
        },
    }
    data.update(overrides)
    path = tmp_path / "wse_profile.json"
    path.write_text(json.dumps(data, indent=2))
    return path


class TestCandidatePlanModel:
    def test_plan_has_required_fields(self):
        plan = CandidatePlan(plan_id="test")
        d = plan.to_dict()
        assert d["auto_execute"] is False
        assert d["auto_select"] is False
        assert d["human_review"] == "PENDING"

    def test_plan_no_auto_language(self):
        plan = CandidatePlan(
            plan_id="test",
            strategy="Test strategy",
            reasoning=["Test reason"],
            risk=["Test risk"],
        )
        d = plan.to_dict()
        text = json.dumps(d)
        assert "必然提升" not in text
        assert "发行级" not in text
        assert "超过人工" not in text

    def test_plan_set_disclaimer(self):
        ps = CandidatePlanSet()
        d = ps.to_dict()
        assert "auto_select_final" in d
        assert d["auto_select_final"] is False
        assert d["human_review_default"] == "PENDING"
        assert "disclaimer" in d


class TestGenerateCandidatePlans:
    def test_generates_three_plans(self, tmp_path):
        profile_path = _make_wse_profile_json(tmp_path)
        plan_set = generate_candidate_plans(str(profile_path))
        assert len(plan_set.plans) == 3
        ids = [p.plan_id for p in plan_set.plans]
        assert "conservative" in ids
        assert "balanced" in ids
        assert "exploratory" in ids

    def test_all_plans_human_review_pending(self, tmp_path):
        profile_path = _make_wse_profile_json(tmp_path)
        plan_set = generate_candidate_plans(str(profile_path))
        for plan in plan_set.plans:
            d = plan.to_dict()
            assert d["human_review"] == "PENDING"
            assert d["auto_execute"] is False
            assert d["auto_select"] is False

    def test_high_crest_triggers_compression(self, tmp_path):
        profile_path = _make_wse_profile_json(tmp_path, level={
            "peak_linear": 0.8, "rms_linear": 0.05, "crest_factor": 16.0,
            "peak_dbfs": -2.0, "rms_db": -26.0,
        })
        plan_set = generate_candidate_plans(str(profile_path))
        balanced = [p for p in plan_set.plans if p.plan_id == "balanced"][0]
        assert any("crest" in e.lower() or "dynamic" in e.lower() for e in balanced.evidence)

    def test_high_lr_correlation_widening(self, tmp_path):
        profile_path = _make_wse_profile_json(tmp_path, stereo={
            "left_right_correlation": 0.95,
        })
        plan_set = generate_candidate_plans(str(profile_path))
        balanced = [p for p in plan_set.plans if p.plan_id == "balanced"][0]
        assert any("narrow" in e.lower() or "widening" in e.lower() or "correlation" in e.lower()
                   for e in balanced.evidence)

    def test_low_lr_correlation_warning(self, tmp_path):
        profile_path = _make_wse_profile_json(tmp_path, stereo={
            "left_right_correlation": 0.1,
        })
        plan_set = generate_candidate_plans(str(profile_path))
        balanced = [p for p in plan_set.plans if p.plan_id == "balanced"][0]
        assert any("phase" in r.lower() or "mono" in r.lower() for r in balanced.risk)

    def test_low_centroid_presence_enhancement(self, tmp_path):
        profile_path = _make_wse_profile_json(tmp_path, spectral={
            "spectral_entropy": 0.5,
            "spectral_centroid_hz": 500.0,
            "spectral_flux": 0.1,
        })
        plan_set = generate_candidate_plans(str(profile_path))
        balanced = [p for p in plan_set.plans if p.plan_id == "balanced"][0]
        assert any("dark" in e.lower() or "centroid" in e.lower() or "presence" in e.lower()
                   for e in balanced.evidence)

    def test_near_clipping_evidence(self, tmp_path):
        profile_path = _make_wse_profile_json(tmp_path, level={
            "peak_linear": 0.98, "rms_linear": 0.3, "crest_factor": 3.3,
            "peak_dbfs": -0.2, "rms_db": -10.0,
        })
        plan_set = generate_candidate_plans(str(profile_path))
        conservative = [p for p in plan_set.plans if p.plan_id == "conservative"][0]
        assert any("clip" in e.lower() or "peak" in e.lower() for e in conservative.evidence)

    def test_exploratory_always_needs_approval(self, tmp_path):
        profile_path = _make_wse_profile_json(tmp_path)
        plan_set = generate_candidate_plans(str(profile_path))
        exploratory = [p for p in plan_set.plans if p.plan_id == "exploratory"][0]
        assert any("explicit" in c.lower() or "approval" in c.lower() for c in exploratory.human_checkpoints)

    def test_all_nulls_handled(self, tmp_path):
        """Profile with all null metrics should still generate plans without crash."""
        data = {
            "profile_version": "1.0.0",
            "source_path": "/tmp/null.wav",
            "source_sha256": "a" * 64,
            "sample_rate": 0,
            "channels": 0,
            "level": {"peak_linear": None, "rms_linear": None, "crest_factor": None},
            "loudness": {"loudness_lufs": None, "lra_lu": None, "true_peak_dbtp": None},
            "spectral": {"spectral_entropy": None, "spectral_centroid_hz": None, "spectral_flux": None},
            "band_fractions": {},
            "stereo": {"left_right_correlation": None},
            "unavailable": {},
            "warnings": ["all metrics null"],
        }
        path = tmp_path / "null_profile.json"
        path.write_text(json.dumps(data))
        plan_set = generate_candidate_plans(str(path))
        assert len(plan_set.plans) == 3  # still generates 3 plans
        for plan in plan_set.plans:
            d = plan.to_dict()
            assert d["human_review"] == "PENDING"
            assert d["auto_execute"] is False

    def test_preset_selection(self):
        # Low centroid → warm_vocal
        profile = {"spectral": {"spectral_centroid_hz": 500}, "stereo": {}, "level": {}}
        assert _pick_preset(profile) == "warm_vocal"

        # High L/R correlation → wide_space
        profile = {"spectral": {"spectral_centroid_hz": 2000}, "stereo": {"left_right_correlation": 0.95}, "level": {}}
        assert _pick_preset(profile) == "wide_space"

        # High crest → clean_master
        profile = {"spectral": {}, "stereo": {}, "level": {"crest_factor": 12}}
        assert _pick_preset(profile) == "clean_master"
