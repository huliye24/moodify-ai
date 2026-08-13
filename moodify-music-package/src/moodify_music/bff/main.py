"""LA Public BFF — /api/v1/music.

Public boundary for Music Web. Forwards to Hangzhou /internal/v1/music
over authenticated server-to-server HTTP. Never connects to PolarDB.

Env:
  MOODIFY_HANGZHOU_BASE   http://120.55.191.146:8000 (default)
  MOODIFY_HANGZHOU_KEY    service key (required in production)
  MOODIFY_BFF_TIMEOUT     5.0
"""

from __future__ import annotations

import functools
import os
import time
import uuid
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from moodify_music.bff.auth import COOKIE_NAME, authenticate_invite, issue_session, verify_session
from moodify_music.bff.media import ALLOWED_MIME, MAX_AUDIO_BYTES, allocate_upload, looks_like_audio, sha256_file
from starlette.concurrency import run_in_threadpool

UPSTREAM = os.environ.get("MOODIFY_HANGZHOU_BASE", "http://120.55.191.146:8000").rstrip("/")
SERVICE_KEY = os.environ.get("MOODIFY_HANGZHOU_KEY", "")
TIMEOUT = float(os.environ.get("MOODIFY_BFF_TIMEOUT", "5.0"))
DEMO_USER_ID = os.environ.get("MOODIFY_BFF_DEMO_USER_ID", "")
AUTH_MODE = os.environ.get("MOODIFY_BFF_AUTH_MODE", "demo_read_only")

app = FastAPI(title="Moodify Music Public BFF", version="0.1.0")

_cache: dict[str, tuple[float, dict]] = {}
_TTL: dict[str, float] = {
    "creator_page": 60.0, "track": 60.0, "album": 300.0, "catalogue": 30.0,
    "bootstrap": 60.0, "inbox": 30.0,
}


def _cached(key: str, ttl_key: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.monotonic()
            hit = _cache.get(key)
            if hit and now - hit[0] < _TTL[ttl_key]:
                return JSONResponse(content=hit[1])
            result = func(*args, **kwargs)
            if isinstance(result, JSONResponse):
                import json as _json

                body = _json.loads(result.body)
                _cache[key] = (now, body)
            return result
        return wrapper
    return decorator


def _actor_user_id(request: Request) -> str | None:
    # Never accept the internal actor header from a public request. Until real
    # session authentication is installed, only the server-owned demo identity
    # may become an upstream actor.
    if AUTH_MODE == "invite_beta":
        return verify_session(request.cookies.get(COOKIE_NAME))
    return DEMO_USER_ID or None


def _account_actions_enabled(request: Request) -> bool:
    return AUTH_MODE == "invite_beta" and bool(_actor_user_id(request))


def _upstream_headers(request: Request, body: dict | None = None) -> dict:
    headers = {"X-Moodify-Service-Key": SERVICE_KEY, "Content-Type": "application/json"}
    rid = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16]
    headers["X-Request-Id"] = rid
    idem = request.headers.get("Idempotency-Key")
    if idem:
        headers["Idempotency-Key"] = idem
    actor = _actor_user_id(request)
    if actor:
        headers["X-Moodify-Actor-User-Id"] = actor
    return headers


def _forward(method: str, path: str, request: Request, body: dict | None = None, *, retries: int = 0):
    url = f"{UPSTREAM}/internal/v1/music{path}"
    headers = _upstream_headers(request, body)
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            r = httpx.request(method, url, headers=headers, json=body, timeout=TIMEOUT)
            if not r.content:
                return JSONResponse(status_code=r.status_code, content={})
            try:
                content = r.json()
            except ValueError:
                return JSONResponse(
                    status_code=502,
                    content={"error": {
                        "code": "UPSTREAM_INVALID_RESPONSE",
                        "message": "Hangzhou data API returned a non-JSON response",
                        "request_id": headers["X-Request-Id"],
                        "upstream_status": r.status_code,
                    }},
                )
            return JSONResponse(status_code=r.status_code, content=content)
        except httpx.TimeoutException as exc:
            last_exc = exc
        except httpx.RequestError:
            return JSONResponse(status_code=502, content={"error": {
                "code": "UPSTREAM_UNAVAILABLE",
                "message": "Hangzhou data API is unavailable",
                "request_id": headers["X-Request-Id"],
            }})
    return JSONResponse(status_code=504, content={"error": {"code": "UPSTREAM_TIMEOUT", "message": "Hangzhou data API timed out", "request_id": request.headers.get("X-Request-Id", "")}})


@app.get("/health")
def health():
    return {"status": "ok", "service": "moodify-music-bff", "direct_db": False}


@app.post("/api/v1/music/session")
async def create_session(request: Request):
    if AUTH_MODE != "invite_beta":
        return _beta_locked(request)
    body = await request.json()
    code = body.get("invite_code") if isinstance(body, dict) else None
    user_id = authenticate_invite(code.strip() if isinstance(code, str) else "")
    if not user_id:
        return JSONResponse(status_code=401, content={"error": {
            "code": "INVITE_INVALID",
            "message": "invite code is invalid",
            "request_id": request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16],
        }})
    try:
        token = issue_session(user_id)
    except RuntimeError:
        return JSONResponse(status_code=503, content={"error": {
            "code": "SESSION_NOT_CONFIGURED",
            "message": "beta session service is not configured",
            "request_id": request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16],
        }})
    response = JSONResponse(content={"authenticated": True})
    response.set_cookie(
        COOKIE_NAME, token, max_age=12 * 60 * 60, httponly=True,
        secure=True, samesite="lax", path="/",
    )
    return response


@app.delete("/api/v1/music/session")
def delete_session():
    response = JSONResponse(content={"authenticated": False})
    response.delete_cookie(COOKIE_NAME, path="/", secure=True, httponly=True, samesite="lax")
    return response


@app.get("/api/v1/music/bootstrap")
def bootstrap(request: Request):
    actor = _actor_user_id(request)
    if actor:
        response = _forward("GET", f"/users/{actor}", request, retries=1)
        if response.status_code != 200:
            return response
        import json as _json
        user = _json.loads(response.body)
        user["auth_state"] = "BETA_INVITE_AUTHENTICATED" if AUTH_MODE == "invite_beta" else "PUBLIC_USER_AUTH_NOT_PRODUCTION_READY"
        user["demo_creator_handle"] = "cadeau10"
        enabled = _account_actions_enabled(request)
        user["capabilities"] = {"account_actions": enabled, "creator_writes": enabled}
        return JSONResponse(content=user)
    return JSONResponse(status_code=200, content={
        "id": None, "display_name": "Moodify Creator", "status": "active",
        "auth_state": "PUBLIC_USER_AUTH_NOT_PRODUCTION_READY",
        "demo_creator_handle": "cadeau10",
        "capabilities": {"account_actions": False, "creator_writes": False},
    })


@app.get("/api/v1/music/catalogue")
@_cached("catalogue", "catalogue")
def catalogue(request: Request):
    return _forward("GET", "/catalogue", request, retries=1)


@app.put("/api/v1/music/media")
async def upload_media(request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    actor = _actor_user_id(request)
    mime = (request.headers.get("content-type") or "").split(";", 1)[0].lower()
    filename = request.headers.get("x-filename") or ""
    try:
        expected_bytes = int(request.headers.get("content-length") or "0")
    except ValueError:
        expected_bytes = 0
    if mime not in ALLOWED_MIME:
        return _media_error(request, 415, "AUDIO_TYPE_UNSUPPORTED", "unsupported audio format")
    if expected_bytes <= 0 or expected_bytes > MAX_AUDIO_BYTES:
        return _media_error(request, 413, "AUDIO_SIZE_INVALID", "audio must be between 1 byte and 100 MiB")
    if not filename or len(filename) > 255:
        return _media_error(request, 400, "FILENAME_INVALID", "valid X-Filename header required")
    asset_key, temporary, final_path = allocate_upload(actor, filename, mime)
    written = 0
    head = bytearray()
    try:
        with temporary.open("wb") as target:
            async for chunk in request.stream():
                written += len(chunk)
                if written > MAX_AUDIO_BYTES:
                    return _media_error(request, 413, "AUDIO_SIZE_INVALID", "audio exceeds 100 MiB")
                if len(head) < 16:
                    head.extend(chunk[: 16 - len(head)])
                await run_in_threadpool(target.write, chunk)
        if written != expected_bytes:
            return _media_error(request, 400, "AUDIO_SIZE_MISMATCH", "received size differs from Content-Length")
        if not looks_like_audio(bytes(head), mime):
            return _media_error(request, 415, "AUDIO_SIGNATURE_INVALID", "file signature does not match audio type")
        digest = await run_in_threadpool(sha256_file, temporary)
        await run_in_threadpool(os.replace, temporary, final_path)
        await run_in_threadpool(os.chmod, final_path, 0o644)
        return JSONResponse(status_code=201, content={
            "asset_key": asset_key, "bytes": written, "sha256": digest, "mime_type": mime,
        })
    finally:
        if temporary.exists():
            temporary.unlink(missing_ok=True)


@app.post("/api/v1/music/creators")
async def create_creator(request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    actor = _actor_user_id(request)
    if not actor:
        return _auth_required(request)
    body = await request.json()
    body["user_id"] = actor
    return _forward("POST", "/creators", request, body)


@app.get("/api/v1/music/creators/by-handle/{handle}")
def creator_by_handle(handle: str, request: Request):
    return _forward("GET", f"/creators/by-handle/{handle}", request, retries=1)


@app.get("/api/v1/music/creators/{creator_id}/page")
def creator_page(creator_id: str, request: Request):
    return _forward("GET", f"/creators/{creator_id}/page", request, retries=1)


@app.get("/api/v1/music/tracks/{track_id}")
def track_detail(track_id: str, request: Request):
    return _forward("GET", f"/tracks/{track_id}", request, retries=1)


@app.get("/api/v1/music/tracks/{track_id}/passport")
def track_passport(track_id: str, request: Request):
    return _forward("GET", f"/tracks/{track_id}/passport", request, retries=1)


@app.post("/api/v1/music/tracks")
async def create_track(request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    return _forward("POST", "/tracks", request, await request.json())


@app.post("/api/v1/music/tracks/{track_id}/versions")
async def create_version(track_id: str, request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    return _forward("POST", f"/tracks/{track_id}/versions", request, await request.json())


@app.post("/api/v1/music/tracks/{track_id}/publish")
async def publish(track_id: str, request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    return _forward("POST", f"/tracks/{track_id}/publish", request, await request.json())


@app.put("/api/v1/music/tracks/{track_id}/passport")
async def upsert_passport(track_id: str, request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    return _forward("PUT", f"/tracks/{track_id}/passport", request, await request.json())


@app.put("/api/v1/music/users/{user_id}/follows/{creator_id}")
async def follow(user_id: str, creator_id: str, request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    if user_id != _actor_user_id(request):
        return _ownership_denied(request)
    return _forward("PUT", f"/users/{user_id}/follows/{creator_id}", request, await request.json())


@app.delete("/api/v1/music/users/{user_id}/follows/{creator_id}")
def unfollow(user_id: str, creator_id: str, request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    if user_id != _actor_user_id(request):
        return _ownership_denied(request)
    return _forward("DELETE", f"/users/{user_id}/follows/{creator_id}", request)


@app.put("/api/v1/music/users/{user_id}/favorites/{track_id}")
async def favorite(user_id: str, track_id: str, request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    if user_id != _actor_user_id(request):
        return _ownership_denied(request)
    return _forward("PUT", f"/users/{user_id}/favorites/{track_id}", request, await request.json())


@app.delete("/api/v1/music/users/{user_id}/favorites/{track_id}")
def unfavorite(user_id: str, track_id: str, request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    if user_id != _actor_user_id(request):
        return _ownership_denied(request)
    return _forward("DELETE", f"/users/{user_id}/favorites/{track_id}", request)


@app.post("/api/v1/music/play-events")
async def play_event(request: Request):
    body = await request.json()
    body["user_id"] = _actor_user_id(request)
    return _forward("POST", "/play-events", request, body)


@app.post("/api/v1/music/license-intents")
async def license_intent(request: Request):
    return _forward("POST", "/license-intents", request, await request.json())


@app.get("/api/v1/music/creators/{creator_id}/license-intents")
def creator_inbox(creator_id: str, request: Request):
    if not _account_actions_enabled(request):
        return _beta_locked(request)
    return _forward("GET", f"/creators/{creator_id}/license-intents", request)


@app.post("/api/v1/music/support-intents")
async def support_intent(request: Request):
    return _forward("POST", "/support-intents", request, await request.json())


def _ownership_denied(request: Request) -> JSONResponse:
    return JSONResponse(status_code=403, content={"error": {
        "code": "OWNERSHIP_DENIED",
        "message": "the authenticated user does not match the requested user",
        "request_id": request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16],
    }})


def _auth_required(request: Request) -> JSONResponse:
    return JSONResponse(status_code=401, content={"error": {
        "code": "AUTH_REQUIRED",
        "message": "authenticated Music identity required",
        "request_id": request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16],
    }})


def _beta_locked(request: Request) -> JSONResponse:
    return JSONResponse(status_code=503, content={"error": {
        "code": "BETA_AUTH_REQUIRED",
        "message": "creator and account actions are locked until production authentication is enabled",
        "request_id": request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16],
    }})


def _media_error(request: Request, status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {
        "code": code, "message": message,
        "request_id": request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16],
    }})
