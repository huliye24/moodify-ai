"""Event candidate merge and debounce (MFY-PHASE1-DEPTH-002).

Deterministic: candidates of the same type whose gaps fall within the
profile's gap tolerance merge into one event; events shorter than the
minimum duration are dropped. Window indices are translated to
millisecond bounds with honest localization precision (one hop).
"""

from __future__ import annotations

from moodify.auditory.events.models import EventCandidate, TemporalEvent
from moodify.auditory.events.temporal_profile import TemporalProfile
from moodify.auditory.identity import logical_id


def merge_candidates(
    candidates: list[EventCandidate],
    profile: TemporalProfile,
    window_times: dict[str, dict[int, tuple[int, int]]],
    hop_ms: int,
) -> list[TemporalEvent]:
    """Merge same-type candidates and emit final TemporalEvents."""
    events: list[TemporalEvent] = []
    by_type: dict[str, list[EventCandidate]] = {}
    for candidate in candidates:
        by_type.setdefault(candidate.event_type, []).append(candidate)

    for event_type, group in by_type.items():
        ordered = sorted(group, key=lambda c: min(c.window_indices))
        merged: list[EventCandidate] = []
        for candidate in ordered:
            if not merged:
                merged.append(candidate)
                continue
            last = merged[-1]
            gap = min(candidate.window_indices) - max(last.window_indices)
            if gap <= max(1, profile.gap_tolerance_ms // hop_ms):
                merged[-1] = EventCandidate(
                    event_type=last.event_type,
                    window_indices=tuple(
                        sorted(set(last.window_indices) | set(candidate.window_indices))
                    ),
                    domain=last.domain,
                    peak_magnitude=max(last.peak_magnitude, candidate.peak_magnitude),
                )
            else:
                merged.append(candidate)

        for candidate in merged:
            start_ms, end_ms = _bounds(candidate, window_times, hop_ms)
            duration_ms = end_ms - start_ms
            if duration_ms < profile.minimum_event_duration_ms:
                continue
            event_identity = {
                "type": event_type,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "windows": candidate.window_indices,
                "profile": profile.profile_id,
                "domain": candidate.domain,
            }
            events.append(TemporalEvent(
                event_id=logical_id("evt", event_identity, 12),
                event_type=event_type,
                start_ms=start_ms,
                end_ms=end_ms,
                confidence=_confidence(candidate, event_type),
                status="ESTIMATOR_DERIVED" if event_type == "HIGH_FREQUENCY_DROPOUT" else "DETECTED",
                evidence_windows=candidate.window_indices,
                rules=(f"threshold:{event_type}",),
                profile_id=profile.profile_id,
                localization_precision_ms=hop_ms,
                domain=candidate.domain,
            ))
    return sorted(events, key=lambda e: e.start_ms)


def _bounds(candidate: EventCandidate, window_times: dict[str, dict[int, tuple[int, int]]],
            hop_ms: int) -> tuple[int, int]:
    indices = candidate.window_indices
    starts: list[int] = []
    ends: list[int] = []
    for idx in indices:
        times = window_times.get(candidate.domain, {}).get(idx)
        if times:
            starts.append(times[0])
            ends.append(times[1])
    if not starts:
        first, last = min(indices), max(indices)
        return first * hop_ms, (last + 1) * hop_ms
    return min(starts), max(ends)


def _confidence(candidate: EventCandidate, event_type: str) -> float:
    if event_type == "HIGH_FREQUENCY_DROPOUT":
        return 0.6  # estimator-derived, explicitly lower confidence
    return min(0.95, 0.6 + 0.1 * len(candidate.window_indices))
