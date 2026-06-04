#!/usr/bin/env python3
"""MHP-078: Calibration Pipeline — process samples, compute MRS, record gates.

Processes all samples in the calibration dataset through their genre-appropriate
presets. Computes before/after MRS (pseudo + MRS Open). Applies graduated
over_dark detection and genre-specific gate thresholds.

Output:
    outputs/nem_mrs_002/calibration_run/
    ├── manifest.csv
    ├── gate_decisions.jsonl
    ├── metrics.jsonl
    ├── over_dark.jsonl
    └── summary.json
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from moodify_runtime.metrics import (
    analyze_wav_stdlib,
    pseudo_mrs,
    compute_mrs_open_v031,
    compare_before_after,
)
from moodify_runtime.over_dark import detect_over_dark
from moodify_runtime.operator_console import decide_candidate_gate
from moodify_runtime.config import RuntimeConfig


PROJECT = Path(__file__).resolve().parent.parent
GENRE_PRESET = {
    "electronic": "clean_master",
    "piano": "warm_vocal",
    "vocal": "warm_vocal",
    "rock": "wide_space",
    "ambient": "wide_space",
}


def process_one(
    source_wav: Path,
    preset: str,
    output_dir: Path,
    timeout: int = 120,
) -> Tuple[bool, str]:
    """Run moodify.cli process on a single WAV file. Returns (success, error)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python3", "-m", "moodify.cli", "process",
        str(source_wav),
        "--output-dir", str(output_dir),
        "--preset", preset,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            timeout=timeout,
            cwd=str(PROJECT),
        )
        ok = result.returncode == 0
        error = result.stderr.strip()[-500:] if not ok else ""
        return ok, error
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def run_pipeline(registry_path: Path, output_root: Path):
    """Main calibration pipeline."""
    output_root.mkdir(parents=True, exist_ok=True)

    # Load registry
    registry = []
    with registry_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                registry.append(json.loads(line))

    print(f"# Calibration Pipeline — {len(registry)} samples")
    print(f"# Output: {output_root}")
    print()

    manifest_rows: List[Dict[str, Any]] = []
    gate_decisions: List[Dict[str, Any]] = []
    metrics_rows: List[Dict[str, Any]] = []
    over_dark_rows: List[Dict[str, Any]] = []

    success_count = 0
    fail_count = 0

    for i, entry in enumerate(registry):
        sid = entry["sample_id"]
        genre = entry["genre"]
        preset = GENRE_PRESET.get(genre, "clean_master")
        source_rel = entry["path"]
        source_path = PROJECT / "data" / "calibration" / "mrs_002" / source_rel

        if not source_path.exists():
            print(f"[{i+1}/{len(registry)}] {sid} SKIP — source not found: {source_path}")
            continue

        # Process directory
        proc_dir = output_root / sid / preset
        proc_dir.mkdir(parents=True, exist_ok=True)

        # ── Process audio ──
        ok, error = process_one(source_path, preset, proc_dir, timeout=120)
        status = "done" if ok else "failed"

        # ── Compute before metrics ──
        before_metrics = analyze_wav_stdlib(source_path)
        before_pseudo = pseudo_mrs(before_metrics) or 0.0
        mrs_before = compute_mrs_open_v031(str(source_path))

        # ── Compute after metrics ──
        after_wavs = sorted(proc_dir.glob("*.wav"))
        after_metrics = {}
        after_pseudo = 0.0
        after_path = ""
        mrs_after = {}
        mrs_delta = None
        mrs_open_delta = None

        if after_wavs:
            after_path = str(after_wavs[0])
            after_metrics = analyze_wav_stdlib(after_wavs[0])
            after_pseudo = pseudo_mrs(after_metrics) or 0.0
            mrs_after = compute_mrs_open_v031(after_path)
            if mrs_before.get("mrs_open") is not None and mrs_after.get("mrs_open") is not None:
                mrs_open_delta = mrs_after["mrs_open"] - mrs_before["mrs_open"]

        pseudo_delta = after_pseudo - before_pseudo
        mrs_delta = pseudo_delta  # default to pseudo for gate decisions

        # ── Over-dark detection ──
        od_result = detect_over_dark(str(source_path), after_path, genre=genre) if after_path else None
        od_dict = od_result.to_dict() if od_result else {"level": "none", "score": 0.0}

        # ── Gate decision ──
        gate = decide_candidate_gate(
            candidate_id=f"{sid}_{preset}",
            job_id=f"CALIBRATION_{sid}",
            runtime_success=ok,
            mrs_score_delta=mrs_delta,
            over_dark_level=od_dict.get("level", "none"),
            genre=genre,
        )

        # ── Record ──
        manifest_rows.append({
            "sample_id": sid,
            "genre": genre,
            "preset": preset,
            "status": status,
            "error": error[:200] if error else "",
            "before_pseudo_mrs": round(before_pseudo, 2),
            "after_pseudo_mrs": round(after_pseudo, 2),
            "pseudo_delta": round(pseudo_delta, 2),
            "mrs_open_before": mrs_before.get("mrs_open"),
            "mrs_open_after": mrs_after.get("mrs_open") if mrs_after else None,
            "mrs_open_delta": round(mrs_open_delta, 4) if mrs_open_delta is not None else None,
            "over_dark_level": od_dict.get("level", "none"),
            "over_dark_score": od_dict.get("score", 0.0),
            "gate_decision": gate["decision"],
            "gate_reasons": ",".join(gate["reasons"]),
            "source": source_rel,
        })

        gate_decisions.append(gate)
        metrics_rows.append({
            "sample_id": sid,
            "genre": genre,
            "preset": preset,
            "before_pseudo": before_pseudo,
            "after_pseudo": after_pseudo,
            "pseudo_delta": pseudo_delta,
            "mrs_open_before": mrs_before.get("mrs_open"),
            "mrs_open_after": mrs_after.get("mrs_open") if mrs_after else None,
            "mrs_open_delta": mrs_open_delta,
        })

        od_dict["sample_id"] = sid
        over_dark_rows.append(od_dict)

        if ok:
            success_count += 1
            tag = gate["decision"][:4]
        else:
            fail_count += 1
            tag = "FAIL"

        print(f"[{i+1:3d}/{len(registry)}] {sid} | {genre:12s} | {preset:15s} | "
              f"pΔ={pseudo_delta:+6.2f} | od={od_dict['level']:6s} | GATE:{tag}")

    # ── Write outputs ──
    # manifest.csv
    fieldnames = list(manifest_rows[0].keys()) if manifest_rows else []
    manifest_path = output_root / "manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(manifest_rows)

    # gate_decisions.jsonl
    with (output_root / "gate_decisions.jsonl").open("w", encoding="utf-8") as f:
        for g in gate_decisions:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")

    # metrics.jsonl
    with (output_root / "metrics.jsonl").open("w", encoding="utf-8") as f:
        for m in metrics_rows:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    # over_dark.jsonl
    with (output_root / "over_dark.jsonl").open("w", encoding="utf-8") as f:
        for o in over_dark_rows:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

    # summary.json
    gate_counts = defaultdict(int)
    for g in gate_decisions:
        gate_counts[g["decision"]] += 1
    od_counts = defaultdict(int)
    for o in over_dark_rows:
        od_counts[o.get("level", "none")] += 1

    summary = {
        "run_id": f"calibration_{uuid.uuid4().hex[:8]}",
        "total_samples": len(registry),
        "processed": success_count,
        "failed": fail_count,
        "gate_counts": dict(gate_counts),
        "over_dark_counts": dict(od_counts),
        "per_genre": {},
    }

    # Per-genre stats
    for genre in ["electronic", "piano", "vocal", "rock", "ambient"]:
        genre_rows = [r for r in manifest_rows if r["genre"] == genre]
        if not genre_rows:
            continue
        deltas = [r["pseudo_delta"] for r in genre_rows if r["status"] == "done"]
        gates = [r["gate_decision"] for r in genre_rows]
        summary["per_genre"][genre] = {
            "count": len(genre_rows),
            "success": sum(1 for r in genre_rows if r["status"] == "done"),
            "mean_pseudo_delta": round(sum(deltas) / len(deltas), 2) if deltas else 0,
            "approve": gates.count("approve"),
            "reprocess": gates.count("reprocess"),
            "reject": gates.count("reject"),
        }

    summary_path = output_root / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    print()
    print(f"=== Pipeline Complete ===")
    print(f"  Processed: {success_count}/{len(registry)}")
    print(f"  Failed: {fail_count}")
    print(f"  Gates: approve={gate_counts.get('approve',0)} reprocess={gate_counts.get('reprocess',0)} reject={gate_counts.get('reject',0)}")
    print(f"  Manifest: {manifest_path}")
    print(f"  Summary: {summary_path}")

    return summary, manifest_rows, metrics_rows


if __name__ == "__main__":
    registry_path = PROJECT / "data" / "calibration" / "mrs_002" / "registry.jsonl"
    output_root = PROJECT / "outputs" / "nem_mrs_002" / "calibration_run"

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-samples", type=int, default=0, help="Limit samples (0=all)")
    ap.add_argument("--registry", default=str(registry_path))
    ap.add_argument("--output", default=str(output_root))
    args = ap.parse_args()

    run_pipeline(Path(args.registry), Path(args.output))
