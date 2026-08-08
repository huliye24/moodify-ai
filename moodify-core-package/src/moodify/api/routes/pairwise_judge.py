"""Pairwise Auditory Judge API contract (DSK-MFY-PAIRWISE-JUDGE-001).

Endpoints:
    POST /api/v1/pairwise-judgments
    POST /api/v1/pairwise-judgments/{judgment_id}/human-decision

Follows the mobile v1 error contract and never leaks absolute filesystem paths.
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
from moodify.evaluation.pairwise.policy import DecisionPolicy
from moodify.evaluation.pairwise.service import record_human_decision, run_pairwise_judge

API_PREFIX = "/api/v1"

router = APIRouter(prefix=API_PREFIX, tags=["pairwise-judge"])


class PairwiseJudgeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    candidate_a_upload_id: str = Field(min_length=1)
    candidate_b_upload_id: str | None = None
    candidate_b_artifact_id: str | None = None
    policy_version: str | None = None


class PairwiseHumanDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    decision: str  # CONFIRM_MODEL | CHOOSE_A | CHOOSE_B | UNDECIDED
    reason: str = ""


def _case_root() -> Path:
    base = os.environ.get("MOODIFY_WORKSPACE_ROOT", "outputs")
    root = Path(base) / "pairwise"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _resolve_audio(asset_id: str, kind: str) -> Path:
    record = _demo_store.get_upload(asset_id) if kind == "upload" else _demo_store.get_artifact(asset_id)
    if record is None or not record.get("path"):
        raise ValueError(f"{kind} asset not found: {asset_id}")
    path = Path(record["path"])
    if not path.is_file():
        raise ValueError(f"{kind} asset file missing: {asset_id}")
    return path


def _error(code: str, message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "request_id": ""}},
    )


@router.post("/pairwise-judgments")
async def v1_pairwise_judgment(request: Request, body: PairwiseJudgeRequest) -> Any:
    if not body.candidate_b_upload_id and not body.candidate_b_artifact_id:
        return _error("VALIDATION", "candidate_b_upload_id or candidate_b_artifact_id is required")
    try:
        audio_a = _resolve_audio(body.candidate_a_upload_id, "upload")
        audio_b = _resolve_audio(
            body.candidate_b_upload_id or body.candidate_b_artifact_id or "",
            "upload" if body.candidate_b_upload_id else "artifact",
        )
    except ValueError as exc:
        return _error("NOT_FOUND", str(exc), 404)

    case_id = f"PW-{uuid.uuid4().hex[:12]}"
    case_root = _case_root() / case_id
    try:
        result = run_pairwise_judge(
            case_id=case_id,
            case_root=case_root,
            candidate_a_path=audio_a,
            candidate_b_path=audio_b,
            policy=DecisionPolicy(),
        )
    except Exception as exc:
        return _error("SERVER_ERROR", f"pairwise judgment failed: {type(exc).__name__}", 500)
    # Never leak filesystem paths in the contract response.
    result.pop("judgment_dir", None)
    return result


@router.post("/pairwise-judgments/{judgment_id}/human-decision")
async def v1_pairwise_human_decision(
    judgment_id: str, request: Request, body: PairwiseHumanDecisionRequest
) -> Any:
    if body.decision not in {"CONFIRM_MODEL", "CHOOSE_A", "CHOOSE_B", "UNDECIDED"}:
        return _error("VALIDATION", f"invalid decision: {body.decision}")
    case_root = _case_root() / judgment_id
    judgment_path = case_root / "06_pairwise" / "judgment.json"
    if not judgment_path.is_file():
        return _error("NOT_FOUND", "pairwise judgment not found", 404)
    judgment = json.loads(judgment_path.read_text(encoding="utf-8"))
    result = record_human_decision(
        case_root=case_root,
        pairwise_case_id=judgment_id,
        decision=body.decision,
        machine_outcome=judgment["outcome"],
        machine_confidence=judgment["confidence_level"],
        override_reason=body.reason,
    )
    return {
        "judgment_id": judgment_id,
        "human_decision": result["human_decision"]["decision"],
        "preference": result["preference_record"],
    }
