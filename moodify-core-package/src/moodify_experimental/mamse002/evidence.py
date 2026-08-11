"""MAMSE-002 evidence contract (T8): manifest + NPZ sketch + log-frequency evidence.

Manifest carries operator/geometry/config hash, source identity, runtime
versions (librosa/numpy/scipy/python), git commit, and feature schema
version. Cache lineage is recorded when a shared cache is used.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import librosa
import numpy as np
import scipy

from .config import EVIDENCE_SCHEMA_VERSION, FEATURE_SCHEMA_VERSION, MANIFEST_SCHEMA_VERSION, CQTConfig
from .cqt import CQTObservation, local_peaks_from_mean
from .sketch import FEATURE_AUTHORITY, LogFrequencySketch


def source_sha256(samples: np.ndarray) -> str:
    return np_sha256(np.ascontiguousarray(samples).tobytes())


def np_sha256(b: bytes) -> str:
    import hashlib

    return hashlib.sha256(b).hexdigest()


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5
        )
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def build_manifest(
    samples: np.ndarray,
    sr: int,
    config: CQTConfig,
    sketch: LogFrequencySketch,
    git_commit: str | None = None,
    cache_lineage: dict | None = None,
) -> dict[str, Any]:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "operator_id": config.operator_id,
        "operator_version": config.operator_version,
        "geometry_id": config.geometry_id,
        "config": config.to_dict(),
        "config_sha256": config.sha256(),
        "source_sha256": source_sha256(samples),
        "sample_rate": sr,
        "duration_s": float(len(samples) / sr),
        "hop_length": config.hop_length,
        "window": config.window,
        "filter_scale": config.filter_scale,
        "sparsity": config.sparsity,
        "fmin_hz": config.fmin_hz,
        "bins_per_octave": config.bins_per_octave,
        "n_bins": config.n_bins,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "feature_authority": FEATURE_AUTHORITY,
        "frame_count": int(len(sketch.times_s)),
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "librosa": librosa.__version__,
        },
        "implementation": {"backend": "librosa.cqt", "res_type": "soxr_hq", "norm": 1, "scale": True},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if cache_lineage is not None:
        manifest["cache_lineage"] = cache_lineage
    return manifest


def geometry_evidence(config: CQTConfig, sr: int) -> dict[str, Any]:
    freqs = config.frequencies()
    windows = config.nominal_window_samples(sr)
    return {
        "bins_per_octave": config.bins_per_octave,
        "adjacent_ratio": float(2 ** (1 / config.bins_per_octave)),
        "semitone_bins": config.bins_per_octave / 12,
        "octave_bins": config.bins_per_octave,
        "q_factor": config.q_factor,
        "lowest_frequency_hz": float(freqs[0]),
        "highest_frequency_hz": float(freqs[-1]),
        "nominal_window_low_ms": float(1000 * windows[0] / sr),
        "nominal_window_a4_ms": float(1000 * windows[int(np.argmin(np.abs(freqs - 440.0)))] / sr),
        "nominal_window_high_ms": float(1000 * windows[-1] / sr),
    }


def observation_evidence(obs: CQTObservation, top_n: int = 8) -> dict[str, Any]:
    peaks = local_peaks_from_mean(obs)[:top_n]
    return {
        "status": obs.status,
        "notes": list(obs.notes),
        "top_mean_peaks": [
            {"bin": int(k), "frequency_hz": f, "mean_power": p}
            for k, f, p in peaks
        ],
    }


def save_case(
    samples: np.ndarray,
    sr: int,
    config: CQTConfig,
    obs: CQTObservation,
    sketch: LogFrequencySketch,
    out_dir: str | Path,
    git_commit: str | None = None,
) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "mamse002_manifest.json"
    npz_path = out / "mamse002_logfreq_sketch.npz"
    evidence_path = out / "log_frequency_evidence.json"

    manifest = build_manifest(samples, sr, config, sketch, git_commit=git_commit)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    np.savez_compressed(
        npz_path,
        times_s=sketch.times_s,
        values=sketch.values,
        frequencies_hz=obs.frequencies_hz,
    )

    evidence = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "source_sha256": manifest["source_sha256"],
        "geometry": geometry_evidence(config, sr),
        "observation": observation_evidence(obs),
        "sketch_status": sketch.status,
        "interpretation_policy": [
            "dominant_midi 是估计量，不等于感知音高",
            "chroma 不等于和声理解",
            "tuning deviation 不等于认证调音器",
            "log-frequency 特征不直接映射为艺术好坏",
        ],
    }
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"manifest": manifest_path, "npz": npz_path, "evidence": evidence_path}


def load_case(json_path: str | Path, npz_path: str | Path) -> dict[str, Any]:
    manifest = json.loads(Path(json_path).read_text(encoding="utf-8"))
    loaded = np.load(npz_path)
    return {
        "manifest": manifest,
        "times_s": loaded["times_s"],
        "values": loaded["values"],
        "frequencies_hz": loaded["frequencies_hz"],
    }
