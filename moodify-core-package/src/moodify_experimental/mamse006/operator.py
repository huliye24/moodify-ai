"""MAMSE-006 entry point: run_mamse006.

Returns (summary, evidence_arrays). Summary carries the modulation
descriptors with EXPERIMENTAL authority and explicit UNAVAILABLE statuses;
evidence carries the surfaces and joint planes for NPZ persistence.
"""

from __future__ import annotations

import hashlib
import time

import numpy as np

from .config import CONFIG_VERSION, MANIFEST_SCHEMA_VERSION, OPERATOR_ID, OPERATOR_VERSION, ModulationConfig
from .features import summarize_modulation
from .modulation import analyze_surface
from .surface import compute_log_frequency_surface

LIMITATIONS = [
    "Temporal modulation bands are engineering descriptors, not universal perceptual categories.",
    "Ridge velocity is a spectrogram-texture velocity candidate, not physical source motion.",
    "Orientation must not be mapped to upward/downward semantics without calibrated convention.",
    "No AI-vs-human or artistic-quality judgment is authorized by this operator.",
]


def source_sha256(samples: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(samples).tobytes()).hexdigest()


def run_mamse006(samples: np.ndarray, cfg: ModulationConfig) -> tuple[dict, dict | None]:
    cfg.validate()
    t0 = time.perf_counter()
    surface, status = compute_log_frequency_surface(samples, cfg)
    base = {
        "operator_id": OPERATOR_ID,
        "operator_version": OPERATOR_VERSION,
        "config_version": CONFIG_VERSION,
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "profile_hash": cfg.profile_hash,
        "config": cfg.to_dict(),
        "source_sha256": source_sha256(np.asarray(samples)),
        **status,
    }
    if surface is None:
        base["runtime_seconds"] = time.perf_counter() - t0
        base["limitations"] = ["No modulation interpretation produced for unavailable input."]
        return base, None

    mod = analyze_surface(
        surface["surface_db"],
        surface["frame_rate_hz"],
        cfg.bands_per_octave,
        cfg.modulation_window_seconds,
        cfg.modulation_hop_seconds,
    )
    summary = summarize_modulation(
        mod,
        temporal_min_hz=cfg.temporal_min_hz,
        temporal_max_hz=cfg.temporal_max_hz,
        spectral_max_cpo=cfg.spectral_max_cpo,
    )
    evidence = {
        "log_frequency_hz": surface["log_frequency_hz"],
        "time_s": surface["time_s"],
        "auditory_surface_db": surface["surface_db"],
        **mod,
    }
    base.update(summary)
    base.update({
        "status": "OK",
        "rms_dbfs": surface["rms_dbfs"],
        "frame_rate_hz": surface["frame_rate_hz"],
        "log_frequency_bins": int(surface["log_frequency_hz"].size),
        "modulation_segments": int(mod["segment_count"]),
        "runtime_seconds": time.perf_counter() - t0,
        "authority": "EXPERIMENTAL_DESCRIPTOR",
        "judgment_eligible": False,
        "limitations": LIMITATIONS,
    })
    return base, evidence
