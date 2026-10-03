"""verify.py — before/after measurement for mix_graph sessions.

Machine evidence only: loudness, peak, dynamics, stereo correlation and
invariant checks. No listening-quality claims — perceptual judgement stays
with the algorithmic review authority (data_factory.algorithmic_review).
"""

from __future__ import annotations

import math

import numpy as np

from moodify.processing.pedalboard_chain import _measure_lufs  # single loudness authority


def measure_audio(audio: np.ndarray, sr: int) -> dict:
    """Measure one audio buffer; deterministic and NaN-safe."""
    mono = audio if audio.ndim == 1 else audio.mean(axis=1)
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    peak_db = 20.0 * math.log10(peak) if peak > 0 else -np.inf
    rms = float(np.sqrt(np.mean(np.square(mono)) + 1e-12))
    rms_db = 20.0 * math.log10(rms)
    metrics: dict = {
        "sample_rate": int(sr),
        "channels": 1 if audio.ndim == 1 else int(audio.shape[1]),
        "duration_s": round(audio.shape[0] / sr, 3),
        "sample_peak_dbfs": round(float(peak_db), 2),
        "rms_dbfs": round(float(rms_db), 2),
        "crest_factor": round(float(peak / rms), 2),
        "integrated_loudness_lufs": round(float(_measure_lufs(audio, sr)), 2),
        "finite": bool(np.all(np.isfinite(audio))),
    }
    if audio.ndim > 1 and audio.shape[1] == 2:
        left, right = audio[:, 0], audio[:, 1]
        denom = float(np.std(left) * np.std(right))
        correlation = float(np.mean(left * right) / denom) if denom > 1e-12 else 1.0
        metrics["stereo_correlation"] = round(max(-1.0, min(1.0, correlation)), 3)
    return metrics


def verify_before_after(before: np.ndarray, after: np.ndarray, sr: int) -> dict:
    """Measure source and rendered audio and compute the deltas between them."""
    before_metrics = measure_audio(before, sr)
    after_metrics = measure_audio(after, sr)
    deltas: dict = {
        "loudness_lu": round(
            after_metrics["integrated_loudness_lufs"]
            - before_metrics["integrated_loudness_lufs"], 2),
        "sample_peak_db": round(
            after_metrics["sample_peak_dbfs"] - before_metrics["sample_peak_dbfs"], 2),
        "crest_factor": round(
            after_metrics["crest_factor"] - before_metrics["crest_factor"], 2),
    }
    invariants = {
        "finite_output": after_metrics["finite"],
        "length_preserved": before.shape[0] == after.shape[0],
        "channels_preserved": before_metrics["channels"] == after_metrics["channels"],
    }
    return {
        "before": before_metrics,
        "after": after_metrics,
        "deltas": deltas,
        "invariants": invariants,
        "status": "measured",
    }


def peak_gate(after_metrics: dict, max_peak_dbfs: float) -> dict:
    """Check the rendered peak against the graph's verification ceiling."""
    measured = after_metrics["sample_peak_dbfs"]
    return {
        "gate": "max_peak_dbfs",
        "limit": max_peak_dbfs,
        "measured": measured,
        "passed": bool(measured <= max_peak_dbfs + 0.01),
    }
