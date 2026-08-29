"""ReconstructionObjective model (MFY-CR-P04)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum

OBJECTIVE_VERSION = "reconstruction-objective-v0.1"


class ObjectiveKind(str, Enum):
    BYPASS = "RO-00"
    BANDWIDTH_BALANCE = "RO-01"   # honestly downgraded from BANDWIDTH_RECOVERY: v0.1 engine cannot restore missing content
    NOISE_REDUCTION = "RO-02"     # may be INTERVENTION_NOT_SUPPORTED_V0_1 when no reliable denoise exists
    DYNAMIC_RECOVERY = "RO-03"
    STEREO_STABILIZATION = "RO-04"
    SPECTRAL_DECONGESTION = "RO-05"
    TRANSFER_REPAIR = "RO-06"


# BANDWIDTH_RECOVERY is the honest name only if the engine truly restores
# missing content; v0.1 engine performs balance work only, so the objective is
# always named BANDWIDTH_BALANCE.
HONEST_BANDWIDTH_NAME = "BANDWIDTH_BALANCE"

# When the current production engine has no reliable denoise, noise reduction
# reports DIAGNOSTIC_SUPPORTED / INTERVENTION_NOT_SUPPORTED_V0_1 instead of
# faking a repair with EQ.
NOISE_NOT_SUPPORTED = "INTERVENTION_NOT_SUPPORTED_V0_1"


def forbidden_changes() -> tuple[str, ...]:
    return (
        "no_duration_change",
        "no_new_clipping",
        "no_channel_count_change",
        "no_sample_rate_downgrade",
        "no_destructive_phase_change",
        "no_unbounded_loudness_increase",
        "no_vocal_replacement",
        "no_generated_instrumentation",
        "no_automatic_stem_remix",
    )


@dataclass(frozen=True)
class ReconstructionObjective:
    """One evidence-led objective for one diagnostic finding.

    Diagnostic findings grant planning authority only when they are
    POSSIBLE_TECHNICAL_LIMITATION with sufficient confidence; everything else
    resolves to BYPASS or HUMAN_REQUIRED.
    """

    objective_id: str
    kind: ObjectiveKind
    production_case_id: str
    source_hash: str
    diagnostic_finding_refs: tuple[str, ...]
    target_conditions: dict[str, object]
    preserve_conditions: dict[str, object]
    parameter_budget: dict[str, float]
    confidence: str  # LOW / MEDIUM / HIGH
    requires_human_review: bool = False
    unsupported_reason: str | None = None
    version: str = OBJECTIVE_VERSION
    created_at: str = ""

    def to_dict(self) -> dict[str, object]:
        d = asdict(self)
        d["kind"] = self.kind.value
        return d
