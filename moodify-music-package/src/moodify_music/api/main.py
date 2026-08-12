"""Hangzhou Music Data API — /internal/v1/music (server-to-server only)."""

from __future__ import annotations

import uuid
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from moodify_music.api.deps import ApiError
from moodify_music.api.routes_cwc import router as cwc_router
from moodify_music.api.routes_intents import router as intents_router
from moodify_music.api.routes_social import router as social_router
from moodify_music.api.routes_tracks import router as tracks_router
from moodify_music.api.routes_users import router as users_router

app = FastAPI(title="Moodify Music Data API", version="0.1.0", docs_url="/internal/v1/music/docs", openapi_url="/internal/v1/music/openapi.json")
logger = logging.getLogger("moodify_music.api")


@app.middleware("http")
async def error_normalization(request: Request, call_next):
    rid = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16]
    try:
        response = await call_next(request)
        return response
    except ApiError as exc:
        return JSONResponse(
            status_code=exc.status,
            content={"error": {"code": exc.code, "message": exc.message, "request_id": rid}},
        )
    except Exception:
        logger.exception("unhandled Music API error request_id=%s path=%s", rid, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": {
                "code": "INTERNAL_ERROR",
                "message": "internal Music API error",
                "request_id": rid,
            }},
        )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "moodify-music-data-api", "version": "0.1.0"}


for router in (users_router, tracks_router, social_router, intents_router, cwc_router):
    app.include_router(router)
