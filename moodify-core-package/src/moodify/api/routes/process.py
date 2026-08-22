"""Reserved processing route for the experimental intelligence API facade."""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1/intelligence", tags=["auditory-intelligence"])


@router.post("/process")
async def process_audio(audio: UploadFile = File(...)) -> JSONResponse:
    """Reserve a service contract without selecting or changing a DSP pipeline."""
    return JSONResponse(
        status_code=501,
        content={
            "status": "NOT_IMPLEMENTED",
            "message": "Processing is not exposed through this experimental API facade.",
            "filename": audio.filename or "upload.wav",
        },
    )
