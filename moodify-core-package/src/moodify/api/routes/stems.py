"""Stem separation API — LALAL-STEMS-001.

Synchronous endpoints (threadpool via FastAPI). Submission is fire-and-check:
POST returns immediately, clients poll GET /jobs/{id} which live-refreshes
against lalal.ai when the poll interval elapsed.
"""

from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile

from moodify.stems import constants as stem_constants
from moodify.stems import service
from moodify.stems.errors import (
    StemError,
    StemLicenseInvalid,
    StemTaskUnknown,
    StemUpstreamError,
    StemUpstreamRejected,
)
from moodify.stems.store import StemStatus

router = APIRouter(prefix="/api/v1/stems")

# Must stay in sync with moodify.api.main (same env vars, same defaults).
MAX_SIZE = int(os.environ.get("MOODIFY_MAX_UPLOAD_BYTES", str(50 * 1024 * 1024)))
ALLOWED_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aac"}
MAX_RETAINED = int(os.environ.get("MOODIFY_MAX_RETAINED_STEMS", "200"))


def _public_job(job) -> dict:
    data = {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "stems": job.stems,
        "extraction_level": job.extraction_level,
        "splitter": job.splitter,
        "dereverb_enabled": job.dereverb_enabled,
        "multivocal": job.multivocal,
        "source_name": job.source_name,
        "estimated_pro_minutes": job.estimated_pro_minutes,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "finished_at": job.finished_at,
    }
    if job.status == StemStatus.SUCCEEDED.value:
        data["results"] = job.result_urls
    if job.status in (StemStatus.FAILED.value, StemStatus.CANCELLED.value):
        data["last_error"] = job.last_error
    return data


def _map_upstream_error(exc: StemError) -> HTTPException:
    if isinstance(exc, StemLicenseInvalid):
        return HTTPException(status_code=502, detail={"code": exc.code, "message": exc.message})
    if isinstance(exc, StemTaskUnknown):
        return HTTPException(status_code=502, detail={"code": exc.code, "message": exc.message})
    if isinstance(exc, StemUpstreamRejected):
        return HTTPException(status_code=502, detail={"code": exc.code, "message": exc.message})
    if isinstance(exc, StemUpstreamError):
        return HTTPException(status_code=502, detail={"code": exc.code, "message": exc.message})
    return HTTPException(status_code=502, detail={"code": "STEM_ERROR", "message": str(exc)})


@router.post("/jobs", status_code=202)
async def create_stem_job(
    audio: UploadFile = File(...),
    stems: str = Form(...),
    extraction_level: str = Form(default=stem_constants.DEFAULT_EXTRACTION_LEVEL),
    splitter: str = Form(default=stem_constants.DEFAULT_SPLITTER),
    dereverb_enabled: bool = Form(default=False),
    multivocal: str | None = Form(default=None),
) -> dict:
    stem_list = [s.strip() for s in stems.split(",") if s.strip()]
    invalid = [s for s in stem_list if s not in stem_constants.STEMS]
    if not stem_list or invalid:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "STEM_TYPE_INVALID",
                "message": f"valid stems: {', '.join(stem_constants.STEMS)}",
            },
        )
    if extraction_level not in stem_constants.EXTRACTION_LEVELS:
        raise HTTPException(
            status_code=422,
            detail={"code": "STEM_PARAM_INVALID", "message": f"extraction_level must be one of {stem_constants.EXTRACTION_LEVELS}"},
        )
    if splitter not in stem_constants.SPLITTERS:
        raise HTTPException(
            status_code=422,
            detail={"code": "STEM_PARAM_INVALID", "message": f"splitter must be one of {stem_constants.SPLITTERS}"},
        )
    if multivocal and multivocal not in stem_constants.MULTIVOCAL_VALUES:
        raise HTTPException(
            status_code=422,
            detail={"code": "STEM_PARAM_INVALID", "message": f"multivocal must be one of {stem_constants.MULTIVOCAL_VALUES}"},
        )
    suffix = Path(audio.filename or "upload.wav").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail={"code": "AUDIO_TYPE_UNSUPPORTED"})
    if service._store().count() >= MAX_RETAINED:
        raise HTTPException(status_code=503, detail={"code": "STEM_CAPACITY_REACHED"})
    if not service._license_present():
        raise HTTPException(status_code=503, detail={"code": "STEM_LICENSE_MISSING"})

    upload_root = service.uploads_dir()
    upload_root.mkdir(parents=True, exist_ok=True)
    path = upload_root / f"upload_{uuid4().hex}{suffix}"
    size = 0
    try:
        with path.open("xb") as handle:
            while chunk := await audio.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_SIZE:
                    raise HTTPException(status_code=413, detail={"code": "AUDIO_TOO_LARGE"})
                handle.write(chunk)
        if size == 0:
            raise HTTPException(status_code=422, detail={"code": "AUDIO_EMPTY"})
        job = service.submit(
            source_path=path,
            source_name=Path(audio.filename or "upload.wav").name,
            source_bytes=size,
            stems=stem_list,
            extraction_level=extraction_level,
            splitter=splitter,
            dereverb_enabled=dereverb_enabled,
            multivocal=multivocal,
        )
    except StemError as exc:
        raise _map_upstream_error(exc) from exc
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return {"job": _public_job(job), "request": {"stems": stem_list}}


@router.get("/jobs")
def list_stem_jobs(status: str | None = None, limit: int = 50) -> dict:
    if status and status not in {s.value for s in StemStatus}:
        raise HTTPException(
            status_code=422,
            detail={"code": "STATUS_INVALID", "message": f"status must be one of {[s.value for s in StemStatus]}"},
        )
    jobs = service._store().list(status=status, limit=limit)
    return {"jobs": [_public_job(job) for job in jobs], "count": len(jobs)}


@router.get("/jobs/{job_id}")
def get_stem_job(job_id: str) -> dict:
    job = service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"code": "STEM_JOB_NOT_FOUND"})
    if not job.is_terminal and service._poll_due(job):
        try:
            job = service.refresh(job)
        except StemError as exc:
            raise _map_upstream_error(exc) from exc
    return {"job": _public_job(job)}


@router.get("/jobs/{job_id}/download/{stem}")
def download_stem(job_id: str, stem: str) -> Response:
    # "vocals_back" addresses the backing track lalal returns alongside the stem.
    base_stem = stem[:-5] if stem.endswith("_back") else stem
    if base_stem not in stem_constants.STEMS:
        raise HTTPException(
            status_code=422,
            detail={"code": "STEM_TYPE_INVALID", "message": f"valid stems: {', '.join(stem_constants.STEMS)} (plus <stem>_back)"},
        )
    job = service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"code": "STEM_JOB_NOT_FOUND"})
    if job.status != StemStatus.SUCCEEDED.value:
        raise HTTPException(status_code=409, detail={"code": "STEM_RESULT_NOT_READY", "status": job.status})
    url = job.result_urls.get(stem)
    if not url:
        raise HTTPException(
            status_code=409,
            detail={"code": "STEM_RESULT_NOT_READY", "message": f"stem '{stem}' was not part of this job"},
        )
    if service.download_expired(job):
        raise HTTPException(status_code=410, detail={"code": "STEM_DOWNLOAD_EXPIRED"})
    return Response(status_code=307, headers={"Location": url})


@router.get("/usage")
def stem_usage() -> dict:
    return service._store().usage()
