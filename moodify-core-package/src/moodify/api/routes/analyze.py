"""Audio-analysis route for the experimental intelligence API facade."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..schemas.audio import AudioAnalysisResponse, AudioRequest
from ..services.audio_service import AudioService

router = APIRouter(prefix="/api/v1/intelligence", tags=["auditory-intelligence"])
_service = AudioService()


def _request(filename: str | None, metadata: str) -> AudioRequest:
    """Build validated request metadata from multipart form data."""
    try:
        parsed: Any = json.loads(metadata) if metadata else {}
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail={"code": "METADATA_INVALID"}) from exc
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail={"code": "METADATA_INVALID"})
    return AudioRequest(file=filename or "upload.wav", metadata=parsed)


@router.post("/analyze", response_model=AudioAnalysisResponse)
async def analyze_audio(
    audio: UploadFile = File(...),
    metadata: str = Form(default=""),
) -> AudioAnalysisResponse:
    """Return basic features from the existing analysis engine."""
    try:
        return await _service.analyze_upload(audio, _request(audio.filename, metadata))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": str(exc)}) from exc
