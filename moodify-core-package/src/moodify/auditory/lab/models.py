"""Controlled auditory lab models (MFY-PHASE1-DEPTH-005).

The lab injects known technical perturbations and measures whether
Moodify detects, localizes, measures and evidences them correctly.
Ground truth derives from operator parameters by construction — never
from Moodify output.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

PERTURBATION_TYPES = {
    "HARD_CLIP", "NEAR_CLIP", "DC_OFFSET", "GAIN_STEP", "SILENCE_INSERT",
    "LOWPASS", "ANTIPHASE_REGION", "NOISE_INJECTION", "DYNAMIC_COMPRESSION",
}

EVENT_EXPECTATIONS = {
    "HARD_CLIP": "CLIPPING_CLUSTER",
    "NEAR_CLIP": "NEAR_CLIPPING_CLUSTER",
    "SILENCE_INSERT": "SILENCE_GAP",
    "ANTIPHASE_REGION": "NEGATIVE_CORRELATION_REGION",
    "GAIN_STEP": "LEVEL_SPIKE",  # positive step
    "LOWPASS": "HIGH_FREQUENCY_DROPOUT",
}


@dataclass(frozen=True)
class PerturbationSpec:
    operator: str
    version: str
    params: dict[str, float | str] = field(default_factory=dict)
    region_start_ms: int = 0
    region_end_ms: int = 0  # 0 = apply per operator semantics (whole file etc.)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PerturbationSpec":
        return cls(**data)


@dataclass(frozen=True)
class GroundTruth:
    source_id: str
    operator: str
    params: dict[str, float | str]
    expected_event_type: str | None
    expected_start_ms: int | None
    expected_end_ms: int | None
    expected_measurement_delta: dict[str, str] | None = None  # metric -> "up"|"down"|"same"
    allowed_secondary_event_types: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GroundTruth":
        data = dict(data)
        data["allowed_secondary_event_types"] = tuple(
            data.get("allowed_secondary_event_types", ())
        )
        return cls(**data)


@dataclass
class ExperimentResult:
    experiment_id: str
    source_id: str
    perturbation: PerturbationSpec
    ground_truth: GroundTruth
    detected_events: list[dict[str, Any]] = field(default_factory=list)
    measurement_delta: dict[str, float] = field(default_factory=dict)
    evidence_complete: bool = False
    failure_class: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "source_id": self.source_id,
            "perturbation": self.perturbation.to_dict(),
            "ground_truth": self.ground_truth.to_dict(),
            "detected_events": self.detected_events,
            "measurement_delta": self.measurement_delta,
            "evidence_complete": self.evidence_complete,
            "failure_class": self.failure_class,
        }
