"""Controlled auditory laboratory (MFY-PHASE1-DEPTH-005)."""

from moodify.auditory.lab.evaluate import aggregate_matrix, evaluate_experiment
from moodify.auditory.lab.ground_truth import build_ground_truth
from moodify.auditory.lab.models import PerturbationSpec
from moodify.auditory.lab.perturbations import LADDERS, PERTURBATION_VERSION, apply_perturbation
from moodify.auditory.lab.runner import run_experiment
from moodify.auditory.lab.sources import SOURCE_SPECS, generate_source

__all__ = [
    "LADDERS",
    "PERTURBATION_VERSION",
    "PerturbationSpec",
    "SOURCE_SPECS",
    "aggregate_matrix",
    "apply_perturbation",
    "build_ground_truth",
    "evaluate_experiment",
    "generate_source",
    "run_experiment",
]
