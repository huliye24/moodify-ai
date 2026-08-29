"""Requested-output planner for the Phase-I local execution graph."""

from __future__ import annotations

from enum import Enum


class ExecutionMode(str, Enum):
    MEASURE_ONLY = "MEASURE_ONLY"
    AUDITORY_REPORT = "AUDITORY_REPORT"
    CONTROLLED_LAB = "CONTROLLED_LAB"


_PLANS = {
    ExecutionMode.MEASURE_ONLY: (
        "source_identity", "decoded_audio", "global_measurements",
    ),
    ExecutionMode.AUDITORY_REPORT: (
        "source_identity", "decoded_audio", "global_measurements",
        "auditory_representation", "temporal_events", "judgment",
        "evidence_bundle", "report",
    ),
    ExecutionMode.CONTROLLED_LAB: (
        "control_source", "perturbation", "ground_truth", "decoded_audio",
        "global_measurements", "auditory_representation", "temporal_events",
        "evaluation", "evidence_bundle",
    ),
}


def build_plan(mode: ExecutionMode | str) -> tuple[str, ...]:
    return _PLANS[ExecutionMode(mode)]
