"""Epistemic state vocabulary (DSK-MFY-CH02-PHASE1-001, Chapter II §17).

Moodify Ear distinguishes how a claim relates to evidence instead of
presenting plausible explanation as apparent fact:

- OBSERVED:  directly measured from the input (source format, metrics).
- INFERRED:  derived from measurements by a deterministic procedure.
- ASSOCIATED: statistical/co-occurrence relation, not causation.
- UNKNOWN:   unmeasured and cannot be inferred from available evidence.

A bounded machine-readable vocabulary: no other epistemic state may
appear in authoritative output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EPISTEMIC_STATES = frozenset({"OBSERVED", "INFERRED", "ASSOCIATED", "UNKNOWN"})


@dataclass(frozen=True)
class EpistemicState:
    state: str
    note: str = ""

    def __post_init__(self) -> None:
        if self.state not in EPISTEMIC_STATES:
            raise ValueError(f"unknown epistemic state: {self.state}")

    def to_dict(self) -> dict[str, Any]:
        return {"state": self.state, "note": self.note}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EpistemicState":
        return cls(state=data["state"], note=data.get("note", ""))
