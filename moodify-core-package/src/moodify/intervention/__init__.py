"""Preserve-identity auditory intervention (MFY_PRESERVE_IDENTITY_INTERVENTION_001).

Bounded, versioned, bypassable intervention primitives for full-mix audio,
designed under the Auditory Intervention Laboratory discipline. Every
primitive declares scope, max strength, identity risk, failure state and
counterfactual evidence. The pipeline is
Measure -> Classify limitation -> Propose -> Render candidate ->
Verify -> Select or Bypass (HUMAN_REQUIRED on identity uncertainty).
"""

from moodify.intervention.identity_gate import IdentityGate, IdentityVerdict
from moodify.intervention.pipeline import (
    INTERVENTION_VERSION,
    Candidate,
    InterventionOutcome,
    Limitation,
    Measurements,
    PipelineResult,
    run_intervention_pipeline,
)
from moodify.intervention.primitives import (
    PRIMITIVES,
    InterventionPrimitive,
    apply_clip_peak_repair,
    apply_dc_offset_fix,
    apply_tonal_balance_conservative,
    detect_clip_segments,
    detect_dc_offset,
    detect_tonal_imbalance,
)
from moodify.intervention.registry import (
    build_registry,
    export_registry_json,
)

__all__ = [
    "INTERVENTION_VERSION",
    "PRIMITIVES",
    "Candidate",
    "IdentityGate",
    "IdentityVerdict",
    "InterventionOutcome",
    "InterventionPrimitive",
    "Limitation",
    "Measurements",
    "PipelineResult",
    "apply_clip_peak_repair",
    "apply_dc_offset_fix",
    "apply_tonal_balance_conservative",
    "build_registry",
    "detect_clip_segments",
    "detect_dc_offset",
    "detect_tonal_imbalance",
    "export_registry_json",
    "run_intervention_pipeline",
]
