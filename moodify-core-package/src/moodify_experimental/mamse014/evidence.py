"""MAMSE-014 evidence contract: manifest + NPZ sketch + masking evidence."""

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
    MaskConfig,
)
from .masking import MaskingObservation
from .sketch import MaskingSketch, FEATURE_AUTHORITY


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
    config: MaskConfig,
    sketch: MaskingSketch,
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
        "n_channels": config.n_channels,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "feature_authority": FEATURE_AUTHORITY,
        "frame_count": int(len(sketch.times_s)),
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
        },
        "implementation": {
            "backend": "stft-erb-channel-masking",
            "model": "spreading-masking-v0.1",
            "model_status": "probabilistic_estimator",
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def geometry_evidence(config: MaskConfig, sr: int) -> dict[str, Any]:
    centers = config.center_frequencies()
    return {
        "n_channels": config.n_channels,
        "lowest_frequency_hz": float(centers[0]),
        "highest_frequency_hz": float(centers[-1]),
        "slope_db_per_erb": config.slope_db_per_erb,
        "offset_db": config.offset_db,
        "soft_range_db": config.soft_range_db,
        "event_ratio_threshold": config.event_ratio_threshold,
        "event_min_frames": config.event_min_frames,
    }


def observation_evidence(obs: MaskingObservation) -> dict[str, Any]:
    return {
        "status": obs.status,
        "notes": list(obs.notes),
        "depth_mean": obs.depth_mean,
        "depth_p95": obs.depth_p95,
        "masked_channel_ratio_mean": obs.masked_channel_ratio_mean,
        "strongest_masker_frequency_hz": obs.strongest_masker_frequency_hz,
        "events": [event.to_dict() for event in obs.events],
    }


def save_case(
    samples: np.ndarray,
    sr: int,
    config: MaskConfig,
    obs: MaskingObservation,
    sketch: MaskingSketch,
    out_dir: str | Path,
    git_commit: str | None = None,
) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "mamse014_manifest.json"
    npz_path = out / "mamse014_masking_sketch.npz"
    evidence_path = out / "masking_evidence.json"

    manifest = build_manifest(samples, sr, config, sketch, git_commit=git_commit)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    np.savez_compressed(
        npz_path,
        times_s=sketch.times_s,
        values=sketch.values,
        channel_power_db=obs.channel_power_db,
        masked_threshold_db=obs.masked_threshold_db,
        audibility=obs.audibility,
        masking_depth=obs.masking_depth,
        masked_channel_ratio=obs.masked_channel_ratio,
    )

    evidence_path.write_text(
        json.dumps(observation_evidence(obs), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"manifest": manifest_path, "npz": npz_path, "evidence": evidence_path}


def load_case(case_dir: str | Path) -> dict[str, Any]:
    case_dir = Path(case_dir)
    manifest = json.loads((case_dir / "mamse014_manifest.json").read_text(encoding="utf-8"))
    npz = np.load(case_dir / "mamse014_masking_sketch.npz")
    evidence = json.loads((case_dir / "masking_evidence.json").read_text(encoding="utf-8"))
    return {
        "manifest": manifest,
        "times_s": npz["times_s"],
        "values": npz["values"],
        "channel_power_db": npz["channel_power_db"],
        "masked_threshold_db": npz["masked_threshold_db"],
        "audibility": npz["audibility"],
        "masking_depth": npz["masking_depth"],
        "masked_channel_ratio": npz["masked_channel_ratio"],
        "evidence": evidence,
    }
