"""Evidence & uncertainty layer (MFY-PHASE1-DEPTH-004)."""

from moodify.auditory.evidence.bundle import build_bundle, logical_hash, save_bundle
from moodify.auditory.evidence.completeness import is_fail_closed, validate_completeness
from moodify.auditory.evidence.conflicts import detect_conflicts
from moodify.auditory.evidence.epistemic import EPISTEMIC_STATES, EpistemicState
from moodify.auditory.evidence.models import (
    Conflict,
    Coverage,
    EvidenceNode,
    JudgmentEvidence,
)
from moodify.auditory.evidence.resolver import assemble_judgment_evidence
from moodify.auditory.evidence.scale import EVIDENCE_SCALES, EvidenceScale, scale_for_duration_ms

__all__ = [
    "EPISTEMIC_STATES",
    "EVIDENCE_SCALES",
    "Conflict",
    "Coverage",
    "EpistemicState",
    "EvidenceNode",
    "EvidenceScale",
    "JudgmentEvidence",
    "assemble_judgment_evidence",
    "build_bundle",
    "detect_conflicts",
    "is_fail_closed",
    "logical_hash",
    "save_bundle",
    "scale_for_duration_ms",
    "validate_completeness",
]
