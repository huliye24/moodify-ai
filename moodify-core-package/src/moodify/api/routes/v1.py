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

import secrets
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
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
            "projects_create": "frozen",
            "projects_get": "frozen",
            "uploads_create": "frozen",
            "jobs_get": "frozen",
            "jobs_cancel": "frozen",
            "artifacts_get": "frozen",
        },
        "presets": sorted(list_presets()),
        "max_upload_bytes": 50 * 1024 * 1024,
        "auth": "bearer-token",
        "server_time": _iso_now(),
    }


# ---------------------------------------------------------------------------
# Schema-frozen endpoints (NOT_IMPLEMENTED until ANDROID-004/005)
# ---------------------------------------------------------------------------


@router.post("/projects")
async def v1_projects_create(request: Request) -> JSONResponse:
    return _v1_error(
        "NOT_IMPLEMENTED",
        "project creation lands in DSK-MFY-ANDROID-004",
        _request_id(request),
    )


@router.get("/projects/{project_id}")
async def v1_projects_get(project_id: str, request: Request) -> JSONResponse:
    return _v1_error(
        "NOT_IMPLEMENTED",
        "project detail lands in DSK-MFY-ANDROID-004",
        _request_id(request),
    )


@router.post("/uploads")
async def v1_uploads_create(request: Request) -> JSONResponse:
    return _v1_error(
        "NOT_IMPLEMENTED",
        "uploads land in DSK-MFY-ANDROID-004",
        _request_id(request),
    )


@router.get("/jobs/{job_id}")
async def v1_jobs_get(job_id: str, request: Request) -> JSONResponse:
    return _v1_error(
        "NOT_IMPLEMENTED",
        "job status lands in DSK-MFY-ANDROID-004",
        _request_id(request),
    )


@router.post("/jobs/{job_id}/cancel")
async def v1_jobs_cancel(job_id: str, request: Request) -> JSONResponse:
    return _v1_error(
        "NOT_IMPLEMENTED",
        "job cancel lands in DSK-MFY-ANDROID-004",
        _request_id(request),
    )


@router.get("/artifacts/{artifact_id}")
async def v1_artifacts_get(artifact_id: str, request: Request) -> JSONResponse:
    return _v1_error(
        "NOT_IMPLEMENTED",
        "artifacts land in DSK-MFY-ANDROID-005",
        _request_id(request),
    )
