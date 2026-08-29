"""MAMSE-001 resource benchmark (T8): wall/CPU time, RSS, swap delta, payload.

Usage: python scripts/mamse001_benchmark.py <wav> <out.json>
Measures 10 s / 45 s / full-length slices of the same source.
"""

from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse001 import build_manifest, compute_multiresolution_sketch, save_case


def _swap_kb() -> float:
    try:
        with open("/proc/meminfo") as f:
            lines = {k.strip(): v for k, v in (ln.split(":") for ln in f)}
        used = int(lines["SwapTotal"].split()[0]) - int(lines["SwapFree"].split()[0])
        return used
    except Exception:
        return float("nan")


def measure(samples: np.ndarray, sr: int, label: str, out_dir: Path) -> dict:
    before_swap = _swap_kb()
    t0 = time.perf_counter()
    cpu0 = time.process_time()
    rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    multi = compute_multiresolution_sketch(samples, sr)
    manifest = build_manifest(multi)
    paths = save_case(multi, out_dir / label)
    cpu1 = time.process_time()
    wall = time.perf_counter() - t0
    rss1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    after_swap = _swap_kb()

    artifact_bytes = sum(p.stat().st_size for p in paths.values())
    return {
        "label": label,
        "duration_s": round(multi["duration_s"], 3),
        "wall_time_s": round(wall, 3),
        "cpu_time_s": round(cpu1 - cpu0, 3),
        "peak_rss_kb": rss1,
        "rss_delta_kb": rss1 - rss0,
        "swap_before_kb": before_swap,
        "swap_after_kb": after_swap,
        "swap_delta_kb": after_swap - before_swap,
        "artifact_bytes": artifact_bytes,
        "frames_per_resolution": {rid: sk["n_frames"] for rid, sk in multi["resolutions"].items()},
        "payload_bytes_per_resolution": {rid: sk["payload_bytes"] for rid, sk in multi["resolutions"].items()},
        "manifest": {
            "operator_id": manifest["operator_id"],
            "operator_version": manifest["operator_version"],
            "git_commit": manifest["git_commit"],
            "python": manifest["runtime"]["python"],
            "numpy": manifest["runtime"]["numpy"],
            "scipy": manifest["runtime"]["scipy"],
            "fft_backend": manifest["fft_backend"],
            "resolution_registry_hash": manifest["resolution_registry"]["hash"],
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out_json")
    args = ap.parse_args()

    samples, sr = sf.read(args.wav, always_2d=True)
    samples = samples.astype(np.float32)
    full = samples
    out_dir = Path(args.out_json).parent

    results = {
        "schema_version": "mamse-001-benchmark-v1",
        "source": args.wav,
        "sample_rate": sr,
        "measurements": [
            measure(full[: sr * 10], sr, "slice_10s", out_dir),
            measure(full[: sr * 45], sr, "slice_45s", out_dir),
            measure(full, sr, "full", out_dir),
        ],
    }
    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:240])


if __name__ == "__main__":
    main()
