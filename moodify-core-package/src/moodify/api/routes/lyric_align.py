"""Lyric alignment API contract (DSK-MFY-LYRIC-TEMPORAL-ALIGNMENT-001, Phase F).

Endpoint:
    POST /api/v1/lyric-alignments

Contract is schema-frozen and follows the mobile v1 error body::

    {"error": {"code": "...", "message": "...", "request_id": "..."}}

Security rules (inherited from v1.py):
    - never return absolute filesystem paths
    - never echo raw tracebacks
"""

from __future__ import annotations

import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from moodify.api.routes.v1 import _demo_store
from moodify.lyric_align.pipeline import run_alignment

API_PREFIX = "/api/v1"

router = APIRouter(prefix=API_PREFIX, tags=["lyric-alignment"])


class LyricAlignRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    audio_asset_id: str = Field(min_length=1)
    lyrics: str = Field(min_length=1)
    language: str = Field(min_length=1, max_length=16)
    translation_lyrics: str | None = None
    score_asset_id: str | None = None
    midi_asset_id: str | None = None
    requested_granularity: list[str] | None = None


class _V1Error(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _request_id(request: Request) -> str:
    return request.headers.get("X-Request-Id", uuid.uuid4().hex[:16])


def _v1_error(code: str, message: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=400 if code != "NOT_FOUND" else 404,
        content={"error": {"code": code, "message": message, "request_id": request_id}},
    )


def _output_root() -> Path:
    import os

    base = os.environ.get("MOODIFY_WORKSPACE_ROOT", "outputs")
    root = Path(base) / "lyric_alignments"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _resolve_audio(audio_asset_id: str) -> Path:
    record = _demo_store.get_upload(audio_asset_id)
    if record is None or not record.get("path"):
        raise _V1Error("NOT_FOUND", "audio asset not found", status_code=404)
    path = Path(record["path"])
    if not path.is_file():
        raise _V1Error("NOT_FOUND", "audio asset file missing", status_code=404)
    return path


@router.post("/lyric-alignments")
async def v1_lyric_alignment(request: Request, body: LyricAlignRequest) -> dict[str, Any]:
    rid = _request_id(request)
    if body.score_asset_id or body.midi_asset_id:
        return _v1_error(
            "NOT_IMPLEMENTED",
            "score/midi priors are not implemented in this release (Phase C deferred)",
            rid,
        )
    try:
        audio = _resolve_audio(body.audio_asset_id)
    except _V1Error as exc:
        return _v1_error(exc.code, exc.message, rid)
    granularity = "line" if body.requested_granularity else None

    alignment_id = f"al-{uuid.uuid4().hex[:12]}"
    out = _output_root() / alignment_id
    try:
        with tempfile.TemporaryDirectory() as td:
            lyrics_path = Path(td) / "lyrics.txt"
            lyrics_path.write_text(body.lyrics, encoding="utf-8")
            translation_path = None
            if body.translation_lyrics:
                translation_path = Path(td) / "translation.txt"
                translation_path.write_text(body.translation_lyrics, encoding="utf-8")
            manifest = run_alignment(
                audio_path=audio,
                lyrics_path=lyrics_path,
                translation_path=translation_path,
                output_dir=out,
                language=body.language,
                backend_name="heuristic",
                granularity=granularity,
            )
    except ValueError as exc:
        return _v1_error("VALIDATION", str(exc), rid)
    except Exception as exc:
        return _v1_error("SERVER_ERROR", f"alignment failed: {type(exc).__name__}", rid)

    quality = {
        "coverage": 0.0,
        "mean_confidence": 0.0,
        "unaligned_token_ratio": 0.0,
    }
    qc_path = out / "qc_report.json"
    if qc_path.is_file():
        import json

        qc = json.loads(qc_path.read_text(encoding="utf-8"))
        quality = {
            "coverage": qc.get("coverage", 0.0),
            "mean_confidence": qc.get("mean_word_confidence", 0.0),
            "unaligned_token_ratio": qc.get("unaligned_token_ratio", 0.0),
        }

    def _exists(name: str) -> bool:
        return (out / name).is_file()

    exports: dict[str, str] = {}
    for key, name in (
        ("lrc", "lyrics.lrc"),
        ("enhanced_lrc", "lyrics.enhanced.lrc"),
        ("srt", "lyrics.srt"),
        ("ass", "lyrics.ass"),
    ):
        if _exists(name):
            exports[key] = name

    review_regions: list[dict[str, Any]] = []
    if qc_path.is_file():
        import json

        qc = json.loads(qc_path.read_text(encoding="utf-8"))
        review_regions = list(qc.get("review_regions", []))

    return {
        "status": manifest["status"],
        "alignment_asset_id": alignment_id,
        "exports": exports,
        "quality": quality,
        "review_regions": review_regions,
        "created_at": _iso_now(),
    }
