"""Reconstruction Objective v0.1 (MFY-CR-P04).

Evidence-led, source-specific, reversible reconstruction planning:
Diagnostic Findings -> Reconstruction Objective -> Candidate Plans A/B/C.
No diagnostic finding automatically grants permission to process. BYPASS is a
valid success outcome. Objectives reuse the ProductionCase / Evidence
authority — this package never defines a second authority.
"""

from moodify.reconstruction_objective.budget import InterventionBudget
from moodify.reconstruction_objective.candidates import (
    OBJECTIVE_PLAN_VERSION,
    generate_reconstruction_candidates,
)
from moodify.reconstruction_objective.generator import build_objectives
from moodify.reconstruction_objective.objective import (
    OBJECTIVE_VERSION,
    ObjectiveKind,
    ReconstructionObjective,
    forbidden_changes,
)

__all__ = [
    "OBJECTIVE_PLAN_VERSION",
    "OBJECTIVE_VERSION",
    "InterventionBudget",
    "ObjectiveKind",
    "ReconstructionObjective",
    "build_objectives",
    "forbidden_changes",
    "generate_reconstruction_candidates",
]
