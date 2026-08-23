"""Commercial insight generation (engine-level, reused by Rating & demo).

Rule-based, evidence-cited commentary on commercial release readiness.
Deterministic: same measurements → same insight. No LLM, no fabrication.
"""

from __future__ import annotations

from typing import Any

from engine.acoustic_analysis.analyzer import AcousticProfile


def build_commercial_insight(
    profile: AcousticProfile,
    overall_score: int,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    """Produce the commercial_insight section of an Intelligence Report."""
    severities = [issue["severity"] for issue in issues]
    high_count = severities.count("high")

    strengths: list[str] = []
    risks: list[str] = []

    if profile.integrated_lufs is not None and abs(profile.integrated_lufs + 14.0) <= 2.0:
        strengths.append("Loudness already aligned with streaming normalization (-14 LUFS).")
    if profile.dynamic_range_db >= 8.0:
        strengths.append("Healthy dynamic contrast — preserves musical expression.")
    if profile.correlation_lr is not None and 0.2 <= profile.correlation_lr <= 0.85:
        strengths.append("Balanced stereo image with good mono compatibility.")
    if profile.peak_db <= -1.0:
        strengths.append("Sufficient true-peak headroom for lossy encoding.")

    if high_count >= 1:
        risks.append("Critical technical issues present — fix before distribution.")
    if profile.dynamic_range_db < 6.0:
        risks.append("Low dynamic range may read as fatiguing in playlist contexts.")
    if profile.peak_db > -0.3:
        risks.append("Near-zero sample peak — clipping risk on downstream codecs.")

    # Readiness verdict
    if overall_score >= 80 and high_count == 0:
        readiness = "ready"
        summary = (
            "This track is technically strong and close to commercial-release "
            "standard; only light mastering polish is advised."
        )
    elif overall_score >= 60:
        readiness = "needs_mastering"
        summary = (
            "This track has strong emotional potential but requires additional "
            "mastering optimization for commercial release."
        )
    else:
        readiness = "not_ready"
        summary = (
            "Significant technical problems must be resolved before this track "
            "is suitable for commercial distribution."
        )

    return {
        "summary": summary,
        "release_readiness": readiness,
        "strengths": strengths,
        "risks": risks,
    }
