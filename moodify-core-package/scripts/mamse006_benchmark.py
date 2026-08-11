"""MAMSE-006 resource benchmark: wall/CPU/artifact size vs duration.

Usage: python scripts/mamse006_benchmark.py <wav> <out.json>
Measures 10 s / 30 s / 45 s slices (mono downmix, 48 kHz).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse006 import ModulationConfig, run_mamse006, save_evidence


def measure(samples: np.ndarray, sr: int, label: str, cfg: ModulationConfig, workdir: Path) -> dict:
    t0 = time.perf_counter()
    cpu0 = time.process_time()
    summary, arrays = run_mamse006(samples, cfg)
    cpu1 = time.process_time()
    wall = time.perf_counter() - t0
    j, n = save_evidence(summary, arrays, workdir / label)
    return {
        "label": label,
        "duration_s": round(len(samples) / sr, 3),
        "wall_time_s": round(wall, 3),
        "cpu_time_s": round(cpu1 - cpu0, 3),
        "profile_hash": cfg.profile_hash[:16],
        "status": summary["status"],
        "log_frequency_bins": summary.get("log_frequency_bins"),
        "modulation_segments": summary.get("modulation_segments"),
        "temporal_peak_hz": summary.get("temporal_peak_hz"),
        "spectral_peak_cpo": summary.get("spectral_peak_cpo"),
        "json_bytes": j.stat().st_size,
        "npz_bytes": n.stat().st_size if n else 0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out_json")
    args = ap.parse_args()

    samples, sr = sf.read(args.wav, always_2d=True)
    samples = samples.astype(np.float32).mean(axis=1)
    cfg = ModulationConfig(sample_rate=sr)
    results = {"schema_version": "mamse-006-benchmark-v1", "source": args.wav, "sample_rate": sr,
               "profile_hash": cfg.profile_hash, "measurements": []}
    workdir = Path(args.out_json).with_suffix("")
    workdir.mkdir(parents=True, exist_ok=True)
    for secs in (10, 30, 45):
        if len(samples) < sr * secs:
            continue
        results["measurements"].append(measure(samples[: sr * secs], sr, f"{secs}s", cfg, workdir))

    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:230])


if __name__ == "__main__":
    main()
