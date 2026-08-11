"""Run MAMSE-001 on real cases (T7) and emit evidence under artifacts/mamse_001/real_cases/.

Usage: python scripts/mamse001_run_real_cases.py <source.wav ...> --out <dir>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse001 import (
    build_cross_resolution_evidence,
    build_manifest,
    narrowband_events,
    save_case,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"cases": []}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)

        from moodify_experimental.mamse001 import compute_multiresolution_sketch

        multi = compute_multiresolution_sketch(samples, sr)
        manifest = build_manifest(multi)
        paths = save_case(multi, case_dir)
        cross = build_cross_resolution_evidence(multi)
        events = narrowband_events(multi)

        manifest_path = Path(paths["manifest"])
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        cross_path = case_dir / "cross_resolution_evidence.json"
        cross_path.write_text(json.dumps(cross, ensure_ascii=False, indent=2), encoding="utf-8")
        (case_dir / "mamse001_events.json").write_text(
            json.dumps({"events": events}, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        summary["cases"].append({
            "case": case_name,
            "source": str(path),
            "duration_s": round(multi["duration_s"], 3),
            "sample_rate": sr,
            "source_sha256": multi["source_sha256"],
            "n_frames_per_resolution": {rid: sk["n_frames"] for rid, sk in multi["resolutions"].items()},
            "payload_bytes": {rid: sk["payload_bytes"] for rid, sk in multi["resolutions"].items()},
            "cross": cross,
            "events": events,
        })
        print(f"done {case_name}: {multi['duration_s']:.1f}s {len(events)} narrowband events")

    (out_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
