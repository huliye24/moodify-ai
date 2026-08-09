"""Open access + CWC compute credit API contract (DSK-MFY-ACCESS-CWC-PATCH-001).

Endpoints:
    POST /api/v1/auth/register        (open registration; referral optional)
    POST /api/v1/referral/redeem
    GET  /api/v1/cwc/balance
    GET  /api/v1/cwc/history
    POST /api/v1/compute/estimate
    POST /api/v1/compute/admit
    POST /api/v1/compute/settle
    GET  /api/v1/compute/quota

CWC is compute credit only — never a token, wallet asset, or financial
instrument. Missing referral codes never block registration.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from moodify.access.policy import AccessPolicy
from moodify.access.service import AccessService

API_PREFIX = "/api/v1"

router = APIRouter(prefix=API_PREFIX, tags=["access-cwc"])


def _service() -> AccessService:
    root = Path(os.environ.get("MOODIFY_ACCESS_ROOT", "outputs/access"))
    return AccessService(root, policy=AccessPolicy.from_yaml())


def _error(code: str, message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "request_id": ""}},
    )


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    user_id: str
    referral_code: str | None = None


class ReferralRedeemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    inviter_id: str
    invitee_id: str


class EstimateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    operation_type: str


class AdmitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    user_id: str
    operation_type: str
    priority_tier: str = "free"


class SettleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    admission_id: str
    actual_cwc: float


@router.post("/auth/register")
async def v1_register(request: Request, body: RegisterRequest) -> Any:
    try:
        return _service().register(body.user_id, referral_code=body.referral_code)
    except ValueError as exc:
        return _error("VALIDATION", str(exc), 400)


@router.post("/referral/redeem")
async def v1_referral_redeem(request: Request, body: ReferralRedeemRequest) -> Any:
    return _service().grant_referral_reward(body.inviter_id, body.invitee_id)


@router.get("/cwc/balance")
async def v1_cwc_balance(user_id: str) -> Any:
    return _service().balance(user_id)


@router.get("/cwc/history")
async def v1_cwc_history(user_id: str) -> Any:
    return {"user_id": user_id, "transactions": _service().history(user_id)}


@router.post("/compute/estimate")
async def v1_compute_estimate(request: Request, body: EstimateRequest) -> Any:
    try:
        return _service().estimate(body.operation_type)
    except ValueError as exc:
        return _error("VALIDATION", str(exc), 400)


@router.post("/compute/admit")
async def v1_compute_admit(request: Request, body: AdmitRequest) -> Any:
    try:
        return _service().admit(body.user_id, body.operation_type, body.priority_tier)
    except ValueError as exc:
        return _error("VALIDATION", str(exc), 400)


@router.post("/compute/settle")
async def v1_compute_settle(request: Request, body: SettleRequest) -> Any:
    try:
        return _service().settle(body.admission_id, body.actual_cwc)
    except ValueError as exc:
        return _error("VALIDATION", str(exc), 400)


@router.get("/compute/quota")
async def v1_compute_quota(user_id: str) -> Any:
    return _service().quota(user_id)
