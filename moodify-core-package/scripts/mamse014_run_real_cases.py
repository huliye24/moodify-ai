"""Run MAMSE-014 on real cases and emit evidence.

Usage: python scripts/mamse014_run_real_cases.py <source.wav ...> --out <dir>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse014 import (
    DEFAULT_CONFIG,
    build_masking_sketch,
    compute_masking_observation,
    save_case,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    summary = []
    for source in args.sources:
        path = Path(source)
        samples, sr = sf.read(path, dtype="float32", always_2d=False)
        if samples.ndim > 1:
            samples = samples.mean(axis=1)
        samples = np.ascontiguousarray(samples, dtype=np.float32)

        obs = compute_masking_observation(samples, sr, DEFAULT_CONFIG)
        sketch = build_masking_sketch(obs, DEFAULT_CONFIG)
        case_dir = out_root / f"{path.stem}_mamse014"
        save_case(samples, sr, DEFAULT_CONFIG, obs, sketch, case_dir)
        summary.append({
            "source": path.name,
            "duration_s": round(float(len(samples) / sr), 2),
            "status": obs.status,
            "masked_channel_ratio_mean": obs.masked_channel_ratio_mean,
            "n_events": len(obs.events),
            "events": [event.to_dict() for event in obs.events],
            "track_features": sketch.track_features,
        })
        print(f"ok {path.name} -> {case_dir}")

    (out_root / "mamse014_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
