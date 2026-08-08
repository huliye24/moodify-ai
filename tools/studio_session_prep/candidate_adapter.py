"""Safe adapter for v01 pipeline candidate generation.

Default mode is dry-run (no audio processing). Explicit --execute-candidates
flag is required for actual processing. Each candidate gets an isolated output
directory with full run metadata.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dry_run_candidate(
    source_path: str,
    candidate_id: str,
    preset: str,
    output_dir: str,
    plan_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Simulate a candidate run without executing the pipeline.

    Returns a run_info dict that would be written by execute_candidate.
    """
    source = Path(source_path)
    run_id = f"dryrun_{candidate_id}_{_utc_now().replace(':', '-')}"
    info = {
        "run_id": run_id,
        "candidate_id": candidate_id,
        "source_path": str(source.resolve()),
        "preset": preset,
        "executed": False,
        "dry_run": True,
        "output_dir": output_dir,
        "output_audio": None,
        "report_path": None,
        "exit_code": None,
        "duration_s": 0.0,
        "pipeline_version": "v01 (not executed)",
        "parameters": {"preset": preset},
        "error": None,
        "warnings": ["Dry-run mode: no audio was processed. Use --execute-candidates to run."],
        "started_at": _utc_now(),
        "finished_at": _utc_now(),
        "plan_info": plan_info or {},
    }
    return info


def execute_candidate(
    source_path: str,
    candidate_id: str,
    preset: str,
    output_dir: str,
    plan_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute one candidate through the v01 pipeline.

    Creates isolated output directory for this candidate.
    All failures are recorded — no auto-retry.
    """
    started_at = _utc_now()
    t0 = time.perf_counter()

    source = Path(source_path)
    run_id = f"run_{candidate_id}_{started_at.replace(':', '-')}"
    cand_dir = Path(output_dir) / f"candidate_{candidate_id}"
    cand_dir.mkdir(parents=True, exist_ok=True)

    info: dict[str, Any] = {
        "run_id": run_id,
        "candidate_id": candidate_id,
        "source_path": str(source.resolve()),
        "preset": preset,
        "executed": True,
        "dry_run": False,
        "output_dir": str(cand_dir),
        "output_audio": None,
        "report_path": None,
        "exit_code": None,
        "duration_s": 0.0,
        "pipeline_version": "v01",
        "parameters": {"preset": preset},
        "error": None,
        "warnings": [],
        "started_at": started_at,
        "finished_at": None,
        "plan_info": plan_info or {},
    }

    try:
        from moodify.v01_pipeline import process_audio
    except ImportError as exc:
        info["error"] = f"Cannot import v01 pipeline: {exc}"
        info["exit_code"] = -1
        info["finished_at"] = _utc_now()
        info["duration_s"] = round(time.perf_counter() - t0, 3)
        return info

    try:
        result = process_audio(
            input_path=str(source),
            preset=preset,
            output_dir=str(cand_dir),
        )
        if result.success and result.output_path:
            info["output_audio"] = result.output_path
            info["report_path"] = getattr(result, "report_path", None)
            info["exit_code"] = 0
        else:
            info["error"] = getattr(result, "error", "Unknown pipeline error")
            info["exit_code"] = 1
            if hasattr(result, "scan") and result.scan:
                info["warnings"].extend(result.scan.warnings)
    except Exception as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"
        info["exit_code"] = -1
        info["traceback"] = traceback.format_exc()

    info["duration_s"] = round(time.perf_counter() - t0, 3)
    info["finished_at"] = _utc_now()

    # Write run_info.json in candidate directory
    run_info_path = cand_dir / "run_info.json"
    with open(run_info_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    return info


def compute_output_sha256(output_path: str) -> str | None:
    """Compute SHA-256 of a candidate output file. Read-only."""
    import hashlib

    p = Path(output_path)
    if not p.is_file():
        return None
    digest = hashlib.sha256()
    with p.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_all_candidates(
    source_path: str,
    plan_set_path: str,
    output_dir: str,
    execute: bool = False,
) -> list[dict[str, Any]]:
    """Run all candidates from a plan set. Dry-run by default."""
    with open(plan_set_path, "r", encoding="utf-8") as f:
        plan_set = json.load(f)

    results = []
    for plan in plan_set.get("plans", []):
        plan_id = plan["plan_id"]
        preset = plan["preset"]

        if execute:
            info = execute_candidate(
                source_path, plan_id, preset, output_dir,
                plan_info={"strategy": plan.get("strategy", ""),
                           "reasoning": plan.get("reasoning", []),
                           "risk": plan.get("risk", [])},
            )
        else:
            info = dry_run_candidate(
                source_path, plan_id, preset, output_dir,
                plan_info={"strategy": plan.get("strategy", ""),
                           "reasoning": plan.get("reasoning", []),
                           "risk": plan.get("risk", [])},
            )

        # Hash output if available
        if info.get("output_audio"):
            info["output_sha256"] = compute_output_sha256(info["output_audio"])

        results.append(info)

    # Write batch summary
    summary_path = Path(output_dir) / "candidate_batch_summary.json"
    summary = {
        "generated_at": _utc_now(),
        "source_path": source_path,
        "plan_set_path": plan_set_path,
        "executed": execute,
        "candidates": results,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return results
