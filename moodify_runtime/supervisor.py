"""MHP-095: Process Supervisor Probe — minimal wrapper for subprocess with timeout, retry, and crash logging.

This is a PROBE experiment. Its purpose is to validate that we can reliably detect and
restart crashed subprocesses before we invest in a full production supervisor in Build NEM.
"""

from __future__ import annotations

import subprocess
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import utc_now_iso


@dataclass
class SupervisedRun:
    command: List[str]
    timeout: float = 300.0
    max_retries: int = 2
    retry_delay: float = 1.0
    started_at: str = ""
    finished_at: str = ""
    exit_code: int = -1
    attempts: int = 0
    stdout_tail: str = ""
    stderr_tail: str = ""
    crashed: bool = False
    timed_out: bool = False
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": " ".join(self.command),
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "exit_code": self.exit_code,
            "attempts": self.attempts,
            "crashed": self.crashed,
            "timed_out": self.timed_out,
            "error": self.error,
        }


def run_supervised(
    command: List[str],
    timeout: float = 300.0,
    max_retries: int = 2,
    retry_delay: float = 1.0,
    cwd: Optional[str] = None,
) -> SupervisedRun:
    """Run a subprocess with timeout, crash detection, and retry.

    Returns a SupervisedRun dataclass with the outcome.

    This is the minimal viable supervisor. It does NOT:
    - Monitor resources (CPU, memory)
    - Send heartbeats (that's MHP-096)
    - Checkpoint state (that's MHP-097)
    - Handle SIGTERM/SIGKILL escalation (that's Build NEM)
    """
    normalized_command = list(command)
    if normalized_command and normalized_command[0] in {"python", "python3"}:
        if shutil.which(normalized_command[0]) is None:
            normalized_command[0] = sys.executable
    elif normalized_command and normalized_command[0] == "echo" and shutil.which("echo") is None:
        message = " ".join(normalized_command[1:])
        normalized_command = [sys.executable, "-c", f"print({message!r})"]
    elif normalized_command and normalized_command[0] == "sleep" and shutil.which("sleep") is None:
        seconds = float(normalized_command[1]) if len(normalized_command) > 1 else 0.0
        normalized_command = [sys.executable, "-c", f"import time; time.sleep({seconds!r})"]

    result = SupervisedRun(
        command=list(command),
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
        started_at=utc_now_iso(),
    )

    for attempt in range(1, max_retries + 2):  # max_retries + initial attempt
        result.attempts = attempt
        try:
            proc = subprocess.run(
                normalized_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )
            result.exit_code = proc.returncode
            result.stdout_tail = proc.stdout[-500:] if proc.stdout else ""
            result.stderr_tail = proc.stderr[-500:] if proc.stderr else ""

            if proc.returncode == 0:
                result.crashed = False
                result.error = ""
                break
            else:
                result.crashed = True
                result.error = f"exit_code={proc.returncode}"
                if attempt <= max_retries:
                    time.sleep(retry_delay)
                    continue
        except subprocess.TimeoutExpired:
            result.timed_out = True
            result.crashed = True
            result.error = f"timeout after {timeout}s"
            if attempt <= max_retries:
                time.sleep(retry_delay)
                continue
        except Exception as e:
            result.crashed = True
            result.error = f"{type(e).__name__}: {e}"
            if attempt <= max_retries:
                time.sleep(retry_delay)
                continue

    result.finished_at = utc_now_iso()
    return result
