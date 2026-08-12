"""Internal users + creators endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select

from moodify_music import audit
from moodify_music.models import Album, CreatorProfile, Track, User, utcnow
from moodify_music.api.deps import Db, actor_user_id, error, service_key_required
from moodify_music.api.idem import idempotent_write, replay_response, request_id

router = APIRouter(prefix="/internal/v1/music", dependencies=[Depends(service_key_required)])


def _user_dict(u: User) -> dict:
    return {
        "id": u.id, "email": u.email, "display_name": u.display_name,
        "status": u.status, "locale": u.locale, "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def _creator_dict(c: CreatorProfile) -> dict:
    return {
        "id": c.id, "user_id": c.user_id, "handle": c.handle,
        "display_name": c.display_name, "bio": c.bio,
        "avatar_asset_key": c.avatar_asset_key, "banner_asset_key": c.banner_asset_key,
        "status": c.status,
    }


@router.post("/users", status_code=201)
def create_user(db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    email = (body.get("email") or "").strip() or None
    if email and db.scalar(select(User).where(User.email == email)):
        raise error(409, "EMAIL_TAKEN", "email already registered")
    u = User(display_name=body.get("display_name", "unnamed").strip()[:120], email=email, locale=body.get("locale"))
    db.add(u)
    db.flush()
    payload = {"email": email, "display_name": u.display_name}
    row, replayed = idempotent_write(db, request, "create_user", payload, response=_user_dict(u), resource_type="user", resource_id=u.id)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=actor_id or u.id, action="user.created", resource_type="user", resource_id=u.id, request_id=request_id(request))
    db.commit()
    return _user_dict(u)


@router.get("/users/{user_id}")
def get_user(user_id: str, db: Db):
    u = db.get(User, user_id)
    if u is None or u.deleted_at is not None:
        raise error(404, "RESOURCE_NOT_FOUND", "user not found")
    return _user_dict(u)


@router.post("/creators", status_code=201)
def create_creator(db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    user_id = body.get("user_id") or actor_id
    if not user_id:
        raise error(400, "VALIDATION_ERROR", "user_id is required")
    if db.get(User, user_id) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "user not found")
    if db.scalar(select(CreatorProfile).where(CreatorProfile.user_id == user_id)):
        raise error(409, "CREATOR_EXISTS", "user already has a creator profile")
    handle = (body.get("handle") or "").strip().lower()
    if not handle or len(handle) > 64:
        raise error(400, "VALIDATION_ERROR", "handle is required (max 64)")
    if db.scalar(select(CreatorProfile).where(CreatorProfile.handle == handle)):
        raise error(409, "HANDLE_TAKEN", "handle already in use")
    c = CreatorProfile(
        user_id=user_id, handle=handle,
        display_name=(body.get("display_name") or "").strip()[:120] or handle,
        bio=body.get("bio"), avatar_asset_key=body.get("avatar_asset_key"),
        banner_asset_key=body.get("banner_asset_key"),
    )
    db.add(c)
    db.flush()
    payload = {"user_id": user_id, "handle": handle}
    row, replayed = idempotent_write(db, request, "create_creator", payload, response=_creator_dict(c), resource_type="creator", resource_id=c.id)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=user_id, action="creator.created", resource_type="creator", resource_id=c.id, request_id=request_id(request))
    db.commit()
    return _creator_dict(c)


@router.get("/creators/{creator_id}")
def get_creator(creator_id: str, db: Db):
    c = db.get(CreatorProfile, creator_id)
    if c is None:
        raise error(404, "RESOURCE_NOT_FOUND", "creator not found")
    return _creator_dict(c)


@router.get("/creators/by-handle/{handle}")
def get_creator_by_handle(handle: str, db: Db):
    c = db.scalar(select(CreatorProfile).where(CreatorProfile.handle == handle.strip().lower()))
    if c is None:
        raise error(404, "RESOURCE_NOT_FOUND", "creator not found")
    return _creator_dict(c)


@router.get("/creators/{creator_id}/page")
def creator_page(creator_id: str, db: Db, viewer_user_id: str | None = None):
    c = db.get(CreatorProfile, creator_id)
    if c is None:
        raise error(404, "RESOURCE_NOT_FOUND", "creator not found")
    tracks = list(
        db.scalars(
            select(Track).where(Track.creator_id == creator_id, Track.status == "published", Track.deleted_at.is_(None))
            .order_by(Track.published_at.desc()).limit(50)
        )
    )
    album_summary = [
        {"id": a.id, "title": a.title, "cover_asset_key": a.cover_asset_key}
        for a in db.scalars(select(Album).where(Album.creator_id == creator_id, Album.status == "published"))
    ]
    from moodify_music.models import Follow

    follower_count = db.scalar(select(func.count()).select_from(Follow).where(Follow.creator_id == creator_id)) or 0
    follow_state = None
    if viewer_user_id:
        follow_state = db.scalar(
            select(Follow).where(Follow.user_id == viewer_user_id, Follow.creator_id == creator_id)
        ) is not None
    return {
        "profile": _creator_dict(c),
        "tracks": [_track_dict(t) for t in tracks],
        "albums": album_summary,
        "follower_count": follower_count,
        "viewer_following": follow_state,
    }


def _track_dict(t: Track) -> dict:
    return {
        "id": t.id, "title": t.title, "status": t.status, "visibility": t.visibility,
        "duration_ms": t.duration_ms, "cover_asset_key": t.cover_asset_key,
        "current_version_id": t.current_version_id, "published_at": t.published_at.isoformat() if t.published_at else None,
    }
