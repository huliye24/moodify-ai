"""MRS Multi-Dimension Quality Surface.

Expands Moodify's MRS from a single score into a discriminative calibration
surface with named quality dimensions. Deterministic, backward compatible.
Part of ECHAIN-MOODIFY-MRS-EXTREME-017 / MHP-910.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

import math


@dataclass
class MRSDimension:
    name: str
    label: str
    value: float
    weight: float
    threshold_good: float
    threshold_warn: float
    status: str = "ok"  # ok, warn, fail


@dataclass
class MRSSurface:
    sample_id: str = ""
    genre: str = ""
    preset: str = ""
    dimensions: list[MRSDimension] = field(default_factory=list)
    composite: float = 0.0
    confidence: float = 0.0
    gate: str = ""
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "genre": self.genre,
            "preset": self.preset,
            "composite": self.composite,
            "confidence": self.confidence,
            "gate": self.gate,
            "flags": self.flags,
            "dimensions": [
                {"name": d.name, "label": d.label, "value": d.value,
                 "weight": d.weight, "status": d.status}
                for d in self.dimensions
            ],
        }


def _dim_status(value: float, threshold_good: float, threshold_warn: float) -> str:
    if value >= threshold_good:
        return "ok"
    if value >= threshold_warn:
        return "warn"
    return "fail"


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def _spectral_fidelity(before_rms: float, after_rms: float, before_crest: float, after_crest: float) -> float:
    """How well the spectral balance is preserved. Lower delta = better."""
    if before_rms <= -60.0:
        return 50.0
    rms_ratio = after_rms / before_rms
    rms_score = 100.0 - abs(1.0 - rms_ratio) * 80.0

    if before_crest <= 0:
        crest_score = 50.0
    else:
        crest_ratio = after_crest / before_crest
        crest_score = 100.0 - abs(1.0 - crest_ratio) * 60.0

    return _clamp(rms_score * 0.5 + crest_score * 0.5)


def _dynamic_preservation(before_dr: float, after_dr: float) -> float:
    """Dynamic range preservation. Score drops if DR is crushed."""
    if before_dr <= 0:
        return 50.0
    dr_ratio = min(after_dr, before_dr) / max(after_dr, before_dr)
    return _clamp(dr_ratio * 100.0)


def _spatial_clarity(before_lr_balance: float, after_lr_balance: float) -> float:
    """Stereo field preservation. Closer to 1:1 L/R = better."""
    def _balance_score(b: float) -> float:
        return 100.0 - abs(b) * 200.0
    before_s = _balance_score(before_lr_balance)
    after_s = _balance_score(after_lr_balance)
    return _clamp((before_s + after_s) / 2.0)


def _intent_preservation(eds_before: float, eds_after: float, emotion: str = "") -> float:
    """How well the intended emotional character is preserved."""
    if eds_before == 0:
        return 50.0
    drift = abs(eds_after - eds_before) / abs(eds_before)
    base = 100.0 - drift * 100.0
    return _clamp(base)


def _artifact_penalty_score(over_dark_level: str, over_dark_score: float) -> float:
    """Invert over-dark detection into a 0-100 quality score."""
    if over_dark_level == "severe":
        return _clamp(100.0 - over_dark_score * 100.0)
    if over_dark_level == "mild":
        return _clamp(100.0 - over_dark_score * 50.0)
    return 100.0


def compute_mrs_surface(
    sample_id: str = "",
    genre: str = "",
    preset: str = "",
    before_metrics: dict[str, Any] | None = None,
    after_metrics: dict[str, Any] | None = None,
    over_dark_level: str = "none",
    over_dark_score: float = 0.0,
    pseudo_mrs_delta: float | None = None,
    emotion: str = "",
) -> MRSSurface:
    before = before_metrics or {}
    after = after_metrics or {}

    b_rms = float(before.get("rms_db", -18) if before.get("rms_db") is not None else -18)
    a_rms = float(after.get("rms_db", -18) if after.get("rms_db") is not None else -18)
    b_crest = float(before.get("crest_factor_db", 12))
    a_crest = float(after.get("crest_factor_db", 12))
    b_dr = float(before.get("dynamic_range_db", 30))
    a_dr = float(after.get("dynamic_range_db", 30))
    b_lr = float(before.get("lr_balance", 0))
    a_lr = float(after.get("lr_balance", 0))
    b_eds = float(before.get("eds", -18))
    a_eds = float(after.get("eds", -18))

    dims = [
        MRSDimension(
            name="spectral_fidelity", label="Spectral Fidelity",
            value=round(_spectral_fidelity(b_rms, a_rms, b_crest, a_crest), 1),
            weight=0.25, threshold_good=80.0, threshold_warn=60.0,
        ),
        MRSDimension(
            name="dynamic_preservation", label="Dynamic Preservation",
            value=round(_dynamic_preservation(b_dr, a_dr), 1),
            weight=0.20, threshold_good=75.0, threshold_warn=50.0,
        ),
        MRSDimension(
            name="spatial_clarity", label="Spatial Clarity",
            value=round(_spatial_clarity(b_lr, a_lr), 1),
            weight=0.15, threshold_good=80.0, threshold_warn=60.0,
        ),
        MRSDimension(
            name="intent_preservation", label="Intent Preservation",
            value=round(_intent_preservation(b_eds, a_eds, emotion), 1),
            weight=0.20, threshold_good=80.0, threshold_warn=60.0,
        ),
        MRSDimension(
            name="artifact_penalty", label="Artifact Control",
            value=round(_artifact_penalty_score(over_dark_level, over_dark_score), 1),
            weight=0.20, threshold_good=85.0, threshold_warn=65.0,
        ),
    ]

    for d in dims:
        d.status = _dim_status(d.value, d.threshold_good, d.threshold_warn)

    composite = round(sum(d.value * d.weight for d in dims), 1)

    n_dims = len(dims)
    confidence = round(80.0 if n_dims >= 5 else n_dims * 16.0, 1)
    if pseudo_mrs_delta is not None:
        confidence = min(100.0, confidence + 5.0)

    flags = []
    for d in dims:
        if d.status == "fail":
            flags.append(f"{d.name}:fail")
        elif d.status == "warn":
            flags.append(f"{d.name}:warn")

    n_fails = sum(1 for d in dims if d.status == "fail")
    n_warns = sum(1 for d in dims if d.status == "warn")
    if n_fails >= 2:
        gate = "REJECT"
    elif n_fails >= 1 or n_warns >= 3:
        gate = "HOLD"
    elif composite >= 70:
        gate = "ADOPT"
    else:
        gate = "HOLD"

    return MRSSurface(
        sample_id=sample_id, genre=genre, preset=preset,
        dimensions=dims, composite=composite, confidence=confidence,
        gate=gate, flags=flags,
    )
