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

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

UPSTREAM = os.environ.get("MOODIFY_HANGZHOU_BASE", "http://120.55.191.146:8000").rstrip("/")
SERVICE_KEY = os.environ.get("MOODIFY_HANGZHOU_KEY", "")
TIMEOUT = float(os.environ.get("MOODIFY_BFF_TIMEOUT", "5.0"))
DEMO_USER_ID = os.environ.get("MOODIFY_BFF_DEMO_USER_ID", "")

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


def _upstream_headers(request: Request, body: dict | None = None) -> dict:
    headers = {"X-Moodify-Service-Key": SERVICE_KEY, "Content-Type": "application/json"}
    rid = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16]
    headers["X-Request-Id"] = rid
    idem = request.headers.get("Idempotency-Key")
    if idem:
        headers["Idempotency-Key"] = idem
    actor = request.headers.get("X-Moodify-Actor-User-Id")
    if not actor and DEMO_USER_ID:
        actor = DEMO_USER_ID
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
            return JSONResponse(status_code=r.status_code, content=r.json() if r.content else {})
        except httpx.TimeoutException as exc:
            last_exc = exc
    return JSONResponse(status_code=504, content={"error": {"code": "UPSTREAM_TIMEOUT", "message": "Hangzhou data API timed out", "request_id": request.headers.get("X-Request-Id", "")}})


@app.get("/health")
def health():
    return {"status": "ok", "service": "moodify-music-bff", "direct_db": False}


@app.get("/api/v1/music/bootstrap")
@_cached("bootstrap", "bootstrap")
def bootstrap(request: Request):
    if DEMO_USER_ID:
        response = _forward("GET", f"/users/{DEMO_USER_ID}", request, retries=1)
        if response.status_code != 200:
            return response
        import json as _json
        user = _json.loads(response.body)
        user["auth_state"] = "PUBLIC_USER_AUTH_NOT_PRODUCTION_READY"
        user["demo_creator_handle"] = "cadeau10"
        return JSONResponse(content=user)
    return JSONResponse(status_code=200, content={
        "id": None, "display_name": "Moodify Creator", "status": "active",
        "auth_state": "PUBLIC_USER_AUTH_NOT_PRODUCTION_READY",
        "demo_creator_handle": "cadeau10",
    })


@app.get("/api/v1/music/catalogue")
@_cached("catalogue", "catalogue")
def catalogue(request: Request):
    return _forward("GET", "/catalogue", request, retries=1)


@app.post("/api/v1/music/creators")
async def create_creator(request: Request):
    return _forward("POST", "/creators", request, await request.json())


@app.get("/api/v1/music/creators/by-handle/{handle}")
@_cached("creator_page", "creator_page")
def creator_by_handle(handle: str, request: Request):
    return _forward("GET", f"/creators/by-handle/{handle}", request, retries=1)


@app.get("/api/v1/music/creators/{creator_id}/page")
@_cached("creator_page", "creator_page")
def creator_page(creator_id: str, request: Request):
    return _forward("GET", f"/creators/{creator_id}/page", request, retries=1)


@app.get("/api/v1/music/tracks/{track_id}")
@_cached("track", "track")
def track_detail(track_id: str, request: Request):
    return _forward("GET", f"/tracks/{track_id}", request, retries=1)


@app.get("/api/v1/music/tracks/{track_id}/passport")
@_cached("track", "track")
def track_passport(track_id: str, request: Request):
    return _forward("GET", f"/tracks/{track_id}/passport", request, retries=1)


@app.post("/api/v1/music/tracks")
async def create_track(request: Request):
    return _forward("POST", "/tracks", request, await request.json())


@app.post("/api/v1/music/tracks/{track_id}/versions")
async def create_version(track_id: str, request: Request):
    return _forward("POST", f"/tracks/{track_id}/versions", request, await request.json())


@app.post("/api/v1/music/tracks/{track_id}/publish")
async def publish(track_id: str, request: Request):
    return _forward("POST", f"/tracks/{track_id}/publish", request, await request.json())


@app.put("/api/v1/music/tracks/{track_id}/passport")
async def upsert_passport(track_id: str, request: Request):
    return _forward("PUT", f"/tracks/{track_id}/passport", request, await request.json())


@app.put("/api/v1/music/users/{user_id}/follows/{creator_id}")
async def follow(user_id: str, creator_id: str, request: Request):
    return _forward("PUT", f"/users/{user_id}/follows/{creator_id}", request, await request.json())


@app.delete("/api/v1/music/users/{user_id}/follows/{creator_id}")
def unfollow(user_id: str, creator_id: str, request: Request):
    return _forward("DELETE", f"/users/{user_id}/follows/{creator_id}", request)


@app.put("/api/v1/music/users/{user_id}/favorites/{track_id}")
async def favorite(user_id: str, track_id: str, request: Request):
    return _forward("PUT", f"/users/{user_id}/favorites/{track_id}", request, await request.json())


@app.delete("/api/v1/music/users/{user_id}/favorites/{track_id}")
def unfavorite(user_id: str, track_id: str, request: Request):
    return _forward("DELETE", f"/users/{user_id}/favorites/{track_id}", request)


@app.post("/api/v1/music/play-events")
async def play_event(request: Request):
    return _forward("POST", "/play-events", request, await request.json())


@app.post("/api/v1/music/license-intents")
async def license_intent(request: Request):
    return _forward("POST", "/license-intents", request, await request.json())


@app.get("/api/v1/music/creators/{creator_id}/license-intents")
@_cached("inbox", "inbox")
def creator_inbox(creator_id: str, request: Request):
    return _forward("GET", f"/creators/{creator_id}/license-intents", request)


@app.post("/api/v1/music/support-intents")
async def support_intent(request: Request):
    return _forward("POST", "/support-intents", request, await request.json())
