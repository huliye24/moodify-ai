"""Shared evidence builders for tests crossing production safety gates."""

import json
from pathlib import Path

from moodify_runtime.operator_console import (
    authorize_operator_job_source,
    create_delivery_record,
)


def authorize_test_job(cfg, job: dict) -> tuple[Path, str]:
    source = Path(job["source_audio"])
    if not source.is_absolute():
        source = cfg.resolved().project_root / source
    manifest = cfg.resolved().project_root / f"rights_{job['job_id']}.json"
    asset_id = f"TEST-{job['job_id']}"
    manifest.write_text(json.dumps({
        "schema_version": "1.0.0",
        "gate_id": "TEST",
        "assets": [{
            "asset_id": asset_id,
            "source_path": str(source.resolve(strict=False)),
            "status": "ready",
        }],
    }), encoding="utf-8")
    authorize_operator_job_source(cfg, job["job_id"], manifest, asset_id)
    return manifest, asset_id


def create_test_delivery(cfg, job: dict, candidate_id: str, **kwargs):
    authorize_test_job(cfg, job)
    kwargs.setdefault("human_approved", True)
    kwargs.setdefault("approved_by", "test-reviewer")
    return create_delivery_record(
        cfg, job_id=job["job_id"], candidate_id=candidate_id, **kwargs
    )
