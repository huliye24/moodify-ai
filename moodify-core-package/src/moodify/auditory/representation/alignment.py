"""Cross-scale temporal alignment (MFY-PHASE1-DEPTH-003).

Sample-index-first source clock: every scale window is defined by
(start_sample, end_sample); milliseconds are derived. Coarse-to-fine
mapping is deterministic interval arithmetic — a coarse window lists
the finer windows it overlaps, and vice versa.
"""

from __future__ import annotations

from moodify.auditory.representation.models import ScalePlane


def windows_overlapping(plane: ScalePlane, start_ms: int, end_ms: int) -> list[int]:
    """Indices of plane windows overlapping [start_ms, end_ms)."""
    return [idx for idx, (w_start, w_end)
            in enumerate(zip(plane.window_starts_ms, plane.window_ends_ms))
            if w_end > start_ms and w_start < end_ms]


def coarse_to_fine(coarse: ScalePlane, fine: ScalePlane, coarse_index: int) -> list[int]:
    """Fine-scale windows covered by one coarse-scale window."""
    start_ms = coarse.window_starts_ms[coarse_index]
    end_ms = coarse.window_ends_ms[coarse_index]
    return windows_overlapping(fine, start_ms, end_ms)


def fine_to_coarse(fine: ScalePlane, coarse: ScalePlane, fine_index: int) -> list[int]:
    """Coarse-scale windows containing one fine-scale window."""
    start_ms = fine.window_starts_ms[fine_index]
    end_ms = fine.window_ends_ms[fine_index]
    return windows_overlapping(coarse, start_ms, end_ms)
