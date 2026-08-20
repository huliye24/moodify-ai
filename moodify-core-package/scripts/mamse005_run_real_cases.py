"""Run MAMSE-005 on real cases and emit evidence.

Usage: python scripts/mamse005_run_real_cases.py <source.wav ...> --out <dir>
Full-length stereo files (mono downmix); saves cepstrum_evidence.json +
mamse005_cepstrum.npz + mamse005_manifest.json per case, plus summary.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse005 import CepstrumConfig, analyze_cepstral_structure, save_result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"schema_version": "mamse-005-real-cases-v1", "cases": []}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        result = analyze_cepstral_structure(samples, sr, CepstrumConfig())
        save_result(result, case_dir)
        s = result["summary"]
        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "source_sha256": s["source_sha256"],
            "availability": s["availability"],
            "frame_count": s["frame_count"],
            "periodicity_available_ratio": s["periodicity_available_ratio"],
            "median_f0_candidate_hz": s["median_f0_candidate_hz"],
            "median_periodicity_score": s["median_periodicity_score"],
            "spectral_envelope_roughness": s["spectral_envelope_roughness"],
            "raw_log_spectrum_roughness": s["raw_log_spectrum_roughness"],
            "fine_to_envelope_energy_ratio": s["fine_to_envelope_energy_ratio"],
            "runtime_seconds": s["runtime_seconds"],
        }
        summary["cases"].append(entry)
        print(f"done {case_name}: avail={s['availability']} f0={s['median_f0_candidate_hz']} "
              f"p_ratio={s['periodicity_available_ratio']:.3f} env_rough={s['spectral_envelope_roughness']:.3f}")

    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
