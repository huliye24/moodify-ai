"""Serial reconstruction job worker (MFY-CR-P08).

Single-process, single-job-at-a-time (concurrency = 1). On startup it recovers
interrupted jobs from a previous worker, runs one retention sweep, then leases
and executes jobs until stopped. Logs are structured and never contain raw
audio, secrets, or tokens.
"""

from __future__ import annotations

import logging
import signal
import time
from dataclasses import dataclass
from pathlib import Path

from moodify.node.resources import safe_to_start

from .contract import RetentionPolicy
from .engine import EngineConfig, run_reconstruction_job
from .retention import sweep_workspaces
from .store import JobStore

logger = logging.getLogger("moodify.reconstruction_job.worker")

SWEEP_INTERVAL_S = 3600


@dataclass(frozen=True)
class WorkerConfig:
    db_path: Path
    workspace_root: Path
    lease_seconds: int = 6 * 60 * 60
    max_attempts: int = 3
    min_memory_mb: int = 256
    min_disk_gb: float = 1.0
    poll_seconds: float = 2.0
    retention: RetentionPolicy = RetentionPolicy()

    def engine_config(self) -> EngineConfig:
        return EngineConfig(workspace_root=self.workspace_root)


class StopFlag:
    def __init__(self) -> None:
        self.stopped = False

    def request_stop(self, *_args) -> None:
        self.stopped = True


def run_forever(config: WorkerConfig | None = None) -> int:
    """Blocking worker loop; returns 0 on clean shutdown."""
    config = config or WorkerConfig(
        db_path=Path("state/reconstruction_jobs.db"),
        workspace_root=Path("state/reconstruction_workspace"),
    )
    store = JobStore(config.db_path, lease_seconds=config.lease_seconds)
    flag = StopFlag()
    signal.signal(signal.SIGINT, flag.request_stop)
    signal.signal(signal.SIGTERM, flag.request_stop)

    recovered = store.recover_interrupted()
    if recovered:
        logger.info("recovered %d interrupted jobs after restart", recovered)
    sweep_workspaces(config.workspace_root, config.retention, store.active_job_ids())

    last_sweep = time.monotonic()
    while not flag.stopped:
        processed = _process_one(store, config)
        if not processed and not flag.stopped:
            now = time.monotonic()
            if now - last_sweep >= SWEEP_INTERVAL_S:
                sweep_workspaces(config.workspace_root, config.retention, store.active_job_ids())
                last_sweep = now
            time.sleep(config.poll_seconds)
    logger.info("worker stopped")
    return 0


def run_once(config: WorkerConfig) -> int:
    """Process at most one job (tests, cron-style operation)."""
    store = JobStore(config.db_path, lease_seconds=config.lease_seconds)
    store.recover_interrupted()
    return 1 if _process_one(store, config) else 0


def _process_one(store: JobStore, config: WorkerConfig) -> bool:
    ok, snapshot, reason = safe_to_start(
        config.workspace_root, config.min_memory_mb, config.min_disk_gb
    )
    if not ok:
        logger.warning("resource precheck DEFER: %s (mem=%sMB disk=%sGB)",
                       reason, snapshot.available_memory_mb, snapshot.available_disk_gb)
        return False
    job = store.lease_next()
    if job is None:
        return False
    logger.info("job %s lease acquired", job.job_id)
    try:
        status = run_reconstruction_job(job, store, config.engine_config())
        logger.info("job %s finished: %s", job.job_id, status)
        return True
    except Exception:
        logger.exception("job %s worker error", job.job_id)
        return True
