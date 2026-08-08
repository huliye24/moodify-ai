"""Configuration for the lyric alignment subsystem (single source of truth).

Thresholds are provisional per DSK-MFY-LYRIC-TEMPORAL-ALIGNMENT-001 and must be
calibrated on a labeled validation set (docs/verification/lyric_align_verification_set.md).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

DEFAULT_CONFIG_PATH = Path(__file__).parent / "configs" / "default.json"


class QualityGate(BaseModel):
    min_coverage: float = 0.92
    max_unaligned_token_ratio: float = 0.05
    min_mean_word_confidence: float = 0.72
    min_line_confidence: float = 0.55
    max_line_overlap_seconds: float = 0.08
    max_boundary_jump_seconds: float = 1.0
    max_rerun_delta_ms: float = 80.0


class AlignConfig(BaseModel):
    sample_rate: int = 16000
    separate_vocals: str = "auto"
    demucs_model: str = "htdemucs"
    active_frame_ms: int = 30
    active_hop_ms: int = 10
    active_threshold_ratio: float = 0.20
    merge_gap_seconds: float = 0.45
    min_active_seconds: float = 0.12
    publish_gate: QualityGate = QualityGate()

    @classmethod
    def from_file(cls, path: str | Path | None = None) -> "AlignConfig":
        source = Path(path) if path else DEFAULT_CONFIG_PATH
        if not source.exists():
            raise FileNotFoundError(f"Alignment config not found: {source}")
        raw: dict[str, Any] = json.loads(source.read_text(encoding="utf-8"))
        gate = QualityGate(**raw.pop("publish_gate", {}))
        return cls(**raw, publish_gate=gate)
