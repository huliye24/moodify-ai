from __future__ import annotations

from math import exp
from statistics import mean, pstdev
from typing import Any


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + exp(-value))


def annotate_note_evidence(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add a non-destructive evidence score.

    Ocean/basic-pitch velocity is treated as model confidence proxy, never as
    acoustic loudness. RMS dynamics, when available, contributes separately.
    No note is removed by this function.
    """
    rms_values = [
        float(note.get("dynamics", {}).get("mean_rms"))
        for note in notes
        if note.get("dynamics", {}).get("mean_rms") is not None
    ]
    rms_mean = mean(rms_values) if rms_values else 0.0
    rms_std = pstdev(rms_values) if len(rms_values) > 1 else 0.0

    annotated: list[dict[str, Any]] = []
    for original in notes:
        note = dict(original)
        velocity = float(note.get("velocity", 0.0))
        confidence_proxy = max(0.0, min(1.0, velocity / 127.0))

        start = float(note.get("start", note.get("start_time", 0.0)))
        end = float(note.get("end", note.get("end_time", start)))
        duration = max(0.0, float(note.get("duration", end - start)))
        duration_score = max(0.0, min(1.0, duration / 0.5))

        rms = note.get("dynamics", {}).get("mean_rms")
        if rms is None or rms_std == 0:
            acoustic_energy_score = None
            composite = 0.75 * confidence_proxy + 0.25 * duration_score
        else:
            z_score = (float(rms) - rms_mean) / rms_std
            acoustic_energy_score = _sigmoid(z_score)
            composite = (
                0.45 * confidence_proxy
                + 0.35 * acoustic_energy_score
                + 0.20 * duration_score
            )

        note["model_confidence_proxy"] = round(confidence_proxy, 4)
        note["acoustic_energy_score"] = (
            round(acoustic_energy_score, 4)
            if acoustic_energy_score is not None
            else None
        )
        note["evidence_score"] = round(composite, 4)
        note["selection_status"] = "candidate"
        note["evidence_warning"] = (
            "basic-pitch velocity is model confidence proxy, not loudness"
        )
        annotated.append(note)
    return annotated
