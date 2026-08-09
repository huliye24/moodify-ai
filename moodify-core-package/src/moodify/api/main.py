"""Canonical Moodify 1.0 API — The Ear of AI."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from moodify.auditory.errors import AuditoryError
from moodify.release import PRODUCT_VERSION, analyze_to_case, reopen_case

MAX_SIZE = 100 * 1024 * 1024

app = FastAPI(
    title="Moodify — The Ear of AI",
    version=PRODUCT_VERSION,
    description="Can machines learn to hear? Evidence-backed auditory intelligence.",
)


def _cases_root() -> Path:
    return Path(os.environ.get("MOODIFY_CASES_ROOT", "outputs/moodify_cases"))


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "product": "Moodify",
        "version": PRODUCT_VERSION,
        "identity": "The Ear of AI",
    }


@app.post("/api/v1/auditory/analyze")
async def analyze(audio: UploadFile = File(...)) -> dict:
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


@app.get("/api/v1/auditory/cases/{case_id}")
async def get_case(case_id: str) -> dict:
    try:
        return reopen_case(_cases_root(), case_id)
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "CASE_NOT_FOUND", "message": "case not found"},
        ) from exc
