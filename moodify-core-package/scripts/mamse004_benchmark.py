"""MAMSE-004 resource benchmark: wall/CPU/artifact size vs duration.

Usage: python scripts/mamse004_benchmark.py <wav> <out.json>
Measures 10 s / 30 s / 45 s slices (stereo, 48 kHz).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse004 import PhaseGeometryConfig, analyze_phase_geometry, save_result


def measure(samples: np.ndarray, sr: int, label: str, cfg: PhaseGeometryConfig, workdir: Path) -> dict:
    t0 = time.perf_counter()
    cpu0 = time.process_time()
    result = analyze_phase_geometry(samples, sr, cfg)
    cpu1 = time.process_time()
    wall = time.perf_counter() - t0
    _, npz, manifest = save_result(result, workdir / label)
    return {
        "label": label,
        "duration_s": round(len(samples) / sr, 3),
        "wall_time_s": round(wall, 3),
        "cpu_time_s": round(cpu1 - cpu0, 3),
        "config_hash": cfg.config_hash[:16],
        "mono_valid_bin_ratio": round(result["summary"]["mono"]["valid_bin_ratio"], 4),
        "group_delay_median_ms": result["summary"]["mono"]["group_delay_median_ms"],
        "stereo_ipd_available": result["summary"]["stereo"]["ipd_available"],
        "interchannel_delay_median_ms": result["summary"]["stereo"]["interchannel_delay_median_ms"],
        "gcc_phat_delay_ms": result["summary"]["stereo"]["gcc_phat_delay_ms"],
        "npz_bytes": npz.stat().st_size,
        "manifest_bytes": manifest.stat().st_size,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out_json")
    args = ap.parse_args()

    samples, sr = sf.read(args.wav, always_2d=True)
    samples = samples.astype(np.float32)
    cfg = PhaseGeometryConfig()
    results = {"schema_version": "mamse-004-benchmark-v1", "source": args.wav, "sample_rate": sr,
               "config_hash": cfg.config_hash, "measurements": []}
    workdir = Path(args.out_json).with_suffix("")
    workdir.mkdir(parents=True, exist_ok=True)
    for secs in (10, 30, 45):
        if len(samples) < sr * secs:
            continue
        results["measurements"].append(measure(samples[: sr * secs], sr, f"{secs}s", cfg, workdir))

    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:220])


if __name__ == "__main__":
    main()
