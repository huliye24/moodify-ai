"""Moodify Mobile API v1 contract (ANDROID-003).

The Android client depends on this protocol permanently. It must never
import Python internals; it only speaks these endpoints.

Live in v0.1.0:
    GET  /api/v1/health
    POST /api/v1/pair
    POST /api/v1/pair/revoke
    GET  /api/v1/capabilities

Schema-frozen, implemented by DSK-MFY-ANDROID-004/005:
    POST /api/v1/projects
    GET  /api/v1/projects/{id}
    POST /api/v1/uploads
    GET  /api/v1/jobs/{id}
    POST /api/v1/jobs/{id}/cancel
    GET  /api/v1/artifacts/{id}

Error contract: every non-2xx response carries a structured body::

    {"error": {"code": "...", "message": "...", "request_id": "..."}}

Client-side error classes: OFFLINE / TIMEOUT are classified by the
client (connection failure). Server returns UNAUTHORIZED / INCOMPATIBLE /
SERVER_ERROR / NOT_FOUND / VALIDATION / NOT_IMPLEMENTED.

Security rules:
    - never return absolute filesystem paths
    - never echo bearer tokens or raw tracebacks
    - pair tokens are revocable and stored outside of logs
"""

from __future__ import annotations

import hashlib
import secrets
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from moodify.v01_presets import list_presets

API_VERSION = "0.1.0"
API_PREFIX = "/api/v1"
MIN_CLIENT_VERSION = "0.1.0"


# ---------------------------------------------------------------------------
# Schemas (frozen; implemented by later packages)
# ---------------------------------------------------------------------------


class V1ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1)
    source_audio_ids: list[str] = Field(min_length=1)


class V1ProjectStatus(BaseModel):
    project_id: str
    title: str
    status: str
    created_at: str
    updated_at: str


class V1UploadCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    project_id: str = Field(min_length=1)
    filename: str = Field(min_length=1)
    size_bytes: int = Field(gt=0)
    sha256: str = Field(min_length=64, max_length=64)


class V1UploadStatus(BaseModel):
    upload_id: str
    project_id: str
    filename: str
    status: str
    received_bytes: int = 0
    total_bytes: int
    created_at: str


class V1JobStatus(BaseModel):
    job_id: str
    project_id: str
    upload_id: str
    status: str
    progress: float = 0.0
    error_code: str | None = None
    created_at: str
    updated_at: str


class V1Artifact(BaseModel):
    artifact_id: str
    job_id: str
    kind: str
    filename: str
    size_bytes: int
    sha256: str
    created_at: str


# ---------------------------------------------------------------------------
# Pair token store (revocable, memory-backed; restart invalidates tokens)
# ---------------------------------------------------------------------------


class PairTokenStore:
    """In-memory revocable token store.

    Tokens die with the process: restarting the service invalidates every
    paired client. This is deliberate (short-lived local trust), and the
    client re-pairs automatically on the next connect attempt.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tokens: dict[str, dict[str, Any]] = {}

    def issue(self, device_id: str, device_name: str) -> dict[str, Any]:
        token = secrets.token_urlsafe(32)
        record = {
            "device_id": device_id,
            "device_name": device_name,
            "issued_at": _iso_now(),
            "revoked": False,
        }
        with self._lock:
            for existing in self._tokens.values():
                if existing["device_id"] == device_id and not existing["revoked"]:
                    return {"token": existing["token"], "token_id": existing["token_id"]}
            token_id = str(uuid.uuid4())
            record["token"] = token
            record["token_id"] = token_id
            self._tokens[token_id] = record
        return {"token": token, "token_id": token_id}

    def revoke(self, token_id: str) -> bool:
        with self._lock:
            record = self._tokens.get(token_id)
            if record is None:
                return False
            record["revoked"] = True
            return True

    def validate(self, token: str) -> dict[str, Any] | None:
        with self._lock:
            for record in self._tokens.values():
                if record["token"] == token and not record["revoked"]:
                    return record
        return None

    def find_by_token(self, token: str) -> tuple[str, dict[str, Any]] | None:
        with self._lock:
            for token_id, record in self._tokens.items():
                if record["token"] == token and not record["revoked"]:
                    return token_id, record
        return None


_pair_store = PairTokenStore()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _v1_error(code: str, message: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=_HTTP_FOR_CODE[code],
        content={"error": {"code": code, "message": message, "request_id": request_id}},
    )


_HTTP_FOR_CODE = {
    "UNAUTHORIZED": 401,
    "INCOMPATIBLE": 409,
    "SERVER_ERROR": 500,
    "NOT_FOUND": 404,
    "VALIDATION": 422,
    "NOT_IMPLEMENTED": 501,
}


def _request_id(request: Request) -> str:
    header = request.headers.get("X-Moodify-Request-Id")
    return header if header else str(uuid.uuid4())


def _bearer_token(request: Request) -> str | None:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return header[7:].strip()


router = APIRouter(prefix=API_PREFIX, tags=["mobile-v1"])


# ---------------------------------------------------------------------------
# Live endpoints
# ---------------------------------------------------------------------------


@router.get("/health")
async def v1_health(request: Request) -> dict[str, Any]:
    """Liveness + version compatibility probe.

    The client compares ``api_version`` against its own supported range and
    classifies a mismatch as INCOMPATIBLE.
    """
    return {
        "status": "ok",
        "api_version": API_VERSION,
        "min_client_version": MIN_CLIENT_VERSION,
        "mode": "mobile-v1",
        "server_time": _iso_now(),
    }


@router.post("/pair")
async def v1_pair(request: Request) -> dict[str, Any]:
    """Pair this device. Idempotent per device_id while its token is live."""
    try:
        payload = await request.json()
    except Exception:
        return _v1_error("VALIDATION", "body must be JSON", _request_id(request))
    device_id = payload.get("device_id")
    device_name = payload.get("device_name", "unknown")
    if not isinstance(device_id, str) or not device_id.strip():
        return _v1_error("VALIDATION", "device_id is required", _request_id(request))
    issued = _pair_store.issue(device_id.strip(), device_name)
    return {
        "token": issued["token"],
        "token_id": issued["token_id"],
        "expires": None,
        "api_version": API_VERSION,
    }


@router.post("/pair/revoke")
async def v1_pair_revoke(request: Request) -> dict[str, Any]:
    """Revoke the caller's own token (Authorization: Bearer <token>)."""
    token = _bearer_token(request)
    if token is None:
        return _v1_error("UNAUTHORIZED", "missing bearer token", _request_id(request))
    found = _pair_store.find_by_token(token)
    if found is None:
        return _v1_error("UNAUTHORIZED", "unknown token", _request_id(request))
    token_id, _ = found
    _pair_store.revoke(token_id)
    return {"revoked": True}


@router.get("/capabilities")
async def v1_capabilities(request: Request) -> dict[str, Any]:
    """What this server can do, without probing individual endpoints."""
    return {
        "api_version": API_VERSION,
        "endpoints": {
            "health": "live",
            "pair": "live",
            "pair_revoke": "live",
            "capabilities": "live",
            "projects_create": "live",
            "projects_get": "live",
            "uploads_create": "live",
            "jobs_get": "live",
            "jobs_cancel": "live",
            "artifacts_get": "live",
        },
        "presets": sorted(list_presets()),
        "max_upload_bytes": 50 * 1024 * 1024,
        "auth": "bearer-token",
        "server_time": _iso_now(),
    }


# ---------------------------------------------------------------------------
# Demo-grade implementations (DSK-MFY-DEMO-001)
# ---------------------------------------------------------------------------
#
# These follow the frozen schemas and error contract from ANDROID-003, but the
# semantics are single-machine demo: memory-backed job registry + files under
# ./data/demo. Restarting the service clears tokens and jobs alike.

_DEMO_DATA_DIR = Path("data/demo")
_DEMO_UPLOAD_DIR = _DEMO_DATA_DIR / "uploads"
_DEMO_OUTPUT_DIR = _DEMO_DATA_DIR / "outputs"

_STAGE_PROGRESS: dict[str, tuple[float, float]] = {
    "scan": (0.05, 0.15),
    "analyze": (0.15, 0.35),
    "diagnose": (0.35, 0.45),
    "process": (0.45, 0.65),
    "validate": (0.65, 0.80),
    "report": (0.80, 0.90),
    "generate": (0.90, 1.0),
}


class _DemoStore:
    """Memory-backed projects/uploads/jobs/artifacts registry (demo semantics)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._projects: dict[str, dict[str, Any]] = {}
        self._uploads: dict[str, dict[str, Any]] = {}
        self._jobs: dict[str, dict[str, Any]] = {}
        self._artifacts: dict[str, dict[str, Any]] = {}

    # -- projects -----------------------------------------------------------
    def create_project(self, title: str, source_audio_ids: list[str]) -> dict[str, Any]:
        now = _iso_now()
        project_id = f"prj-{uuid.uuid4().hex[:12]}"
        record = {
            "project_id": project_id,
            "title": title,
            "status": "active",
            "source_audio_ids": source_audio_ids,
            "created_at": now,
            "updated_at": now,
        }
        with self._lock:
            self._projects[project_id] = record
        return record

    def get_project(self, project_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._projects.get(project_id)

    # -- uploads ------------------------------------------------------------
    def create_upload(self, project_id: str, filename: str,
                      total_bytes: int, path: Path) -> dict[str, Any]:
        now = _iso_now()
        upload_id = f"up-{uuid.uuid4().hex[:12]}"
        record = {
            "upload_id": upload_id,
            "project_id": project_id,
            "filename": filename,
            "status": "received",
            "received_bytes": total_bytes,
            "total_bytes": total_bytes,
            "path": str(path),
            "created_at": now,
        }
        with self._lock:
            self._uploads[upload_id] = record
        return record

    def get_upload(self, upload_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._uploads.get(upload_id)

    # -- jobs ---------------------------------------------------------------
    def create_job(self, project_id: str, upload_id: str) -> dict[str, Any]:
        now = _iso_now()
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        record = {
            "job_id": job_id,
            "project_id": project_id,
            "upload_id": upload_id,
            "status": "queued",
            "progress": 0.0,
            "stage": "queued",
            "error_code": None,
            "created_at": now,
            "updated_at": now,
        }
        with self._lock:
            self._jobs[job_id] = record
        return record

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update_job(self, job_id: str, *, status: str | None = None,
                   stage: str | None = None, progress: float | None = None,
                   error_code: str | None = None) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            if status is not None:
                job["status"] = status
            if stage is not None:
                job["stage"] = stage
            if progress is not None:
                job["progress"] = progress
            if error_code is not None:
                job["error_code"] = error_code
            job["updated_at"] = _iso_now()

    def cancel_job(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None or job["status"] in ("done", "failed", "cancelled"):
                return False
            job["status"] = "cancelled"
            job["stage"] = "cancelled"
            job["updated_at"] = _iso_now()
            return True

    def set_job_result(self, job_id: str, summary: dict[str, Any]) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                job["result"] = summary

    def get_artifact_for_job(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            for artifact in self._artifacts.values():
                if artifact["job_id"] == job_id:
                    return artifact
        return None

    # -- artifacts ----------------------------------------------------------
    def add_artifact(self, job_id: str, kind: str, filename: str,
                     size_bytes: int, path: Path) -> dict[str, Any]:
        now = _iso_now()
        artifact_id = f"art-{uuid.uuid4().hex[:12]}"
        record = {
            "artifact_id": artifact_id,
            "job_id": job_id,
            "kind": kind,
            "filename": filename,
            "size_bytes": size_bytes,
            "sha256": _sha256_file(path),
            "path": str(path),
            "created_at": now,
        }
        with self._lock:
            self._artifacts[artifact_id] = record
        return record

    def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._artifacts.get(artifact_id)


_demo_store = _DemoStore()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_token(request: Request) -> dict[str, Any] | JSONResponse:
    token = _bearer_token(request)
    if token is None:
        return _v1_error("UNAUTHORIZED", "missing bearer token", _request_id(request))
    record = _pair_store.validate(token)
    if record is None:
        return _v1_error("UNAUTHORIZED", "unknown or revoked token", _request_id(request))
    return record


def _run_job_worker(job_id: str, input_path: str) -> None:
    """Run the real v01 pipeline in a background thread, mirroring progress."""
    from moodify.v01_pipeline import process_audio

    def on_stage(stage: str, progress: float) -> None:
        _demo_store.update_job(job_id, status="processing", stage=stage, progress=progress)

    _demo_store.update_job(job_id, status="processing", stage="scan", progress=0.05)
    try:
        result = process_audio(
            input_path,
            preset="clean_master",
            output_dir=str(_DEMO_OUTPUT_DIR),
            on_stage=on_stage,
        )
        if not result.success:
            _demo_store.update_job(
                job_id, status="failed", stage="failed",
                progress=1.0, error_code=f"PROCESS_FAILED: {result.error}",
            )
            return
        output_path = Path(result.output_path)
        artifact = _demo_store.add_artifact(
            job_id, "processed_audio", output_path.name,
            output_path.stat().st_size, output_path,
        )
        gate = result.quality_gate.to_dict() if result.quality_gate else {}
        _demo_store.set_job_result(job_id, {
            "preset": result.preset,
            "mrs_before": gate.get("mrs_before"),
            "mrs_after": gate.get("mrs_after"),
            "mrs_delta": gate.get("mrs_delta"),
            "quality_gate": gate,
            "issues": list(result.diagnosis.issues)[:3] if result.diagnosis else [],
            "stage_timings": result.stage_timings,
            "output_filename": output_path.name,
            "artifact_id": artifact["artifact_id"],
        })
        _demo_store.update_job(job_id, status="done", stage="done", progress=1.0)
    except Exception as exc:
        _demo_store.update_job(
            job_id, status="failed", stage="failed",
            progress=1.0, error_code=f"SERVER_ERROR: {exc}",
        )


def _job_summary(job: dict[str, Any]) -> dict[str, Any]:
    """Result summary for the app's work library (real metrics from the run)."""
    upload = _demo_store.get_upload(job["upload_id"])
    result = job.get("result") or {}
    return {
        "job_id": job["job_id"],
        "upload_id": job["upload_id"],
        "filename": upload["filename"] if upload else "",
        "preset": result.get("preset", ""),
        "mrs_before": result.get("mrs_before"),
        "mrs_after": result.get("mrs_after"),
        "mrs_delta": result.get("mrs_delta"),
        "quality_gate": result.get("quality_gate"),
        "issues": result.get("issues", []),
        "stage_timings": result.get("stage_timings", {}),
        "output_filename": result.get("output_filename", ""),
        "artifact_id": result.get("artifact_id"),
    }


# ---------------------------------------------------------------------------
# Demo-grade endpoints (replace NOT_IMPLEMENTED)
# ---------------------------------------------------------------------------


@router.post("/uploads")
async def v1_uploads_create(
    request: Request,
    project_id: str = Form(None),
    filename: str = Form(None),
    size_bytes: int = Form(None),
    sha256: str = Form(None),
    file: UploadFile = File(None),
):
    """Receive a real audio file (multipart), verify sha256, store it."""
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth

    if not project_id or not filename or size_bytes is None or not sha256 or file is None:
        return _v1_error("VALIDATION", "project_id/filename/size_bytes/sha256/file required", _request_id(request))

    _DEMO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target = _DEMO_UPLOAD_DIR / f"{uuid.uuid4().hex[:12]}_{Path(filename).name}"
    digest = hashlib.sha256()
    total = 0
    with target.open("wb") as out:
        while True:
            chunk = await file.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
            digest.update(chunk)
            total += len(chunk)
            if total > 50 * 1024 * 1024:
                target.unlink(missing_ok=True)
                return _v1_error("VALIDATION", "file exceeds max_upload_bytes", _request_id(request))
    if total != size_bytes:
        target.unlink(missing_ok=True)
        return _v1_error("VALIDATION", "size_bytes mismatch", _request_id(request))
    if digest.hexdigest() != sha256:
        target.unlink(missing_ok=True)
        return _v1_error("VALIDATION", "sha256 mismatch", _request_id(request))

    upload = _demo_store.create_upload(project_id, filename, total, target)
    return {
        "upload_id": upload["upload_id"],
        "project_id": upload["project_id"],
        "filename": upload["filename"],
        "status": upload["status"],
        "received_bytes": upload["received_bytes"],
        "total_bytes": upload["total_bytes"],
        "created_at": upload["created_at"],
    }


@router.post("/projects")
async def v1_projects_create(request: Request):
    """Create a project and auto-start the first job (demo semantics)."""
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth
    try:
        payload = await request.json()
    except Exception:
        return _v1_error("VALIDATION", "body must be JSON", _request_id(request))
    title = payload.get("title")
    source_audio_ids = payload.get("source_audio_ids")
    if not isinstance(title, str) or not title.strip():
        return _v1_error("VALIDATION", "title is required", _request_id(request))
    if not isinstance(source_audio_ids, list) or not source_audio_ids:
        return _v1_error("VALIDATION", "source_audio_ids is required", _request_id(request))
    upload = _demo_store.get_upload(source_audio_ids[0])
    if upload is None:
        return _v1_error("NOT_FOUND", "source upload not found", _request_id(request))

    project = _demo_store.create_project(title.strip(), source_audio_ids)
    job = _demo_store.create_job(project["project_id"], upload["upload_id"])
    threading.Thread(
        target=_run_job_worker,
        args=(job["job_id"], upload["path"]),
        daemon=True,
    ).start()
    return {
        "project_id": project["project_id"],
        "title": project["title"],
        "status": project["status"],
        "created_at": project["created_at"],
        "updated_at": project["updated_at"],
        "job_id": job["job_id"],
    }


@router.get("/projects/{project_id}")
async def v1_projects_get(project_id: str, request: Request):
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth
    project = _demo_store.get_project(project_id)
    if project is None:
        return _v1_error("NOT_FOUND", "project not found", _request_id(request))
    return {
        "project_id": project["project_id"],
        "title": project["title"],
        "status": project["status"],
        "created_at": project["created_at"],
        "updated_at": project["updated_at"],
    }


@router.get("/jobs/{job_id}")
async def v1_jobs_get(job_id: str, request: Request):
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth
    job = _demo_store.get_job(job_id)
    if job is None:
        return _v1_error("NOT_FOUND", "job not found", _request_id(request))
    return {
        "job_id": job["job_id"],
        "project_id": job["project_id"],
        "upload_id": job["upload_id"],
        "status": job["status"],
        "progress": job["progress"],
        "stage": job["stage"],
        "error_code": job["error_code"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
    }


@router.post("/jobs/{job_id}/cancel")
async def v1_jobs_cancel(job_id: str, request: Request):
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth
    job = _demo_store.get_job(job_id)
    if job is None:
        return _v1_error("NOT_FOUND", "job not found", _request_id(request))
    _demo_store.cancel_job(job_id)
    updated = _demo_store.get_job(job_id)
    return {
        "job_id": updated["job_id"],
        "project_id": updated["project_id"],
        "upload_id": updated["upload_id"],
        "status": updated["status"],
        "progress": updated["progress"],
        "stage": updated["stage"],
        "error_code": updated["error_code"],
        "created_at": updated["created_at"],
        "updated_at": updated["updated_at"],
    }


@router.get("/jobs/{job_id}/result")
async def v1_jobs_result(job_id: str, request: Request):
    """Real processing summary for the app work library (demo extension)."""
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth
    job = _demo_store.get_job(job_id)
    if job is None:
        return _v1_error("NOT_FOUND", "job not found", _request_id(request))
    if job["status"] != "done":
        return _v1_error("VALIDATION", "job not finished", _request_id(request))
    summary = _job_summary(job)
    artifacts = _demo_store.get_artifact_for_job(job_id)
    return {
        "job_id": job_id,
        "upload_id": summary["upload_id"],
        "filename": summary["filename"],
        "preset": summary["preset"],
        "mrs_before": summary["mrs_before"],
        "mrs_after": summary["mrs_after"],
        "mrs_delta": summary["mrs_delta"],
        "quality_gate": summary["quality_gate"],
        "issues": summary["issues"],
        "stage_timings": summary["stage_timings"],
        "output_filename": summary["output_filename"],
        "artifact_id": artifacts["artifact_id"] if artifacts else None,
    }


@router.get("/artifacts/{artifact_id}")
async def v1_artifacts_get(artifact_id: str, request: Request):
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth
    artifact = _demo_store.get_artifact(artifact_id)
    if artifact is None:
        return _v1_error("NOT_FOUND", "artifact not found", _request_id(request))
    return {
        "artifact_id": artifact["artifact_id"],
        "job_id": artifact["job_id"],
        "kind": artifact["kind"],
        "filename": artifact["filename"],
        "size_bytes": artifact["size_bytes"],
        "sha256": artifact["sha256"],
        "created_at": artifact["created_at"],
    }


@router.get("/artifacts/{artifact_id}/download")
async def v1_artifacts_download(artifact_id: str, request: Request):
    """Download the processed audio (demo extension)."""
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth
    artifact = _demo_store.get_artifact(artifact_id)
    if artifact is None:
        return _v1_error("NOT_FOUND", "artifact not found", _request_id(request))
    path = Path(artifact["path"])
    if not path.exists():
        return _v1_error("SERVER_ERROR", "artifact file missing", _request_id(request))
    return FileResponse(path, media_type="audio/wav", filename=artifact["filename"])


@router.get("/uploads/{upload_id}/download")
async def v1_uploads_download(upload_id: str, request: Request):
    """Download the original (unprocessed) audio for A/B comparison (demo extension)."""
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth
    upload = _demo_store.get_upload(upload_id)
    if upload is None:
        return _v1_error("NOT_FOUND", "upload not found", _request_id(request))
    path = Path(upload["path"])
    if not path.exists():
        return _v1_error("SERVER_ERROR", "upload file missing", _request_id(request))
    return FileResponse(path, media_type="audio/wav", filename=upload["filename"])


# ---------------------------------------------------------------------------
# Platform catalog (DSK-MFY-PLAYER-001): songs browsable on the home screen
# ---------------------------------------------------------------------------

_CATALOG_DIR = Path("data/demo/catalog")
_AUDIO_EXTS = {".wav", ".mp3", ".flac", ".m4a"}


def _catalog_songs() -> list[dict[str, Any]]:
    """Scan the catalog folder; wav duration read from header, others unknown."""
    if not _CATALOG_DIR.exists():
        return []
    songs: list[dict[str, Any]] = []
    for path in sorted(_CATALOG_DIR.iterdir()):
        if path.is_file() and path.suffix.lower() in _AUDIO_EXTS:
            duration = _wav_duration(path) if path.suffix.lower() == ".wav" else None
            songs.append({
                "song_id": f"song-{path.stem}",
                "title": path.stem,
                "artist": "泫榛",
                "filename": path.name,
                "duration_s": duration,
                "preset": "clean_master",
            })
    return songs


def _wav_duration(path: Path) -> int | None:
    try:
        import wave
        with wave.open(str(path), "rb") as w:
            return int(w.getnframes() / max(w.getframerate(), 1))
    except Exception:
        return None


@router.get("/catalog")
async def v1_catalog(request: Request):
    """Platform song catalog for the home screen (demo folder scanned)."""
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth
    return {"songs": _catalog_songs(), "source": "demo-catalog"}


@router.get("/catalog/{song_id}/download")
async def v1_catalog_download(song_id: str, request: Request):
    """Stream a catalog song."""
    auth = _require_token(request)
    if isinstance(auth, JSONResponse):
        return auth
    songs = _catalog_songs()
    song = next((s for s in songs if s["song_id"] == song_id), None)
    if song is None:
        return _v1_error("NOT_FOUND", "song not found", _request_id(request))
    path = _CATALOG_DIR / song["filename"]
    if not path.exists():
        return _v1_error("SERVER_ERROR", "song file missing", _request_id(request))
    return FileResponse(path, media_type="audio/wav", filename=song["filename"])
