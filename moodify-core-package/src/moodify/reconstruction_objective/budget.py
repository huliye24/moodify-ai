"""Intervention budget (MFY-CR-P04).

Bounded per-objective budgets: many "small reasonable" changes must never
stack into a different song. Budgets are derived from confidence and source
severity; thresholds are conservative defaults from the current DSP engine
capabilities, validated by tests, not invented in a document.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

# Conservative v0.1 ceilings (validated by hard-gate tests)
MAX_EQ_GAIN_DB = 3.0
MAX_LOUDNESS_DELTA_DB = 0.5
MAX_PARAMETER_DISTANCE = 1.0
MAX_STEREO_WIDTH_DELTA = 0.2


@dataclass(frozen=True)
class InterventionBudget:
    eq_gain_db_max: float = MAX_EQ_GAIN_DB
    loudness_delta_db_max: float = MAX_LOUDNESS_DELTA_DB
    parameter_distance_max: float = MAX_PARAMETER_DISTANCE
    stereo_width_delta_max: float = MAX_STEREO_WIDTH_DELTA

    def to_dict(self) -> dict[str, float]:
        return asdict(self)
