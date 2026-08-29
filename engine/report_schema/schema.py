"""Moodify Intelligence Report — unified schema (engine/report_schema).

Single source of truth for the report contract shared by every Moodify
product (QA, Master, Rating, Supply) and the demo pipeline.

Schema id: ``moodify.intelligence-report.v1``

Sections:
    track_info          — source track identity and container facts
    audio_features      — measured acoustic facts (loudness/spectrum/dynamics/stereo)
    quality_score       — engine scores (overall, audio quality, dynamics, MRS)
    issues              — detected problems with evidence
    recommendations     — actionable next steps
    commercial_insight  — release-readiness and asset-value commentary
    meta                — provenance (engine version, schema version, timestamp)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

SCHEMA_ID = "moodify.intelligence-report.v1"

REQUIRED_SECTIONS = (
    "track_info",
    "audio_features",
    "quality_score",
    "issues",
    "recommendations",
    "commercial_insight",
    "meta",
)

ENGINE_VERSION = "0.1.0"


# ── section builders ─────────────────────────────────────────


@dataclass
class TrackInfo:
    file_name: str
    file_path: str
    format: str
    duration_s: float
    sample_rate: int
    channels: int


@dataclass
class AudioFeatures:
    loudness: dict[str, Any]          # integrated_lufs, loudness_range_lu, peak_db, crest_factor
    spectrum: dict[str, float]        # sub, bass, low_mid, mid, presence, air (dB rel. total)
    dynamics: dict[str, float]        # dynamic_range_db, crest_factor
    stereo: dict[str, Any]            # correlation_lr, width_rating


@dataclass
class QualityScore:
    overall: int                      # 0-100
    audio_quality: int                # 0-100
    dynamic_range: int                # 0-100
    mrs: dict[str, Any]               # raw MRS result (method, contributions, ...)


@dataclass
class Issue:
    issue_id: str
    severity: str                     # "high" | "medium" | "low"
    title: str
    detail: str
    evidence: dict[str, Any]


@dataclass
class Recommendation:
    action: str
    target: str
    rationale: str
    priority: str                     # "high" | "medium" | "low"


@dataclass
class CommercialInsight:
    summary: str
    release_readiness: str            # "ready" | "needs_mastering" | "not_ready"
    strengths: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)


@dataclass
class IntelligenceReport:
    track_info: TrackInfo
    audio_features: AudioFeatures
    quality_score: QualityScore
    issues: list[Issue]
    recommendations: list[Recommendation]
    commercial_insight: CommercialInsight
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.meta:
            self.meta = {
                "schema_id": SCHEMA_ID,
                "engine_version": ENGINE_VERSION,
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }

    # ── serialization ────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_id": self.meta.get("schema_id", SCHEMA_ID),
            "meta": dict(self.meta),
            "track_info": {
                "file_name": self.track_info.file_name,
                "file_path": self.track_info.file_path,
                "format": self.track_info.format,
                "duration_s": round(self.track_info.duration_s, 1),
                "sample_rate": self.track_info.sample_rate,
                "channels": self.track_info.channels,
            },
            "audio_features": {
                "loudness": _round_tree(self.audio_features.loudness),
                "spectrum": _round_tree(self.audio_features.spectrum),
                "dynamics": _round_tree(self.audio_features.dynamics),
                "stereo": _round_tree(self.audio_features.stereo),
            },
            "quality_score": {
                "overall": self.quality_score.overall,
                "audio_quality": self.quality_score.audio_quality,
                "dynamic_range": self.quality_score.dynamic_range,
                "mrs": _round_tree(self.quality_score.mrs),
            },
            "issues": [
                {
                    "id": i.issue_id,
                    "severity": i.severity,
                    "title": i.title,
                    "detail": i.detail,
                    "evidence": _round_tree(i.evidence),
                }
                for i in self.issues
            ],
            "recommendations": [
                {
                    "action": r.action,
                    "target": r.target,
                    "rationale": r.rationale,
                    "priority": r.priority,
                }
                for r in self.recommendations
            ],
            "commercial_insight": {
                "summary": self.commercial_insight.summary,
                "release_readiness": self.commercial_insight.release_readiness,
                "strengths": list(self.commercial_insight.strengths),
                "risks": list(self.commercial_insight.risks),
            },
        }


def _round_tree(value: Any, digits: int = 2) -> Any:
    if isinstance(value, dict):
        return {k: _round_tree(v, digits) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_round_tree(v, digits) for v in value]
    if isinstance(value, float):
        return round(value, digits)
    return value


# ── validation ───────────────────────────────────────────────


def validate_report_dict(data: dict[str, Any]) -> list[str]:
    """Validate a serialized report. Returns a list of problems (empty = valid)."""
    problems: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in data:
            problems.append(f"missing section: {section}")
    if data.get("schema_id") != SCHEMA_ID:
        problems.append(f"schema_id must be {SCHEMA_ID!r}, got {data.get('schema_id')!r}")

    qs = data.get("quality_score", {})
    for key in ("overall", "audio_quality", "dynamic_range"):
        score = qs.get(key)
        if not isinstance(score, (int, float)) or not 0 <= score <= 100:
            problems.append(f"quality_score.{key} must be a number in [0, 100]")

    for idx, issue in enumerate(data.get("issues", [])):
        if issue.get("severity") not in ("high", "medium", "low"):
            problems.append(f"issues[{idx}].severity must be high|medium|low")

    readiness = data.get("commercial_insight", {}).get("release_readiness")
    if readiness not in ("ready", "needs_mastering", "not_ready"):
        problems.append("commercial_insight.release_readiness must be "
                        "ready|needs_mastering|not_ready")
    return problems
