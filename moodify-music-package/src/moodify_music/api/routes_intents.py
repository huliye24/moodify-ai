"""Internal license / support intent endpoints (Creator Inbox source)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select

from moodify_music import audit
from moodify_music.models import CreatorProfile, LicenseIntent, SupportIntent, Track
from moodify_music.api.deps import Db, actor_user_id, error, service_key_required
from moodify_music.api.idem import idempotent_write, replay_response, request_id

router = APIRouter(prefix="/internal/v1/music", dependencies=[Depends(service_key_required)])

LICENSE_STATUSES = {"submitted", "reviewing", "contacted", "accepted", "declined", "closed"}
SUPPORT_STATUSES = {"expressed", "contact_requested", "cancelled"}


@router.post("/license-intents", status_code=201)
def create_license_intent(db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    track_id = body.get("track_id")
    t = db.get(Track, track_id) if track_id else None
    if t is None:
        raise error(404, "RESOURCE_NOT_FOUND", "track not found")
    license_type = (body.get("license_type") or "").strip()
    usage = (body.get("usage_description") or "").strip()
    if not license_type or not usage:
        raise error(400, "VALIDATION_ERROR", "license_type and usage_description are required")
    li = LicenseIntent(
        requester_user_id=actor_id, requester_name=(body.get("requester_name") or "").strip()[:120] or None,
        requester_email=(body.get("requester_email") or "").strip()[:320] or None,
        creator_id=t.creator_id, track_id=track_id, license_type=license_type[:64],
        usage_description=usage[:4000], territory=body.get("territory"),
        term_description=body.get("term_description"),
        budget_amount_minor=body.get("budget_amount_minor"), budget_currency=body.get("budget_currency"),
    )
    db.add(li)
    db.flush()
    payload = {"track_id": track_id, "license_type": license_type, "usage_description": usage}
    resp = {"id": li.id, "track_id": track_id, "creator_id": t.creator_id, "status": li.status}
    row, replayed = idempotent_write(db, request, "license_intent", payload, response=resp, resource_type="license_intent", resource_id=li.id)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=actor_id or "guest", action="license_intent.created", resource_type="license_intent", resource_id=li.id, request_id=request_id(request))
    db.commit()
    return resp


@router.get("/license-intents/{intent_id}")
def get_license_intent(intent_id: str, db: Db, actor_id: str | None = Depends(actor_user_id)):
    li = db.get(LicenseIntent, intent_id)
    if li is None:
        raise error(404, "RESOURCE_NOT_FOUND", "license intent not found")
    if actor_id:
        c = db.get(CreatorProfile, li.creator_id)
        if c is None or (c.user_id != actor_id and li.requester_user_id != actor_id):
            raise error(403, "OWNERSHIP_DENIED", "not authorized to view this intent")
    return {
        "id": li.id, "track_id": li.track_id, "creator_id": li.creator_id,
        "license_type": li.license_type, "usage_description": li.usage_description,
        "requester_name": li.requester_name, "requester_email": li.requester_email,
        "territory": li.territory, "term_description": li.term_description,
        "budget_amount_minor": li.budget_amount_minor, "budget_currency": li.budget_currency,
        "status": li.status, "created_at": li.created_at.isoformat() if li.created_at else None,
    }


@router.get("/creators/{creator_id}/license-intents")
def creator_license_inbox(creator_id: str, db: Db, actor_id: str | None = Depends(actor_user_id)):
    """Creator Inbox V1 — intents for one creator, newest first."""
    c = db.get(CreatorProfile, creator_id)
    if c is None:
        raise error(404, "RESOURCE_NOT_FOUND", "creator not found")
    if actor_id and c.user_id != actor_id:
        raise error(403, "OWNERSHIP_DENIED", "not authorized to view this inbox")
    rows = db.scalars(
        select(LicenseIntent).where(LicenseIntent.creator_id == creator_id).order_by(LicenseIntent.created_at.desc()).limit(100)
    )
    return {
        "creator_id": creator_id,
        "intents": [
            {
                "id": r.id, "track_id": r.track_id, "license_type": r.license_type,
                "usage_description": r.usage_description, "requester_name": r.requester_name,
                "budget_amount_minor": r.budget_amount_minor, "budget_currency": r.budget_currency,
                "status": r.status, "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.post("/support-intents", status_code=201)
def create_support_intent(db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    creator_id = body.get("creator_id")
    if db.get(CreatorProfile, creator_id) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "creator not found")
    si = SupportIntent(
        supporter_user_id=actor_id, creator_id=creator_id, track_id=body.get("track_id"),
        amount_minor=body.get("amount_minor"), currency=body.get("currency"),
        message=(body.get("message") or "").strip()[:2000] or None,
    )
    db.add(si)
    db.flush()
    payload = {"creator_id": creator_id, "amount_minor": si.amount_minor}
    resp = {"id": si.id, "creator_id": creator_id, "status": si.status, "track_id": si.track_id}
    row, replayed = idempotent_write(db, request, "support_intent", payload, response=resp, resource_type="support_intent", resource_id=si.id)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=actor_id or "guest", action="support_intent.created", resource_type="support_intent", resource_id=si.id, request_id=request_id(request))
    db.commit()
    return resp


@router.get("/support-intents/{intent_id}")
def get_support_intent(intent_id: str, db: Db, actor_id: str | None = Depends(actor_user_id)):
    si = db.get(SupportIntent, intent_id)
    if si is None:
        raise error(404, "RESOURCE_NOT_FOUND", "support intent not found")
    if actor_id:
        c = db.get(CreatorProfile, si.creator_id)
        if c is None or (c.user_id != actor_id and si.supporter_user_id != actor_id):
            raise error(403, "OWNERSHIP_DENIED", "not authorized to view this intent")
    return {
        "id": si.id, "creator_id": si.creator_id, "track_id": si.track_id,
        "amount_minor": si.amount_minor, "currency": si.currency, "message": si.message,
        "status": si.status, "created_at": si.created_at.isoformat() if si.created_at else None,
    }
