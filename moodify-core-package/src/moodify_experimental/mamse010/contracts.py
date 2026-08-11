"""MAMSE-010 tensor contracts: axes, fields, bundle, interval alignment.

Every axis is named/typed/unit-aware; missing values use an explicit
validity mask (never physical zeros); time alignment is interval-overlap
based, not array-index based; heterogeneous planes are never stacked raw.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

import numpy as np

SCHEMA_VERSION = "mamse010-tensor-v0.1"
OPERATOR_ID = "MAMSE-010"
EPS = 1e-12


class TensorContractError(ValueError):
    pass


@dataclass(frozen=True)
class AxisSpec:
    name: str
    values: tuple[Any, ...]
    unit: str = "index"
    semantic_type: str = "coordinate"
    ordered: bool = True
    interpolation_policy: str = "none"

    def __post_init__(self) -> None:
        if not self.name:
            raise TensorContractError("axis name cannot be empty")
        if len(self.values) == 0:
            raise TensorContractError(f"axis {self.name} cannot be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "values": list(self.values),
            "unit": self.unit,
            "semantic_type": self.semantic_type,
            "ordered": self.ordered,
            "interpolation_policy": self.interpolation_policy,
        }


@dataclass
class TensorField:
    name: str
    data: np.ndarray
    axes: tuple[AxisSpec, ...]
    valid_mask: np.ndarray | None = None
    unit: str = "unknown"
    authority_class: str = "EXPERIMENTAL_DESCRIPTOR"
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.data = np.asarray(self.data)
        if self.data.ndim != len(self.axes):
            raise TensorContractError(
                f"field {self.name}: data.ndim={self.data.ndim} but axes={len(self.axes)}"
            )
        names = [a.name for a in self.axes]
        if len(set(names)) != len(names):
            raise TensorContractError(f"field {self.name}: duplicate axis names")
        for i, axis in enumerate(self.axes):
            if self.data.shape[i] != len(axis.values):
                raise TensorContractError(
                    f"field {self.name}: axis {axis.name} length "
                    f"{len(axis.values)} != shape[{i}]={self.data.shape[i]}"
                )
        if self.valid_mask is None:
            self.valid_mask = np.isfinite(self.data)
        else:
            self.valid_mask = np.asarray(self.valid_mask, dtype=bool)
            if self.valid_mask.shape != self.data.shape:
                raise TensorContractError("valid_mask shape must equal data shape")
        self.valid_mask = self.valid_mask & np.isfinite(self.data)

    def axis_index(self, name: str) -> int:
        for i, a in enumerate(self.axes):
            if a.name == name:
                return i
        raise KeyError(name)

    def to_meta(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "shape": list(self.data.shape),
            "dtype": str(self.data.dtype),
            "unit": self.unit,
            "authority_class": self.authority_class,
            "axes": [a.to_dict() for a in self.axes],
            "valid_fraction": float(np.mean(self.valid_mask)),
            "provenance": self.provenance,
        }


@dataclass
class AuditoryTensorBundle:
    source_sha256: str
    fields: dict[str, TensorField]
    profile_ids: dict[str, str] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.fields:
            raise TensorContractError("bundle must contain at least one tensor field")

    @property
    def tensor_id(self) -> str:
        payload = {
            "schema_version": self.schema_version,
            "source_sha256": self.source_sha256,
            "profile_ids": self.profile_ids,
            "fields": {name: f.to_meta() for name, f in sorted(self.fields.items())},
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
        return "tensor-" + hashlib.sha256(raw).hexdigest()[:16]

    def to_meta(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "operator_id": OPERATOR_ID,
            "tensor_id": self.tensor_id,
            "source_sha256": self.source_sha256,
            "profile_ids": dict(self.profile_ids),
            "fields": {name: f.to_meta() for name, f in sorted(self.fields.items())},
        }


def interval_overlap_weighted(
    values: np.ndarray,
    starts_ms: np.ndarray,
    ends_ms: np.ndarray,
    dst_starts_ms: np.ndarray,
    dst_ends_ms: np.ndarray,
    valid: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Align a windowed series onto destination intervals using overlap weights."""
    values = np.asarray(values, dtype=float)
    starts_ms = np.asarray(starts_ms, dtype=np.int64)
    ends_ms = np.asarray(ends_ms, dtype=np.int64)
    ds = np.asarray(dst_starts_ms, dtype=np.int64)
    de = np.asarray(dst_ends_ms, dtype=np.int64)
    if not (len(values) == len(starts_ms) == len(ends_ms)):
        raise TensorContractError("source series/interval lengths mismatch")
    if np.any(ends_ms <= starts_ms) or np.any(de <= ds):
        raise TensorContractError("intervals must have positive duration")
    valid_src = np.isfinite(values) if valid is None else (np.asarray(valid, bool) & np.isfinite(values))

    out = np.full(len(ds), np.nan, dtype=float)
    mask = np.zeros(len(ds), dtype=bool)
    for j, (a, b) in enumerate(zip(ds, de)):
        left = np.maximum(starts_ms, a)
        right = np.minimum(ends_ms, b)
        overlap = np.maximum(0, right - left).astype(float)
        overlap *= valid_src
        total = float(np.sum(overlap))
        if total > 0:
            out[j] = float(np.sum(overlap * np.where(valid_src, values, 0.0)) / total)
            mask[j] = True
    return out, mask


def regular_time_grid(duration_ms: int, hop_ms: int) -> tuple[np.ndarray, np.ndarray]:
    if duration_ms <= 0 or hop_ms <= 0:
        raise TensorContractError("duration_ms and hop_ms must be positive")
    starts = np.arange(0, duration_ms, hop_ms, dtype=np.int64)
    ends = np.minimum(starts + hop_ms, duration_ms)
    keep = ends > starts
    return starts[keep], ends[keep]


def build_scale_feature_tensor(
    planes: dict[str, dict[str, Any]],
    *,
    feature_names: list[str],
    duration_ms: int,
    grid_hop_ms: int = 100,
) -> TensorField:
    """TIME x SCALE x FEATURE view over canonical planes with overlap alignment.

    Features absent from a scale remain NaN with valid_mask=False.
    """
    scale_ids = tuple(sorted(planes))
    ts, te = regular_time_grid(duration_ms, grid_hop_ms)
    data = np.full((len(ts), len(scale_ids), len(feature_names)), np.nan, dtype=float)
    mask = np.zeros_like(data, dtype=bool)

    for si, sid in enumerate(scale_ids):
        p = planes[sid]
        names = list(p["feature_names"])
        vals = np.asarray(p["values"], dtype=float)
        starts = np.asarray(p["window_starts_ms"], dtype=np.int64)
        ends = np.asarray(p["window_ends_ms"], dtype=np.int64)
        if vals.ndim != 2 or vals.shape[0] != len(starts) or vals.shape[1] != len(names):
            raise TensorContractError(f"invalid plane shape for {sid}")
        for fi, feature in enumerate(feature_names):
            if feature not in names:
                continue
            col = names.index(feature)
            aligned, ok = interval_overlap_weighted(vals[:, col], starts, ends, ts, te)
            data[:, si, fi] = aligned
            mask[:, si, fi] = ok

    axes = (
        AxisSpec(
            "time",
            tuple(((ts + te) / 2.0).tolist()),
            unit="ms",
            semantic_type="interval_center",
            interpolation_policy="overlap_weighted",
        ),
        AxisSpec("scale", scale_ids, unit="id", semantic_type="analysis_scale", ordered=True),
        AxisSpec("feature", tuple(feature_names), unit="mixed", semantic_type="feature_id", ordered=False),
    )
    return TensorField(
        "scale_feature_view",
        data,
        axes,
        valid_mask=mask,
        unit="mixed",
        authority_class="EXPERIMENTAL_VIEW",
        provenance={"alignment": "interval_overlap_weighted", "grid_hop_ms": grid_hop_ms},
    )
