"""Internal playlist endpoints — minimal real playlists (V1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select

from moodify_music import audit
from moodify_music.models import Playlist, PlaylistItem, Track, User
from moodify_music.api.deps import Db, actor_user_id, error, require_actor_matches, service_key_required
from moodify_music.api.idem import idempotent_write, replay_response, request_id

router = APIRouter(prefix="/internal/v1/music", dependencies=[Depends(service_key_required)])


def _playlist_dict(db: Db, p: Playlist, include_items: bool = True) -> dict:
    items = []
    if include_items:
        rows = db.scalars(select(PlaylistItem).where(PlaylistItem.playlist_id == p.id).order_by(PlaylistItem.position, PlaylistItem.added_at))
        items = [{"track_id": r.track_id, "position": r.position, "added_at": r.added_at.isoformat() if r.added_at else None} for r in rows]
    return {
        "id": p.id, "owner_user_id": p.owner_user_id, "title": p.title,
        "visibility": p.visibility,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        "items": items,
    }


@router.post("/playlists", status_code=201)
def create_playlist(db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    owner = body.get("owner_user_id") or actor_id
    require_actor_matches(actor_id, owner)
    if db.get(User, owner) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "user not found")
    title = (body.get("title") or "").strip()
    if not title or len(title) > 200:
        raise error(400, "VALIDATION_ERROR", "title is required (max 200)")
    visibility = body.get("visibility") or "private"
    if visibility not in ("private", "public"):
        raise error(400, "VALIDATION_ERROR", "visibility must be private or public")
    p = Playlist(owner_user_id=owner, title=title, visibility=visibility)
    db.add(p)
    db.flush()
    payload = {"owner_user_id": owner, "title": title, "visibility": visibility}
    resp = _playlist_dict(db, p, include_items=False)
    row, replayed = idempotent_write(db, request, "playlist", payload, response=resp, resource_type="playlist", resource_id=p.id)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=owner, action="playlist.created", resource_type="playlist", resource_id=p.id, request_id=request_id(request))
    db.commit()
    return resp


@router.get("/playlists/{playlist_id}")
def get_playlist(playlist_id: str, db: Db, actor_id: str | None = Depends(actor_user_id)):
    p = db.get(Playlist, playlist_id)
    if p is None:
        raise error(404, "RESOURCE_NOT_FOUND", "playlist not found")
    if p.visibility != "public" and p.owner_user_id != actor_id:
        raise error(403, "OWNERSHIP_DENIED", "private playlist belongs to another user")
    return _playlist_dict(db, p)


@router.patch("/playlists/{playlist_id}")
def update_playlist(playlist_id: str, db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    p = db.get(Playlist, playlist_id)
    if p is None:
        raise error(404, "RESOURCE_NOT_FOUND", "playlist not found")
    require_actor_matches(actor_id, p.owner_user_id)
    if "title" in body and body["title"] is not None:
        title = str(body["title"]).strip()
        if not title or len(title) > 200:
            raise error(400, "VALIDATION_ERROR", "title is required (max 200)")
        p.title = title
    if "visibility" in body and body["visibility"] is not None:
        if body["visibility"] not in ("private", "public"):
            raise error(400, "VALIDATION_ERROR", "visibility must be private or public")
        p.visibility = body["visibility"]
    from moodify_music.models import utcnow
    p.updated_at = utcnow()
    audit.record(db, actor_type="user", actor_id=actor_id, action="playlist.updated", resource_type="playlist", resource_id=p.id, request_id=request_id(request))
    db.commit()
    return _playlist_dict(db, p)


@router.delete("/playlists/{playlist_id}")
def delete_playlist(playlist_id: str, db: Db, request: Request, actor_id: str | None = Depends(actor_user_id)):
    """Delete the playlist container only — never tracks or media."""
    p = db.get(Playlist, playlist_id)
    if p is None:
        raise error(404, "RESOURCE_NOT_FOUND", "playlist not found")
    require_actor_matches(actor_id, p.owner_user_id)
    db.execute(PlaylistItem.__table__.delete().where(PlaylistItem.playlist_id == playlist_id))
    db.delete(p)
    audit.record(db, actor_type="user", actor_id=actor_id, action="playlist.deleted", resource_type="playlist", resource_id=playlist_id, request_id=request_id(request))
    db.commit()
    return {"deleted": playlist_id}


@router.post("/playlists/{playlist_id}/items", status_code=201)
def add_playlist_item(playlist_id: str, db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    p = db.get(Playlist, playlist_id)
    if p is None:
        raise error(404, "RESOURCE_NOT_FOUND", "playlist not found")
    require_actor_matches(actor_id, p.owner_user_id)
    track_id = body.get("track_id")
    if not track_id or db.get(Track, track_id) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "track not found")
    existing = db.scalar(select(PlaylistItem).where(PlaylistItem.playlist_id == playlist_id, PlaylistItem.track_id == track_id))
    if existing is not None:
        raise error(409, "DUPLICATE_ITEM", "track already in playlist (duplicates rejected)")
    position = db.scalar(select(PlaylistItem.position).where(PlaylistItem.playlist_id == playlist_id).order_by(PlaylistItem.position.desc())) or 0
    item = PlaylistItem(playlist_id=playlist_id, track_id=track_id, position=position + 1)
    db.add(item)
    audit.record(db, actor_type="user", actor_id=actor_id, action="playlist.item_added", resource_type="playlist", resource_id=playlist_id, request_id=request_id(request), metadata={"track_id": track_id})
    db.commit()
    return {"playlist_id": playlist_id, "track_id": track_id, "position": item.position}


@router.delete("/playlists/{playlist_id}/items/{track_id}")
def remove_playlist_item(playlist_id: str, track_id: str, db: Db, request: Request, actor_id: str | None = Depends(actor_user_id)):
    p = db.get(Playlist, playlist_id)
    if p is None:
        raise error(404, "RESOURCE_NOT_FOUND", "playlist not found")
    require_actor_matches(actor_id, p.owner_user_id)
    item = db.scalar(select(PlaylistItem).where(PlaylistItem.playlist_id == playlist_id, PlaylistItem.track_id == track_id))
    if item is None:
        return {"playlist_id": playlist_id, "track_id": track_id, "removed": False}  # idempotent removal
    db.delete(item)
    audit.record(db, actor_type="user", actor_id=actor_id, action="playlist.item_removed", resource_type="playlist", resource_id=playlist_id, request_id=request_id(request), metadata={"track_id": track_id})
    db.commit()
    return {"playlist_id": playlist_id, "track_id": track_id, "removed": True}


@router.get("/users/{user_id}/playlists")
def my_playlists(user_id: str, db: Db, actor_id: str | None = Depends(actor_user_id)):
    require_actor_matches(actor_id, user_id)
    rows = db.scalars(select(Playlist).where(Playlist.owner_user_id == user_id).order_by(Playlist.updated_at.desc()).limit(100))
    return {"playlists": [_playlist_dict(db, p, include_items=False) for p in rows]}
