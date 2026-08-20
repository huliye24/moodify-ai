"""MAMSE-013 evidence contract: manifest + NPZ sketch + ERB evidence.

Manifest carries operator/geometry/config hash, source identity, runtime
versions, feature schema version and the perceptual-view boundary
(descriptor, not psychoacoustic truth).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .config import (
    EVIDENCE_SCHEMA_VERSION,
    FEATURE_SCHEMA_VERSION,
    MANIFEST_SCHEMA_VERSION,
    ERBConfig,
    erb_bandwidth_hz,
)
from .gammatone import ErbObservation
from .sketch import ErbSketch, FEATURE_AUTHORITY


def source_sha256(samples: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(samples).tobytes()).hexdigest()


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
    config: ERBConfig,
    sketch: ErbSketch,
    git_commit: str | None = None,
) -> dict[str, Any]:
    return {
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
        "window_samples": config.window_samples,
        "fmin_hz": config.fmin_hz,
        "fmax_hz": config.fmax_hz,
        "n_channels": config.n_channels,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "feature_authority": FEATURE_AUTHORITY,
        "frame_count": int(len(sketch.times_s)),
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
        },
        "implementation": {
            "backend": "gammatone-ir-fftconvolve",
            "filter_normalization": "unit_peak_gain",
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def geometry_evidence(config: ERBConfig, sr: int) -> dict[str, Any]:
    channels = config.center_frequencies()
    bw = config.bandwidth_scale * erb_bandwidth_hz(channels)
    return {
        "n_channels": config.n_channels,
        "spacing_erb_steps": 1.0 / config.channels_per_erb,
        "lowest_frequency_hz": float(channels[0]),
        "highest_frequency_hz": float(channels[-1]),
        "erb_bandwidth_lowest_hz": float(bw[0]),
        "erb_bandwidth_high_hz": float(bw[-1]),
        "filter_gain": "unit_peak_normalized",
        "gamma_order": config.gamma_order,
    }


def observation_evidence(obs: ErbObservation, top_n: int = 5) -> dict[str, Any]:
    order = np.argsort(obs.mean_channel_power)[::-1][:top_n]
    return {
        "status": obs.status,
        "notes": list(obs.notes),
        "top_channels": [
            {
                "channel": int(k),
                "frequency_hz": float(obs.center_frequencies_hz[k]),
                "mean_power": float(obs.mean_channel_power[k]),
            }
            for k in order
        ],
    }


def save_case(
    samples: np.ndarray,
    sr: int,
    config: ERBConfig,
    obs: ErbObservation,
    sketch: ErbSketch,
    out_dir: str | Path,
    git_commit: str | None = None,
) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "mamse013_manifest.json"
    npz_path = out / "mamse013_erb_sketch.npz"
    evidence_path = out / "erb_evidence.json"

    manifest = build_manifest(samples, sr, config, sketch, git_commit=git_commit)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    np.savez_compressed(
        npz_path,
        times_s=sketch.times_s,
        values=sketch.values,
        channel_energies=obs.channel_energies,
        center_frequencies_hz=obs.center_frequencies_hz,
        mean_channel_power=obs.mean_channel_power,
    )

    evidence_path.write_text(
        json.dumps(observation_evidence(obs), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"manifest": manifest_path, "npz": npz_path, "evidence": evidence_path}


def load_case(case_dir: str | Path) -> dict[str, Any]:
    case_dir = Path(case_dir)
    manifest = json.loads((case_dir / "mamse013_manifest.json").read_text(encoding="utf-8"))
    npz = np.load(case_dir / "mamse013_erb_sketch.npz")
    evidence = json.loads((case_dir / "erb_evidence.json").read_text(encoding="utf-8"))
    return {
        "manifest": manifest,
        "times_s": npz["times_s"],
        "values": npz["values"],
        "channel_energies": npz["channel_energies"],
        "center_frequencies_hz": npz["center_frequencies_hz"],
        "mean_channel_power": npz["mean_channel_power"],
        "evidence": evidence,
    }
