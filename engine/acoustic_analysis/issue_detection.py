"""Transparent rule-based issue detection on an AcousticProfile.

Part of the engine (shared by QA / Master / Rating / demo). Rules are
explicit thresholds on measured facts — no hidden model, no magic.
Each rule cites the evidence it used, so reports stay auditable
(AGENTS.md: judgment must be scoped and evidence-backed).
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from engine.acoustic_analysis.analyzer import AcousticProfile

# Reference loudness target: streaming normalization (Spotify/YouTube ~ -14 LUFS).
STREAMING_TARGET_LUFS = -14.0
LOUDNESS_TOLERANCE_LU = 2.0


def detect_issues(profile: AcousticProfile) -> list[dict[str, Any]]:
    """Return a list of engine issue records for one profile."""
    issues: list[dict[str, Any]] = []
    spec = profile.spectrum

    # 1. High-frequency harshness: presence band dominating the mid band.
    if spec.get("presence", -99) - spec.get("mid", -99) > 2.0:
        issues.append(_issue(
            "high_frequency_harshness", "medium",
            "High frequency harshness detected",
            "The 2–5 kHz presence band sits above the mid band by more than "
            "2 dB, which commonly reads as harsh or fatiguing on commercial "
            "playback systems.",
            {"presence_db": spec.get("presence"), "mid_db": spec.get("mid"),
             "delta_db": round(spec.get("presence", 0) - spec.get("mid", 0), 1)},
        ))

    # 2. Low dynamic contrast: short-window dynamic range below 6 dB.
    if profile.dynamic_range_db < 6.0:
        issues.append(_issue(
            "low_dynamic_contrast", "high" if profile.dynamic_range_db < 3.0 else "medium",
            "Low dynamic contrast",
            f"P95–P05 short-window RMS spread is {profile.dynamic_range_db:.1f} dB. "
            "Tracks below ~6 dB tend to sound flat and over-compressed.",
            {"dynamic_range_db": profile.dynamic_range_db},
        ))

    # 3. Possible over-compression: low crest factor + low dynamic range.
    if profile.crest_factor < 4.0 and profile.dynamic_range_db < 6.0:
        issues.append(_issue(
            "possible_over_compression", "high",
            "Possible over-compression",
            f"Crest factor is {profile.crest_factor:.2f} with only "
            f"{profile.dynamic_range_db:.1f} dB of dynamic spread — a signature "
            "of heavy bus compression / limiting.",
            {"crest_factor": profile.crest_factor,
             "dynamic_range_db": profile.dynamic_range_db},
        ))

    # 4. Clipping risk: sample peak near 0 dBFS.
    if profile.peak_db > -0.3:
        issues.append(_issue(
            "clipping_risk", "high",
            "Digital clipping risk",
            f"Sample peak reaches {profile.peak_db:.1f} dBFS; decoded MP3 or "
            "lossy conversions may clip above 0 dBFS.",
            {"peak_db": profile.peak_db},
        ))

    # 5. Loudness off streaming target.
    if profile.integrated_lufs is not None:
        deviation = profile.integrated_lufs - STREAMING_TARGET_LUFS
        if abs(deviation) > LOUDNESS_TOLERANCE_LU:
            direction = "quieter" if deviation < 0 else "louder"
            issues.append(_issue(
                "loudness_off_target", "low",
                f"Loudness {abs(deviation):.1f} LU {direction} than streaming target",
                f"Integrated loudness is {profile.integrated_lufs} LUFS vs the "
                f"-14 LUFS streaming normalization target "
                f"(deviation {deviation:+.1f} LU).",
                {"integrated_lufs": profile.integrated_lufs,
                 "target_lufs": STREAMING_TARGET_LUFS,
                 "deviation_lu": round(deviation, 1)},
            ))

    # 6. Thin low end: sub/bass energy far below mid energy.
    if spec.get("bass", -99) - spec.get("mid", -99) < -18.0:
        issues.append(_issue(
            "thin_low_end", "medium",
            "Thin low end",
            "Bass band energy is more than 18 dB below the mid band; the "
            "track may lack weight on full-range systems.",
            {"bass_db": spec.get("bass"), "mid_db": spec.get("mid")},
        ))

    # 7. Narrow stereo image.
    if profile.correlation_lr is not None and profile.correlation_lr > 0.95:
        issues.append(_issue(
            "narrow_stereo_image", "low",
            "Narrow stereo image",
            f"L/R correlation is {profile.correlation_lr:.2f}; the stereo "
            "image is nearly mono.",
            {"correlation_lr": profile.correlation_lr},
        ))

    return issues


def _issue(issue_id: str, severity: str, title: str, detail: str,
           evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": issue_id,
        "severity": severity,
        "title": title,
        "detail": detail,
        "evidence": evidence,
    }
