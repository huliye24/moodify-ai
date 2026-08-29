"""MAMSE-016 evidence contract: manifest + NPZ sketch + pitch evidence."""

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
    PitchConfig,
)
from .pitch import PitchObservation
from .sketch import PitchSketch, FEATURE_AUTHORITY


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
    config: PitchConfig,
    sketch: PitchSketch,
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
        "frame_samples": config.frame_samples,
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
            "backend": "yin-lite-acf",
            "model": "multi-candidate-f0-v0.1",
            "model_status": "probabilistic_estimator",
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def geometry_evidence(config: PitchConfig, sr: int) -> dict[str, Any]:
    lo, hi = config.lag_range(sr)
    return {
        "fmin_hz": config.fmin_hz,
        "fmax_hz": config.fmax_hz,
        "lag_range_samples": [lo, hi],
        "cmndf_threshold": config.cmndf_threshold,
        "max_candidates": config.max_candidates,
        "event_min_frames": config.event_min_frames,
        "event_stability_cents": config.event_stability_cents,
    }


def observation_evidence(obs: PitchObservation, top_candidates: int = 3) -> dict[str, Any]:
    voiced_frames = np.where(obs.voiced)[0]
    peaks = []
    if voiced_frames.size:
        order = np.argsort(obs.confidence[voiced_frames])[::-1][:top_candidates]
        for idx in order:
            frame_i = int(voiced_frames[idx])
            peaks.append({
                "frame": frame_i,
                "time_s": float(obs.times_s[frame_i]),
                "frequency_hz": float(obs.dominant_f0[frame_i]),
                "confidence": float(obs.confidence[frame_i]),
            })
    return {
        "status": obs.status,
        "notes": list(obs.notes),
        "voicing_fraction": obs.voicing_fraction,
        "harmonic_consistency_mean": obs.harmonic_consistency_mean,
        "top_voiced_frames": peaks,
        "events": [event.to_dict() for event in obs.events],
    }


def save_case(
    samples: np.ndarray,
    sr: int,
    config: PitchConfig,
    obs: PitchObservation,
    sketch: PitchSketch,
    out_dir: str | Path,
    git_commit: str | None = None,
) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "mamse016_manifest.json"
    npz_path = out / "mamse016_pitch_sketch.npz"
    evidence_path = out / "pitch_evidence.json"

    manifest = build_manifest(samples, sr, config, sketch, git_commit=git_commit)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    np.savez_compressed(
        npz_path,
        times_s=sketch.times_s,
        values=sketch.values,
        voiced=obs.voiced,
        dominant_f0=obs.dominant_f0,
        confidence=obs.confidence,
        harmonic_support=obs.harmonic_support,
    )

    evidence_path.write_text(
        json.dumps(observation_evidence(obs), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"manifest": manifest_path, "npz": npz_path, "evidence": evidence_path}


def load_case(case_dir: str | Path) -> dict[str, Any]:
    case_dir = Path(case_dir)
    manifest = json.loads((case_dir / "mamse016_manifest.json").read_text(encoding="utf-8"))
    npz = np.load(case_dir / "mamse016_pitch_sketch.npz")
    evidence = json.loads((case_dir / "pitch_evidence.json").read_text(encoding="utf-8"))
    return {
        "manifest": manifest,
        "times_s": npz["times_s"],
        "values": npz["values"],
        "voiced": npz["voiced"],
        "dominant_f0": npz["dominant_f0"],
        "confidence": npz["confidence"],
        "harmonic_support": npz["harmonic_support"],
        "evidence": evidence,
    }
