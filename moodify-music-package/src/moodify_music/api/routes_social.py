"""Internal follows / favorites / play-events endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select

from moodify_music import audit
from moodify_music.models import CreatorProfile, Favorite, Follow, PlayEvent, Track, User
from moodify_music.api.deps import Db, actor_user_id, error, require_actor_matches, service_key_required
from moodify_music.api.idem import idempotent_write, replay_response, request_id

router = APIRouter(prefix="/internal/v1/music", dependencies=[Depends(service_key_required)])


@router.put("/users/{user_id}/follows/{creator_id}")
def follow_creator(user_id: str, creator_id: str, db: Db, request: Request, actor_id: str | None = Depends(actor_user_id)):
    require_actor_matches(actor_id, user_id)
    if db.get(User, user_id) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "user not found")
    if db.get(CreatorProfile, creator_id) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "creator not found")
    existing = db.scalar(select(Follow).where(Follow.user_id == user_id, Follow.creator_id == creator_id))
    if existing is not None:
        return {"user_id": user_id, "creator_id": creator_id, "following": True, "replayed": True}
    f = Follow(user_id=user_id, creator_id=creator_id)
    db.add(f)
    db.flush()
    payload = {"user_id": user_id, "creator_id": creator_id}
    resp = {"user_id": user_id, "creator_id": creator_id, "following": True}
    row, replayed = idempotent_write(db, request, "follow", payload, response=resp, resource_type="follow", resource_id=f.id, status_code=200)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=user_id, action="follow.created", resource_type="follow", resource_id=creator_id, request_id=request_id(request))
    db.commit()
    return resp


@router.delete("/users/{user_id}/follows/{creator_id}")
def unfollow_creator(user_id: str, creator_id: str, db: Db, request: Request, actor_id: str | None = Depends(actor_user_id)):
    require_actor_matches(actor_id, user_id)
    existing = db.scalar(select(Follow).where(Follow.user_id == user_id, Follow.creator_id == creator_id))
    if existing is not None:
        db.delete(existing)
        audit.record(db, actor_type="user", actor_id=user_id, action="follow.removed", resource_type="follow", resource_id=creator_id, request_id=request_id(request))
    db.commit()
    return {"user_id": user_id, "creator_id": creator_id, "following": False}


@router.get("/users/{user_id}/follows/{creator_id}")
def get_follow_state(user_id: str, creator_id: str, db: Db, actor_id: str | None = Depends(actor_user_id)):
    require_actor_matches(actor_id, user_id)
    following = db.scalar(select(Follow).where(Follow.user_id == user_id, Follow.creator_id == creator_id)) is not None
    return {"user_id": user_id, "creator_id": creator_id, "following": following}


@router.put("/users/{user_id}/favorites/{track_id}")
def favorite_track(user_id: str, track_id: str, db: Db, request: Request, actor_id: str | None = Depends(actor_user_id)):
    require_actor_matches(actor_id, user_id)
    if db.get(User, user_id) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "user not found")
    if db.get(Track, track_id) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "track not found")
    existing = db.scalar(select(Favorite).where(Favorite.user_id == user_id, Favorite.track_id == track_id))
    if existing is not None:
        return {"user_id": user_id, "track_id": track_id, "favorited": True, "replayed": True}
    f = Favorite(user_id=user_id, track_id=track_id)
    db.add(f)
    db.flush()
    payload = {"user_id": user_id, "track_id": track_id}
    resp = {"user_id": user_id, "track_id": track_id, "favorited": True}
    row, replayed = idempotent_write(db, request, "favorite", payload, response=resp, resource_type="favorite", resource_id=f.id, status_code=200)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=user_id, action="favorite.created", resource_type="favorite", resource_id=track_id, request_id=request_id(request))
    db.commit()
    return resp


@router.delete("/users/{user_id}/favorites/{track_id}")
def unfavorite_track(user_id: str, track_id: str, db: Db, request: Request, actor_id: str | None = Depends(actor_user_id)):
    require_actor_matches(actor_id, user_id)
    existing = db.scalar(select(Favorite).where(Favorite.user_id == user_id, Favorite.track_id == track_id))
    if existing is not None:
        db.delete(existing)
        audit.record(db, actor_type="user", actor_id=user_id, action="favorite.removed", resource_type="favorite", resource_id=track_id, request_id=request_id(request))
    db.commit()
    return {"user_id": user_id, "track_id": track_id, "favorited": False}


@router.post("/play-events", status_code=201)
def create_play_event(db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    track_id = body.get("track_id")
    if not track_id or db.get(Track, track_id) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "track not found")
    ev = PlayEvent(
        user_id=actor_id, track_id=track_id,
        session_id=body.get("session_id"), played_ms=body.get("played_ms"),
        source=body.get("source"),
    )
    db.add(ev)
    db.commit()
    return {"id": ev.id, "track_id": track_id, "created_at": ev.created_at.isoformat() if ev.created_at else None}
