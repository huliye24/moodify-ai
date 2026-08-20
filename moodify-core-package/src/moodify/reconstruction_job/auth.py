"""Owner boundary and short-lived access tokens (MFY-CR-P08).

MOODIFY_AUTH_MODE=single_user (default) accepts any actor and records jobs
under the fixed owner 'dev-user' — explicitly NOT_MULTIUSER_PRODUCTION_READY.
MOODIFY_AUTH_MODE=owner requires X-Moodify-Actor-User-Id and enforces owner
checks on every read/cancel/result. Audio access uses HMAC-signed short-lived
tokens; missing secret fails closed.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time

from fastapi import HTTPException, Request

SINGLE_USER_OWNER = "dev-user"
AUDIO_TOKEN_TTL_S = 15 * 60

_ACTOR_HEADER = "x-moodify-actor-user-id"


def auth_mode() -> str:
    return os.environ.get("MOODIFY_AUTH_MODE", "single_user").strip().lower()


def actor_from_request(request: Request) -> str:
    """Resolve the acting owner; owner mode requires the actor header."""
    mode = auth_mode()
    if mode == "owner":
        actor = request.headers.get(_ACTOR_HEADER, "").strip()
        if not actor:
            raise HTTPException(status_code=401, detail={"code": "ACTOR_REQUIRED"})
        return actor
    return SINGLE_USER_OWNER


def require_owner(job_owner: str, actor: str) -> None:
    """Cross-owner access is denied as 404 (existence must not leak)."""
    if job_owner != actor:
        raise HTTPException(status_code=404, detail={"code": "JOB_NOT_FOUND"})


def _token_secret() -> str | None:
    secret = os.environ.get("MOODIFY_AUDIO_TOKEN_SECRET", "").strip()
    return secret or None


def issue_audio_token(job_id: str, owner_id: str) -> str:
    secret = _token_secret()
    if secret is None:
        raise HTTPException(status_code=500, detail={"code": "TOKEN_SECRET_MISSING"})
    exp = str(int(time.time()) + AUDIO_TOKEN_TTL_S)
    payload = f"{job_id}:{owner_id}:{exp}"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def verify_audio_token(token: str, job_id: str, owner_id: str) -> None:
    """Validate token ownership and expiry; failures are 401/403 without detail."""
    secret = _token_secret()
    if secret is None:
        raise HTTPException(status_code=500, detail={"code": "TOKEN_SECRET_MISSING"})
    parts = token.split(":")
    if len(parts) != 4:
        raise HTTPException(status_code=401, detail={"code": "TOKEN_INVALID"})
    token_job, token_owner, token_exp, token_sig = parts
    if token_job != job_id:
        raise HTTPException(status_code=401, detail={"code": "TOKEN_INVALID"})
    payload = f"{token_job}:{token_owner}:{token_exp}"
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(token_sig, expected):
        raise HTTPException(status_code=401, detail={"code": "TOKEN_INVALID"})
    if int(token_exp) < int(time.time()):
        raise HTTPException(status_code=401, detail={"code": "TOKEN_EXPIRED"})
    if token_owner != owner_id:
        raise HTTPException(status_code=403, detail={"code": "OWNERSHIP_DENIED"})
