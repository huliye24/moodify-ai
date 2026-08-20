"""Measure -> Classify -> Propose -> Render -> Verify -> Select or Bypass.

MFY_PRESERVE_IDENTITY_INTERVENTION_001: DeepSeek only produces *structured
candidate explanations*; it never decides arbitrary DSP values and never
approves listening quality. Machine gates select or bypass; identity
uncertainty escalates to HUMAN_REQUIRED / INCONCLUSIVE.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from moodify.intervention.identity_gate import IdentityGate
from moodify.intervention.primitives import (
    CLIP_MAX_REPAIR_SEGMENT,
    PRIMITIVES,
    InterventionPrimitive,
)

INTERVENTION_VERSION = "mfy-intervention-v1"


@dataclass(frozen=True)
class Measurements:
    """Structured measurement record (case_measurements evidence)."""

    primitive: str
    values: dict[str, float]


@dataclass(frozen=True)
class Limitation:
    """A classified limitation: type + severity + evidence pointer."""

    primitive_id: str
    severity: str  # NONE | LOW | MEDIUM
    evidence: dict[str, float]


@dataclass(frozen=True)
class Candidate:
    """Structured candidate explanation — never an arbitrary DSP value."""

    primitive_id: str
    version: str
    strength: dict[str, float]
    identity_risk: str
    rationale: str
    measurements: dict[str, float]


@dataclass(frozen=True)
class InterventionOutcome:
    decision: str  # SELECTED | BYPASSED | HUMAN_REQUIRED | INCONCLUSIVE
    candidate: Candidate | None = None
    verify: dict[str, float] | None = None
    identity: str | None = None
    reason: str = ""


@dataclass(frozen=True)
class PipelineResult:
    """One case's full pipeline trace (candidate_evidence evidence)."""

    case_id: str
    version: str
    measurements: list[Measurements]
    limitations: list[Limitation]
    proposals: list[Candidate]
    outcomes: list[InterventionOutcome]
    final_audio: np.ndarray
    input_shape: tuple[int, ...]
    sr: int
    all_bypassed: bool

    def summary(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "version": self.version,
            "decisions": [o.decision for o in self.outcomes],
            "all_bypassed": self.all_bypassed,
        }


def _measure(primitive: InterventionPrimitive, audio: np.ndarray, sr: int) -> Measurements:
    return Measurements(primitive=primitive.contract.primitive_id, values=primitive.detect(audio, sr))


def _classify(m: Measurements, primitive: InterventionPrimitive) -> Limitation:
    active = m.values.get("active", 0.0) > 0.0
    severity = "NONE" if not active else "LOW"
    if primitive.contract.identity_risk == "MEDIUM":
        severity = "MEDIUM" if active else "NONE"
    return Limitation(primitive_id=primitive.contract.primitive_id, severity=severity, evidence=m.values)


def _propose(limitation: Limitation, primitive: InterventionPrimitive) -> Candidate | None:
    """Structured explanation; strength is derived from measurements and clamped."""
    if limitation.severity == "NONE":
        return None
    if primitive.contract.primitive_id == "dc_offset_fix":
        strength: dict[str, float] = {"remove_dc": 1.0}
        rationale = "DC offset detected; removing constant offset (no gain change)"
    elif primitive.contract.primitive_id == "clip_peak_repair":
        n = int(limitation.evidence.get("clip_repairable", 0.0))
        strength = {"repair_segments": float(n), "max_segment": float(CLIP_MAX_REPAIR_SEGMENT)}
        rationale = f"{n} short clipped segment(s) detected; linear transition repair within max strength"
    elif primitive.contract.primitive_id == "tonal_balance_very_conservative":
        # Strength is derived from the detected share deficit and clamped to the
        # declared max; never arbitrary.
        from moodify.intervention.primitives import TONAL_MAX_SHELF_DB

        low_share_db = limitation.evidence.get("low_band_share_db", -300.0)
        high_share_db = limitation.evidence.get("high_band_share_db", -300.0)
        low_gain = float(np.clip((-46.0 - low_share_db) * 0.02, 0.0, TONAL_MAX_SHELF_DB))
        high_gain = float(np.clip((-46.0 - high_share_db) * 0.02, 0.0, TONAL_MAX_SHELF_DB))
        strength = {"low_gain_db": low_gain, "high_gain_db": high_gain}
        rationale = "band share deficit detected; conservative shelf correction clamped to ±0.5 dB"
    else:
        return None
    return Candidate(
        primitive_id=primitive.contract.primitive_id,
        version=primitive.contract.version,
        strength=strength,
        identity_risk=primitive.contract.identity_risk,
        rationale=rationale,
        measurements=limitation.evidence,
    )


def _verify(input_audio: np.ndarray, candidate_audio: np.ndarray, sr: int) -> dict[str, float]:
    """Objective safety gate: loudness match, no clipping, no NaN, shape/duration match."""
    verify: dict[str, float] = {}
    verify["shape_match"] = 1.0 if input_audio.shape == candidate_audio.shape else 0.0
    verify["duration_match_ms"] = abs(input_audio.shape[0] - candidate_audio.shape[0])
    if input_audio.shape != candidate_audio.shape:
        return verify
    rms_in = np.sqrt(np.mean(input_audio**2))
    rms_out = np.sqrt(np.mean(candidate_audio**2))
    verify["loudness_diff_db"] = round(
        float(20.0 * np.log10((rms_out + 1e-12) / (rms_in + 1e-12))), 4
    )
    verify["peak_abs"] = round(float(np.abs(candidate_audio).max()), 6)
    verify["clipped"] = float(np.abs(candidate_audio).max() >= 0.999)
    verify["has_nan"] = float(not np.isfinite(candidate_audio).all())
    verify["safe"] = float(
        abs(verify["loudness_diff_db"]) <= 0.5
        and verify["clipped"] == 0.0
        and verify["has_nan"] == 0.0
        and verify["shape_match"] == 1.0
        and verify["duration_match_ms"] == 0.0
    )
    return verify


def run_intervention_pipeline(
    audio: np.ndarray,
    sr: int,
    case_id: str,
    enabled_primitives: list[str] | None = None,
    force_pass_identity: bool = False,
) -> PipelineResult:
    """Full pipeline for one case. Returns processed audio and structured trace.

    force_pass_identity is for tests only (identity gate is validated separately).
    """
    if enabled_primitives is None:
        enabled_primitives = [p for p, pr in PRIMITIVES.items() if pr.contract.default_enabled]

    measurements: list[Measurements] = []
    limitations: list[Limitation] = []
    proposals: list[Candidate] = []
    outcomes: list[InterventionOutcome] = []

    work = audio.astype(np.float32) if audio.dtype != np.float32 else audio
    identity_gate = IdentityGate()

    # 1) Measure ALL limitations on the ORIGINAL input, independently. A
    # primitive's detector must see the pre-intervention signal (e.g. clipped
    # flat segments before any DC removal would pull them below the clip
    # level); serialised re-measurement would make detectors order-dependent.
    for pid in enabled_primitives:
        primitive = PRIMITIVES[pid]
        m = _measure(primitive, audio, sr)
        measurements.append(m)
        limitations.append(_classify(m, primitive))

    # 2) Fixed render order: clip repair first (needs the raw flat segments),
    # then DC removal, then tonal (off by default).
    render_order = ["clip_peak_repair", "dc_offset_fix", "tonal_balance_very_conservative"]
    for pid in (p for p in render_order if p in enabled_primitives):
        primitive = PRIMITIVES[pid]
        limitation = next(lim for lim in limitations if lim.primitive_id == pid)
        candidate = _propose(limitation, primitive)
        if candidate is None:
            outcomes.append(
                InterventionOutcome(decision="BYPASSED", reason=f"no {pid} limitation detected")
            )
            continue
        proposals.append(candidate)

        # Render candidate (pure function) on the current work.
        try:
            candidate_audio = primitive.apply(work, sr, candidate.strength)
        except ValueError as exc:
            outcomes.append(InterventionOutcome(decision="BYPASSED", reason=f"failure_state: {exc}"))
            continue

        verify = _verify(work, candidate_audio, sr)
        if verify["safe"] != 1.0:
            outcomes.append(
                InterventionOutcome(decision="BYPASSED", candidate=candidate, verify=verify,
                                    reason=f"objective safety failed: {verify}")
            )
            continue

        # Identity gate (machine check; never listening approval).
        if force_pass_identity:
            verdict = None
            identity_pass = True
        else:
            verdict = identity_gate.verify(work, candidate_audio, sr)
            identity_pass = verdict.passed
        if not identity_pass:
            outcomes.append(
                InterventionOutcome(decision="HUMAN_REQUIRED", candidate=candidate, verify=verify,
                                    identity=verdict.decision if verdict else None,
                                    reason="identity evidence conflicting; escalate, never guess")
            )
            continue

        work = candidate_audio
        outcomes.append(
            InterventionOutcome(decision="SELECTED", candidate=candidate, verify=verify,
                                identity=verdict.decision if verdict else "PASS")
        )

    # 3) Final safety gate: whole chain vs original input.
    final_verify = _verify(audio, work, sr)
    if final_verify["safe"] != 1.0:
        outcomes.append(
            InterventionOutcome(decision="INCONCLUSIVE", verify=final_verify,
                                reason=f"final chain objective safety failed: {final_verify}")
        )

    all_bypassed = all(o.decision == "BYPASSED" for o in outcomes)
    return PipelineResult(
        case_id=case_id,
        version=INTERVENTION_VERSION,
        measurements=measurements,
        limitations=limitations,
        proposals=proposals,
        outcomes=outcomes,
        final_audio=work,
        input_shape=audio.shape,
        sr=sr,
        all_bypassed=all_bypassed,
    )
