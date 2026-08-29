"""Temporal analysis profile (MFY-PHASE1-DEPTH-002).

One versioned source of window/hop/merge policies. Every timeline
artifact and event records the profile_id; changing the profile
invalidates compatible derived events. Detector thresholds are versioned
here too, so event semantics are auditable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_PROFILE_PATH = Path(__file__).resolve().parents[4] / "configs" / "temporal_profile_v1.yaml"


@dataclass(frozen=True)
class DomainConfig:
    window_ms: int
    hop_ms: int


@dataclass(frozen=True)
class TemporalProfile:
    profile_id: str = "temporal-hearing-v1"
    domains: dict[str, DomainConfig] = field(default_factory=dict)
    gap_tolerance_ms: int = 150
    minimum_event_duration_ms: int = 100
    thresholds: dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str | Path = DEFAULT_PROFILE_PATH) -> "TemporalProfile":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        domains = {
            name: DomainConfig(window_ms=int(cfg["window_ms"]), hop_ms=int(cfg["hop_ms"]))
            for name, cfg in data["analysis_domains"].items()
        }
        merge = data.get("event_merge", {})
        thresholds = {k: float(v) for k, v in data.get("detector_thresholds", {}).items()}
        return cls(
            profile_id=data["profile_id"],
            domains=domains,
            gap_tolerance_ms=int(merge.get("default_gap_tolerance_ms", 150)),
            minimum_event_duration_ms=int(merge.get("minimum_event_duration_ms", 100)),
            thresholds=thresholds,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "analysis_domains": {
                name: {"window_ms": cfg.window_ms, "hop_ms": cfg.hop_ms}
                for name, cfg in self.domains.items()
            },
            "event_merge": {
                "default_gap_tolerance_ms": self.gap_tolerance_ms,
                "minimum_event_duration_ms": self.minimum_event_duration_ms,
            },
            "detector_thresholds": dict(self.thresholds),
        }
