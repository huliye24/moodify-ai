"""Canonical Moodify 1.0 API — The Ear of AI."""

from __future__ import annotations

import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from moodify.auditory.errors import AuditoryError
from moodify.release import PRODUCT_VERSION, analyze_to_case, reopen_case
from moodify.node.config import NodeConfig
from moodify.node.queue import JobQueue
from moodify.api.routes.analyze import router as intelligence_analyze_router
from moodify.api.routes.evaluate import router as intelligence_evaluate_router
from moodify.api.routes.process import router as intelligence_process_router
from moodify.api.routes.reviews import router as reviews_router
from moodify.api.routes.stems import router as stems_router
from moodify.reconstruction_job.routes_reconstruction import router as reconstruction_router

MAX_SIZE = int(os.environ.get("MOODIFY_MAX_UPLOAD_BYTES", str(50 * 1024 * 1024)))
ALLOWED_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aac"}

app = FastAPI(
    title="Moodify — The Ear of AI",
    version=PRODUCT_VERSION,
    description="Can machines learn to hear? Evidence-backed auditory intelligence.",
)


def _cases_root() -> Path:
    return Path(os.environ.get("MOODIFY_CASES_ROOT", "outputs/moodify_cases"))


def _node_config() -> NodeConfig:
    return NodeConfig.from_env()


def _queue() -> JobQueue:
    config = _node_config()
    return JobQueue(config.db_path, lease_seconds=config.lease_seconds)


def _public_job(job) -> dict:
    payload = asdict(job)
    payload.pop("source_path", None)
    payload.pop("output_root", None)
    payload.pop("case_dir", None)
    if payload.get("last_error"):
        payload["last_error"] = "Auditory processing failed; the evidence was retained for operator review."
    payload["result_ready"] = job.status == "SUCCEEDED" and bool(job.case_dir)
    return payload


def _safe_json(path: Path) -> dict | list | None:
    import json
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


app.include_router(reviews_router)
app.include_router(stems_router)
app.include_router(reconstruction_router)
app.include_router(intelligence_analyze_router)
app.include_router(intelligence_evaluate_router)
app.include_router(intelligence_process_router)


@app.get("/health")
async def health() -> dict:
    counts = _queue().counts()
    return {
        "status": "ok",
        "product": "Moodify",
        "version": PRODUCT_VERSION,
        "identity": "The Ear of AI",
        "queue": counts,
    }


@app.get("/api/v1/health")
async def api_health() -> dict:
    return await health()


@app.post("/api/v1/auditory/analyze")
async def analyze(audio: UploadFile = File(...)) -> dict:
    """Preserve the existing production-case analysis contract."""
    content = await audio.read(MAX_SIZE + 1)
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail={"code": "AUDIO_TOO_LARGE"})
    suffix = Path(audio.filename or "upload.wav").suffix or ".wav"
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
            handle.write(content)
            tmp_path = Path(handle.name)
        return analyze_to_case(
            tmp_path,
            _cases_root(),
            display_name=Path(audio.filename or "upload.wav").name,
        )
    except AuditoryError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": type(exc).__name__.upper(), "message": str(exc)},
        ) from exc
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "ANALYSIS_FAILED", "message": str(exc)},
        ) from exc
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


@app.post("/api/v1/auditory/jobs", status_code=202)
async def create_job(audio: UploadFile = File(...), prompt: str = Form(default="")) -> dict:
    """Persist an upload and enqueue it in the canonical unattended node queue."""
    config = _node_config()
    queue = _queue()
    if sum(queue.counts().values()) >= int(os.environ.get("MOODIFY_MAX_RETAINED_JOBS", "500")):
        raise HTTPException(status_code=503, detail={"code": "QUEUE_CAPACITY_REACHED"})
    suffix = Path(audio.filename or "upload.wav").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail={"code": "AUDIO_TYPE_UNSUPPORTED"})
    upload_root = config.state_dir / "uploads"
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
        job = queue.enqueue(path, config.output_root)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return {
        "job": _public_job(job),
        "request": {"filename": Path(audio.filename or "upload").name, "prompt": prompt[:1000]},
    }


@app.get("/api/v1/auditory/jobs/{job_id}")
async def get_job(job_id: str) -> dict:
    job = _queue().get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"code": "JOB_NOT_FOUND"})
    return {"job": _public_job(job)}


@app.get("/api/v1/auditory/jobs/{job_id}/result")
async def get_job_result(job_id: str) -> dict:
    job = _queue().get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"code": "JOB_NOT_FOUND"})
    if job.status != "SUCCEEDED" or not job.case_dir:
        raise HTTPException(status_code=409, detail={"code": "RESULT_NOT_READY", "status": job.status})
    case_dir = Path(job.case_dir).resolve()
    output_root = Path(job.output_root).resolve()
    if output_root not in case_dir.parents:
        raise HTTPException(status_code=500, detail={"code": "RESULT_PATH_INVALID"})
    return {
        "job": _public_job(job),
        "case_manifest": _safe_json(case_dir / "case_manifest.json"),
        "production_case": _safe_json(case_dir / "production_case.json"),
        "algorithmic_review": _safe_json(case_dir / "06_human_review" / "review.json"),
        "algorithmic_scores": _safe_json(case_dir / "06_human_review" / "algorithmic_scores.json"),
    }


@app.get("/api/v1/auditory/cases/{case_id}")
async def get_case(case_id: str) -> dict:
    try:
        return reopen_case(_cases_root(), case_id)
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "CASE_NOT_FOUND", "message": "case not found"},
        ) from exc
