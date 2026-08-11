"""MAMSE-010 resource benchmark: dense bytes, tiles, HOSVD runtime/memory.

Usage: python scripts/mamse010_benchmark.py <wav> <out.json>
Builds the channel-spectral view (TIME x FREQ x CHANNEL) and a
scale-feature view, fits HOSVD, and records shape/dtype/runtime/bytes.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse010 import (
    build_channel_spectral_tensor,
    build_scale_feature_tensor,
    estimate_dense_bytes,
    guard_materialization,
    hosvd,
)

FEATURE_NAMES = ["rms_db", "peak_db", "stereo_correlation", "spectral_centroid_hz",
                 "band_sub", "band_bass", "band_low_mid", "band_mid", "band_core_mid",
                 "band_presence", "band_brilliance", "band_air"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out_json")
    args = ap.parse_args()

    samples, sr = sf.read(args.wav, always_2d=True)
    samples = samples.astype(np.float32)
    rep = build_representation(samples, sr, source_sha256="benchmark")
    planes = {sid: {
        "values": np.asarray(rep.planes[sid].values),
        "feature_names": list(rep.planes[sid].feature_names),
        "window_starts_ms": np.asarray(rep.planes[sid].window_starts_ms),
        "window_ends_ms": np.asarray(rep.planes[sid].window_ends_ms),
    } for sid in ("S0", "S1", "S2")}

    results = {"schema_version": "mamse-010-benchmark-v1", "source": args.wav, "sample_rate": sr,
               "measurements": []}
    workdir = Path(args.out_json).with_suffix("")
    workdir.mkdir(parents=True, exist_ok=True)

    # 1. scale-feature view
    t0 = time.perf_counter()
    sfv = build_scale_feature_tensor(planes, feature_names=FEATURE_NAMES,
                                     duration_ms=int(len(samples) / sr * 1000))
    t_sfv = time.perf_counter() - t0
    results["measurements"].append({
        "label": "scale_feature_view",
        "shape": list(sfv.data.shape),
        "dtype": str(sfv.data.dtype),
        "dense_bytes": estimate_dense_bytes(sfv.data.shape, sfv.data.dtype),
        "valid_fraction": round(float(np.mean(sfv.valid_mask)), 4),
        "build_wall_time_s": round(t_sfv, 4),
    })

    # 2. channel-spectral view + HOSVD
    t0 = time.perf_counter()
    csv = build_channel_spectral_tensor(samples, sr)
    t_view = time.perf_counter() - t0
    bytes_ = estimate_dense_bytes(csv.data.shape, csv.data.dtype)
    guard_materialization(csv.data.shape, csv.data.dtype, max_bytes=1 << 30)
    ranks = (8, 8, 2)
    t0 = time.perf_counter()
    model = hosvd(csv.data, ranks)
    t_hosvd = time.perf_counter() - t0
    rec = model.reconstruct()
    rel = float(np.linalg.norm(csv.data - rec) / np.linalg.norm(csv.data))
    results["measurements"].append({
        "label": "channel_spectral_view",
        "shape": list(csv.data.shape),
        "dtype": str(csv.data.dtype),
        "dense_bytes": bytes_,
        "build_wall_time_s": round(t_view, 4),
        "hosvd_ranks": list(ranks),
        "hosvd_wall_time_s": round(t_hosvd, 4),
        "hosvd_relative_reconstruction_error": round(rel, 6),
        "model_id": model.model_id,
    })

    # 3. materialization guard behavior
    results["measurements"].append({
        "label": "guard_5d_probe",
        "5d_shape": list((10000, 100, 24, 8, 8)),
        "estimated_bytes": estimate_dense_bytes((10000, 100, 24, 8, 8)),
        "guard_max_bytes": 1 << 30,
        "would_raise": estimate_dense_bytes((10000, 100, 24, 8, 8)) > (1 << 30),
    })

    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:240])


if __name__ == "__main__":
    main()
