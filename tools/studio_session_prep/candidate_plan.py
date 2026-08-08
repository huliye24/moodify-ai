"""Candidate processing plan generation.

Generates 2–3 processing hypotheses (conservative, balanced, exploratory)
based on WSE profile metrics and explicit thresholds.

Plans are hypotheses, NOT decisions. No automatic execution or selection.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import TOOL_VERSION

PLAN_VERSION = "1.0.0"


@dataclass
class CandidatePlan:
    """A single candidate processing hypothesis."""

    plan_id: str  # e.g. "conservative", "balanced", "exploratory"
    plan_version: str = PLAN_VERSION
    tool_version: str = TOOL_VERSION
    strategy: str = ""
    preset: str = "clean_master"
    reasoning: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    risk: list[str] = field(default_factory=list)
    parameter_adjustments: dict[str, Any] = field(default_factory=dict)
    human_checkpoints: list[str] = field(default_factory=list)
    redline_failures: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "plan_version": self.plan_version,
            "tool_version": self.tool_version,
            "strategy": self.strategy,
            "preset": self.preset,
            "reasoning": self.reasoning,
            "evidence": self.evidence,
            "risk": self.risk,
            "parameter_adjustments": self.parameter_adjustments,
            "human_checkpoints": self.human_checkpoints,
            "redline_failures": self.redline_failures,
            "auto_execute": False,
            "auto_select": False,
            "human_review": "PENDING",
            "generated_at": self.generated_at,
        }


@dataclass
class CandidatePlanSet:
    """A set of 2-3 candidate plans for manual review."""

    plan_set_version: str = PLAN_VERSION
    tool_version: str = TOOL_VERSION
    source_sha256: str = ""
    source_path: str = ""
    plans: list[CandidatePlan] = field(default_factory=list)
    general_warnings: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_set_version": self.plan_set_version,
            "tool_version": self.tool_version,
            "source_sha256": self.source_sha256,
            "source_path": self.source_path,
            "plans": [p.to_dict() for p in self.plans],
            "general_warnings": self.general_warnings,
            "human_review_default": "PENDING",
            "auto_select_final": False,
            "auto_promote_rule": False,
            "disclaimer": (
                "These are processing hypotheses based on measured metrics. "
                "They do not represent claims of improvement, release quality, "
                "or superiority over human engineering. All plans require "
                "human review before execution."
            ),
            "generated_at": self.generated_at,
        }


def _pick_preset(profile: dict[str, Any]) -> str:
    """Simple rule-based preset suggestion from profile metrics."""
    spectral = profile.get("spectral", {})
    centroid = spectral.get("spectral_centroid_hz")
    level = profile.get("level", {})
    crest = level.get("crest_factor")
    stereo = profile.get("stereo", {})
    lr_corr = stereo.get("left_right_correlation")

    reasons = []

    # Check for dark spectrum → warm_vocal
    if centroid is not None and centroid < 800:
        reasons.append(("warm_vocal", "low spectral centroid — may benefit from presence enhancement"))

    # Check for narrow stereo → wide_space
    if lr_corr is not None and lr_corr > 0.9:
        reasons.append(("wide_space", "high L/R correlation — narrow stereo image"))

    # Check for high crest → clean_master
    if crest is not None and crest > 10:
        reasons.append(("clean_master", "high crest factor — transparent mastering may be appropriate"))

    if reasons:
        return reasons[0][0]

    return "clean_master"


def generate_candidate_plans(
    wse_profile_path: str,
    source_sha256: str = "",
) -> CandidatePlanSet:
    """Generate 2-3 candidate plans from a WSE profile JSON file.

    Thresholds are explicit and auditable. No ML or hidden heuristics.
    """
    with open(wse_profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    plan_set = CandidatePlanSet()
    plan_set.source_sha256 = source_sha256 or profile.get("source_sha256", "")
    plan_set.source_path = profile.get("source_path", "")
    plan_set.generated_at = datetime.now(timezone.utc).isoformat()

    spectral = profile.get("spectral", {})
    level = profile.get("level", {})
    loudness = profile.get("loudness", {})
    bands = profile.get("band_fractions", {})
    stereo = profile.get("stereo", {})

    centroid = spectral.get("spectral_centroid_hz")
    entropy = spectral.get("spectral_entropy")
    peak_db = level.get("peak_dbfs")
    rms_db = level.get("rms_db")
    crest = level.get("crest_factor")
    lufs = loudness.get("loudness_lufs")
    lr_corr = stereo.get("left_right_correlation")

    # ── Conservative Plan ──
    conservative = CandidatePlan(
        plan_id="conservative",
        strategy="Minimal intervention. Only correct clear technical issues (clipping, DC offset, extreme narrowness). "
                  "Preserve original character as much as possible.",
        preset="clean_master",
        reasoning=[
            "Conservative approach prioritizes source fidelity.",
            "Only applies processing when there is clear technical justification.",
        ],
        evidence=[],
        risk=[
            "May not address subtle spectral or dynamic issues.",
            "Client may expect more noticeable improvement.",
        ],
        human_checkpoints=[
            "Listen for any unintended changes in tonal balance.",
            "Verify loudness is not perceptually softer than source.",
            "Check mono fold-down still works (if stereo).",
        ],
    )

    # Evidence for conservative
    if peak_db is not None and peak_db > -0.3:
        conservative.evidence.append(f"Peak at {peak_db} dBFS — near clipping, conservative limiting advised.")
    if crest is not None and crest < 3:
        conservative.evidence.append(f"Low crest factor ({crest:.1f}) — already compressed, minimal processing.")
    if lufs is not None and lufs > -14:
        conservative.evidence.append(f"Integrated loudness {lufs:.1f} LUFS — already loud, no gain needed.")

    if not conservative.evidence:
        conservative.evidence.append("No clear technical issues detected. Conservative plan preserves source.")

    # ── Balanced Plan ──
    balanced = CandidatePlan(
        plan_id="balanced",
        strategy="Moderate enhancement of clarity, warmth, and stereo width where metrics suggest room for improvement.",
        preset=_pick_preset(profile),
        reasoning=[],
        evidence=[],
        risk=[
            "Moderate processing may introduce subtle coloration.",
            "Stereo widening may reduce mono compatibility.",
        ],
        human_checkpoints=[
            "A/B compare with loudness-matched original.",
            "Check for added harshness in presence band (2-8 kHz).",
            "Verify low end is not boomy or thin after processing.",
        ],
    )

    if centroid is not None:
        if centroid < 800:
            balanced.evidence.append(f"Low spectral centroid ({centroid:.0f} Hz) — may benefit from presence/air enhancement.")
            balanced.reasoning.append("Low spectral centroid suggests dark tonal balance; moderate high-end lift.")
        elif centroid > 3000:
            balanced.evidence.append(f"High spectral centroid ({centroid:.0f} Hz) — may be bright/thin; warm low-end enhancement.")
            balanced.reasoning.append("High spectral centroid suggests bright tonal balance; moderate low-end warmth.")

    if lr_corr is not None:
        if lr_corr > 0.9:
            balanced.evidence.append(f"High L/R correlation ({lr_corr:.2f}) — narrow image; moderate widening.")
            balanced.reasoning.append("Narrow stereo image; balanced widening with mono compatibility check.")
        elif lr_corr < 0.3:
            balanced.evidence.append(f"Low L/R correlation ({lr_corr:.2f}) — wide or out-of-phase; may need mid-side adjustment.")
            balanced.risk.append("Low L/R correlation — widening may cause phase issues on mono playback.")

    if crest is not None and crest > 8:
        balanced.evidence.append(f"High crest factor ({crest:.1f}) — dynamic, may benefit from gentle compression.")
        balanced.reasoning.append("High dynamic range; gentle compression for more consistent level.")

    if entropy is not None and entropy > 0.8:
        balanced.evidence.append(f"High spectral entropy ({entropy:.3f}) — rich but possibly noisy spectrum.")

    if not balanced.evidence:
        balanced.evidence.append("No strong metric signals. Balanced plan refines with clean_master preset.")

    bf_low = bands.get("band_20_250_fraction")
    bf_high = bands.get("band_8000_20000_fraction")

    if bf_low is not None and bf_low < 0.05:
        balanced.evidence.append(f"Low bass energy ({bf_low:.3f}) — may benefit from sub/bass enhancement.")

    if bf_high is not None and bf_high < 0.05:
        balanced.evidence.append(f"Low air energy ({bf_high:.3f}) — may benefit from high shelf.")

    # ── Exploratory Plan ──
    exploratory = CandidatePlan(
        plan_id="exploratory",
        strategy="More aggressive processing: wider soundstage, enhanced presence, dynamic shaping. "
                  "Higher risk of artifacts. Use only if conservative/balanced plans are insufficient.",
        preset="wide_space",
        reasoning=[
            "Exploratory approach trades safety for potential impact.",
            "Higher risk of artifacts, phase issues, or over-processing.",
        ],
        evidence=[],
        risk=[
            "HIGHER RISK: May introduce audible artifacts (pumping, harshness, phase smear).",
            "Stereo widening may collapse in mono.",
            "Dynamic processing may reduce punch or transient impact.",
            "Must be reviewed on multiple playback systems before delivery.",
        ],
        human_checkpoints=[
            "Critical: Check on mono playback (phone speaker).",
            "Check for pumping/breathing artifacts on quiet passages.",
            "Verify transients (drums, plucks) are not softened.",
            "Listen on small speakers + full-range monitors + headphones.",
            "Client must explicitly approve exploratory processing.",
        ],
    )

    exploratory.preset = "wide_space" if (lr_corr is not None and lr_corr > 0.7) else "warm_vocal"
    exploratory.evidence.append(
        "Exploratory plan always requires explicit human approval before execution. "
        "Risk profile is elevated compared to conservative/balanced plans."
    )

    # Set generated_at for all plans
    now = datetime.now(timezone.utc).isoformat()
    conservative.generated_at = now
    balanced.generated_at = now
    exploratory.generated_at = now

    plan_set.plans = [conservative, balanced, exploratory]
    plan_set.general_warnings = [
        "All plans are processing hypotheses. No automatic execution.",
        "LRA, true peak, phase, and masking metrics are unavailable — null values do not indicate safety.",
        "Spectral differences must not be interpreted as 'better sounding' without controlled listening.",
        "Human review is MANDATORY. Default status: PENDING.",
    ]

    return plan_set


def write_candidate_plans(plan_set: CandidatePlanSet, output_dir: Path) -> Path:
    """Write candidate plan set to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "candidate_plans.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan_set.to_dict(), f, ensure_ascii=False, indent=2)
    return path
