"""Multi-scale auditory representation (MFY-PHASE1-DEPTH-003)."""

from moodify.auditory.representation.build import build_representation
from moodify.auditory.representation.models import AuditoryRepresentation, ScalePlane
from moodify.auditory.representation.scales import SCALES, ScaleDef

__all__ = [
    "AuditoryRepresentation",
    "SCALES",
    "ScaleDef",
    "ScalePlane",
    "build_representation",
]
