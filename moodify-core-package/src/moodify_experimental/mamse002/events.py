"""MAMSE-002 product-consumable payloads (T11).

Semantic events only — consumers never see the transform name. Each event
carries evidence refs; the product layer may translate to natural language
but must not imply the machine understands pitch/harmony completely.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .config import CQTConfig, DEFAULT_CONFIG, hz_to_midi
from .cqt import CQTObservation
from .sketch import LogFrequencySketch


def _column(sketch: LogFrequencySketch, name: str) -> np.ndarray:
    return sketch.values[:, sketch.feature_names.index(name)]


def _contiguous_ranges(times_s: np.ndarray, mask: np.ndarray) -> list[tuple[float, float]]:
    ranges: list[tuple[float, float]] = []
    if len(mask) == 0:
        return ranges
    start = None
    prev = None
    for t, m in zip(times_s, mask):
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


def low_register_adjacent_tonal_events(
    obs: CQTObservation,
    sketch: LogFrequencySketch,
    config: CQTConfig = DEFAULT_CONFIG,
) -> list[dict[str, Any]]:
    """Low-register adjacent tonal structure: two close log-frequency peaks
    (<= ~2 semitones apart) in the low region, sustained over a window."""
    events: list[dict[str, Any]] = []
    if sketch.status != "OK" or obs.power.size == 0:
        return events

    peaks = _mean_peaks(obs)
    low_peaks = [p for p in peaks if p["frequency_hz"] < 150.0]
    if len(low_peaks) < 2:
        return events
    pairs: list[tuple[dict, dict]] = []
    for i in range(len(low_peaks)):
        for j in range(i + 1, len(low_peaks)):
            a, b = low_peaks[i], low_peaks[j]
            dist_semitones = abs(float(hz_to_midi(a["frequency_hz"]) - hz_to_midi(b["frequency_hz"])))
            if dist_semitones <= 2.1:
                pairs.append((a, b))
    if not pairs:
        return events

    times = sketch.times_s
    dom = _column(sketch, "dominant_frequency_hz")
    for a, b in pairs:
        within = (np.abs(dom - a["frequency_hz"]) < 3.0) | (np.abs(dom - b["frequency_hz"]) < 3.0)
        ranges = _contiguous_ranges(times, within)
        for start, end in ranges:
            if end - start < 1.0:
                continue
            events.append({
                "event": "LOW_REGISTER_ADJACENT_TONAL_STRUCTURE",
                "time_range_ms": [float(start * 1000), float(end * 1000)],
                "status": "SUPPORTED",
                "frequency_geometry": config.geometry_id,
                "estimated_centers_hz": sorted([round(a["frequency_hz"], 1), round(b["frequency_hz"], 1)]),
                "musical_distance_semitones": round(abs(float(hz_to_midi(a["frequency_hz"]) - hz_to_midi(b["frequency_hz"]))), 2),
                "linear_path_resolution": "PARTIAL",
                "log_frequency_increment": "RESOLVED",
                "evidence_refs": ["log_frequency_evidence.json", "mamse002_logfreq_sketch.npz"],
            })
    return events


def _mean_peaks(obs: CQTObservation) -> list[dict[str, Any]]:
    from .cqt import local_peaks_from_mean

    return [
        {"bin": int(k), "frequency_hz": f, "mean_power": p}
        for k, f, p in local_peaks_from_mean(obs)[:10]
    ]
