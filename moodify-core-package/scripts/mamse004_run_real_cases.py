"""Run MAMSE-004 on real cases and emit evidence.

Usage: python scripts/mamse004_run_real_cases.py <source.wav ...> --out <dir>
Full-length stereo files; saves phase_geometry_evidence.json +
mamse004_phase_geometry.npz + mamse004_manifest.json per case, plus a
summary.json comparing phase descriptors across cases.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse004 import PhaseGeometryConfig, analyze_phase_geometry, save_result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"schema_version": "mamse-004-real-cases-v1", "cases": []}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        result = analyze_phase_geometry(samples, sr, PhaseGeometryConfig())
        save_result(result, case_dir)
        mono = result["summary"]["mono"]
        stereo = result["summary"]["stereo"]
        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "source_sha256": result["summary"]["source_sha256"],
            "mono": mono,
            "stereo": stereo,
            "runtime_seconds": result["summary"]["runtime_seconds"],
        }
        summary["cases"].append(entry)
        gd = mono["group_delay_median_ms"]
        icd = stereo["interchannel_delay_median_ms"]
        gcc = stereo["gcc_phat_delay_ms"]
        print(f"done {case_name}: gd_median={gd}ms icd={icd}ms gcc={gcc}ms valid={mono['valid_bin_ratio']:.3f}")

    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
