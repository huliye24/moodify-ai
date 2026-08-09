"""Canonical scale registry (MFY-PHASE1-DEPTH-003).

Exactly four scales. Window/hop values are versioned here with rationale;
no other module may invent window constants on the representation path.
All windows map to absolute source time through the sample clock.
"""

from __future__ import annotations

from dataclasses import dataclass

REPRESENTATION_VERSION = "rep-v1"


@dataclass(frozen=True)
class ScaleDef:
    scale_id: str
    name: str
    window_ms: int
    hop_ms: int
    rationale: str

    def __post_init__(self) -> None:
        # S3 TRACK is a whole-source window (window_ms == 0 sentinel).
        if self.scale_id == "S3":
            return
        if self.window_ms <= 0 or self.hop_ms <= 0 or self.hop_ms > self.window_ms:
            raise ValueError(f"invalid scale {self.scale_id}: window/hop")


SCALES: tuple[ScaleDef, ...] = (
    ScaleDef(
        "S0", "MICRO", 40, 20,
        "transient/clipping/near-clipping integrity at very local resolution",
    ),
    ScaleDef(
        "S1", "SHORT", 400, 100,
        "local level/stereo/spectral state; aligns with Phase I-B level & stereo hops",
    ),
    ScaleDef(
        "S2", "MEDIUM", 2000, 500,
        "sustained state/dropout/dynamic context; spectral summaries need stable windows",
    ),
    ScaleDef(
        "S3", "TRACK", 0, 0,
        "whole-source Phase I-A metrics; single global window",
    ),
)


def get_scale(scale_id: str) -> ScaleDef:
    for scale in SCALES:
        if scale.scale_id == scale_id:
            return scale
    raise ValueError(f"unknown scale: {scale_id}")
