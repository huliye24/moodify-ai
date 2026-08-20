"""MAMSE-015 evidence contract: manifest + NPZ sketch + object evidence."""

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
    SoftObjectConfig,
)
from .objects import SoftObjectObservation
from .sketch import SoftObjectSketch, FEATURE_AUTHORITY


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
    config: SoftObjectConfig,
    sketch: SoftObjectSketch,
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
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "feature_authority": FEATURE_AUTHORITY,
        "frame_count": int(len(sketch.times_s)),
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "librosa": __import__("librosa").__version__,
        },
        "implementation": {
            "backend": "librosa-cues",
            "model": "soft-role-cues-v0.1",
            "model_status": "probabilistic_estimator",
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def geometry_evidence(config: SoftObjectConfig, sr: int) -> dict[str, Any]:
    return {
        "hypotheses": ["TONAL_CORE", "NOISE_TEXTURE", "PERCUSSIVE", "UNRESOLVED"],
        "hop_length": config.hop_length,
        "n_fft": config.n_fft,
        "label_confidence_gate": config.label_confidence_gate,
        "min_region_frames": config.min_region_frames,
        "max_objects": config.max_objects,
        "cue_model": "flatness/centroid/flux sigmoid gates",
    }


def observation_evidence(obs: SoftObjectObservation) -> dict[str, Any]:
    return {
        "status": obs.status,
        "notes": list(obs.notes),
        "unresolved_fraction": obs.unresolved_fraction,
        "mean_confidence": obs.mean_confidence,
        "objects": [obj.to_dict() for obj in obs.objects],
    }


def save_case(
    samples: np.ndarray,
    sr: int,
    config: SoftObjectConfig,
    obs: SoftObjectObservation,
    sketch: SoftObjectSketch,
    out_dir: str | Path,
    git_commit: str | None = None,
) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "mamse015_manifest.json"
    npz_path = out / "mamse015_soft_object_sketch.npz"
    evidence_path = out / "soft_object_evidence.json"

    manifest = build_manifest(samples, sr, config, sketch, git_commit=git_commit)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    np.savez_compressed(
        npz_path,
        times_s=sketch.times_s,
        values=sketch.values,
        frame_probabilities=obs.frame_probabilities,
        frame_unresolved=obs.frame_unresolved,
        frame_labels=obs.frame_labels,
    )

    evidence_path.write_text(
        json.dumps(observation_evidence(obs), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"manifest": manifest_path, "npz": npz_path, "evidence": evidence_path}


def load_case(case_dir: str | Path) -> dict[str, Any]:
    case_dir = Path(case_dir)
    manifest = json.loads((case_dir / "mamse015_manifest.json").read_text(encoding="utf-8"))
    npz = np.load(case_dir / "mamse015_soft_object_sketch.npz")
    evidence = json.loads((case_dir / "soft_object_evidence.json").read_text(encoding="utf-8"))
    return {
        "manifest": manifest,
        "times_s": npz["times_s"],
        "values": npz["values"],
        "frame_probabilities": npz["frame_probabilities"],
        "frame_unresolved": npz["frame_unresolved"],
        "frame_labels": npz["frame_labels"],
        "evidence": evidence,
    }
