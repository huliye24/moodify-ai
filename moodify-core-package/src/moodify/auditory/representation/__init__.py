"""Multi-scale auditory representation (MFY-PHASE1-DEPTH-003)."""

from moodify.auditory.representation.build import build_representation
from moodify.auditory.representation.models import AuditoryRepresentation, ScalePlane
from moodify.auditory.representation.scales import SCALES, ScaleDef
from moodify.auditory.hearing_state import (
    HearingObservation,
    HearingState,
    ProviderProvenance,
    ProviderRun,
)
from moodify.auditory.net_gain import GainDimension, NetGainEvidence

__all__ = [
    "AuditoryRepresentation",
    "SCALES",
    "ScaleDef",
    "ScalePlane",
    "build_representation",
    "HearingObservation",
    "HearingState",
    "ProviderProvenance",
    "ProviderRun",
    "GainDimension",
    "NetGainEvidence",
]
