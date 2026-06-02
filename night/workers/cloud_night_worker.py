#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodify Cloud Night Worker  v2
------------------------------
目的：
  在云服务器夜间自动批量处理 AI 音乐样本，生成日志、manifest、summary。
  v2: 面向整夜持续运行的加固版。

原则：
  1. 不侵入 moodify 核心代码。
  2. 默认只通过现有 CLI 命令调用工程。
  3. 失败可追踪，第二天可以复盘。
  4. 支持 dry-run / smoke test / resume。
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg"}
MIN_PYTHON = (3, 8)

_shutdown_requested = False


def _signal_handler(signum: int, frame: Any) -> None:
    global _shutdown_requested
    _shutdown_requested = True


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)

# ---------------------------------------------------------------------------
# Default config
# ---------------------------------------------------------------------------

DEFAULT_CONFIG: Dict[str, Any] = {
    "project_root": ".",
    "input_dir": "data/night_inputs",
    "output_base_dir": "outputs/night_runs",
    "presets": ["warm_vocal", "clean_master", "wide_space"],
    "max_files": 30,
    "recurse": False,
    "timeout_seconds_per_task": 900,
    "sleep_seconds_between_tasks": 2,
    "max_retries_per_task": 2,
    "keep_last_n_runs": 10,
    "min_free_disk_gb": 1.0,
    "python": sys.executable,
    "stop_on_first_success_template": True,
    "preflight_commands": [
        "{python} --version",
        "{python} cli.py --help",
    ],
    "command_templates": [
        "{python} cli.py process --input {input} --output {output_dir} --preset {preset}",
        "{python} -m moodify.cli process --input {input} --output {output_dir} --preset {preset}",
        "{python} cli.py process {input} --output {output_dir} --preset {preset}",
    ],
    "env": {
        "PYTHONUNBUFFERED": "1",
        "MOODIFY_NIGHT_RUN": "1",
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def check_python_version() -> None:
    if sys.version_info < MIN_PYTHON:
        raise RuntimeError(
            f"Python {'.'.join(map(str, MIN_PYTHON))}+ required, "
            f"got {sys.version_info.major}.{sys.version_info.minor}"
        )


def load_config(path: Optional[Path]) -> Dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)
    if path:
        with path.open("r", encoding="utf-8") as f:
            user_cfg = json.load(f)
        cfg = deep_merge(cfg, user_cfg)
    return cfg


def deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def resolve_path(project_root: Path, p: str | Path) -> Path:
    p = Path(p)
    if p.is_absolute():
        return p
    return project_root / p


def discover_audio(input_dir: Path, recurse: bool, max_files: int) -> List[Path]:
    if not input_dir.exists():
        return []
    iterator = input_dir.rglob("*") if recurse else input_dir.glob("*")
    files = sorted(
        [p for p in iterator if p.is_file() and p.suffix.lower() in AUDIO_SUFFIXES],
        key=lambda x: x.name.lower(),
    )
    if max_files and max_files > 0:
        files = files[:max_files]
    return files


def check_disk_space(path: Path, min_free_gb: float) -> Tuple[bool, float]:
    try:
        usage = shutil.disk_usage(path)
        free_gb = usage.free / (1024**3)
        return free_gb >= min_free_gb, free_gb
    except Exception:
        return True, -1.0


def cleanup_old_runs(base: Path, keep_last: int, logger: "NightLogger") -> None:
    if keep_last <= 0 or not base.exists():
        return
    run_dirs = sorted(
        [d for d in base.iterdir() if d.is_dir() and d.name != "latest"],
        key=lambda d: d.name,
        reverse=True,
    )
    for d in run_dirs[keep_last:]:
        try:
            shutil.rmtree(d)
            logger.write(f"CLEANUP removed old run: {d.name}")
        except Exception as e:
            logger.write(f"CLEANUP failed {d.name}: {e}")

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------


class NightLogger:
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, msg: str) -> None:
        line = f"[{dt.datetime.now().isoformat(timespec='seconds')}] {msg}"
        print(line, flush=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

# ---------------------------------------------------------------------------
# Subprocess (with process-group kill on timeout)
# ---------------------------------------------------------------------------


def format_command(template: str, ctx: Dict[str, str]) -> List[str]:
    rendered = template.format(**ctx)
    return shlex.split(rendered)


def run_subprocess(
    cmd: List[str],
    cwd: Path,
    env: Dict[str, str],
    timeout: int,
    logger: NightLogger,
) -> Tuple[int, str, str, float]:
    start = time.time()
    logger.write("RUN " + " ".join(shlex.quote(x) for x in cmd))
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        stdout, stderr = proc.communicate(timeout=timeout)
        elapsed = time.time() - start
        code = proc.returncode
        if stdout and stdout.strip():
            logger.write("STDOUT(last 4000 chars):\n" + stdout.strip()[-4000:])
        if stderr and stderr.strip():
            logger.write("STDERR(last 4000 chars):\n" + stderr.strip()[-4000:])
        return code, stdout or "", stderr or "", elapsed

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        logger.write(f"TIMEOUT after {elapsed:.1f}s — killing process group")
        _kill_process_group(proc)
        return 124, "", f"timeout after {timeout}s", elapsed

    except Exception as e:
        elapsed = time.time() - start
        logger.write(f"EXCEPTION {type(e).__name__}: {e}")
        return 125, "", str(e), elapsed


def _kill_process_group(proc: subprocess.Popen) -> None:
    try:
        if hasattr(os, "killpg"):
            pgid = os.getpgid(proc.pid)
            os.killpg(pgid, signal.SIGTERM)
            time.sleep(2)
            try:
                os.killpg(pgid, signal.SIGKILL)
            except (ProcessLookupError, OSError):
                pass
        else:
            proc.kill()
    except (ProcessLookupError, OSError):
        proc.kill()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

# ---------------------------------------------------------------------------
# Lock file
# ---------------------------------------------------------------------------


def acquire_lock(lock_path: Path) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"pid={os.getpid()}\ntime={dt.datetime.now().isoformat()}\n")
    except FileExistsError:
        raise RuntimeError(
            f"Night worker lock already exists: {lock_path}\n"
            "如果确认没有旧任务在跑，可以手动删除这个 lock 文件。"
        )


def release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink(missing_ok=True)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def update_latest_symlink(output_base_dir: Path, run_dir: Path) -> None:
    latest = output_base_dir / "latest"
    try:
        if latest.is_symlink():
            latest.unlink()
        elif latest.is_dir():
            backup = output_base_dir / f"latest.old.{now_stamp()}"
            latest.rename(backup)
        elif latest.exists():
            latest.unlink()
        latest.symlink_to(run_dir.name, target_is_directory=True)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------


def preflight(
    cfg: Dict[str, Any],
    project_root: Path,
    env: Dict[str, str],
    logger: NightLogger,
    dry_run: bool,
) -> None:
    logger.write("PREFLIGHT start")
    logger.write(f"project_root={project_root}")
    logger.write(f"python={cfg['python']}")
    if not project_root.exists():
        raise RuntimeError(f"project_root does not exist: {project_root}")
    for template in cfg.get("preflight_commands", []):
        ctx = {"python": cfg["python"], "project_root": str(project_root)}
        try:
            cmd = format_command(template, ctx)
        except KeyError as e:
            logger.write(f"Skip invalid preflight template {template}: missing {e}")
            continue
        if dry_run:
            logger.write("[DRY-RUN] preflight " + " ".join(cmd))
            continue
        code, _, _, _ = run_subprocess(cmd, project_root, env, 60, logger)
        if code != 0:
            logger.write(f"WARNING preflight command failed with code={code}: {template}")
    logger.write("PREFLIGHT end")

# ---------------------------------------------------------------------------
# Manifest (CSV)
# ---------------------------------------------------------------------------

_MANIFEST_FIELDS = [
    "run_id", "audio", "preset", "status", "return_code",
    "elapsed_seconds", "output_dir", "template_index", "error",
]


def init_manifest(path: Path) -> None:
    if path.exists():
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_MANIFEST_FIELDS)
        writer.writeheader()


def append_manifest(path: Path, row: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=_MANIFEST_FIELDS).writerow(row)

# ---------------------------------------------------------------------------
# Task markers (started / done)
# ---------------------------------------------------------------------------


def _started_marker(output_dir: Path) -> Path:
    return output_dir / ".moodify_night_started"


def _done_marker(output_dir: Path) -> Path:
    return output_dir / ".moodify_night_done"


def _write_full_error(output_dir: Path, stderr: str, stdout: str) -> None:
    err_path = output_dir / ".moodify_night_error.log"
    err_path.write_text(
        f"STDERR:\n{stderr}\n\nSTDOUT:\n{stdout}", encoding="utf-8"
    )

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    check_python_version()

    parser = argparse.ArgumentParser(description="Moodify Cloud Night Worker")
    parser.add_argument("--config", type=str, default=None, help="JSON 配置文件路径")
    parser.add_argument("--project-root", type=str, default=None)
    parser.add_argument("--input-dir", type=str, default=None)
    parser.add_argument("--output-base-dir", type=str, default=None)
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument("--smoke", action="store_true", help="只跑 1 个音频 × 1 个 preset")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不执行处理")
    parser.add_argument("--resume", action="store_true", help="已完成的任务自动跳过")
    args = parser.parse_args()

    # --- Config ---
    cfg = load_config(Path(args.config) if args.config else None)
    if args.project_root:
        cfg["project_root"] = args.project_root
    if args.input_dir:
        cfg["input_dir"] = args.input_dir
    if args.output_base_dir:
        cfg["output_base_dir"] = args.output_base_dir
    if args.max_files is not None:
        cfg["max_files"] = args.max_files

    project_root = Path(cfg["project_root"]).resolve()
    input_dir = resolve_path(project_root, cfg["input_dir"]).resolve()
    output_base_dir = resolve_path(project_root, cfg["output_base_dir"]).resolve()
    run_id = now_stamp()
    run_dir = output_base_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    logger = NightLogger(run_dir / "night_worker.log")
    lock_path = output_base_dir / "night_worker.lock"
    manifest_path = run_dir / "manifest.csv"
    summary_path = run_dir / "summary.json"

    update_latest_symlink(output_base_dir, run_dir)
    init_manifest(manifest_path)

    # --- Env ---
    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in cfg.get("env", {}).items()})
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(project_root) + (os.pathsep + existing_pp if existing_pp else "")

    # --- Summary ---
    summary: Dict[str, Any] = {
        "run_id": run_id,
        "started_at": dt.datetime.now().isoformat(timespec="seconds"),
        "project_root": str(project_root),
        "input_dir": str(input_dir),
        "run_dir": str(run_dir),
        "dry_run": args.dry_run,
        "smoke": args.smoke,
        "total_tasks": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "files": [],
    }

    try:
        acquire_lock(lock_path)
        logger.write("Moodify Cloud Night Worker START (v2)")

        # --- Disk check ---
        min_disk = float(cfg.get("min_free_disk_gb", 1.0))
        ok, free_gb = check_disk_space(output_base_dir, min_disk)
        logger.write(f"Disk check: free={free_gb:.1f}GB threshold={min_disk:.1f}GB")
        if not ok:
            raise RuntimeError(f"Insufficient disk space: {free_gb:.1f}GB free, need {min_disk:.1f}GB")

        preflight(cfg, project_root, env, logger, args.dry_run)

        files = discover_audio(
            input_dir,
            bool(cfg.get("recurse")),
            int(cfg.get("max_files", 0) or 0),
        )
        presets = list(cfg.get("presets") or [])
        if args.smoke:
            files = files[:1]
            presets = presets[:1] if presets else ["warm_vocal"]

        logger.write(f"Discovered audio files: {len(files)}")
        logger.write(f"Presets: {presets}")

        if not files:
            logger.write("No audio files found. Put wav/mp3/flac files into input_dir.")
            summary["error"] = "no_audio_files"
            write_json(summary_path, summary)
            return 2

        write_json(run_dir / "effective_config.json", cfg)

        max_retries = int(cfg.get("max_retries_per_task", 2))
        stop_on_first = bool(cfg.get("stop_on_first_success_template", True))
        sleep_between = float(cfg.get("sleep_seconds_between_tasks", 2))

        for audio in files:
            if _shutdown_requested:
                logger.write("SHUTDOWN requested — stopping task loop")
                break

            for preset in presets:
                if _shutdown_requested:
                    break

                stem_safe = audio.stem.replace(" ", "_")
                task_output_dir = run_dir / stem_safe / preset
                task_output_dir.mkdir(parents=True, exist_ok=True)

                done_marker = _done_marker(task_output_dir)
                started_marker = _started_marker(task_output_dir)

                summary["total_tasks"] += 1
                ctx = {
                    "python": str(cfg["python"]),
                    "project_root": str(project_root),
                    "input": str(audio),
                    "output_dir": str(task_output_dir),
                    "preset": str(preset),
                    "stem": stem_safe,
                    "timestamp": run_id,
                    "run_id": run_id,
                }

                # --- Resume: skip if done ---
                if args.resume and done_marker.exists():
                    logger.write(f"SKIP done audio={audio.name} preset={preset}")
                    summary["skipped"] += 1
                    append_manifest(manifest_path, {
                        "run_id": run_id, "audio": str(audio), "preset": preset,
                        "status": "skipped", "return_code": "", "elapsed_seconds": "",
                        "output_dir": str(task_output_dir), "template_index": "", "error": "",
                    })
                    write_json(summary_path, summary)
                    continue

                # --- Resume: detect incomplete (started but no done) ---
                if args.resume and started_marker.exists():
                    logger.write(f"RESUME redoing incomplete audio={audio.name} preset={preset}")
                    try:
                        started_marker.unlink()
                    except Exception:
                        pass

                # --- Dry-run ---
                if args.dry_run:
                    for i, template in enumerate(cfg.get("command_templates", [])):
                        logger.write(f"[DRY-RUN] template#{i}: " + template.format(**ctx))
                    append_manifest(manifest_path, {
                        "run_id": run_id, "audio": str(audio), "preset": preset,
                        "status": "dry_run", "return_code": "", "elapsed_seconds": "",
                        "output_dir": str(task_output_dir), "template_index": "", "error": "",
                    })
                    continue

                # --- Retry loop ---
                task_ok = False
                last_error = ""
                last_code: Any = ""
                last_elapsed = 0.0
                last_template_index: Any = ""
                max_attempts = 1 + max_retries

                for attempt in range(max_attempts):
                    if _shutdown_requested:
                        logger.write("SHUTDOWN mid-task — aborting retries")
                        break

                    if attempt == 0:
                        started_marker.write_text(
                            f"started_at={dt.datetime.now().isoformat(timespec='seconds')}\n"
                            f"audio={audio}\npreset={preset}\n",
                            encoding="utf-8",
                        )

                    for i, template in enumerate(cfg.get("command_templates", [])):
                        try:
                            cmd = format_command(template, ctx)
                        except KeyError as e:
                            last_error = f"template missing key: {e}"
                            logger.write(f"Invalid template#{i}: {last_error}")
                            continue

                        code, stdout, stderr, elapsed = run_subprocess(
                            cmd=cmd,
                            cwd=project_root,
                            env=env,
                            timeout=int(cfg.get("timeout_seconds_per_task", 900)),
                            logger=logger,
                        )
                        last_code = code
                        last_elapsed = elapsed
                        last_template_index = i

                        if code == 0:
                            task_ok = True
                            done_marker.write_text(
                                f"done_at={dt.datetime.now().isoformat(timespec='seconds')}\n"
                                f"audio={audio}\npreset={preset}\n"
                                f"template_index={i}\nattempt={attempt + 1}\n",
                                encoding="utf-8",
                            )
                            try:
                                started_marker.unlink(missing_ok=True)
                            except Exception:
                                pass
                            if stop_on_first:
                                break
                        else:
                            last_error = (stderr or stdout or f"return_code={code}")[-500:]
                            _write_full_error(task_output_dir, stderr, stdout)

                    if task_ok:
                        break

                    # Retry with backoff
                    if attempt < max_attempts - 1:
                        backoff = sleep_between * (2**attempt)
                        logger.write(
                            f"Retry {attempt + 2}/{max_attempts} for "
                            f"{audio.name}/{preset} after {backoff:.0f}s"
                        )
                        try:
                            time.sleep(backoff)
                        except KeyboardInterrupt:
                            _shutdown_requested = True
                            break
                    else:
                        try:
                            started_marker.unlink(missing_ok=True)
                        except Exception:
                            pass

                # --- Record result ---
                if task_ok:
                    logger.write(f"SUCCESS audio={audio.name} preset={preset}")
                    summary["success"] += 1
                    append_manifest(manifest_path, {
                        "run_id": run_id, "audio": str(audio), "preset": preset,
                        "status": "success", "return_code": last_code,
                        "elapsed_seconds": f"{last_elapsed:.2f}",
                        "output_dir": str(task_output_dir),
                        "template_index": last_template_index, "error": "",
                    })
                elif _shutdown_requested:
                    logger.write(f"ABORTED (shutdown) audio={audio.name} preset={preset}")
                    summary["failed"] += 1
                    append_manifest(manifest_path, {
                        "run_id": run_id, "audio": str(audio), "preset": preset,
                        "status": "aborted", "return_code": "", "elapsed_seconds": "",
                        "output_dir": str(task_output_dir), "template_index": "", "error": "shutdown",
                    })
                else:
                    logger.write(f"FAILED audio={audio.name} preset={preset} error={last_error}")
                    summary["failed"] += 1
                    append_manifest(manifest_path, {
                        "run_id": run_id, "audio": str(audio), "preset": preset,
                        "status": "failed", "return_code": last_code,
                        "elapsed_seconds": f"{last_elapsed:.2f}",
                        "output_dir": str(task_output_dir),
                        "template_index": last_template_index, "error": last_error,
                    })

                # Incremental summary
                write_json(summary_path, summary)

                # Disk check after each task
                ok, free_gb = check_disk_space(output_base_dir, min_disk)
                if not ok:
                    raise RuntimeError(
                        f"Disk full during run: {free_gb:.1f}GB free, threshold {min_disk:.1f}GB"
                    )

                try:
                    time.sleep(sleep_between)
                except KeyboardInterrupt:
                    _shutdown_requested = True
                    break

        # --- Finalize ---
        if _shutdown_requested:
            summary["shutdown_requested"] = True
        summary["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
        write_json(summary_path, summary)

        keep_last = int(cfg.get("keep_last_n_runs", 10))
        cleanup_old_runs(output_base_dir, keep_last, logger)

        logger.write("Moodify Cloud Night Worker FINISH")
        logger.write(
            f"Summary: success={summary['success']} failed={summary['failed']} "
            f"skipped={summary['skipped']}"
        )
        return 0 if summary["failed"] == 0 else 1

    except Exception as e:
        summary["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
        summary["fatal_error"] = f"{type(e).__name__}: {e}"
        write_json(summary_path, summary)
        logger.write(f"FATAL {type(e).__name__}: {e}")
        return 99
    finally:
        release_lock(lock_path)


if __name__ == "__main__":
    raise SystemExit(main())
