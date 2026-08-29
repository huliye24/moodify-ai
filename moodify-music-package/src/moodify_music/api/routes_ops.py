"""Internal ops endpoints — media reference audit + operator audit records."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select

from moodify_music import audit
from moodify_music.models import TrackVersion
from moodify_music.api.deps import Db, actor_user_id, error, service_key_required
from moodify_music.api.idem import request_id

router = APIRouter(prefix="/internal/v1/music", dependencies=[Depends(service_key_required)])


@router.get("/media/references")
def media_references(db: Db):
    """All media asset keys referenced by any track version (source of truth for orphan audit)."""
    keys = sorted({k for (k,) in db.execute(
        select(TrackVersion.audio_asset_key).where(TrackVersion.audio_asset_key.is_not(None))
    )})
    return {"references": keys}


@router.post("/audit-events", status_code=201)
def record_audit_event(db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    """Operator/system audit record (e.g. media cleanup apply)."""
    action = (body.get("action") or "").strip()
    if not action or len(action) > 64:
        raise error(400, "VALIDATION_ERROR", "action is required (max 64)")
    ev = audit.record(
        db,
        actor_type=body.get("actor_type") or "system",
        actor_id=actor_id or body.get("actor_id"),
        action=action,
        resource_type=(body.get("resource_type") or "media")[:64],
        resource_id=(body.get("resource_id") or "")[:64] or None,
        request_id=request_id(request),
        metadata=body.get("metadata"),
    )
    db.commit()
    return {"id": ev.id, "action": ev.action, "resource_id": ev.resource_id}
