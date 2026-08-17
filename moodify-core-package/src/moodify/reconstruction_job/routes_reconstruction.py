"""Reconstruction job API routes (MFY-CR-P08).

Product-facing surface only: no engineering parameters, no internal paths,
no public URLs. Android (P09) will consume exactly these endpoints.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, Header, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse

from moodify.reconstruction_job.audio_util import sha256_file

from . import auth
from .contract import (
    BILLING_STATE_NOT_IMPLEMENTED,
    JobStatus,
    ReconstructionJob,
    progress_label,
)
from .store import JobStore

router = APIRouter(prefix="/api/v1/reconstruction", tags=["reconstruction"])

MAX_SIZE = int(os.environ.get("MOODIFY_MAX_UPLOAD_BYTES", str(50 * 1024 * 1024)))
MAX_RETAINED_JOBS = int(os.environ.get("MOODIFY_MAX_RETAINED_JOBS", "500"))
ALLOWED_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg"}

RECONSTRUCTION_VERSION = "reconstruction-job-v0.1"


def _workspace_root() -> Path:
    return Path(os.environ.get("MOODIFY_RECON_WORKSPACE_ROOT", "state/reconstruction_workspace"))


def _db_path() -> Path:
    return Path(os.environ.get("MOODIFY_RECON_DB", "state/reconstruction_jobs.db"))


def _store() -> JobStore:
    return JobStore(_db_path(), lease_seconds=int(os.environ.get("MOODIFY_RECON_LEASE_SECONDS", "21600")))


def _reject_engineering_params(mode: str | None, training: str | None, demo: str | None) -> None:
    if mode not in (None, "auto"):
        raise HTTPException(status_code=400, detail={"code": "MODE_UNSUPPORTED"})
    if str(training).lower() in ("true", "1"):
        raise HTTPException(status_code=400, detail={"code": "TRAINING_DISALLOWED"})
    if str(demo).lower() in ("true", "1"):
        raise HTTPException(status_code=400, detail={"code": "PUBLIC_DEMO_DISALLOWED"})


@router.get("/capabilities")
async def capabilities() -> dict:
    return {
        "api_version": "v0.1",
        "supported_formats": sorted(ALLOWED_SUFFIXES),
        "max_file_size_bytes": MAX_SIZE,
        "max_duration_seconds": None,
        "reconstruction_mode": ["auto"],
        "reconstruction_version": RECONSTRUCTION_VERSION,
        "stems_available": False,
        "human_review_available": True,
        "auth_mode": auth.auth_mode(),
    }


@router.post("/jobs", status_code=202)
async def create_job(
    request: Request,
    response: Response,
    source: UploadFile = File(...),
    reconstruction_mode: str | None = Form(default=None),
    training_permission: str | None = Form(default=None),
    public_demo_permission: str | None = Form(default=None),
    idempotency_key: str | None = Header(default=None),
    x_moodify_rebuild: str | None = Header(default=None),
) -> dict:
    _reject_engineering_params(reconstruction_mode, training_permission, public_demo_permission)
    actor = auth.actor_from_request(request)

    suffix = Path(source.filename or "upload.wav").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail={"code": "AUDIO_TYPE_UNSUPPORTED"})

    store = _store()
    if sum(store.counts().values()) >= MAX_RETAINED_JOBS:
        raise HTTPException(status_code=503, detail={"code": "QUEUE_CAPACITY_REACHED"})

    workspace_root = _workspace_root()
    workspace_root.mkdir(parents=True, exist_ok=True)
    staging = workspace_root / f"staging_{uuid4().hex}{suffix}"
    size = 0
    try:
        with staging.open("xb") as handle:
            while chunk := await source.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_SIZE:
                    raise HTTPException(status_code=413, detail={"code": "AUDIO_TOO_LARGE"})
                handle.write(chunk)
        if size == 0:
            raise HTTPException(status_code=422, detail={"code": "AUDIO_EMPTY"})
        sha256 = sha256_file(staging)
    except Exception:
        staging.unlink(missing_ok=True)
        raise

    if idempotency_key:
        existing = store.find_existing(actor, sha256, RECONSTRUCTION_VERSION, idempotency_key)
        if existing is not None:
            staging.unlink(missing_ok=True)
            response.status_code = 200
            return {"job": existing.product_view(), "source_sha256": sha256,
                    "idempotency": "RETURN_EXISTING"}

    rebuild = str(x_moodify_rebuild).lower() in ("true", "1")
    if not rebuild:
        prior = store.find_latest_success(actor, sha256, RECONSTRUCTION_VERSION)
        if prior is not None:
            staging.unlink(missing_ok=True)
            response.status_code = 200
            return {"job": prior.product_view(), "source_sha256": sha256,
                    "idempotency": "RETURN_EXISTING"}

    job_id = f"job_{uuid4().hex}"
    job_dir = workspace_root / job_id
    input_dir = job_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    final_path = input_dir / f"original{suffix}"
    shutil.move(str(staging), final_path)
    (job_dir / "tmp").mkdir(parents=True, exist_ok=True)

    from moodify.contracts.base import utc_now
    now = utc_now().isoformat(timespec="seconds")
    job = ReconstructionJob(
        job_id=job_id,
        owner_id=actor,
        source_asset_id=f"sha256:{sha256}",
        source_sha256=sha256,
        status=JobStatus.QUEUED.value,
        progress_stage=None,
        requested_at=now,
        reconstruction_version=RECONSTRUCTION_VERSION,
        billing_state_placeholder=BILLING_STATE_NOT_IMPLEMENTED,
        idempotency_key=idempotency_key,
        workspace_path=str(job_dir),
    )
    store.insert_job(job)
    return {"job": job.product_view(), "source_sha256": sha256, "idempotency": "CREATED"}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, request: Request) -> dict:
    actor = auth.actor_from_request(request)
    job = _store().get_job(actor, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"code": "JOB_NOT_FOUND"})
    return {"job": job.product_view()}


@router.post("/jobs/{job_id}/cancel", status_code=202)
async def cancel_job(job_id: str, request: Request) -> dict:
    actor = auth.actor_from_request(request)
    store = _store()
    job = store.get_job(actor, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"code": "JOB_NOT_FOUND"})
    if job.status in (JobStatus.SUCCEEDED.value, JobStatus.SOURCE_WINS.value,
                      JobStatus.FAILED.value, JobStatus.CANCELLED.value,
                      JobStatus.HUMAN_REQUIRED.value):
        raise HTTPException(status_code=409, detail={"code": "JOB_TERMINAL", "status": job.status})
    updated = store.request_cancel(actor, job_id)
    return {"job": updated.product_view()}


@router.get("/jobs/{job_id}/result")
async def get_result(job_id: str, request: Request) -> dict:
    actor = auth.actor_from_request(request)
    store = _store()
    job = store.get_job(actor, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"code": "JOB_NOT_FOUND"})
    if job.status == JobStatus.HUMAN_REQUIRED.value:
        return {"status": JobStatus.HUMAN_REQUIRED.value,
                "progress": progress_label(job.status),
                "user_action_required": True}
    if job.status not in (JobStatus.SUCCEEDED.value, JobStatus.SOURCE_WINS.value):
        raise HTTPException(status_code=409, detail={"code": "RESULT_NOT_READY", "status": job.status})
    result = store.get_result(actor, job_id)
    if result is None:
        raise HTTPException(status_code=409, detail={"code": "RESULT_NOT_READY", "status": job.status})
    payload = result.to_dict()
    payload["audio_url"] = f"/api/v1/reconstruction/jobs/{job_id}/result/audio?token={auth.issue_audio_token(job_id, actor)}"
    return {"result": payload}


@router.get("/jobs/{job_id}/result/audio")
async def get_result_audio(job_id: str, request: Request, token: str) -> FileResponse:
    actor = auth.actor_from_request(request)
    auth.verify_audio_token(token, job_id, actor)
    store = _store()
    result = store.get_result(actor, job_id)
    if result is None:
        raise HTTPException(status_code=404, detail={"code": "RESULT_NOT_FOUND"})
    workspace_root = _workspace_root().resolve()
    audio = (workspace_root / result.audio_object_ref).resolve()
    if workspace_root not in audio.parents:
        raise HTTPException(status_code=403, detail={"code": "ACCESS_DENIED"})
    if not audio.is_file():
        raise HTTPException(status_code=404, detail={"code": "RESULT_NOT_FOUND"})
    return FileResponse(audio, media_type="audio/wav", filename=Path(result.audio_object_ref).name)
