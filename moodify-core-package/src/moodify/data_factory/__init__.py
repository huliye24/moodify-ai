"""Moodify Phase-I auditory data factory.

This package orchestrates existing authoritative auditory and DSP components.
It must not become a second scan/judgment implementation.
"""

from .dataset_builder import aggregate_dataset, build_case_dataset
from .plan_generator import generate_abc_plans
from .runner import run_production_case

__all__ = [
    "aggregate_dataset",
    "build_case_dataset",
    "generate_abc_plans",
    "run_production_case",
]
