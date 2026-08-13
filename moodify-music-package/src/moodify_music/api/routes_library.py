"""Internal library endpoints — my favorites and recent plays (server identity)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from moodify_music.models import Favorite, PlayEvent, Track, TrackVersion, User
from moodify_music.api.deps import Db, actor_user_id, error, require_actor_matches, service_key_required

router = APIRouter(prefix="/internal/v1/music", dependencies=[Depends(service_key_required)])

PAGE = 30


def _track_summary(db: Db, track_id: str) -> dict | None:
    t = db.get(Track, track_id)
    if t is None or t.deleted_at is not None:
        return None
    v = db.get(TrackVersion, t.current_version_id) if t.current_version_id else None
    return {
        "id": t.id,
        "title": t.title,
        "status": t.status,
        "primary_language": t.primary_language,
        "duration_ms": t.duration_ms,
        "audio_asset_key": v.audio_asset_key if v else None,
    }


@router.get("/users/{user_id}/favorites")
def my_favorites(user_id: str, db: Db, actor_id: str | None = Depends(actor_user_id), cursor: str | None = None):
    """Favorites for the authenticated user, newest first, stable cursor (created_at+id)."""
    require_actor_matches(actor_id, user_id)
    if db.get(User, user_id) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "user not found")
    query = select(Favorite).where(Favorite.user_id == user_id)
    if cursor:
        parts = cursor.split(":")
        if len(parts) != 2:
            raise error(400, "INVALID_CURSOR", "malformed cursor")
        created_at, fav_id = parts[0], parts[1]
        query = query.where((Favorite.created_at < created_at) | ((Favorite.created_at == created_at) & (Favorite.id < fav_id)))
    rows = db.scalars(query.order_by(Favorite.created_at.desc(), Favorite.id.desc()).limit(PAGE + 1))
    items = list(rows)
    next_cursor = None
    if len(items) > PAGE:
        items = items[:PAGE]
        last = items[-1]
        next_cursor = f"{last.created_at.isoformat()}:{last.id}"
    tracks = []
    for fav in items:
        summary = _track_summary(db, fav.track_id)
        if summary:
            summary["favorited_at"] = fav.created_at.isoformat() if fav.created_at else None
            tracks.append(summary)
    return {"tracks": tracks, "next_cursor": next_cursor}


@router.get("/users/{user_id}/recent-plays")
def my_recent_plays(user_id: str, db: Db, actor_id: str | None = Depends(actor_user_id), limit: int = 20):
    """Most recent distinct tracks played by the authenticated user."""
    require_actor_matches(actor_id, user_id)
    if limit < 1 or limit > 50:
        raise error(400, "VALIDATION_ERROR", "limit must be 1..50")
    latest = func.max(PlayEvent.created_at).label("latest")
    rows = db.execute(
        select(PlayEvent.track_id, latest)
        .where(PlayEvent.user_id == user_id, PlayEvent.track_id.is_not(None))
        .group_by(PlayEvent.track_id)
        .order_by(latest.desc())
        .limit(limit)
    )
    tracks = []
    for track_id, last_played in rows:
        summary = _track_summary(db, track_id)
        if summary:
            summary["last_played_at"] = last_played.isoformat() if last_played else None
            tracks.append(summary)
    return {"tracks": tracks}
