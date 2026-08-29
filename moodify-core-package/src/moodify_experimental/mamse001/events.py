"""MAMSE-001 simplified product-consumable event interface (T9).

Not a UI surface: emits structured observations a future consumer (app,
playback adapter, report) could read. No new app navigation or buttons.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _column(sketch: dict[str, Any], name: str) -> np.ndarray:
    names = list(sketch["feature_names"])
    return sketch["values"][:, names.index(name)]


def _contiguous_ranges(times_ms: np.ndarray, mask: np.ndarray) -> list[tuple[float, float]]:
    ranges: list[tuple[float, float]] = []
    if len(mask) == 0:
        return ranges
    start = None
    prev = None
    for t, m in zip(times_ms, mask):
        if m and start is None:
            start, prev = float(t), float(t)
        elif m:
            prev = float(t)
        elif start is not None:
            ranges.append((start, prev))
            start = None
    if start is not None:
        ranges.append((start, prev))
    return ranges


def narrowband_events(multi: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect narrowband-persistent structure using R2/R3 agreement.

    A frame is narrowband when its flatness is low. Long-resolution (R2/R3)
    agreement across time is reported as an event; R0 disagreement is listed
    as a conflict, not merged away.
    """
    events: list[dict[str, Any]] = []
    sk = multi["resolutions"]
    if "R2" not in sk or "R3" not in sk:
        return events
    r2_times = sk["R2"]["frame_centers_ms"]
    r2_flat = _column(sk["R2"], "spectral_flatness")
    r3_flat = _column(sk["R3"], "spectral_flatness")

    r3_times = sk["R3"]["frame_centers_ms"]
    r3_nearest = np.array([
        r3_flat[int(np.argmin(np.abs(r3_times - float(t))))] for t in r2_times
    ])
    mask = (r2_flat < 0.15) & (r3_nearest < 0.15)
    if len(mask) < 2:
        return events
    for start, end in _contiguous_ranges(r2_times, mask):
        if end - start < 2000:
            continue
        idx = np.where(mask)[0]
        seg = idx[(r2_times[idx] >= start) & (r2_times[idx] <= end)]
        if len(seg) == 0:
            continue
        dom = _column(sk["R2"], "dominant_frequency_hz")[seg]
        freq = float(np.median(dom)) if np.all(np.isfinite(dom)) else None
        events.append({
            "event": "NARROWBAND_PERSISTENT_STRUCTURE",
            "time_range_ms": [float(start), float(end)],
            "confidence": "PARTIAL",
            "median_dominant_frequency_hz": freq,
            "supporting_resolutions": ["R2", "R3"],
            "conflicting_resolutions": [],
            "evidence_refs": ["cross_resolution_evidence.json"],
        })
    return events
