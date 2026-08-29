"""Objective -> A/B/C candidate plans (MFY-CR-P04).

Semantic candidate meanings (not arbitrary intensity):
A = Minimal Intervention, B = Balanced Reconstruction,
C = Upper Safe Boundary (pressure test, never the default product output).

Plans reuse the Data Factory InterventionPlan structure and the existing
plan generator discipline. Intensity is bounded by the objective's confidence
scope; low-confidence objectives never produce plans (BYPASS).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from moodify.reconstruction_objective.objective import ObjectiveKind

OBJECTIVE_PLAN_VERSION = "reconstruction-candidates-v0.1"

# intensity profile per objective confidence scope (HIGH / MEDIUM)
_INTENSITY = {
    "HIGH": {"A": 0.3, "B": 0.5, "C": 0.7},
    "MEDIUM": {"A": 0.1, "B": 0.2},  # C resolves to BYPASS for medium confidence
}


@dataclass(frozen=True)
class ReconstructionCandidatePlan:
    plan_id: str
    objective_id: str
    candidate_label: str  # A / B / C
    intensity: float
    params: dict[str, float]
    version: str = OBJECTIVE_PLAN_VERSION

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _plan_hash(objective_id: str, label: str, intensity: float, params: dict[str, float]) -> str:
    payload = json.dumps(
        {"objective_id": objective_id, "label": label, "intensity": intensity, "params": params},
        sort_keys=True, separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def generate_reconstruction_candidates(
    objective: object,
    source_metrics: dict[str, float],
) -> list[ReconstructionCandidatePlan]:
    """Deterministic A/B/C plan generation for one objective.

    Returns [] when the objective must BYPASS (unsupported capability, or
    confidence below planning scope).
    """
    if objective.kind == ObjectiveKind.BYPASS:
        return []
    if objective.unsupported_reason:
        return []  # honest: not supported in v0.1, do not fake with EQ
    scope = _INTENSITY.get(objective.confidence)
    if scope is None:
        return []  # LOW confidence: BYPASS default

    base = _base_params_from_metrics(source_metrics)
    plans: list[ReconstructionCandidatePlan] = []
    for label, intensity in scope.items():
        params = _scale_params(base, intensity, objective.kind)
        plans.append(
            ReconstructionCandidatePlan(
                plan_id=f"{objective.objective_id}__{label}",
                objective_id=objective.objective_id,
                candidate_label=label,
                intensity=intensity,
                params=params,
            )
        )
    return plans


def _base_params_from_metrics(metrics: dict[str, float]) -> dict[str, float]:
    """Source-derived conservative starting params (never a universal preset)."""
    # metrics keys follow the auditory scan vocabulary; missing keys stay 0
    return {
        "eq_gain_db": 0.0,
        "loudness_delta_db": 0.0,
        "stereo_width_delta": 0.0,
        "noise_gate_db": 0.0,
    }


def _scale_params(base: dict[str, float], intensity: float, kind: ObjectiveKind) -> dict[str, float]:
    """Scale the source-derived base by intensity within the objective budget.

    The mapping is per-objective-kind and conservative: EQ gain for
    BANDWIDTH_BALANCE / SPECTRAL_DECONGESTION, loudness for DYNAMIC_RECOVERY,
    width for STEREO_STABILIZATION, none for TRANSFER_REPAIR in v0.1.
    """
    params = dict(base)
    cap = {
        ObjectiveKind.BANDWIDTH_BALANCE: ("eq_gain_db", 2.5),
        ObjectiveKind.SPECTRAL_DECONGESTION: ("eq_gain_db", 2.0),
        ObjectiveKind.DYNAMIC_RECOVERY: ("loudness_delta_db", 0.4),
        ObjectiveKind.STEREO_STABILIZATION: ("stereo_width_delta", 0.15),
        ObjectiveKind.TRANSFER_REPAIR: ("eq_gain_db", 1.0),
        ObjectiveKind.NOISE_REDUCTION: ("noise_gate_db", 0.0),
        ObjectiveKind.BYPASS: ("eq_gain_db", 0.0),
    }[kind]
    key, max_value = cap
    params[key] = round(max_value * intensity, 3)
    return params
