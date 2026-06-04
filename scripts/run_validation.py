#!/usr/bin/env python3
"""MHP-061: Validation Run Script — process validation dataset and collect metrics.

Usage:
    python3 scripts/run_validation.py [--samples N] [--timeout-minutes M]

Output:
    outputs/nem_validate_001/
    ├── manifest.csv
    ├── summary.json
    ├── timing.jsonl
    ├── mrs_distribution.json
    ├── failure_log.jsonl
    └── run.log
"""

import csv
import json
import os
import sys
import time
import uuid
from pathlib import Path
from collections import defaultdict

# Add project to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.operator_console import (
    create_operator_job,
    plan_operator_runtime,
    run_operator_job,
    get_operator_job,
)


def build_config(output_root: Path) -> RuntimeConfig:
    project_root = Path(__file__).resolve().parent.parent
    return RuntimeConfig(
        project_root=project_root,
        data_root=project_root / "data",
        input_dirs=[project_root / "data" / "validation" / "samples"],
        output_root=project_root / "outputs" / "nem_validate_001",
        report_dir=project_root / "reports" / "nem_validate_001",
        registry_path=project_root / "data" / "validation" / "registry.jsonl",
        queue_path=project_root / "outputs" / "nem_validate_001" / "queue.jsonl",
        operator_jobs_path=project_root / "outputs" / "nem_validate_001" / "operator_jobs.jsonl",
        operator_detail_dir=project_root / "outputs" / "nem_validate_001" / "operator_details",
        python="python3",
        timeout_seconds_per_task=300,
        sleep_seconds_between_tasks=1.0,
        max_retries_per_task=2,
        keep_last_n_runs=10,
        command_templates=[
            "python3 -m moodify.cli process {input} --output-dir {output_dir} --preset {preset}",
            "python3 -m moodify.cli process {input} --output-dir {output_dir} --preset {preset} --json",
        ],
    )


def collect_metrics(run_dir: Path, output_root: Path) -> dict:
    """Read manifest.csv and compute aggregate metrics."""
    manifest_path = run_dir / "manifest.csv"
    if not manifest_path.exists():
        return {"error": "No manifest.csv found", "run_dir": str(run_dir)}

    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    timing = []
    mrs_by_preset = defaultdict(list)
    failures = []
    status_counts = defaultdict(int)

    for row in rows:
        st = row.get("status", "unknown")
        status_counts[st] += 1

        elapsed = row.get("elapsed_seconds", "")
        if elapsed:
            timing.append(float(elapsed))

        preset = row.get("preset", "unknown")
        for key in ("pseudo_mrs_before", "pseudo_mrs_after", "pseudo_delta_mrs"):
            val = row.get(key, "")
            if val:
                try:
                    mrs_by_preset[f"{preset}/{key}"].append(float(val))
                except ValueError:
                    pass

        if st in ("failed", "error", "timeout"):
            failures.append({
                "task_id": row.get("task_id", ""),
                "sample_id": row.get("sample_id", ""),
                "preset": preset,
                "status": st,
                "error": row.get("error", ""),
                "return_code": row.get("return_code", ""),
            })

    # Compute distributions
    mrs_summary = {}
    for key, vals in mrs_by_preset.items():
        if vals:
            mrs_summary[key] = {
                "count": len(vals),
                "mean": sum(vals) / len(vals),
                "min": min(vals),
                "max": max(vals),
            }

    return {
        "run_dir": str(run_dir),
        "total_tasks": len(rows),
        "status_counts": dict(status_counts),
        "success_rate": status_counts.get("done", 0) / max(len(rows), 1),
        "mean_elapsed": sum(timing) / len(timing) if timing else 0,
        "total_elapsed": sum(timing),
        "timing": timing,
        "mrs_distribution": mrs_summary,
        "failure_count": len(failures),
        "failures": failures,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Run validation dataset processing")
    ap.add_argument("--samples", type=int, default=30, help="Max samples to process")
    ap.add_argument("--timeout-minutes", type=int, default=360, help="Max runtime in minutes")
    ap.add_argument("--dry-run", action="store_true", help="Plan but don't execute")
    args = ap.parse_args()

    project = Path(__file__).resolve().parent.parent
    output_root = project / "outputs" / "nem_validate_001"
    output_root.mkdir(parents=True, exist_ok=True)
    log_path = output_root / "run.log"

    # Clean up previous run state
    for f in output_root.glob("operator_jobs.jsonl*"):
        f.unlink()
    for f in output_root.glob("queue.jsonl*"):
        f.unlink()

    def log(msg):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    log("=== NEM-18 Validate-6: Unattended Run ===")
    cfg = build_config(output_root)
    log(f"Config: {cfg.project_root}")
    log(f"Max samples: {args.samples}, Timeout: {args.timeout_minutes}min")

    # Collect audio files from dataset directories
    dataset = project / "data" / "validation" / "samples"
    audio_files = sorted(dataset.rglob("*.mp3")) + sorted(dataset.rglob("*.wav"))
    audio_files = audio_files[:args.samples]
    log(f"Audio files found: {len(audio_files)}")

    presets = ["warm_vocal", "clean_master", "wide_space"]
    results = []
    start_time = time.time()
    job_count = 0

    for audio_path in audio_files:
        elapsed = time.time() - start_time
        if elapsed > args.timeout_minutes * 60:
            log(f"Timeout reached ({args.timeout_minutes}min). Stopping.")
            break

        genre = audio_path.parent.name
        log(f"[{job_count+1}/{len(audio_files)}] Processing: {audio_path.name} ({genre})")

        try:
            job = create_operator_job(
                cfg,
                source_audio=str(audio_path),
                processing_depth="quick_scan",
                project_label=f"validate-{genre}",
            )
            plan = plan_operator_runtime(cfg, job_id=job["job_id"])

            if args.dry_run:
                results.append({"job_id": job["job_id"], "status": "planned", "audio": audio_path.name})
                continue

            result = run_operator_job(cfg, job_id=job["job_id"], dry_run=False)
            job_after = get_operator_job(cfg, job["job_id"])
            results.append({
                "job_id": job["job_id"],
                "audio": audio_path.name,
                "genre": genre,
                "status": result.get("status", "unknown"),
                "run_id": result.get("run_id", ""),
                "job_status": job_after.get("status", "unknown"),
                "run_started_at": job_after.get("run_started_at", ""),
                "run_finished_at": job_after.get("run_finished_at", ""),
            })
            job_count += 1

        except Exception as e:
            log(f"  ERROR: {e}")
            results.append({"job_id": "N/A", "status": "exception", "audio": audio_path.name, "error": str(e)})

    total_elapsed = time.time() - start_time

    # Collect metrics from each run's manifest
    all_metrics = []
    for r in results:
        if r.get("run_id"):
            run_dir = output_root / r["run_id"]
            metrics = collect_metrics(run_dir, output_root)
            all_metrics.append(metrics)

    # Write summary
    summary = {
        "run_id": f"nem_validate_001_{uuid.uuid4().hex[:8]}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_jobs": len(results),
        "completed_jobs": sum(1 for r in results if r.get("job_status") in ("gate_review", "reprocess", "delivered")),
        "failed_jobs": sum(1 for r in results if r.get("status") in ("failed", "exception")),
        "total_elapsed_seconds": round(total_elapsed, 1),
        "results": results,
        "aggregate_metrics": all_metrics,
    }

    summary_path = output_root / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    log(f"Summary written to {summary_path}")

    # Write timing log
    timing_path = output_root / "timing.jsonl"
    with timing_path.open("w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    log(f"=== Run complete: {job_count} jobs in {total_elapsed:.0f}s ===")
    log(f"Success rate: {summary['completed_jobs']}/{summary['total_jobs']}")
    return summary


if __name__ == "__main__":
    main()
