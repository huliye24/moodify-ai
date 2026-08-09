"""Recommendation / For You feed API contract (DSK-MFY-TASTE-FEED-PATCH-001).

Endpoints:
    GET  /api/v1/feed/for-you
    POST /api/v1/feed/request
    POST /api/v1/feed/feedback
    GET  /api/v1/tracks/{track_id}/auditory-profile
    GET  /api/v1/library/saved
    POST /api/v1/library/save

The auditory-analysis API surface is preserved untouched. CWC/token/
collectible semantics stay absent.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from moodify.recommendation.feedback import EVENT_TYPES
from moodify.recommendation.policy import RecommendationPolicy
from moodify.recommendation.service import FeedService

API_PREFIX = "/api/v1"

router = APIRouter(prefix=API_PREFIX, tags=["recommendation"])


def _service() -> FeedService:
    root = Path(os.environ.get("MOODIFY_FEED_ROOT", "outputs/feed"))
    return FeedService(root, policy=RecommendationPolicy.from_yaml())


def _error(code: str, message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "request_id": ""}},
    )


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    user_id: str
    track_id: str
    event_type: str
    request_id: str = ""
    playback_session_id: str = ""
    rank_position: int | None = None
    elapsed_ms: int | None = None
    duration_ms: int | None = None


class RegisterTrackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    track_id: str
    source_audio_id: str
    feature_vector: list[float] = []
    quality_state: str = "ELIGIBLE"
    quality_confidence: float = 0.0


class SaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    user_id: str
    track_id: str


@router.get("/feed/for-you")
async def v1_feed_for_you(user_id: str, size: int | None = None) -> Any:
    try:
        return _service().get_for_you(user_id, size=size)
    except ValueError as exc:
        return _error("NOT_FOUND", str(exc), 404)


@router.post("/feed/request")
async def v1_feed_request(user_id: str, size: int | None = None) -> Any:
    try:
        return _service().get_for_you(user_id, size=size)
    except ValueError as exc:
        return _error("NOT_FOUND", str(exc), 404)


@router.post("/feed/feedback")
async def v1_feed_feedback(request: Request, body: FeedbackRequest) -> Any:
    if body.event_type not in EVENT_TYPES:
        return _error("VALIDATION", f"unknown event_type: {body.event_type}")
    return _service().record_feedback(
        body.user_id, body.track_id, body.event_type,
        request_id=body.request_id, playback_session_id=body.playback_session_id,
        rank_position=body.rank_position, elapsed_ms=body.elapsed_ms,
        duration_ms=body.duration_ms,
    )


@router.post("/tracks/register")
async def v1_register_track(request: Request, body: RegisterTrackRequest) -> Any:
    return _service().register_track(
        body.track_id, body.source_audio_id,
        feature_vector=body.feature_vector,
        quality_state=body.quality_state,
        quality_confidence=body.quality_confidence,
    )


@router.get("/tracks/{track_id}/auditory-profile")
async def v1_track_auditory_profile(track_id: str) -> Any:
    profile = _service().auditory_profile(track_id)
    if profile is None:
        return _error("NOT_FOUND", f"track not found: {track_id}", 404)
    return profile.to_dict()


@router.get("/library/saved")
async def v1_library_saved(user_id: str) -> Any:
    return {"user_id": user_id, "saved_track_ids": _service().saved_tracks(user_id)}


@router.post("/library/save")
async def v1_library_save(request: Request, body: SaveRequest) -> Any:
    return _service().save_track(body.user_id, body.track_id)


@router.delete("/library/save/{track_id}")
async def v1_library_unsave(user_id: str, track_id: str) -> Any:
    return _service().unsave_track(user_id, track_id)
