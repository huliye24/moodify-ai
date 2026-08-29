"""MAMSE-005 entry point: analyze_cepstral_structure.

Per-frame real cepstrum -> envelope/fine decomposition -> periodicity (F0
candidate) -> resonance candidates. All outputs are EXPERIMENTAL
descriptors; f0 is a cepstral candidate, not ground-truth pitch; resonance
candidates are envelope peaks, not formants. Silence/short inputs return
UNAVAILABLE with a reason — nothing is fabricated.
"""

from __future__ import annotations

import hashlib
import json
import time

import numpy as np

from .cepstrum import cepstral_decompose_frame, frame_signal
from .config import CONFIG_VERSION, OPERATOR_ID, OPERATOR_VERSION, CepstrumConfig
from .envelope import resonance_candidates, roughness_measure
from .periodicity import estimate_periodicity, rms_dbfs

LIMITATIONS = [
    "source-filter interpretation is strongest for controlled voiced/single-source signals and is not universal for full mixes",
    "f0 is a cepstral candidate, not ground-truth pitch",
    "resonance candidates are envelope peaks, not automatically formants",
    "lifter cutoff and frame size are versioned modeling choices",
]


def _sha(x: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()


def analyze_cepstral_structure(samples: np.ndarray, sr: int, cfg: CepstrumConfig | None = None) -> dict:
    cfg = cfg or CepstrumConfig()
    cfg.validate()
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim == 2:
        mono = x.mean(axis=1)
    elif x.ndim == 1:
        mono = x
    else:
        raise ValueError("samples must be 1D or 2D")
    source_sha = _sha(x)
    t0 = time.perf_counter()
    frames = frame_signal(mono, cfg.n_fft, cfg.hop_length)
    if frames.shape[0] == 0:
        summary = {
            "operator_id": OPERATOR_ID,
            "operator_version": OPERATOR_VERSION,
            "config_version": CONFIG_VERSION,
            "config_hash": cfg.config_hash,
            "config": cfg.to_dict(),
            "source_sha256": source_sha,
            "sample_rate": sr,
            "availability": "UNAVAILABLE_TOO_SHORT",
            "reason": f"signal shorter than n_fft ({len(mono)} < {cfg.n_fft})",
            "frame_count": 0,
            "runtime_seconds": 0.0,
            "judgment_eligible": False,
            "authority_class": "EXPERIMENTAL_DESCRIPTOR_ESTIMATOR",
            "limitations": LIMITATIONS,
        }
        return {"summary": summary, "raw": None}

    win_times = (np.arange(frames.shape[0]) * cfg.hop_length + cfg.n_fft / 2) / sr
    all_cep, all_env, all_fine, f0, score, available, rms, candidates = [], [], [], [], [], [], [], []
    for frame in frames:
        level = rms_dbfs(frame)
        rms.append(level)
        d = cepstral_decompose_frame(frame, sr, cfg.n_fft, cfg.window, cfg.magnitude_floor, cfg.lifter_cutoff_ms)
        all_cep.append(d["cepstrum"][:cfg.n_fft // 2 + 1])
        all_env.append(d["envelope_logmag"])
        all_fine.append(d["fine_logmag"])
        if level < cfg.min_rms_dbfs:
            p = {"available": False, "reason": "low_energy", "f0_candidate_hz": None, "periodicity_score": 0.0}
        else:
            p = estimate_periodicity(d["cepstrum"], sr, cfg.f0_min_hz, cfg.f0_max_hz, cfg.min_periodicity_score)
        f0.append(np.nan if p.get("f0_candidate_hz") is None else p["f0_candidate_hz"])
        score.append(float(p.get("periodicity_score") or 0.0))
        available.append(bool(p.get("available")))
        candidates.append(resonance_candidates(d["envelope_logmag"], sr, cfg.n_fft, cfg.max_resonance_hz,
                                               cfg.resonance_prominence_db, cfg.max_resonance_candidates))

    cep = np.asarray(all_cep)
    env = np.asarray(all_env)
    fine = np.asarray(all_fine)
    f0a = np.asarray(f0, float)
    sc = np.asarray(score, float)
    av = np.asarray(available, bool)
    rmsa = np.asarray(rms, float)
    freqs = np.fft.rfftfreq(cfg.n_fft, 1 / sr)
    quef = np.arange(cfg.n_fft // 2 + 1) / sr
    finite_f0 = f0a[np.isfinite(f0a)]
    env_rough = float(np.median([roughness_measure(row) for row in env]))
    raw_log = env + fine
    raw_rough = float(np.median([roughness_measure(row) for row in raw_log]))
    env_energy = float(np.mean(env * env))
    fine_energy = float(np.mean(fine * fine))
    runtime_seconds = time.perf_counter() - t0
    summary = {
        "operator_id": OPERATOR_ID,
        "operator_version": OPERATOR_VERSION,
        "config_version": CONFIG_VERSION,
        "config_hash": cfg.config_hash,
        "config": cfg.to_dict(),
        "source_sha256": source_sha,
        "sample_rate": sr,
        "availability": "AVAILABLE",
        "frame_count": int(frames.shape[0]),
        "periodicity_available_ratio": float(np.mean(av)),
        "median_f0_candidate_hz": None if finite_f0.size == 0 else float(np.median(finite_f0)),
        "median_periodicity_score": float(np.median(sc)),
        "spectral_envelope_roughness": env_rough,
        "raw_log_spectrum_roughness": raw_rough,
        "fine_to_envelope_energy_ratio": float(fine_energy / (env_energy + 1e-12)),
        "runtime_seconds": runtime_seconds,
        "authority_class": "EXPERIMENTAL_DESCRIPTOR_ESTIMATOR",
        "judgment_eligible": False,
        "limitations": LIMITATIONS,
    }
    return {
        "summary": summary,
        "raw": {
            "frame_time_s": win_times,
            "frequency_hz": freqs,
            "quefrency_s": quef,
            "cepstrum": cep,
            "envelope_logmag": env,
            "fine_logmag": fine,
            "f0_candidate_hz": f0a,
            "periodicity_score": sc,
            "periodicity_available": av,
            "rms_dbfs": rmsa,
            "resonance_candidates": candidates,
        },
    }


def logical_json(result: dict) -> str:
    """Logical identity of a result; runtime bookkeeping is excluded."""
    summary = {k: v for k, v in result["summary"].items() if k != "runtime_seconds"}
    return json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
