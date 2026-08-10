"""Node queue data models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class Job:
    job_id: str
    source_path: str
    output_root: str
    status: str
    attempts: int
    created_at: str
    updated_at: str
    started_at: str | None = None
    finished_at: str | None = None
    lease_until: str | None = None
    case_dir: str | None = None
    last_error: str | None = None
