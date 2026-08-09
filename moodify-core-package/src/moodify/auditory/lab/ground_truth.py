"""Ground-truth manifests (MFY-PHASE1-DEPTH-005).

Truth derives from construction and operator parameters — never from
detector output. Each manifest declares the expected event (type +
bounds) and expected measurement deltas for the perturbed region.
"""

from __future__ import annotations

from moodify.auditory.lab.models import (
    EVENT_EXPECTATIONS,
    GroundTruth,
    PerturbationSpec,
)

MEASUREMENT_DELTA = {
    "HARD_CLIP": {"clipping_sample_ratio": "up", "true_peak_dbfs": "up"},
    "NEAR_CLIP": {"near_clipping_sample_count": "up"},
    "DC_OFFSET": {"dc_offset_left": "up"},
    "GAIN_STEP": {"rms_dbfs": "up"},
    "SILENCE_INSERT": {"silence_ratio": "up"},
    "LOWPASS": {"estimated_high_frequency_cutoff_hz": "down"},
    "ANTIPHASE_REGION": {"stereo_correlation": "down"},
    "NOISE_INJECTION": {"estimated_noise_floor_dbfs": "up"},
    "DYNAMIC_COMPRESSION": {"crest_factor_db": "down"},
}


def build_ground_truth(source_id: str, spec: PerturbationSpec) -> GroundTruth:
    expected_event = EVENT_EXPECTATIONS.get(spec.operator)
    start = spec.region_start_ms if spec.region_start_ms > 0 else None
    end = spec.region_end_ms if spec.region_end_ms > 0 else None
    if spec.operator == "SILENCE_INSERT":
        end = spec.region_end_ms if spec.region_end_ms > 0 else None
    return GroundTruth(
        source_id=source_id,
        operator=spec.operator,
        params=dict(spec.params),
        expected_event_type=expected_event,
        expected_start_ms=start,
        expected_end_ms=end,
        expected_measurement_delta=MEASUREMENT_DELTA.get(spec.operator),
    )
