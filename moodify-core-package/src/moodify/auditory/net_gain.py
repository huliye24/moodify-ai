"""Uncalibrated net-gain evidence envelope for Judge After.

The model comes from Emotional Wave Engineering PRINCIPLE-001/MATH-001,
but intentionally does not collapse dimensions into a score.  Parameters and
weights in those research documents remain M0/M1 and have not been calibrated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


DimensionState = Literal["IMPROVED", "UNCHANGED", "DEGRADED", "NOT_MEASURED", "INCONCLUSIVE"]


@dataclass(frozen=True)
class GainDimension:
    name: Literal[
        "TARGET_GAIN",
        "IDENTITY_PRESERVATION",
        "NEW_ARTIFACT_RISK",
        "LOUDNESS_BIAS",
        "OPERATION_COST",
        "REPRODUCIBILITY",
        "HUMAN_PREFERENCE",
    ]
    state: DimensionState
    evidence_refs: tuple[str, ...] = ()
    value: float | None = None
    unit: str | None = None
    calibration_status: Literal["CALIBRATED", "UNCALIBRATED", "NOT_APPLICABLE"] = "UNCALIBRATED"
    notes: str = ""

    def __post_init__(self) -> None:
        if self.state == "NOT_MEASURED" and self.value is not None:
            raise ValueError("NOT_MEASURED dimension cannot carry a value")
        if self.state not in {"NOT_MEASURED", "INCONCLUSIVE"} and not self.evidence_refs:
            raise ValueError("evaluated dimension requires evidence_refs")


@dataclass(frozen=True)
class NetGainEvidence:
    """Component ledger; never an automatic aesthetic verdict or scalar score."""

    schema_version: str
    source_sha256: str
    candidate_sha256: str
    loudness_matched: bool
    dimensions: tuple[GainDimension, ...]
    theory_refs: tuple[str, ...] = (
        "EWE:PRINCIPLE-001:v0.1",
        "EWE:MATH-001:v0.1:sections-6-9",
    )

    def __post_init__(self) -> None:
        if self.schema_version != "net-gain-evidence-v0.experimental":
            raise ValueError("unsupported net-gain evidence version")
        if len(self.source_sha256) != 64 or len(self.candidate_sha256) != 64:
            raise ValueError("audio identities must be SHA-256 digests")
        names = [dimension.name for dimension in self.dimensions]
        if len(names) != len(set(names)):
            raise ValueError("duplicate net-gain dimension")

    @property
    def evidence_complete(self) -> bool:
        required = {
            "TARGET_GAIN",
            "IDENTITY_PRESERVATION",
            "NEW_ARTIFACT_RISK",
            "LOUDNESS_BIAS",
            "REPRODUCIBILITY",
        }
        by_name = {dimension.name: dimension for dimension in self.dimensions}
        return self.loudness_matched and required.issubset(by_name) and all(
            by_name[name].state not in {"NOT_MEASURED", "INCONCLUSIVE"}
            for name in required
        )

    @property
    def workflow_recommendation(self) -> str:
        if not self.evidence_complete:
            return "INCONCLUSIVE"
        by_name = {dimension.name: dimension for dimension in self.dimensions}
        if by_name["IDENTITY_PRESERVATION"].state == "DEGRADED":
            return "HUMAN_REQUIRED"
        if by_name["NEW_ARTIFACT_RISK"].state == "DEGRADED":
            return "KEEP_ORIGINAL"
        if by_name["TARGET_GAIN"].state != "IMPROVED":
            return "KEEP_ORIGINAL"
        return "HUMAN_REQUIRED"

    def to_dict(self) -> dict[str, object]:
        return {
            **asdict(self),
            "evidence_complete": self.evidence_complete,
            "workflow_recommendation": self.workflow_recommendation,
            "authority": "EVIDENCE_ONLY",
            "aggregate_score": None,
        }

