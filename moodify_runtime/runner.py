from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .config import RuntimeConfig
from .hardening_gates import authorize_audio_source
from .metrics import compare_before_after
from .queue import load_queue, rewrite_queue
from .utils import (
    LineLogger,
    LockFile,
    atomic_append_csv,
    atomic_write_json,
    check_disk_space,
    cleanup_old_runs,
    local_stamp,
    quote_cmd,
    render_template_to_argv,
    run_command,
    shutdown_requested,
    utc_now_iso,
)

MANIFEST_FIELDS = [
    "run_id", "task_id", "sample_id", "input_path", "preset", "status",
    "return_code", "elapsed_seconds", "output_dir", "template_index",
    "pseudo_mrs_before", "pseudo_mrs_after", "pseudo_delta_mrs",
    "mrs_open_v031_before", "mrs_open_v031_after", "delta_mrs_open_v031",
    "mrs_open_flags", "error",
]


def select_pending_tasks(
    queue_rows: List[Dict[str, Any]], limit: int = 0
) -> List[Dict[str, Any]]:
    pending = [r for r in queue_rows if r.get("status") in ("pending", "retry")]
    pending.sort(key=lambda r: (int(r.get("priority", 5)), r.get("created_at") or ""))
    if limit and limit > 0:
        return pending[:limit]
    return pending


def replace_task(
    queue_rows: List[Dict[str, Any]], updated: Dict[str, Any]
) -> List[Dict[str, Any]]:
    out = []
    for row in queue_rows:
        if row.get("task_id") == updated.get("task_id"):
            out.append(updated)
        else:
            out.append(row)
    return out


def _write_full_error(output_dir: Path, result: Dict[str, Any]) -> None:
    err_path = output_dir / ".moodify_error.log"
    err_path.write_text(
        f"STDERR:\n{result.get('stderr_full', '')}\n\n"
        f"STDOUT:\n{result.get('stdout_full', '')}",
        encoding="utf-8",
    )


def run_daily(
    cfg: RuntimeConfig,
    limit: int = 0,
    dry_run: bool = False,
    run_id: Optional[str] = None,
    rights_manifest: Optional[str] = None,
    rights_asset_id: str = "",
    task_filter: Optional[Callable[[Dict[str, Any]], bool]] = None,
) -> Dict[str, Any]:
    cfg = cfg.resolved()
    run_id = run_id or local_stamp()
    run_dir = cfg.output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    logger = LineLogger(run_dir / "daily_run.log")
    lock = LockFile(cfg.output_root / "daily_run.lock")
    summary: Dict[str, Any] = {
        "run_id": run_id,
        "started_at": utc_now_iso(),
        "dry_run": dry_run,
        "run_dir": str(run_dir),
        "queue_path": str(cfg.queue_path),
        "success": 0,
        "failed": 0,
        "rights_blocked": 0,
        "dry_run_tasks": 0,
        "total_selected": 0,
        "tasks": [],
    }

    try:
        lock.acquire()
        logger.write("Moodify Daily Run START (v2)")
        logger.write(f"project_root={cfg.project_root}")
        logger.write(f"queue_path={cfg.queue_path}")

        # --- Disk check ---
        min_disk = float(cfg.min_free_disk_gb)
        ok, free_gb = check_disk_space(cfg.output_root, min_disk)
        logger.write(f"Disk check: free={free_gb:.1f}GB threshold={min_disk:.1f}GB")
        if not ok:
            raise RuntimeError(
                f"Insufficient disk space: {free_gb:.1f}GB free, need {min_disk:.1f}GB"
            )

        queue_rows = load_queue(cfg)
        tasks = select_pending_tasks(queue_rows, limit=limit)
        if task_filter is not None:
            tasks = [t for t in tasks if task_filter(t)]
        summary["total_selected"] = len(tasks)
        logger.write(f"selected_tasks={len(tasks)}")

        env = os.environ.copy()
        env.update({str(k): str(v) for k, v in cfg.env.items()})
        existing_pp = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(cfg.project_root) + (
            os.pathsep + existing_pp if existing_pp else ""
        )

        max_retries = int(cfg.max_retries_per_task)
        stop_on_first = bool(cfg.stop_on_first_success_template)
        sleep_between = float(cfg.sleep_seconds_between_tasks)

        for task in tasks:
            if shutdown_requested():
                logger.write("SHUTDOWN requested — stopping task loop")
                break

            task = dict(task)
            task["run_id"] = run_id
            task["started_at"] = utc_now_iso()

            input_path = Path(task["input_path"])
            preset = task["preset"]
            sample_id = task["sample_id"]
            task_output_dir = run_dir / sample_id / preset
            task_output_dir.mkdir(parents=True, exist_ok=True)
            task["output_dir"] = str(task_output_dir)

            if dry_run:
                logger.write(
                    f"[DRY-RUN] task={task['task_id']} input={input_path} preset={preset}"
                )
                for i, template in enumerate(cfg.command_templates):
                    try:
                        context = {
                            "python": cfg.python,
                            "project_root": cfg.project_root,
                            "input": input_path,
                            "output_dir": task_output_dir,
                            "preset": preset,
                            "sample_id": sample_id,
                            "task_id": task["task_id"],
                            "run_id": run_id,
                        }
                        argv = render_template_to_argv(template, context)
                        logger.write(f"[DRY-RUN] template#{i}: {quote_cmd(argv)}")
                    except Exception as e:
                        logger.write(f"[DRY-RUN] template#{i} invalid: {e}")
                task["status"] = "pending"
                summary["dry_run_tasks"] += 1
                continue

            # ── Rights gate: fail-closed per-task authorization ──────
            if rights_manifest:
                ok, reason = authorize_audio_source(
                    rights_manifest, rights_asset_id, input_path
                )
                if not ok:
                    task["status"] = "rights_blocked"
                    task["last_error"] = f"rights: {reason}"
                    task["finished_at"] = utc_now_iso()
                    summary["rights_blocked"] += 1
                    queue_rows = replace_task(queue_rows, task)
                    rewrite_queue(cfg, queue_rows)
                    logger.write(f"RIGHTS_BLOCKED task={task['task_id']} reason={reason}")
                    summary["tasks"].append({
                        "run_id": run_id,
                        "task_id": task["task_id"],
                        "sample_id": sample_id,
                        "input_path": str(input_path),
                        "preset": preset,
                        "status": "rights_blocked",
                        "return_code": "",
                        "elapsed_seconds": "",
                        "output_dir": str(task_output_dir),
                        "template_index": "",
                        "pseudo_mrs_before": "",
                        "pseudo_mrs_after": "",
                        "pseudo_delta_mrs": "",
                        "mrs_open_v031_before": "",
                        "mrs_open_v031_after": "",
                        "delta_mrs_open_v031": "",
                        "mrs_open_flags": "",
                        "error": f"rights: {reason}",
                    })
                    continue

            task["attempts"] = int(task.get("attempts") or 0) + 1

            context = {
                "python": cfg.python,
                "project_root": cfg.project_root,
                "input": input_path,
                "output_dir": task_output_dir,
                "preset": preset,
                "sample_id": sample_id,
                "task_id": task["task_id"],
                "run_id": run_id,
            }

            # --- Retry loop ---
            task_ok = False
            chosen_result: Optional[Dict[str, Any]] = None
            chosen_template_index: Optional[int] = None
            error = ""
            max_attempts = 1 + max_retries

            for attempt in range(max_attempts):
                if shutdown_requested():
                    logger.write("SHUTDOWN mid-task — aborting retries")
                    break

                for i, template in enumerate(cfg.command_templates):
                    try:
                        argv = render_template_to_argv(template, context)
                    except Exception as e:
                        error = f"template_error: {e}"
                        logger.write(error)
                        continue

                    logger.write(
                        f"RUN task={task['task_id']} attempt={attempt+1} "
                        f"template={i} cmd={quote_cmd(argv)}"
                    )
                    result = run_command(
                        argv,
                        cwd=cfg.project_root,
                        env=env,
                        timeout=cfg.timeout_seconds_per_task,
                    )
                    logger.write(
                        f"RESULT code={result['return_code']} "
                        f"elapsed={result['elapsed_seconds']:.2f}s"
                    )
                    if result.get("stdout_tail"):
                        logger.write("STDOUT tail:\n" + result["stdout_tail"].strip())
                    if result.get("stderr_tail"):
                        logger.write("STDERR tail:\n" + result["stderr_tail"].strip())

                    chosen_result = result
                    chosen_template_index = i

                    if result["return_code"] == 0:
                        task_ok = True
                        break
                    error = (
                        result.get("stderr_tail")
                        or result.get("stdout_tail")
                        or f"return_code={result['return_code']}"
                    )

                if task_ok:
                    break

                # Retry with backoff
                if attempt < max_attempts - 1:
                    backoff = sleep_between * (2**attempt)
                    logger.write(
                        f"Retry {attempt + 2}/{max_attempts} for "
                        f"{sample_id}/{preset} after {backoff:.0f}s"
                    )
                    try:
                        time.sleep(backoff)
                    except KeyboardInterrupt:
                        break

            # --- Metrics ---
            metrics = compare_before_after(input_path, task_output_dir)
            atomic_write_json(task_output_dir / "metrics_before_after.json", metrics)

            # --- Record result ---
            if task_ok:
                task["status"] = "done"
                task["last_error"] = None
                summary["success"] += 1
            else:
                task["status"] = "failed"
                task["last_error"] = error[-1000:] if error else "unknown_error"
                summary["failed"] += 1
                if chosen_result:
                    _write_full_error(task_output_dir, chosen_result)

            task["finished_at"] = utc_now_iso()
            queue_rows = replace_task(queue_rows, task)
            rewrite_queue(cfg, queue_rows)

            manifest_row = {
                "run_id": run_id,
                "task_id": task["task_id"],
                "sample_id": sample_id,
                "input_path": str(input_path),
                "preset": preset,
                "status": task["status"],
                "return_code": (
                    "" if not chosen_result else chosen_result.get("return_code")
                ),
                "elapsed_seconds": (
                    ""
                    if not chosen_result
                    else f"{chosen_result.get('elapsed_seconds', 0):.2f}"
                ),
                "output_dir": str(task_output_dir),
                "template_index": (
                    "" if chosen_template_index is None else chosen_template_index
                ),
                "pseudo_mrs_before": metrics.get("pseudo_mrs_before"),
                "pseudo_mrs_after": metrics.get("pseudo_mrs_after"),
                "pseudo_delta_mrs": metrics.get("pseudo_delta_mrs"),
                "mrs_open_v031_before": metrics.get("mrs_open_v031_before"),
                "mrs_open_v031_after": metrics.get("mrs_open_v031_after"),
                "delta_mrs_open_v031": metrics.get("delta_mrs_open_v031"),
                "mrs_open_flags": ",".join(metrics.get("mrs_open_flags", [])) if metrics.get("mrs_open_flags") else "",
                "error": task.get("last_error") or "",
            }
            atomic_append_csv(run_dir / "manifest.csv", manifest_row, MANIFEST_FIELDS)
            summary["tasks"].append(manifest_row)

            # Incremental summary
            atomic_write_json(run_dir / "summary.json", summary)

            # Disk check after each task
            ok, free_gb = check_disk_space(cfg.output_root, min_disk)
            if not ok:
                raise RuntimeError(
                    f"Disk full during run: {free_gb:.1f}GB free, "
                    f"threshold {min_disk:.1f}GB"
                )

            try:
                time.sleep(sleep_between)
            except KeyboardInterrupt:
                break

        # --- Finalize ---
        if shutdown_requested():
            summary["shutdown_requested"] = True
        summary["finished_at"] = utc_now_iso()
        atomic_write_json(run_dir / "summary.json", summary)

        keep_last = int(cfg.keep_last_n_runs)
        cleanup_old_runs(cfg.output_root, keep_last, logger)

        logger.write(
            f"FINISH success={summary['success']} failed={summary['failed']} "
            f"dry_run={summary['dry_run_tasks']}"
        )
        return summary

    except Exception as e:
        summary["finished_at"] = utc_now_iso()
        summary["fatal_error"] = f"{type(e).__name__}: {e}"
        atomic_write_json(run_dir / "summary.json", summary)
        logger.write(f"FATAL {type(e).__name__}: {e}")
        return summary
    finally:
        lock.release()
