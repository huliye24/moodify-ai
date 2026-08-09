"""Evidence & uncertainty layer (MFY-PHASE1-DEPTH-004)."""

from moodify.auditory.evidence.bundle import build_bundle, logical_hash, save_bundle
from moodify.auditory.evidence.completeness import is_fail_closed, validate_completeness
from moodify.auditory.evidence.conflicts import detect_conflicts
from moodify.auditory.evidence.models import (
    Conflict,
    Coverage,
    EvidenceNode,
    JudgmentEvidence,
)
from moodify.auditory.evidence.resolver import assemble_judgment_evidence

__all__ = [
    "Conflict",
    "Coverage",
    "EvidenceNode",
    "JudgmentEvidence",
    "assemble_judgment_evidence",
    "build_bundle",
    "detect_conflicts",
    "is_fail_closed",
    "logical_hash",
    "save_bundle",
    "validate_completeness",
]
