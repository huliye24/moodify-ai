"""Run MAMSE-006 on real cases and emit evidence (no threshold tuning).

Per CODEX section 7, real-case thresholds are deferred to the September
data experiment; this script only records descriptors and evidence.

Usage: python scripts/mamse006_run_real_cases.py <source.wav ...> --out <dir>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse006 import ModulationConfig, run_mamse006, save_evidence


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"schema_version": "mamse-006-real-cases-v1", "cases": []}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32).mean(axis=1)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        s, arrays = run_mamse006(samples, ModulationConfig(sample_rate=sr))
        save_evidence(s, arrays, case_dir)
        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "source_sha256": s["source_sha256"],
            "status": s["status"],
            **{k: s[k] for k in (
                "rms_dbfs", "temporal_peak_hz", "temporal_centroid_hz", "slow_energy_ratio",
                "mid_energy_ratio", "fast_energy_ratio", "temporal_modulation_entropy",
                "spectral_peak_cpo", "diagonal_orientation_index", "ridge",
                "log_frequency_bins", "modulation_segments", "runtime_seconds",
            ) if k in s},
        }
        summary["cases"].append(entry)
        print(f"done {case_name}: status={s['status']} t_peak={s.get('temporal_peak_hz')} "
              f"s_peak={s.get('spectral_peak_cpo')} orient={s.get('diagonal_orientation_index')}")

    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
