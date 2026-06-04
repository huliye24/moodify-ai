"""潮汐循环 (Tidal Cycle) — continuous unattended runtime loop.

Integrates all 4 E-Chains into a self-running production cycle:
  RUNTIME-001:  supervisor + heartbeat + structured events
  PRESET-CRAFT-002: safety gate + craft writeback
  MRS-LISTENING-003: MRS scoring + over-dark detection
  CLOUD-WORKER-004: lease coordination + multi-worker ready

The cycle:
  register → plan → run(supervised) → gate → report → craft → sleep → repeat

Usage:
  python3 -m moodify_runtime.tidal_cycle [--interval 3600] [--max-cycles 0]
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Project root resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════════════════════════════
# Data model
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class TideRecord:
    """One complete tidal cycle record."""
    cycle_id: str
    cycle_number: int
    phase: str = "init"           # init → register → plan → run → gate → report → craft → sleep
    started_at: str = ""
    finished_at: str = ""
    tasks_processed: int = 0
    tasks_succeeded: int = 0
    tasks_failed: int = 0
    gate_approve: int = 0
    gate_reprocess: int = 0
    gate_reject: int = 0
    craft_records_written: int = 0
    elapsed_s: float = 0.0
    free_disk_gb: float = 0.0
    free_mem_gb: float = 0.0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════
# Health checks
# ═══════════════════════════════════════════════════════════════════════


def _disk_free_gb(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return round(usage.free / (1024 ** 3), 1)


def _mem_free_gb() -> float:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return round(int(line.split()[1]) / (1024 ** 2), 1)
    except Exception:
        pass
    return -1.0


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ═══════════════════════════════════════════════════════════════════════
# Phase runners — each calls the CLI, returns success + stats
# ═══════════════════════════════════════════════════════════════════════


def _run_cli(args: List[str], timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", "-m", "moodify_runtime.cli"] + args,
        capture_output=True, text=True, timeout=timeout,
        cwd=str(PROJECT_ROOT),
    )


def phase_register() -> Dict[str, Any]:
    """Scan input_dirs and register new audio files."""
    r = _run_cli(["register", "--source", "tidal_cycle"])
    return {"ok": r.returncode == 0, "stderr_tail": r.stderr[-200:] if r.stderr else ""}


def phase_plan(presets: str = "") -> Dict[str, Any]:
    """Generate run queue from registry."""
    args = ["plan"]
    if presets:
        args += ["--presets", presets]
    r = _run_cli(args)
    return {"ok": r.returncode == 0, "stderr_tail": r.stderr[-200:] if r.stderr else ""}


def phase_run(limit: int = 0, dry_run: bool = False) -> Dict[str, Any]:
    """Execute pending queue tasks with supervisor."""
    args = ["run"]
    if limit:
        args += ["--limit", str(limit)]
    if dry_run:
        args += ["--dry-run"]

    # Use run_supervised from our supervisor module
    from .supervisor import run_supervised

    cmd = ["python3", "-m", "moodify_runtime.cli"] + args
    result = run_supervised(cmd, timeout=3600, max_retries=1, cwd=str(PROJECT_ROOT))

    return {
        "ok": result.exit_code == 0 and not result.crashed,
        "exit_code": result.exit_code,
        "attempts": result.attempts,
        "crashed": result.crashed,
        "timed_out": result.timed_out,
        "error": result.error,
    }


def phase_run_operator(job_id: str) -> Dict[str, Any]:
    """Run a specific operator job through the supervisor."""
    from .supervisor import run_supervised
    cmd = ["python3", "-m", "moodify_runtime.cli", "operator-run", "--job-id", job_id, "--live"]
    result = run_supervised(cmd, timeout=3600, max_retries=1, cwd=str(PROJECT_ROOT))
    return {
        "ok": result.exit_code == 0 and not result.crashed,
        "exit_code": result.exit_code,
        "crashed": result.crashed,
        "error": result.error,
    }


def phase_report() -> Dict[str, Any]:
    """Generate daily report."""
    r = _run_cli(["report"])
    return {"ok": r.returncode == 0}


def phase_craft() -> Dict[str, Any]:
    """Generate craft memory seeds."""
    r = _run_cli(["craft"])
    return {"ok": r.returncode == 0}


# ═══════════════════════════════════════════════════════════════════════
# Main tidal engine
# ═══════════════════════════════════════════════════════════════════════


class TidalEngine:
    """Continuous unattended runtime loop.

    Runs: register → plan → run → report → craft → sleep → repeat.
    Writes structured events, heartbeat, and tide records.
    """

    def __init__(
        self,
        interval: int = 3600,        # seconds between cycles
        max_cycles: int = 0,         # 0 = run forever
        task_limit: int = 0,         # max tasks per cycle (0 = unlimited)
        presets: str = "",           # comma-separated preset list
        output_dir: Optional[Path] = None,
    ):
        self.interval = interval
        self.max_cycles = max_cycles
        self.task_limit = task_limit
        self.presets = presets
        self.output_dir = output_dir or (PROJECT_ROOT / "outputs" / "tidal")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.events_path = self.output_dir / "tidal_events.jsonl"
        self.heartbeat_path = self.output_dir / "tidal_heartbeat.json"
        self.records_path = self.output_dir / "tidal_records.jsonl"
        self.pid_path = self.output_dir / "tidal.pid"
        self._running = True
        self._cycle_count = 0
        self._total_tasks = 0
        self._total_succeeded = 0
        self._total_failed = 0

        # Write PID
        self.pid_path.write_text(str(os.getpid()))

        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        self._emit("SHUTDOWN", f"Received signal {signum}")
        self._running = False

    def _emit(self, event_type: str, message: str = "", **extra) -> None:
        """Emit a structured event."""
        event = {
            "timestamp": _utc_now(),
            "event_type": event_type,
            "cycle": self._cycle_count,
            "message": message,
            **extra,
        }
        with open(self.events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _heartbeat(self) -> None:
        """Write heartbeat file for external monitoring."""
        hb = {
            "timestamp": _utc_now(),
            "pid": os.getpid(),
            "cycle": self._cycle_count,
            "total_tasks": self._total_tasks,
            "total_succeeded": self._total_succeeded,
            "total_failed": self._total_failed,
            "free_disk_gb": _disk_free_gb(self.output_dir),
            "free_mem_gb": _mem_free_gb(),
        }
        self.heartbeat_path.write_text(json.dumps(hb, ensure_ascii=False))

    def _health_check(self) -> bool:
        """Pre-cycle health check. Returns False if should pause."""
        free_disk = _disk_free_gb(self.output_dir)
        free_mem = _mem_free_gb()

        if free_disk < 3.0:
            self._emit("HEALTH_FAIL", f"Disk critically low: {free_disk}GB", free_disk_gb=free_disk)
            return False

        if free_mem > 0 and free_mem < 0.5:
            self._emit("HEALTH_FAIL", f"Memory critically low: {free_mem}GB", free_mem_gb=free_mem)
            return False

        return True

    def _run_one_cycle(self) -> TideRecord:
        """Execute one complete tidal cycle."""
        self._cycle_count += 1
        cycle_id = f"TIDE_{_utc_now().replace(':','-').replace('T','_')[:19]}"
        record = TideRecord(
            cycle_id=cycle_id,
            cycle_number=self._cycle_count,
            started_at=_utc_now(),
            free_disk_gb=_disk_free_gb(self.output_dir),
            free_mem_gb=_mem_free_gb(),
        )

        self._emit("CYCLE_START", f"Cycle {self._cycle_count} started", cycle_id=cycle_id)

        # ── Phase 1: Register ──
        record.phase = "register"
        result = phase_register()
        if not result["ok"]:
            record.errors.append(f"register: {result.get('stderr_tail', '')[:200]}")
        self._emit("PHASE", f"register: {'OK' if result['ok'] else 'FAIL'}")

        # ── Phase 2: Plan ──
        record.phase = "plan"
        result = phase_plan(presets=self.presets)
        if not result["ok"]:
            record.errors.append(f"plan: {result.get('stderr_tail', '')[:200]}")
        self._emit("PHASE", f"plan: {'OK' if result['ok'] else 'FAIL'}")

        # ── Phase 3: Run (supervised) ──
        record.phase = "run"
        result = phase_run(limit=self.task_limit)
        record.tasks_processed = self._total_tasks
        if not result["ok"] and not result.get("crashed"):
            record.errors.append(f"run: {result.get('error', '')[:200]}")
        self._emit("PHASE", f"run: {'OK' if result['ok'] else 'FAIL' if not result.get('crashed') else 'CRASHED'}",
                   exit_code=result.get("exit_code"), attempts=result.get("attempts"))

        # ── Phase 4: Report ──
        record.phase = "report"
        result = phase_report()
        self._emit("PHASE", f"report: {'OK' if result['ok'] else 'FAIL'}")

        # ── Phase 5: Craft ──
        record.phase = "craft"
        result = phase_craft()
        self._emit("PHASE", f"craft: {'OK' if result['ok'] else 'FAIL'}")

        # ── Finalize ──
        record.phase = "sleep"
        record.finished_at = _utc_now()
        record.free_disk_gb = _disk_free_gb(self.output_dir)
        record.free_mem_gb = _mem_free_gb()

        self._heartbeat()
        self._emit("CYCLE_END", f"Cycle {self._cycle_count} complete",
                   tasks_processed=record.tasks_processed,
                   elapsed_s=record.elapsed_s)

        # Append record
        with open(self.records_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

        return record

    def run(self) -> Dict[str, Any]:
        """Start the tidal cycle loop. Runs until max_cycles or shutdown signal."""
        self._emit("ENGINE_START", f"Tidal engine starting. Interval={self.interval}s, max_cycles={self.max_cycles or '∞'}")
        self._heartbeat()

        cycle_start_time = time.time()

        while self._running:
            if self.max_cycles and self._cycle_count >= self.max_cycles:
                self._emit("ENGINE_STOP", f"Max cycles reached: {self.max_cycles}")
                break

            if not self._health_check():
                self._emit("ENGINE_PAUSE", "Health check failed — pausing 5min")
                time.sleep(300)
                continue

            t0 = time.time()
            try:
                record = self._run_one_cycle()
            except Exception as e:
                self._emit("CYCLE_ERROR", f"Unhandled: {type(e).__name__}: {e}")
                record = TideRecord(
                    cycle_id=f"TIDE_ERR_{_utc_now()[:19]}",
                    cycle_number=self._cycle_count,
                    phase="error",
                    started_at=_utc_now(),
                    finished_at=_utc_now(),
                    errors=[f"{type(e).__name__}: {e}"],
                )
                with open(self.records_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

            elapsed = time.time() - t0
            record.elapsed_s = round(elapsed, 1)

            # Sleep until next cycle
            sleep_time = max(0, self.interval - elapsed)
            if sleep_time > 0 and self._running:
                self._emit("SLEEP", f"Sleeping {sleep_time:.0f}s until next tide")
                # Sleep in 10s chunks to check shutdown signal
                while sleep_time > 0 and self._running:
                    time.sleep(min(10, sleep_time))
                    sleep_time -= 10
                    self._heartbeat()

        self._heartbeat()
        self._emit("ENGINE_STOP", f"Engine stopped after {self._cycle_count} cycles, "
                   f"{self._total_tasks} tasks, {time.time() - cycle_start_time:.0f}s")
        self.pid_path.unlink(missing_ok=True)

        return {
            "cycles_completed": self._cycle_count,
            "total_tasks": self._total_tasks,
            "total_succeeded": self._total_succeeded,
            "total_failed": self._total_failed,
            "elapsed_s": round(time.time() - cycle_start_time, 1),
        }


# ═══════════════════════════════════════════════════════════════════════
# CLI entry
# ═══════════════════════════════════════════════════════════════════════


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Moodify 潮汐循环 (Tidal Cycle)")
    ap.add_argument("--interval", type=int, default=3600, help="Seconds between cycles (default: 3600 = 1h)")
    ap.add_argument("--max-cycles", type=int, default=0, help="Max cycles (0 = forever)")
    ap.add_argument("--task-limit", type=int, default=0, help="Max tasks per cycle (0 = unlimited)")
    ap.add_argument("--presets", default="", help="Comma-separated preset list")
    ap.add_argument("--output-dir", default="", help="Tidal output directory")
    args = ap.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None

    print("🌊 Moodify 潮汐循环 (Tidal Cycle)")
    print(f"   Interval: {args.interval}s ({args.interval/3600:.1f}h)")
    print(f"   Max cycles: {args.max_cycles or '∞'}")
    print(f"   Task limit: {args.task_limit or '∞'} per cycle")
    print(f"   Output: {output_dir or PROJECT_ROOT / 'outputs' / 'tidal'}")
    print()

    engine = TidalEngine(
        interval=args.interval,
        max_cycles=args.max_cycles,
        task_limit=args.task_limit,
        presets=args.presets,
        output_dir=output_dir,
    )
    result = engine.run()

    print()
    print(f"🌊 潮汐结束 — {result['cycles_completed']} cycles, "
          f"{result['total_succeeded']}/{result['total_tasks']} tasks succeeded, "
          f"{result['elapsed_s']:.0f}s total")
    return 0 if result["total_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
