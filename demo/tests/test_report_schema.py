"""Tests for the unified Intelligence Report schema."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.report_schema.schema import (  # noqa: E402
    SCHEMA_ID,
    AudioFeatures,
    CommercialInsight,
    IntelligenceReport,
    Issue,
    QualityScore,
    Recommendation,
    TrackInfo,
    validate_report_dict,
)


def _report() -> IntelligenceReport:
    return IntelligenceReport(
        track_info=TrackInfo(
            file_name="test.mp3", file_path="/tmp/test.mp3", format="mp3",
            duration_s=60.0, sample_rate=48000, channels=2,
        ),
        audio_features=AudioFeatures(
            loudness={"integrated_lufs": -14.0, "loudness_range_lu": 8.0, "peak_db": -1.2},
            spectrum={"sub": -20.0, "bass": -6.0, "low_mid": -10.0,
                      "mid": -12.0, "presence": -15.0, "air": -22.0},
            dynamics={"dynamic_range_db": 9.5, "crest_factor": 8.2},
            stereo={"correlation_lr": 0.55, "width_rating": "balanced"},
        ),
        quality_score=QualityScore(
            overall=82, audio_quality=85, dynamic_range=78,
            mrs={"quality_score": 82.0, "technical_score": 82.0,
                 "listening_score": None, "method": "test",
                 "feature_contributions": {}},
        ),
        issues=[Issue("low_dynamic_contrast", "medium", "Low dynamic contrast",
                      "detail", {"dynamic_range_db": 5.0})],
        recommendations=[Recommendation("Relax bus compression", "master bus",
                                        "rationale", "high")],
        commercial_insight=CommercialInsight(
            summary="Test summary.",
            release_readiness="needs_mastering",
            strengths=["ok"], risks=["risk"],
        ),
    )


def test_roundtrip_serialization():
    report = _report()
    data = report.to_dict()
    assert data["schema_id"] == SCHEMA_ID
    assert data["quality_score"]["overall"] == 82
    assert data["issues"][0]["id"] == "low_dynamic_contrast"
    assert data["recommendations"][0]["action"] == "Relax bus compression"


def test_valid_report_passes_validation():
    problems = validate_report_dict(_report().to_dict())
    assert problems == []


def test_missing_section_fails():
    data = _report().to_dict()
    del data["issues"]
    problems = validate_report_dict(data)
    assert any("issues" in p for p in problems)


def test_score_out_of_range_fails():
    data = _report().to_dict()
    data["quality_score"]["overall"] = 150
    problems = validate_report_dict(data)
    assert any("overall" in p for p in problems)


def test_bad_severity_fails():
    data = _report().to_dict()
    data["issues"][0]["severity"] = "extreme"
    problems = validate_report_dict(data)
    assert problems


def test_meta_autofilled():
    report = _report()
    assert report.meta["schema_id"] == SCHEMA_ID
    assert report.meta["engine_version"]
    assert report.meta["generated_at"]
