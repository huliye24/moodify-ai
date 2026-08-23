"""MRS-evaluation route for the experimental intelligence API facade."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..schemas.audio import MRSResponse
from ..services.audio_service import AudioService
from .analyze import _request

router = APIRouter(prefix="/api/v1/intelligence", tags=["auditory-intelligence"])
_service = AudioService()


@router.post("/evaluate", response_model=MRSResponse)
async def evaluate_audio(
    audio: UploadFile = File(...),
    metadata: str = Form(default=""),
    normalized_features: str | None = Form(default=None),
) -> MRSResponse:
    """Return an experimental MRS result when explicit inputs are supplied."""
    try:
        request = _request(audio.filename, metadata)
        return await _service.evaluate_upload(audio, request, normalized_features)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": str(exc)}) from exc
