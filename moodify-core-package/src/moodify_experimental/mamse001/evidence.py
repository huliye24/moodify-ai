"""MAMSE-001 evidence contract: manifest, NPZ planes, cross-resolution evidence.

The manifest records full runtime identity (git commit, Python, numpy/scipy,
FFT backend) so every case can be traced back to the exact implementation.
Cross-resolution observations are preserved — conflicts are listed, never
averaged into a single score.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .registry import (
    EVIDENCE_SCHEMA_VERSION,
    FEATURE_SCHEMA_VERSION,
    OPERATOR_ID,
    OPERATOR_VERSION,
    REGISTRY_VERSION,
    RESOLUTIONS,
    registry_hash,
)
from .sketch import compute_multiresolution_sketch


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5
        )
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _fft_backend_identity() -> dict[str, str]:
    import numpy as _np

    return {
        "backend": "numpy.fft.rfft",
        "numpy_version": _np.__version__,
    }


def _dependency_identity() -> dict[str, str]:
    try:
        import scipy

        scipy_version = scipy.__version__
    except Exception:
        scipy_version = "unavailable"
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy_version,
        "ffmpeg": _ffmpeg_version(),
    }


def _ffmpeg_version() -> str:
    try:
        out = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        return out.stdout.splitlines()[0].split()[2] if out.returncode == 0 else "unavailable"
    except Exception:
        return "unavailable"


def build_manifest(
    multi: dict[str, Any],
    *,
    git_commit: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "mamse-001-manifest-v1",
        "operator_id": OPERATOR_ID,
        "operator_version": OPERATOR_VERSION,
        "source_sha256": multi["source_sha256"],
        "sample_rate": multi["sample_rate"],
        "duration_s": multi["duration_s"],
        "resolution_registry": {
            "version": REGISTRY_VERSION,
            "hash": registry_hash(),
            "resolutions": [asdict(spec) for spec in RESOLUTIONS],
        },
        "window": "hann",
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": _dependency_identity()["scipy"],
            "ffmpeg": _dependency_identity()["ffmpeg"],
        },
        "fft_backend": _fft_backend_identity(),
        "band_source": multi["band_source"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def build_cross_resolution_evidence(multi: dict[str, Any]) -> dict[str, Any]:
    resolutions: dict[str, dict[str, Any]] = multi["resolutions"]
    ids = sorted(resolutions)

    frequency_resolution = {
        rid: {
            "bin_hz": float(resolutions[rid]["bin_hz"]),
            "window_ms": float(resolutions[rid]["window_ms"]),
            "hop_ms": float(resolutions[rid]["hop_ms"]),
            "n_frames": int(resolutions[rid]["n_frames"]),
        }
        for rid in ids
    }

    dominant_medians: dict[str, float | None] = {}
    max_flux: dict[str, float | None] = {}
    max_flux_time_ms: dict[str, float | None] = {}
    payload_bytes: dict[str, int] = {}
    for rid in ids:
        sk = resolutions[rid]
        dom = _column(sk, "dominant_frequency_hz")
        flux = _column(sk, "spectral_flux")
        dominant_medians[rid] = float(np.median(dom)) if len(dom) else None
        if len(flux):
            idx = int(np.argmax(flux))
            max_flux[rid] = float(flux[idx])
            max_flux_time_ms[rid] = float(sk["frame_centers_ms"][idx])
        else:
            max_flux[rid] = None
            max_flux_time_ms[rid] = None
        payload_bytes[rid] = int(sk["payload_bytes"])

    band_names = [n for n in resolutions[ids[0]]["feature_names"] if n.startswith("band_")]
    coarse_id = max(ids, key=lambda rid: resolutions[rid]["window_ms"])
    coarse_times = resolutions[coarse_id]["frame_centers_ms"]
    band_spread: dict[str, dict[str, float | None]] = {}
    for band in band_names:
        per_t: list[float] = []
        for t in coarse_times:
            vals = np.asarray(
                [_nearest_value(resolutions[rid]["frame_centers_ms"], _column(resolutions[rid], band), float(t)) for rid in ids],
                dtype=float,
            )
            if np.all(np.isfinite(vals)):
                mean = float(np.mean(vals))
                per_t.append(float(np.std(vals) / (abs(mean) + 1e-12)))
        band_spread[band] = {
            "median_relative_spread": float(np.median(per_t)) if per_t else None,
            "samples": len(per_t),
        }

    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "source_sha256": multi["source_sha256"],
        "frequency_bin_table_hz": frequency_resolution,
        "dominant_frequency_median_hz": dominant_medians,
        "max_spectral_flux": max_flux,
        "max_spectral_flux_time_ms": max_flux_time_ms,
        "band_cross_resolution_spread": band_spread,
        "conflicts": _conflict_list(resolutions, ids),
        "payload_bytes": payload_bytes,
        "interpretation_policy": [
            "不同 R 分辨率不得平均为单一艺术质量分数",
            "短窗优先支持瞬态定位证据，长窗优先支持窄带/谐波定位证据",
            "跨分辨率冲突保留为证据，不得静默覆盖",
        ],
    }


def _column(sketch: dict[str, Any], name: str) -> np.ndarray:
    names = list(sketch["feature_names"])
    return sketch["values"][:, names.index(name)]


def _nearest_value(times: np.ndarray, values: np.ndarray, t: float) -> float:
    if len(times) == 0:
        return float("nan")
    idx = int(np.argmin(np.abs(times - t)))
    return float(values[idx])


def _conflict_list(
    resolutions: dict[str, dict[str, Any]], ids: list[str]
) -> list[dict[str, Any]]:
    """Explicit cross-resolution conflicts; never flattened into one score."""
    conflicts: list[dict[str, Any]] = []
    coarse_id = max(ids, key=lambda rid: resolutions[rid]["window_ms"])
    fine_id = min(ids, key=lambda rid: resolutions[rid]["window_ms"])
    coarse_times = resolutions[coarse_id]["frame_centers_ms"]
    if len(coarse_times) == 0 or len(resolutions[fine_id]["frame_centers_ms"]) == 0:
        return conflicts

    coarse_dom = _column(resolutions[coarse_id], "dominant_frequency_hz")
    fine_dom = _column(resolutions[fine_id], "dominant_frequency_hz")
    fine_flux = _column(resolutions[fine_id], "spectral_flux")
    for i, t in enumerate(coarse_times):
        fine_dom_at_t = _nearest_value(resolutions[fine_id]["frame_centers_ms"], fine_dom, float(t))
        fine_flux_at_t = _nearest_value(resolutions[fine_id]["frame_centers_ms"], fine_flux, float(t))
        if not np.isfinite(fine_dom_at_t) or not np.isfinite(coarse_dom[i]):
            continue
        # A fine-resolution dominant is far from the coarse dominant while the
        # fine frame is energetic: the two resolutions genuinely disagree.
        if abs(float(fine_dom_at_t) - float(coarse_dom[i])) > 500.0 and float(fine_flux_at_t) > 0.05:
            conflicts.append({
                "time_ms": float(t),
                "coarse_dominant_hz": float(coarse_dom[i]),
                "fine_dominant_hz": float(fine_dom_at_t),
                "fine_flux": float(fine_flux_at_t),
                "resolutions": [fine_id, coarse_id],
            })
    return conflicts


def save_case(multi: dict[str, Any], out_dir: str | Path) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    npz_path = out / "mamse001_planes.npz"
    manifest_path = out / "mamse001_manifest.json"
    cross_path = out / "cross_resolution_evidence.json"

    arrays: dict[str, np.ndarray] = {}
    manifest = {k: v for k, v in multi.items() if k != "resolutions"}
    manifest["resolutions"] = {}
    for rid, sk in multi["resolutions"].items():
        arrays[f"{rid}__values"] = sk["values"]
        arrays[f"{rid}__frame_centers_ms"] = sk["frame_centers_ms"]
        manifest["resolutions"][rid] = {
            k: v for k, v in sk.items() if k not in {"values", "frame_centers_ms"}
        }
        manifest["resolutions"][rid]["array_keys"] = {
            "values": f"{rid}__values",
            "frame_centers_ms": f"{rid}__frame_centers_ms",
        }

    np.savez_compressed(npz_path, **arrays)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    cross_path.write_text(
        json.dumps(build_cross_resolution_evidence(multi), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"manifest": manifest_path, "npz": npz_path, "cross": cross_path}


def load_case(json_path: str | Path, npz_path: str | Path) -> dict[str, Any]:
    manifest = json.loads(Path(json_path).read_text(encoding="utf-8"))
    loaded = np.load(npz_path)
    for rid, sk in manifest["resolutions"].items():
        keys = sk.pop("array_keys")
        sk["values"] = loaded[keys["values"]]
        sk["frame_centers_ms"] = loaded[keys["frame_centers_ms"]]
        sk["feature_names"] = tuple(sk["feature_names"])
    return manifest


def run_case(
    samples: np.ndarray,
    sample_rate: int,
    out_dir: str | Path,
    source_sha256: str | None = None,
) -> dict[str, Any]:
    """One MAMSE-001 case: sketch + manifest + cross-resolution evidence."""
    multi = compute_multiresolution_sketch(samples, sample_rate, source_sha256)
    manifest = build_manifest(multi)
    paths = save_case(multi, out_dir)
    return {"manifest": manifest, "paths": paths}
