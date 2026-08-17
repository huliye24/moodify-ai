"""Reconstruction objective + golden pipeline (MFY-CR-P06, P04-absorbed).

P04 (Reconstruction Objective) was absent from the package sequence; P06
absorbs a minimal objective layer here so the golden run can proceed:

    Source -> Scan -> Era Diagnostic -> Objective (A/B/C) -> Render
      -> Hard Gates -> Identity Guard -> Technical Ranking -> Blind Listening

Everything is deterministic and versioned; SOURCE is always an eligible result.
"""

from __future__ import annotations

from moodify.reconstruction.blind import (
    BlindKit,
    finalize_blind_mapping,
    level_match,
    make_blind_kit,
)
from moodify.reconstruction.objective import (
    RECONSTRUCTION_OBJECTIVE_POLICY_V1,
    plan_from_findings,
)
from moodify.reconstruction.pipeline import run_golden_pipeline
from moodify.reconstruction.record import (
    GOLDEN_PENDING,
    GoldenReconstructionRecord,
)

__all__ = [
    "RECONSTRUCTION_OBJECTIVE_POLICY_V1",
    "GoldenReconstructionRecord",
    "GOLDEN_PENDING",
    "plan_from_findings",
    "run_golden_pipeline",
    "BlindKit",
    "make_blind_kit",
    "level_match",
    "finalize_blind_mapping",
]

RECONSTRUCTION_VERSION = "reconstruction-v0.1"
