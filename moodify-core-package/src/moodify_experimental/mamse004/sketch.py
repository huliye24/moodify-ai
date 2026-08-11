"""MAMSE-004 entry point: analyze_phase_geometry.

Returns a dict {summary, mono_raw, stereo_raw} plus runtime statistics.
Every output is an EXPERIMENTAL_DESCRIPTOR_ESTIMATOR; nonzero group delay is
never automatically a defect; low-magnitude bins are masked (UNAVAILABLE),
never fabricated as zero.
"""

from __future__ import annotations

import hashlib
import json
import time

import numpy as np

from .config import CONFIG_VERSION, OPERATOR_ID, OPERATOR_VERSION, PhaseGeometryConfig
from .phase import analyze_mono_phase
from .stereo import analyze_stereo_phase


def _sha(x: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()


def analyze_phase_geometry(samples: np.ndarray, sr: int, cfg: PhaseGeometryConfig | None = None) -> dict:
    cfg = cfg or PhaseGeometryConfig()
    cfg.validate()
    x = np.asarray(samples, dtype=np.float64)
    t0 = time.perf_counter()
    if x.ndim == 1:
        mono = x
        stereo = None
    elif x.ndim == 2:
        mono = x.mean(axis=1)
        stereo = analyze_stereo_phase(x[:, 0], x[:, 1], sr, cfg) if x.shape[1] >= 2 else None
    else:
        raise ValueError("samples must be 1D or 2D")
    m = analyze_mono_phase(mono, sr, cfg)
    runtime_seconds = time.perf_counter() - t0
    summary = {
        "operator_id": OPERATOR_ID,
        "operator_version": OPERATOR_VERSION,
        "config_version": CONFIG_VERSION,
        "config_hash": cfg.config_hash,
        "config": cfg.to_dict(),
        "source_sha256": _sha(x),
        "sample_rate": sr,
        "mono": m["summary"],
        "stereo": stereo["summary"] if stereo else {
            "ipd_available": False,
            "reason": "mono input",
            "valid_bin_ratio": 0.0,
            "interchannel_delay_median_ms": None,
            "interchannel_delay_mad_ms": None,
            "gcc_phat_delay_ms": None,
            "cross_method_disagreement_ms": None,
        },
        "authority_class": "EXPERIMENTAL_DESCRIPTOR_ESTIMATOR",
        "judgment_eligible": False,
        "runtime_seconds": runtime_seconds,
        "limitations": [
            "nonzero group delay is not automatically a defect",
            "low-magnitude bins are masked by relative threshold, not encoded as 0",
            "STFT/window/cross-spectrum conventions are part of the versioned result",
        ],
    }
    return {"summary": summary, "mono_raw": m, "stereo_raw": stereo}


def logical_json(result: dict) -> str:
    """Logical identity of a result; runtime bookkeeping is excluded."""
    summary = {k: v for k, v in result["summary"].items() if k != "runtime_seconds"}
    return json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
