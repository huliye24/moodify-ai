"""Demo pipeline — orchestrates the engine into one closed loop.

    input file
        → engine.acoustic_analysis.analyze_track        (measure)
        → engine.acoustic_analysis.detect_issues        (diagnose)
        → engine.scoring_engine.score_quality           (MRS baseline score)
        → engine.scoring_engine.build_recommendations   (fix plan)
        → engine.music_understanding.build_commercial_insight
        → engine.report_schema.IntelligenceReport       (unified contract)

The pipeline module itself does zero math — it only composes engine calls,
so QA / Master / Rating can reuse exactly the same chain.
"""

from __future__ import annotations

from pathlib import Path

from engine.acoustic_analysis import AcousticProfile, analyze_track, detect_issues
from engine.music_understanding import build_commercial_insight
from engine.report_schema.schema import (
    AudioFeatures,
    CommercialInsight,
    IntelligenceReport,
    Issue,
    QualityScore,
    Recommendation,
    TrackInfo,
    validate_report_dict,
)
from engine.scoring_engine import (
    build_recommendations,
    score_quality,
)


def run_analysis(input_path: str | Path) -> IntelligenceReport:
    """Run the full demo loop for one audio file and return the report."""
    profile: AcousticProfile = analyze_track(input_path)

    issues_raw = detect_issues(profile)
    mrs = score_quality(profile)

    # Overall score: MRS technical baseline, softened by issue severities
    # (transparent, deterministic combination — documented in
    # docs/MOODIFY_DEMO_PIPELINE.md §2).
    penalty = {"high": 12, "medium": 5, "low": 1}
    overall = max(0, min(100, round(
        mrs["quality_score"] - sum(penalty[i["severity"]] for i in issues_raw)
    )))
    audio_quality = max(0, min(100, round(
        100 * (0.5 * _loudness_ok(profile) + 0.5 * _spectral_ok(profile))
        - 4 * sum(1 for i in issues_raw if i["severity"] == "high")
    )))
    dynamic_range = max(0, min(100, round(
        min(profile.dynamic_range_db / 12.0, 1.0) * 70
        + min(profile.crest_factor / 10.0, 1.0) * 30
    )))

    recommendations_raw = build_recommendations(issues_raw)
    insight_raw = build_commercial_insight(profile, overall, issues_raw)

    report = IntelligenceReport(
        track_info=TrackInfo(
            file_name=profile.file_name,
            file_path=profile.file_path,
            format=profile.format,
            duration_s=profile.duration_s,
            sample_rate=profile.sample_rate,
            channels=profile.channels,
        ),
        audio_features=AudioFeatures(
            loudness={
                "integrated_lufs": profile.integrated_lufs,
                "loudness_range_lu": profile.loudness_range_lu,
                "peak_db": profile.peak_db,
            },
            spectrum=dict(profile.spectrum),
            dynamics={
                "dynamic_range_db": profile.dynamic_range_db,
                "crest_factor": profile.crest_factor,
            },
            stereo={
                "correlation_lr": profile.correlation_lr,
                "width_rating": profile.stereo_width_rating,
            },
        ),
        quality_score=QualityScore(
            overall=overall,
            audio_quality=audio_quality,
            dynamic_range=dynamic_range,
            mrs=mrs,
        ),
        issues=[
            Issue(
                issue_id=i["id"],
                severity=i["severity"],
                title=i["title"],
                detail=i["detail"],
                evidence=i["evidence"],
            )
            for i in issues_raw
        ],
        recommendations=[
            Recommendation(
                action=r["action"],
                target=r["target"],
                rationale=r["rationale"],
                priority=r["priority"],
            )
            for r in recommendations_raw
        ],
        commercial_insight=CommercialInsight(
            summary=insight_raw["summary"],
            release_readiness=insight_raw["release_readiness"],
            strengths=insight_raw["strengths"],
            risks=insight_raw["risks"],
        ),
    )

    problems = validate_report_dict(report.to_dict())
    if problems:
        raise ValueError(f"generated report is invalid: {problems}")
    return report


def _loudness_ok(profile: AcousticProfile) -> float:
    if profile.integrated_lufs is None:
        return 0.5
    return 1.0 if abs(profile.integrated_lufs + 14.0) <= 2.0 else \
        max(0.0, 1.0 - abs(profile.integrated_lufs + 14.0) / 20.0)


def _spectral_ok(profile: AcousticProfile) -> float:
    from engine.scoring_engine.quality import build_features
    return build_features(profile).spectral
