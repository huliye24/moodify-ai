"""Internal search — published tracks and active creators only."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select

from moodify_music.models import CreatorProfile, Track, TrackVersion
from moodify_music.api.deps import Db, error, service_key_required

router = APIRouter(prefix="/internal/v1/music", dependencies=[Depends(service_key_required)])

MIN_QUERY = 2
MAX_LIMIT = 50


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@router.get("/search")
def search(db: Db, q: str = "", type: str = "track", limit: int = 10, cursor: str | None = None):
    query = q.strip().lower()
    if len(query) < MIN_QUERY:
        raise error(400, "QUERY_TOO_SHORT", f"query must be at least {MIN_QUERY} characters")
    if type not in ("track", "creator"):
        raise error(400, "INVALID_TYPE", "type must be track or creator")
    if limit < 1 or limit > MAX_LIMIT:
        raise error(400, "INVALID_LIMIT", f"limit must be 1..{MAX_LIMIT}")
    pattern = f"%{_escape_like(query)}%"

    if type == "track":
        rows = db.scalars(
            select(Track)
            .where(
                Track.status == "published",
                Track.deleted_at.is_(None),
                or_(Track.title.ilike(pattern, escape="\\"), Track.primary_language.ilike(pattern, escape="\\")),
            )
            .order_by(Track.published_at.desc())
            .limit(limit)
        )
        tracks = []
        for t in rows:
            v = db.get(TrackVersion, t.current_version_id) if t.current_version_id else None
            tracks.append({
                "id": t.id, "title": t.title, "creator_id": t.creator_id,
                "primary_language": t.primary_language, "duration_ms": t.duration_ms,
                "published_at": t.published_at.isoformat() if t.published_at else None,
                "audio_asset_key": v.audio_asset_key if v else None,
            })
        return {"type": "track", "query": query, "tracks": tracks}
    else:
        rows = db.scalars(
            select(CreatorProfile)
            .where(
                CreatorProfile.status == "active",
                or_(CreatorProfile.handle.ilike(pattern, escape="\\"), CreatorProfile.display_name.ilike(pattern, escape="\\")),
            )
            .order_by(CreatorProfile.handle)
            .limit(limit)
        )
        creators = [{
            "id": c.id, "handle": c.handle, "display_name": c.display_name,
            "bio": c.bio, "avatar_asset_key": c.avatar_asset_key,
        } for c in rows]
        return {"type": "creator", "query": query, "creators": creators}
