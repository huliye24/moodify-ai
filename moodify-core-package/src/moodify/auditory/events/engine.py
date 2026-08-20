"""Temporal hearing engine (MFY-PHASE1-DEPTH-002).

AUDIO -> WINDOW MEASUREMENTS -> EVENT CANDIDATES -> EVENT MERGE ->
EVIDENCE WINDOWS -> EVENTS. One pass per analysis domain (no repeated
full-track transforms); every event references its evidence windows,
rules and profile version.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from moodify.auditory.events.merge import merge_candidates
from moodify.auditory.events.models import TemporalEvent, WindowMeasurement
from moodify.auditory.events.rules import compute_domain_measurements, detect_candidates
from moodify.auditory.events.temporal_profile import TemporalProfile

DOMAINS = ("integrity", "level", "spectrum", "stereo")


@dataclass
class TemporalHearingResult:
    events: list[TemporalEvent]
    measurements: dict[str, list[WindowMeasurement]]
    profile: TemporalProfile

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile.profile_id,
            "events": [event.to_dict() for event in self.events],
            "window_counts": {domain: len(rows) for domain, rows in self.measurements.items()},
        }


def run_temporal_hearing(samples: np.ndarray, sr: int,
                         profile: TemporalProfile | None = None) -> TemporalHearingResult:
    """Detect time-localized technical auditory events with evidence."""
    profile = profile or TemporalProfile.from_yaml()
    if samples.ndim == 1:
        samples = samples[:, None]

    measurements: dict[str, list[WindowMeasurement]] = {}
    window_times: dict[str, dict[int, tuple[int, int]]] = {}
    hop_ms: dict[str, int] = {}
    for domain in DOMAINS:
        rows = compute_domain_measurements(samples, sr, domain, profile)
        measurements[domain] = rows
        window_times[domain] = {row.window_index: (row.start_ms, row.end_ms) for row in rows}
        hop_ms[domain] = profile.domains[domain].hop_ms

    candidates = detect_candidates(measurements, profile)
    # Merge within each domain's own hop precision.
    events: list[TemporalEvent] = []
    for domain in DOMAINS:
        domain_candidates = [c for c in candidates if c.domain == domain]
        events.extend(merge_candidates(
            domain_candidates, profile, window_times, hop_ms[domain],
        ))
    events.sort(key=lambda e: (e.start_ms, e.event_type))
    return TemporalHearingResult(events=events, measurements=measurements, profile=profile)
