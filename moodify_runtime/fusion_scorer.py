"""Overprocessing and Artifact Fusion Scorer.

Unifies artifact detection, overprocessing assessment, and intent-loss
evaluation into one deterministic penalty surface. Explainable, no ML.
Part of ECHAIN-MOODIFY-MRS-EXTREME-017 / MHP-912.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ArtifactSignal:
    band: str
    severity: float  # 0-1
    cause: str = ""


@dataclass
class FusionScore:
    sample_id: str = ""
    preset: str = ""
    genre: str = ""

    artifact_penalty: float = 0.0
    overprocessing_penalty: float = 0.0
    intent_loss_penalty: float = 0.0
    composite_penalty: float = 0.0
    composite_quality: float = 100.0

    artifact_signals: list[ArtifactSignal] = field(default_factory=list)
    overprocessing_flags: list[str] = field(default_factory=list)
    intent_loss_flags: list[str] = field(default_factory=list)

    verdict: str = "PASS"
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "preset": self.preset,
            "genre": self.genre,
            "artifact_penalty": self.artifact_penalty,
            "overprocessing_penalty": self.overprocessing_penalty,
            "intent_loss_penalty": self.intent_loss_penalty,
            "composite_penalty": self.composite_penalty,
            "composite_quality": self.composite_quality,
            "artifact_signals": [asdict(s) for s in self.artifact_signals],
            "overprocessing_flags": self.overprocessing_flags,
            "intent_loss_flags": self.intent_loss_flags,
            "verdict": self.verdict,
            "explanation": self.explanation,
        }


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def compute_artifact_penalty(
    over_dark_level: str,
    over_dark_score: float,
    over_dark_bands: list[str],
    band_scores: dict[str, float] | None = None,
) -> tuple[float, list[ArtifactSignal]]:
    band_scores = band_scores or {}
    signals: list[ArtifactSignal] = []

    for band in over_dark_bands:
        sev = band_scores.get(band, 0.5)
        signals.append(ArtifactSignal(
            band=band,
            severity=round(min(sev, 1.0), 3),
            cause=f"over_dark_{band}",
        ))

    if over_dark_level == "severe":
        base = 40.0
    elif over_dark_level == "mild":
        base = 15.0
    else:
        base = 0.0

    score_boost = over_dark_score * 25.0
    penalty = _clamp(base + score_boost, 0.0, 100.0)
    return round(penalty, 1), signals


def compute_overprocessing_penalty(
    dr_before: float,
    dr_after: float,
    crest_before: float,
    crest_after: float,
    rms_before: float,
    rms_after: float,
    num_steps: int = 0,
) -> tuple[float, list[str]]:
    flags: list[str] = []
    penalty = 0.0

    # Dynamic range crush
    if dr_before > 0:
        dr_loss = (dr_before - dr_after) / dr_before
        if dr_loss > 0.5:
            penalty += 35.0
            flags.append(f"dr_crush:{dr_loss:.1%}")
        elif dr_loss > 0.25:
            penalty += 15.0
            flags.append(f"dr_reduced:{dr_loss:.1%}")

    # Crest factor flattening (transient loss)
    if crest_before > 0:
        crest_loss = (crest_before - crest_after) / crest_before
        if crest_loss > 0.3:
            penalty += 25.0
            flags.append(f"crest_flattened:{crest_loss:.1%}")

    # Excessive loudness gain
    if rms_before < 0:
        rms_gain = rms_after - rms_before
        if rms_gain > 8.0:
            penalty += 20.0
            flags.append(f"excessive_gain:{rms_gain:.1f}dB")

    # Step count penalty (more steps = more risk)
    if num_steps > 15:
        penalty += min(15.0, (num_steps - 15) * 1.5)
        flags.append(f"high_step_count:{num_steps}")

    return round(_clamp(penalty, 0.0, 100.0), 1), flags


def compute_intent_loss_penalty(
    eds_before: float,
    eds_after: float,
    emotion: str = "",
) -> tuple[float, list[str]]:
    flags: list[str] = []
    penalty = 0.0

    if abs(eds_before) > 0.1:
        eds_drift = abs(eds_after - eds_before) / abs(eds_before)
        if eds_drift > 0.5:
            penalty += 40.0
            flags.append(f"eds_large_drift:{eds_drift:.1%}")
        elif eds_drift > 0.25:
            penalty += 20.0
            flags.append(f"eds_moderate_drift:{eds_drift:.1%}")

    if emotion and eds_before != 0:
        sign_flip = (eds_before > 0) != (eds_after > 0) and abs(eds_before) > 1.0 and abs(eds_after) > 1.0
        if sign_flip:
            penalty += 30.0
            flags.append("emotion_sign_flip")

    return round(_clamp(penalty, 0.0, 100.0), 1), flags


def compute_fusion_score(
    sample_id: str = "",
    preset: str = "",
    genre: str = "",
    over_dark_level: str = "none",
    over_dark_score: float = 0.0,
    over_dark_bands: list[str] | None = None,
    band_scores: dict[str, float] | None = None,
    dr_before: float = 30.0,
    dr_after: float = 30.0,
    crest_before: float = 12.0,
    crest_after: float = 12.0,
    rms_before: float = -18.0,
    rms_after: float = -18.0,
    eds_before: float = -18.0,
    eds_after: float = -18.0,
    emotion: str = "",
    num_steps: int = 0,
) -> FusionScore:
    artifact_p, artifacts = compute_artifact_penalty(
        over_dark_level, over_dark_score,
        over_dark_bands or [], band_scores,
    )
    over_p, over_flags = compute_overprocessing_penalty(
        dr_before, dr_after, crest_before, crest_after,
        rms_before, rms_after, num_steps,
    )
    intent_p, intent_flags = compute_intent_loss_penalty(
        eds_before, eds_after, emotion,
    )

    weights = {"artifact": 0.35, "overprocessing": 0.35, "intent": 0.30}
    composite = round(
        artifact_p * weights["artifact"]
        + over_p * weights["overprocessing"]
        + intent_p * weights["intent"],
        1,
    )
    quality = round(100.0 - composite, 1)

    total_penalties = [artifact_p, over_p, intent_p]
    max_p = max(total_penalties)

    if composite < 15.0:
        verdict = "PASS"
    elif composite < 35.0:
        verdict = "REVIEW"
    else:
        verdict = "REJECT"

    all_flags = set(over_flags + intent_flags)
    explanation = _build_explanation(verdict, artifact_p, over_p, intent_p, composite)

    return FusionScore(
        sample_id=sample_id, preset=preset, genre=genre,
        artifact_penalty=artifact_p,
        overprocessing_penalty=over_p,
        intent_loss_penalty=intent_p,
        composite_penalty=composite,
        composite_quality=quality,
        artifact_signals=artifacts,
        overprocessing_flags=over_flags,
        intent_loss_flags=intent_flags,
        verdict=verdict,
        explanation=explanation,
    )


def _build_explanation(
    verdict: str,
    artifact_p: float,
    over_p: float,
    intent_p: float,
    composite: float,
) -> str:
    parts = []
    if artifact_p > 10:
        parts.append(f"artifact penalty {artifact_p:.0f}")
    if over_p > 10:
        parts.append(f"overprocessing penalty {over_p:.0f}")
    if intent_p > 10:
        parts.append(f"intent-loss penalty {intent_p:.0f}")
    if not parts:
        return "Clean: all penalty dimensions below threshold."
    return f"{verdict} (composite={composite:.0f}): " + "; ".join(parts) + "."


def format_fusion_report(fs: FusionScore) -> str:
    lines = [
        "# Fusion Score Report",
        "",
        f"**Sample**: {fs.sample_id} | **Preset**: {fs.preset} | **Genre**: {fs.genre}",
        f"**Verdict**: **{fs.verdict}** | **Quality**: {fs.composite_quality:.1f}",
        "",
        "## Penalty Breakdown",
        "",
        f"| Penalty | Score | Flags |",
        f"|---|---|---|",
        f"| Artifact | {fs.artifact_penalty:.1f} | {len(fs.artifact_signals)} signal(s) |",
        f"| Overprocessing | {fs.overprocessing_penalty:.1f} | {', '.join(fs.overprocessing_flags) if fs.overprocessing_flags else 'none'} |",
        f"| Intent Loss | {fs.intent_loss_penalty:.1f} | {', '.join(fs.intent_loss_flags) if fs.intent_loss_flags else 'none'} |",
        f"| **Composite** | **{fs.composite_penalty:.1f}** | Quality: {fs.composite_quality:.1f} |",
        "",
        fs.explanation,
    ]
    return "\n".join(lines)
