"""N-track ranking API contract (DSK-MFY-NTRACK-RANKER-001).

Endpoints:
    POST /api/v1/rankings
    POST /api/v1/rankings/{ranking_id}/human-ranking
    GET  /api/v1/rankings/{ranking_id}

Follows the mobile v1 error contract and never leaks absolute
filesystem paths. Synchronous execution is bounded by the comparison
budget; batch-size limits are documented in the ranking policy.
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from moodify.api.routes.v1 import _demo_store
from moodify.evaluation.ntrack.policy import RankingPolicy
from moodify.evaluation.ntrack.service import record_human_ranking, run_ntrack_ranking

API_PREFIX = "/api/v1"

router = APIRouter(prefix=API_PREFIX, tags=["ntrack-ranking"])


class NTrackRankingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    track_upload_ids: list[str] = []
    mode: str = "TRACK_STRENGTH"  # TRACK_STRENGTH | ALBUM_SELECTION
    top_k: int | None = None


class NTrackHumanRankingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    human_order: list[str] = Field(min_length=2)
    top_k: int | None = None
    must_keep: list[str] = []
    rejected: list[str] = []
    reason: str = ""


def _case_root() -> Path:
    base = os.environ.get("MOODIFY_WORKSPACE_ROOT", "outputs")
    root = Path(base) / "rankings"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _resolve_upload(upload_id: str) -> Path:
    record = _demo_store.get_upload(upload_id)
    if record is None or not record.get("path"):
        raise ValueError(f"upload asset not found: {upload_id}")
    path = Path(record["path"])
    if not path.is_file():
        raise ValueError(f"upload asset file missing: {upload_id}")
    return path


def _error(code: str, message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "request_id": ""}},
    )


def _public_result(result: dict[str, Any]) -> dict[str, Any]:
    public = dict(result)
    public.pop("ranking_dir", None)
    return public


@router.post("/rankings")
async def v1_create_ranking(request: Request, body: NTrackRankingRequest) -> Any:
    if len(body.track_upload_ids) < 2:
        return _error("VALIDATION", "at least 2 track uploads are required")
    if body.mode not in {"TRACK_STRENGTH", "ALBUM_SELECTION"}:
        return _error("VALIDATION", f"invalid mode: {body.mode}")
    if body.top_k is not None and body.top_k < 1:
        return _error("VALIDATION", "top_k must be >= 1")
    try:
        track_paths = [_resolve_upload(upload_id) for upload_id in body.track_upload_ids]
    except ValueError as exc:
        return _error("NOT_FOUND", str(exc), 404)

    ranking_id = f"RK-{uuid.uuid4().hex[:12]}"
    case_root = _case_root() / ranking_id
    try:
        result = run_ntrack_ranking(
            case_id=ranking_id,
            case_root=case_root,
            track_paths=track_paths,
            mode=body.mode,
            top_k=body.top_k,
            ranking_policy=RankingPolicy(),
        )
    except Exception as exc:
        return _error("SERVER_ERROR", f"ntrack ranking failed: {type(exc).__name__}", 500)
    return _public_result(result)


@router.post("/rankings/{ranking_id}/human-ranking")
async def v1_ranking_human_decision(
    ranking_id: str, request: Request, body: NTrackHumanRankingRequest
) -> Any:
    case_root = _case_root() / ranking_id
    if not (case_root / "05_ntrack" / "estimate.json").is_file():
        return _error("NOT_FOUND", "ranking not found", 404)
    try:
        result = record_human_ranking(
            case_root=case_root,
            ranking_case_id=ranking_id,
            human_order=body.human_order,
            top_k=body.top_k,
            must_keep=body.must_keep or None,
            rejected=body.rejected or None,
            optional_reason=body.reason,
        )
    except ValueError as exc:
        return _error("VALIDATION", str(exc), 400)
    return {
        "ranking_id": ranking_id,
        "derived_preference_count": result["derived_preference_count"],
        "human_ranking_decision_id": result["human_ranking_decision"]["human_ranking_decision_id"],
    }


@router.get("/rankings/{ranking_id}")
async def v1_get_ranking(ranking_id: str) -> Any:
    case_root = _case_root() / ranking_id
    ntrack_dir = case_root / "05_ntrack"
    if not ntrack_dir.is_dir():
        return _error("NOT_FOUND", "ranking not found", 404)
    try:
        estimate = json.loads((ntrack_dir / "estimate.json").read_text(encoding="utf-8"))
        case = json.loads((ntrack_dir / "ranking_case.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _error("SERVER_ERROR", f"ranking state unreadable: {type(exc).__name__}", 500)
    payload = {
        "ranking_id": ranking_id,
        "mode": case.get("mode"),
        "status": case.get("status"),
        "top_k": case.get("top_k"),
        "ranking_estimate_id": estimate.get("ranking_estimate_id"),
        "ordered_candidates": estimate.get("ordered_candidates", []),
        "tie_bands": estimate.get("tie_bands", []),
        "pairwise_edge_count": estimate.get("pairwise_edge_count", 0),
    }
    album_path = ntrack_dir / "album_rerank.json"
    if album_path.is_file():
        album = json.loads(album_path.read_text(encoding="utf-8"))
        payload["album_rerank"] = {
            "selected_candidate_ids": album.get("selected_candidate_ids", []),
            "explanations": album.get("explanations", []),
        }
    return payload
