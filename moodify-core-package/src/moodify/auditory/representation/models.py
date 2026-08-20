"""Multi-scale auditory representation models (MFY-PHASE1-DEPTH-003).

One canonical, versioned internal representation unifying Phase I-A
measurements and Phase I-B temporal events. Every plane resolves to a
Phase I-A metric definition (feature registry) and a Phase I-C scale
definition (scale registry); missing values are NaN/null, never a
silent physical zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ScalePlane:
    scale_id: str  # S0 | S1 | S2 | S3
    window_ms: int
    hop_ms: int
    feature_names: tuple[str, ...]
    window_starts_ms: tuple[int, ...]
    window_ends_ms: tuple[int, ...]
    values: np.ndarray  # shape (n_windows, n_features); NaN = unavailable
    feature_meta: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scale_id": self.scale_id,
            "window_ms": self.window_ms,
            "hop_ms": self.hop_ms,
            "feature_names": list(self.feature_names),
            "window_starts_ms": list(self.window_starts_ms),
            "window_ends_ms": list(self.window_ends_ms),
            "feature_meta": self.feature_meta,
            "values": self.values.tolist(),  # NaN -> null in JSON
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScalePlane":
        return cls(
            scale_id=data["scale_id"],
            window_ms=data["window_ms"],
            hop_ms=data["hop_ms"],
            feature_names=tuple(data["feature_names"]),
            window_starts_ms=tuple(data["window_starts_ms"]),
            window_ends_ms=tuple(data["window_ends_ms"]),
            values=np.asarray(data["values"], dtype=np.float64),
            feature_meta=data.get("feature_meta", {}),
        )


@dataclass(frozen=True)
class AuditoryRepresentation:
    representation_id: str
    source_sha256: str
    representation_version: str  # "rep-v1"
    profile_ids: dict[str, str]  # domain -> profile_id
    scale_ids: tuple[str, ...]
    global_summary: dict[str, Any]
    planes: dict[str, ScalePlane]
    event_refs: dict[str, dict[str, Any]]  # event_id -> {type, start_ms, end_ms, windows}
    evidence_refs: dict[str, Any]
    duration_ms: int = 0
    sample_rate: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "representation_id": self.representation_id,
            "source_sha256": self.source_sha256,
            "representation_version": self.representation_version,
            "profile_ids": dict(self.profile_ids),
            "scale_ids": list(self.scale_ids),
            "global_summary": self.global_summary,
            "planes": {sid: plane.to_dict() for sid, plane in self.planes.items()},
            "event_refs": self.event_refs,
            "evidence_refs": self.evidence_refs,
            "duration_ms": self.duration_ms,
            "sample_rate": self.sample_rate,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuditoryRepresentation":
        return cls(
            representation_id=data["representation_id"],
            source_sha256=data["source_sha256"],
            representation_version=data["representation_version"],
            profile_ids=dict(data["profile_ids"]),
            scale_ids=tuple(data["scale_ids"]),
            global_summary=data["global_summary"],
            planes={sid: ScalePlane.from_dict(p) for sid, p in data["planes"].items()},
            event_refs=data["event_refs"],
            evidence_refs=data["evidence_refs"],
            duration_ms=data.get("duration_ms", 0),
            sample_rate=data.get("sample_rate", 0),
        )
