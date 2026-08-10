"""Serial unattended worker for low-resource Moodify hosts."""

from __future__ import annotations

import logging
import signal
import time
from dataclasses import dataclass

from .config import NodeConfig
from .queue import JobQueue
from .resources import safe_to_start
from .runner_adapter import run_data_factory

LOG = logging.getLogger("moodify.node.worker")


@dataclass
class StopFlag:
    requested: bool = False


def run_forever(config: NodeConfig | None = None) -> int:
    config = config or NodeConfig.from_env()
    config.state_dir.mkdir(parents=True, exist_ok=True)
    config.output_root.mkdir(parents=True, exist_ok=True)
    queue = JobQueue(config.db_path, lease_seconds=config.lease_seconds)
    recovered = queue.recover_interrupted()
    if recovered:
        LOG.warning("recovered_interrupted_jobs=%s", recovered)

    stop = StopFlag()

    def request_stop(signum, _frame):
        LOG.info("stop_requested signal=%s", signum)
        stop.requested = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    while not stop.requested:
        allowed, snap, reason = safe_to_start(
            config.output_root,
            config.min_available_memory_mb,
            config.min_free_disk_gb,
        )
        if not allowed:
            LOG.warning(
                "resource_defer reason=%s mem_mb=%.0f disk_gb=%.2f",
                reason,
                snap.available_memory_mb,
                snap.free_disk_gb,
            )
            time.sleep(config.poll_seconds)
            continue

        job = queue.lease_next()
        if job is None:
            time.sleep(config.poll_seconds)
            continue

        LOG.info("job_started job_id=%s source=%s attempt=%s", job.job_id, job.source_path, job.attempts)
        try:
            case_dir = run_data_factory(job.source_path, job.output_root, config.scan_profile_id)
        except Exception as exc:
            LOG.exception("job_failed job_id=%s", job.job_id)
            queue.fail(job.job_id, f"{type(exc).__name__}: {exc}")
        else:
            queue.succeed(job.job_id, case_dir)
            LOG.info("job_succeeded job_id=%s case_dir=%s", job.job_id, case_dir)

    return 0
