from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Version check
# ---------------------------------------------------------------------------

MIN_PYTHON = (3, 8)


def check_python_version() -> None:
    if sys.version_info < MIN_PYTHON:
        raise RuntimeError(
            f"Python {'.'.join(map(str, MIN_PYTHON))}+ required, "
            f"got {sys.version_info.major}.{sys.version_info.minor}"
        )

# ---------------------------------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------------------------------

_shutdown_requested = False


def _signal_handler(signum: int, frame: Any) -> None:
    global _shutdown_requested
    _shutdown_requested = True


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


def shutdown_requested() -> bool:
    return _shutdown_requested

# ---------------------------------------------------------------------------
# Time helpers (timezone-aware, no deprecated utcnow)
# ---------------------------------------------------------------------------


def utc_now_iso() -> str:
    try:
        return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    except AttributeError:
        return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def local_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")

# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def check_disk_space(path: Path, min_free_gb: float) -> Tuple[bool, float]:
    """Returns (ok, free_gb)."""
    try:
        usage = shutil.disk_usage(path)
        free_gb = usage.free / (1024**3)
        return free_gb >= min_free_gb, free_gb
    except Exception:
        return True, -1.0


def cleanup_old_runs(base: Path, keep_last: int, logger: "LineLogger") -> None:
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
# JSON / JSONL
# ---------------------------------------------------------------------------


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=False) + "\n")


def write_json(path: Path, obj: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_json(path: Path, obj: Any) -> None:
    """Write JSON via temp file + rename for crash safety."""
    ensure_parent(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def atomic_write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    """Write JSONL via temp file + rename for crash safety."""
    ensure_parent(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")
    tmp.replace(path)

# ---------------------------------------------------------------------------
# File identity
# ---------------------------------------------------------------------------


def file_sha1(path: Path, max_bytes: Optional[int] = None) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        if max_bytes is None:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        else:
            remaining = max_bytes
            while remaining > 0:
                chunk = f.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                h.update(chunk)
                remaining -= len(chunk)
    return h.hexdigest()


def stable_sample_id(path: Path) -> str:
    stat = path.stat()
    h = hashlib.sha1()
    h.update(path.name.encode("utf-8", errors="ignore"))
    h.update(str(stat.st_size).encode())
    h.update(file_sha1(path, max_bytes=2 * 1024 * 1024).encode())
    return "SMP_" + h.hexdigest()[:16].upper()

# ---------------------------------------------------------------------------
# Audio discovery
# ---------------------------------------------------------------------------


def discover_audio_files(
    input_dirs: Iterable[Path], suffixes: Iterable[str], recurse: bool, max_files: int = 0
) -> List[Path]:
    suffix_set = {s.lower() for s in suffixes}
    files: List[Path] = []
    for input_dir in input_dirs:
        if not input_dir.exists():
            continue
        iterator = input_dir.rglob("*") if recurse else input_dir.glob("*")
        for p in iterator:
            if p.is_file() and p.suffix.lower() in suffix_set:
                files.append(p)
    files = sorted(set(files), key=lambda x: str(x).lower())
    if max_files and max_files > 0:
        files = files[:max_files]
    return files

# ---------------------------------------------------------------------------
# Subprocess (with process-group kill on timeout)
# ---------------------------------------------------------------------------


def quote_cmd(cmd: List[str]) -> str:
    return " ".join(shlex.quote(x) for x in cmd)


def render_template_to_argv(template: str, values: Dict[str, Any]) -> List[str]:
    return shlex.split(template.format(**{k: shlex.quote(str(v)) for k, v in values.items()}))


def run_command(
    cmd: List[str], cwd: Path, env: Dict[str, str], timeout: int
) -> Dict[str, Any]:
    start = time.time()
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
        return {
            "return_code": proc.returncode,
            "elapsed_seconds": elapsed,
            "stdout_tail": (stdout or "")[-4000:],
            "stderr_tail": (stderr or "")[-4000:],
            "stdout_full": stdout or "",
            "stderr_full": stderr or "",
            "timed_out": False,
            "exception": None,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        _kill_process_group(proc)
        return {
            "return_code": 124,
            "elapsed_seconds": elapsed,
            "stdout_tail": "",
            "stderr_tail": f"timeout after {timeout}s",
            "stdout_full": "",
            "stderr_full": f"timeout after {timeout}s",
            "timed_out": True,
            "exception": "TimeoutExpired",
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "return_code": 125,
            "elapsed_seconds": elapsed,
            "stdout_tail": "",
            "stderr_tail": str(e),
            "stdout_full": "",
            "stderr_full": str(e),
            "timed_out": False,
            "exception": type(e).__name__,
        }


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


class LockFile:
    def __init__(self, path: Path):
        self.path = path

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(f"pid={os.getpid()}\ncreated_at={utc_now_iso()}\n")
        except FileExistsError:
            raise RuntimeError(
                f"Lock exists: {self.path}. "
                "Confirm no worker is running before deleting it."
            )

    def release(self) -> None:
        try:
            self.path.unlink(missing_ok=True)
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------


class LineLogger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, message: str) -> None:
        line = f"[{dt.datetime.now().isoformat(timespec='seconds')}] {message}"
        print(line, flush=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------


def append_csv(path: Path, row: Dict[str, Any], fieldnames: List[str]) -> None:
    ensure_parent(path)
    exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in fieldnames})
