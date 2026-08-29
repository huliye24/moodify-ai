"""Run MAMSE-009 on real cases with canonical-event overlap report.

Usage: python scripts/mamse009_run_real_cases.py <source.wav ...> --out <dir>
Input = S1 band-energy ratios (audited space). Emits RPCA evidence +
an overlap report between SPARSE_STRUCTURE_CANDIDATE intervals and
canonical temporal-hearing events (coexist, never overwrite).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.events.engine import run_temporal_hearing
from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse009 import RPCAConfig, event_overlap_report, principal_component_pursuit, save_result

BAND_COLS = ("band_sub", "band_bass", "band_low_mid", "band_mid", "band_core_mid",
             "band_presence", "band_brilliance", "band_air")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"schema_version": "mamse-009-real-cases-v1", "input": "S1 band-energy ratios", "cases": []}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        rep = build_representation(samples, sr, source_sha256=f"real:{case_name}")
        plane = rep.planes["S1"]
        names = list(plane.feature_names)
        idx = [names.index(c) for c in BAND_COLS]
        V = np.asarray(plane.values, dtype=np.float64)[:, idx].T
        hop_ms = plane.hop_ms
        n_frames = V.shape[1]
        frame_times_s = np.arange(n_frames) * hop_ms / 1000.0

        r = principal_component_pursuit(V, RPCAConfig(max_iter=1000), space_id=f"real:{case_name}")
        save_result(r, V, case_dir, space_id=f"real:{case_name}", frame_times_s=frame_times_s)
        summary_json = json.loads((case_dir / "rpca_summary.json").read_text(encoding="utf-8"))
        candidates = summary_json["candidate_intervals"]

        hearing = run_temporal_hearing(samples, sr)
        events = [e.to_dict() if hasattr(e, "to_dict") else e for e in hearing.events]
        overlap = event_overlap_report(candidates, events)

        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "input": "S1 band-energy ratios",
            "features": int(V.shape[0]),
            "frames": int(V.shape[1]),
            "model_id": r.model_id,
            "converged": r.converged,
            "iterations": r.iterations,
            "rank_L": r.rank_L,
            "sparsity_S": r.sparsity_S,
            "relative_constraint_error": r.relative_constraint_error,
            "runtime_seconds": r.runtime_seconds,
            "candidate_count": len(candidates),
            "candidates": candidates,
            "canonical_event_count": len(events),
            "overlap": overlap,
        }
        summary["cases"].append(entry)
        (case_dir / "overlap_report.json").write_text(
            json.dumps(overlap, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"done {case_name}: cand={len(candidates)} events={len(events)} rank={r.rank_L} "
              f"sparsity={r.sparsity_S:.4f} runtime={r.runtime_seconds:.3f}s")

    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
