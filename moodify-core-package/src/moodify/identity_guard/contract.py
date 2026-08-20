"""Identity Guard contract (MFY-CR-P05).

Identity is multi-dimensional protection, never a single score. This contract
defines the dimensions, guard states, per-dimension deltas and the overall
verdict. It is a derived result of existing Evidence/Comparison — it creates
no second Evidence authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

IDENTITY_GUARD_VERSION = "identity-guard-v0.1"


class GuardState(str, Enum):
    PASS = "PASS"
    CAUTION = "CAUTION"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"
    REJECT = "REJECT"
    NOT_MEASURABLE = "NOT_MEASURABLE"


class IdentityDimension(str, Enum):
    IG_01_VOCAL_MID = "IG-01"
    IG_02_DYNAMICS = "IG-02"
    IG_03_REVERB_SPACE = "IG-03"
    IG_04_STEREO = "IG-04"
    IG_05_LOW_END = "IG-05"
    IG_06_LOUDNESS_DENSITY = "IG-06"


DIMENSION_NAMES = {
    IdentityDimension.IG_01_VOCAL_MID: "Vocal / Mid-band Character",
    IdentityDimension.IG_02_DYNAMICS: "Transient / Dynamic Character",
    IdentityDimension.IG_03_REVERB_SPACE: "Reverb / Spatial Character",
    IdentityDimension.IG_04_STEREO: "Stereo Character",
    IdentityDimension.IG_05_LOW_END: "Low-end Character",
    IdentityDimension.IG_06_LOUDNESS_DENSITY: "Loudness / Density Character",
}

# PROXY vs MEASURABLE honesty: what can the current measurement chain really say?
DIMENSION_CAPABILITY = {
    IdentityDimension.IG_01_VOCAL_MID: "PROXY",          # stereo-level mid-band proxies only
    IdentityDimension.IG_02_DYNAMICS: "MEASURABLE",      # LRA / crest / PLR
    IdentityDimension.IG_03_REVERB_SPACE: "NOT_MEASURABLE",  # no validated decay/late-energy detector
    IdentityDimension.IG_04_STEREO: "MEASURABLE",        # correlation / width / mid-side
    IdentityDimension.IG_05_LOW_END: "MEASURABLE",       # band energy deltas
    IdentityDimension.IG_06_LOUDNESS_DENSITY: "MEASURABLE",  # LUFS / LRA / clipping
}


def dimension_name(dimension: IdentityDimension) -> str:
    return DIMENSION_NAMES[dimension]


@dataclass(frozen=True)
class IdentityDelta:
    """One dimension's source-vs-candidate delta for one candidate."""

    candidate_id: str
    source_id: str
    dimension: IdentityDimension
    guard_state: GuardState
    measurement_refs: tuple[str, ...] = ()
    source_value: float | None = None
    candidate_value: float | None = None
    normalized_delta: float | None = None
    threshold_version: str = IDENTITY_GUARD_VERSION
    confidence: str = "LOW"
    human_review_required: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_id": self.source_id,
            "dimension": self.dimension.value,
            "dimension_name": dimension_name(self.dimension),
            "capability": DIMENSION_CAPABILITY[self.dimension],
            "guard_state": self.guard_state.value,
            "measurement_refs": list(self.measurement_refs),
            "source_value": self.source_value,
            "candidate_value": self.candidate_value,
            "normalized_delta": self.normalized_delta,
            "threshold_version": self.threshold_version,
            "confidence": self.confidence,
            "human_review_required": self.human_review_required,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class IdentityVerdict:
    """Overall guard decision for one candidate (veto semantics, no averaging)."""

    candidate_id: str
    source_id: str
    state: GuardState
    deltas: tuple[IdentityDelta, ...] = ()
    version: str = IDENTITY_GUARD_VERSION
    human_review_question: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_id": self.source_id,
            "state": self.state.value,
            "deltas": [d.to_dict() for d in self.deltas],
            "version": self.version,
            "human_review_question": self.human_review_question,
        }
