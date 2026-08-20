"""Objective generator (MFY-CR-P04).

Pure function: P03 findings -> reconstruction objectives. Deterministic:
same findings produce the same objectives.

Rules:
- Only POSSIBLE_TECHNICAL_LIMITATION findings can generate an objective.
- HIGH confidence -> full A/B/C planning scope.
- MEDIUM confidence -> minimal/conservative only; C resolves to BYPASS.
- LOW confidence -> BYPASS (or HUMAN_REQUIRED when a finding is flagged).
- LIKELY_ARTISTIC_CHARACTER / INSUFFICIENT_EVIDENCE / NOT_APPLICABLE never
  grant processing authority.
"""

from __future__ import annotations

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    DiagnosticCategory,
    FindingStatus,
)
from moodify.reconstruction_objective.budget import InterventionBudget
from moodify.reconstruction_objective.objective import (
    NOISE_NOT_SUPPORTED,
    ObjectiveKind,
    ReconstructionObjective,
)

_CATEGORY_TO_KIND = {
    DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION: ObjectiveKind.BANDWIDTH_BALANCE,
    DiagnosticCategory.ED_02_PERSISTENT_NOISE: ObjectiveKind.NOISE_REDUCTION,
    DiagnosticCategory.ED_03_DYNAMIC_DAMAGE: ObjectiveKind.DYNAMIC_RECOVERY,
    DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION: ObjectiveKind.STEREO_STABILIZATION,
    DiagnosticCategory.ED_05_SPECTRAL_CONGESTION: ObjectiveKind.SPECTRAL_DECONGESTION,
    DiagnosticCategory.ED_06_TRANSFER_ENCODING_DEGRADATION: ObjectiveKind.TRANSFER_REPAIR,
}


def _deterministic_id(source_hash: str, finding_id: str) -> str:
    import hashlib

    blob = f"{source_hash}:{finding_id}".encode("utf-8")
    return f"obj_{hashlib.sha256(blob).hexdigest()[:16]}"


def build_objectives(
    findings: list[object],
    *,
    source_hash: str,
    production_case_id: str,
    budget: InterventionBudget | None = None,
) -> list[ReconstructionObjective]:
    """Deterministic objective construction from diagnostic findings."""
    budget = budget or InterventionBudget()
    out: list[ReconstructionObjective] = []

    for finding in findings:
        status = finding.status
        conf = finding.confidence
        if status != FindingStatus.POSSIBLE_TECHNICAL_LIMITATION:
            continue  # diagnosis != authorisation
        if conf is None:
            continue

        kind = _CATEGORY_TO_KIND.get(finding.category)
        if kind is None:
            continue

        # Honest capability downgrades (v0.1 engine limits)
        unsupported: str | None = None
        if kind == ObjectiveKind.BANDWIDTH_BALANCE:
            # engine performs balance only; the objective name already
            # reflects that (BANDWIDTH_BALANCE, never RECOVERY)
            pass
        if kind == ObjectiveKind.NOISE_REDUCTION:
            unsupported = NOISE_NOT_SUPPORTED  # no reliable denoise in v0.1 engine

        # Confidence gates planning scope
        if conf == ConfidenceLevel.LOW:
            continue  # default BYPASS; no aggressive processing on low evidence

        max_plan_intensity = {
            ConfidenceLevel.HIGH: 0.7,
            ConfidenceLevel.MEDIUM: 0.2,  # minimal/conservative only
        }[conf]
        requires_human = conf == ConfidenceLevel.MEDIUM or bool(finding.requires_human_review)

        out.append(
            ReconstructionObjective(
                objective_id=_deterministic_id(source_hash, finding.finding_id),
                kind=kind,
                production_case_id=production_case_id,
                source_hash=source_hash,
                diagnostic_finding_refs=(finding.finding_id,),
                target_conditions={
                    "category": finding.category.value,
                    "max_plan_intensity": max_plan_intensity,
                    "unsupported": unsupported or "none",
                },
                preserve_conditions={"no_new_clipping": True, "no_duration_change": True},
                parameter_budget=budget.to_dict(),
                confidence=conf.value,
                requires_human_review=requires_human,
                unsupported_reason=unsupported,
            )
        )

    return out
