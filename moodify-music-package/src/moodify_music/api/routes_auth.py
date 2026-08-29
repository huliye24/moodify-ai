"""Internal auth endpoints — session issue/validate/revoke.

MFY_PLATFORM_IDENTITY_ACCESS_PRIVACY_001. Server-to-server only (service key).
The BFF validates invite codes and proxies here; actors are never resolved
from client-supplied headers.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from moodify_music.api.deps import Db, error, service_key_required
from moodify_music.api.identity import (
    DEFAULT_TTL_SECONDS,
    _user_dict,
    create_session,
    ensure_user,
    resolve_session,
    revoke_session,
)

router = APIRouter(prefix="/internal/v1/music/auth", dependencies=[Depends(service_key_required)])


@router.post("/sessions", status_code=201)
def issue_session(db: Db, body: dict):
    user_id = str(body.get("user_id") or "")
    if not user_id:
        raise error(422, "USER_ID_REQUIRED", "user_id is required")
    user = ensure_user(db, user_id, display_name=body.get("display_name"))
    ttl = body.get("ttl_seconds")
    token, row = create_session(db, user_id, ttl_seconds=int(ttl) if ttl else DEFAULT_TTL_SECONDS)
    db.commit()
    return {
        "token": token,
        "session_id": row.id,
        "expires_at": row.expires_at.isoformat(),
        "user": _user_dict(user),
    }


@router.post("/validate")
def validate_session(db: Db, body: dict):
    user = resolve_session(db, body.get("token"))
    if user is None:
        raise error(401, "SESSION_INVALID", "session is missing, expired, or revoked")
    db.commit()
    return {"user": _user_dict(user)}


@router.delete("/sessions")
def revoke(db: Db, body: dict):
    ok = revoke_session(db, body.get("token"))
    db.commit()
    return {"revoked": ok}


@router.post("/ensure-user", status_code=201)
def ensure(db: Db, body: dict):
    user_id = str(body.get("user_id") or "")
    user = ensure_user(db, user_id, display_name=body.get("display_name"))
    db.commit()
    return _user_dict(user)
