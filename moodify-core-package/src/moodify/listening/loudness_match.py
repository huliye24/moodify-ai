"""A/B loudness matching validation (MFY_MOBILE_LISTENING_VALIDATION_001).

Machine-side check that the A/B pair handed to the reviewer is loudness
matched within the pre-registered threshold. Thresholds are frozen in the
protocol; failing the check means the pair must not be played.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from moodify.listening.protocol import LEVEL_MATCH_DB_MAX, SWITCH_LATENCY_MS_MAX


@dataclass(frozen=True)
class LevelMatchResult:
    passed: bool
    loudness_diff_db: float
    switch_latency_ms: float
    reason: str = ""


def _rms_db(audio: np.ndarray) -> float:
    return float(20.0 * np.log10(np.sqrt(np.mean(audio**2)) + 1e-12))


def verify_level_match(
    audio_a: np.ndarray,
    audio_b: np.ndarray,
    sr: int,
    switch_latency_ms: float = 0.0,
    level_match_db_max: float = LEVEL_MATCH_DB_MAX,
) -> LevelMatchResult:
    """Pure check: RMS-based loudness difference + declared switch latency.

    switch_latency_ms is measured by the playback harness (not estimated here);
    a future device harness reports it per session.
    """
    if audio_a.shape != audio_b.shape:
        return LevelMatchResult(False, 0.0, switch_latency_ms, "shape mismatch")
    diff = _rms_db(audio_b) - _rms_db(audio_a)
    ok = abs(diff) <= level_match_db_max and switch_latency_ms <= SWITCH_LATENCY_MS_MAX
    return LevelMatchResult(ok, round(diff, 4), switch_latency_ms)
