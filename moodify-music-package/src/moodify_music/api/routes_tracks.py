"""Internal tracks / versions / passport / publish / albums endpoints."""

from __future__ import annotations

import base64
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy import and_, or_, select

from moodify_music import audit
from moodify_music.models import (
    Album, AlbumTrack, CreationPassport, CreatorProfile, Track, TrackVersion, utcnow,
)
from moodify_music.api.deps import Db, actor_user_id, error, service_key_required
from moodify_music.api.idem import idempotent_write, replay_response, request_id

router = APIRouter(prefix="/internal/v1/music", dependencies=[Depends(service_key_required)])

TRACK_FIELDS = {
    "title": 300, "slug": 200, "primary_language": 16, "duration_ms": None,
    "cover_asset_key": 512, "ear_production_case_ref": 128, "approved_evidence_ref": 128,
}


def _require_owner(db: Db, creator_id: str, actor: str | None) -> CreatorProfile:
    c = db.get(CreatorProfile, creator_id)
    if c is None:
        raise error(404, "RESOURCE_NOT_FOUND", "creator not found")
    if actor and c.user_id != actor:
        raise error(403, "OWNERSHIP_DENIED", "actor does not own this creator profile")
    return c


def _get_track(db: Db, track_id: str) -> Track:
    t = db.get(Track, track_id)
    if t is None or t.deleted_at is not None:
        raise error(404, "RESOURCE_NOT_FOUND", "track not found")
    return t


def _track_dict(t: Track, current_version: TrackVersion | None = None, creator_handle: str | None = None) -> dict:
    return {
        "id": t.id, "creator_id": t.creator_id, "title": t.title, "slug": t.slug,
        "status": t.status, "visibility": t.visibility, "primary_language": t.primary_language,
        "duration_ms": t.duration_ms, "cover_asset_key": t.cover_asset_key,
        "current_version_id": t.current_version_id,
        "published_at": t.published_at.isoformat() if t.published_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        "ear_production_case_ref": t.ear_production_case_ref,
        "approved_evidence_ref": t.approved_evidence_ref,
        "creator_handle": creator_handle,
        "version": {
            "id": v.id, "version_no": v.version_no, "audio_asset_key": v.audio_asset_key,
        } if (v := current_version) is not None else None,
    }


def _encode_catalogue_cursor(published_at: datetime, track_id: str) -> str:
    payload = json.dumps(
        {"published_at": published_at.isoformat(), "id": track_id},
        separators=(",", ":"),
    ).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def _decode_catalogue_cursor(cursor: str) -> tuple[datetime, str]:
    try:
        padding = "=" * (-len(cursor) % 4)
        payload = json.loads(base64.urlsafe_b64decode(cursor + padding))
        published_at = datetime.fromisoformat(payload["published_at"])
        track_id = str(payload["id"])
        if not track_id:
            raise ValueError
        return published_at, track_id
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise error(400, "INVALID_CURSOR", "catalogue cursor is invalid")


@router.get("/catalogue")
def catalogue(db: Db, limit: int = 50, cursor: str | None = None):
    """Published tracks for discovery — newest first."""
    page_size = min(max(limit, 1), 100)
    conditions = [Track.status == "published", Track.deleted_at.is_(None)]
    if cursor:
        published_at, track_id = _decode_catalogue_cursor(cursor)
        conditions.append(or_(
            Track.published_at < published_at,
            and_(Track.published_at == published_at, Track.id < track_id),
        ))
    rows = db.execute(
        select(Track, TrackVersion, CreatorProfile.handle)
        .outerjoin(TrackVersion, TrackVersion.id == Track.current_version_id)
        .outerjoin(CreatorProfile, CreatorProfile.id == Track.creator_id)
        .where(*conditions)
        .order_by(Track.published_at.desc(), Track.id.desc())
        .limit(page_size + 1)
    ).all()
    page = rows[:page_size]
    next_cursor = None
    if len(rows) > page_size and page:
        last_track = page[-1][0]
        if last_track.published_at is not None:
            next_cursor = _encode_catalogue_cursor(last_track.published_at, last_track.id)
    return {
        "tracks": [_track_dict(track, version, handle) for track, version, handle in page],
        "next_cursor": next_cursor,
    }


@router.post("/tracks", status_code=201)
def create_track(db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    creator_id = body.get("creator_id")
    _require_owner(db, creator_id, actor_id)
    title = (body.get("title") or "").strip()
    if not title:
        raise error(400, "VALIDATION_ERROR", "title is required")
    t = Track(
        creator_id=creator_id, created_by_user_id=actor_id or creator_id, title=title[:300],
        slug=(body.get("slug") or "").strip()[:200] or None,
        primary_language=body.get("primary_language"),
        duration_ms=body.get("duration_ms"),
        cover_asset_key=body.get("cover_asset_key"),
        ear_production_case_ref=body.get("ear_production_case_ref"),
        approved_evidence_ref=body.get("approved_evidence_ref"),
    )
    db.add(t)
    db.flush()
    payload = {"creator_id": creator_id, "title": title}
    row, replayed = idempotent_write(db, request, "create_track", payload, response=_track_dict(t), resource_type="track", resource_id=t.id)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=actor_id or creator_id, action="track.created", resource_type="track", resource_id=t.id, request_id=request_id(request), metadata={"title": title})
    db.commit()
    return _track_dict(t)


@router.get("/tracks/{track_id}")
def get_track(track_id: str, db: Db):
    t = _get_track(db, track_id)
    v = db.get(TrackVersion, t.current_version_id) if t.current_version_id else None
    c = db.get(CreatorProfile, t.creator_id)
    return _track_dict(t, v, c.handle if c else None)


@router.patch("/tracks/{track_id}")
def update_track(track_id: str, db: Db, body: dict, actor_id: str | None = Depends(actor_user_id),
                 if_match: str = Header(default="")):
    t = _get_track(db, track_id)
    _require_owner(db, t.creator_id, actor_id)
    if if_match:
        if not t.updated_at or t.updated_at.isoformat() != if_match:
            raise error(412, "PRECONDITION_FAILED", "track was modified elsewhere; refresh before editing")
    for field, maxlen in TRACK_FIELDS.items():
        if field in body and body[field] is not None:
            value = body[field]
            if maxlen and isinstance(value, str):
                value = value[:maxlen]
            setattr(t, field, value)
    t.updated_at = utcnow()
    db.commit()
    return _track_dict(t)


@router.post("/tracks/{track_id}/versions", status_code=201)
def create_track_version(track_id: str, db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    t = _get_track(db, track_id)
    _require_owner(db, t.creator_id, actor_id)
    audio_key = body.get("audio_asset_key")
    if not audio_key:
        raise error(400, "VALIDATION_ERROR", "audio_asset_key is required (MEDIA_UPLOAD_DEFERRED: reference existing asset)")
    max_no = db.scalar(select(TrackVersion.version_no).where(TrackVersion.track_id == track_id).order_by(TrackVersion.version_no.desc())) or 0
    v = TrackVersion(
        track_id=track_id, version_no=max_no + 1, audio_asset_key=audio_key,
        lyrics_text=body.get("lyrics_text"), metadata_json=body.get("metadata_json"),
        created_by_user_id=actor_id or t.creator_id,
    )
    db.add(v)
    db.flush()
    t.current_version_id = v.id
    t.duration_ms = body.get("duration_ms") or t.duration_ms
    t.updated_at = utcnow()
    payload = {"track_id": track_id, "audio_asset_key": audio_key}
    resp = {"id": v.id, "track_id": v.track_id, "version_no": v.version_no, "audio_asset_key": v.audio_asset_key}
    row, replayed = idempotent_write(db, request, "create_version", payload, response=resp, resource_type="track_version", resource_id=v.id)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=actor_id or t.creator_id, action="track.version_created", resource_type="track_version", resource_id=v.id, request_id=request_id(request))
    db.commit()
    return resp


@router.post("/tracks/{track_id}/publish")
def publish_track(track_id: str, db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    t = _get_track(db, track_id)
    _require_owner(db, t.creator_id, actor_id)
    if t.current_version_id is None:
        raise error(409, "PUBLISH_REQUIRES_VERSION", "track has no current version")
    if not db.scalar(select(CreationPassport).where(CreationPassport.track_id == track_id)):
        raise error(409, "PUBLISH_REQUIRES_PASSPORT", "track has no creation passport")
    prev = t.status
    if prev == "published":
        # safe replay: response was lost client-side; track is already published
        return _track_dict(t)
    t.status = "published"
    t.published_at = utcnow()
    t.updated_at = utcnow()
    # stable idempotency payload: no mutable "from" field
    payload = {"track_id": track_id, "to": "published"}
    row, replayed = idempotent_write(db, request, "publish", payload, response=_track_dict(t), resource_type="track", resource_id=t.id, status_code=200)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=actor_id or t.creator_id, action="track.published", resource_type="track", resource_id=t.id, request_id=request_id(request), metadata={"from": prev})
    db.commit()
    return _track_dict(t)


@router.put("/tracks/{track_id}/passport")
def upsert_passport(track_id: str, db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    t = _get_track(db, track_id)
    _require_owner(db, t.creator_id, actor_id)
    p = db.scalar(select(CreationPassport).where(CreationPassport.track_id == track_id))
    fields = {
        "origin_type": 32, "generation_tool": 128, "generation_model": 128,
        "generation_model_version": 64, "prompt_disclosure": 16, "lyrics_author_type": 32,
        "human_editing_notes": 4000, "rights_statement": 4000, "commercial_use_claim": 4000,
    }
    data = {}
    for key, maxlen in fields.items():
        if key in body and body[key] is not None:
            value = body[key]
            data[key] = value[:maxlen] if isinstance(value, str) and maxlen else value
    if p is None:
        p = CreationPassport(track_id=track_id, **data)
        db.add(p)
    else:
        for k, v in data.items():
            setattr(p, k, v)
        p.updated_at = utcnow()
    db.flush()
    row, replayed = idempotent_write(db, request, "passport", {"track_id": track_id, **data}, response={"id": p.id, "track_id": track_id, **data}, resource_type="creation_passport", resource_id=p.id, status_code=200)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=actor_id or t.creator_id, action="passport.updated", resource_type="creation_passport", resource_id=p.id, request_id=request_id(request))
    db.commit()
    return {"id": p.id, "track_id": track_id, **data}


@router.get("/tracks/{track_id}/passport")
def get_passport(track_id: str, db: Db):
    p = db.scalar(select(CreationPassport).where(CreationPassport.track_id == track_id))
    if p is None:
        raise error(404, "RESOURCE_NOT_FOUND", "passport not found")
    return {"id": p.id, "track_id": p.track_id, "origin_type": p.origin_type, "generation_tool": p.generation_tool,
            "generation_model": p.generation_model, "generation_model_version": p.generation_model_version,
            "prompt_disclosure": p.prompt_disclosure, "lyrics_author_type": p.lyrics_author_type,
            "human_editing_notes": p.human_editing_notes, "rights_statement": p.rights_statement,
            "commercial_use_claim": p.commercial_use_claim}


@router.post("/albums", status_code=201)
def create_album(db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    creator_id = body.get("creator_id")
    _require_owner(db, creator_id, actor_id)
    title = (body.get("title") or "").strip()
    if not title:
        raise error(400, "VALIDATION_ERROR", "title is required")
    a = Album(creator_id=creator_id, title=title[:300], description=body.get("description"), cover_asset_key=body.get("cover_asset_key"))
    db.add(a)
    db.flush()
    payload = {"creator_id": creator_id, "title": title}
    resp = {"id": a.id, "creator_id": a.creator_id, "title": a.title}
    row, replayed = idempotent_write(db, request, "create_album", payload, response=resp, resource_type="album", resource_id=a.id)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="user", actor_id=actor_id or creator_id, action="album.created", resource_type="album", resource_id=a.id, request_id=request_id(request))
    db.commit()
    return resp


@router.get("/albums/{album_id}")
def get_album(album_id: str, db: Db):
    a = db.get(Album, album_id)
    if a is None:
        raise error(404, "RESOURCE_NOT_FOUND", "album not found")
    members = db.scalars(
        select(AlbumTrack).where(AlbumTrack.album_id == album_id).order_by(AlbumTrack.position)
    )
    return {"id": a.id, "creator_id": a.creator_id, "title": a.title, "description": a.description,
            "cover_asset_key": a.cover_asset_key, "status": a.status,
            "tracks": [{"track_id": m.track_id, "position": m.position} for m in members]}


@router.post("/albums/{album_id}/tracks", status_code=201)
def add_album_track(album_id: str, db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    a = db.get(Album, album_id)
    if a is None:
        raise error(404, "RESOURCE_NOT_FOUND", "album not found")
    _require_owner(db, a.creator_id, actor_id)
    track_id = body.get("track_id")
    t = _get_track(db, track_id)
    if t.creator_id != a.creator_id:
        raise error(403, "OWNERSHIP_DENIED", "track does not belong to album creator")
    pos = db.scalar(select(AlbumTrack.position).where(AlbumTrack.album_id == album_id).order_by(AlbumTrack.position.desc())) or 0
    m = AlbumTrack(album_id=album_id, track_id=track_id, position=pos + 1)
    db.add(m)
    db.commit()
    return {"album_id": album_id, "track_id": track_id, "position": m.position}


# ============================================================
# MFY_MUSIC_CREATOR_LIFECYCLE_001 — server-authoritative recovery
# ============================================================

def _draft_stage(db: Db, t: Track) -> dict:
    """Derive lifecycle stage from server facts (no second state machine)."""
    version = db.get(TrackVersion, t.current_version_id) if t.current_version_id else None
    passport = db.scalar(select(CreationPassport).where(CreationPassport.track_id == t.id))
    if t.status == "published":
        stage, next_action = "published", "view"
    elif t.status == "archived":
        stage, next_action = "archived", "read_only"
    elif version is None:
        stage, next_action = "draft", "create_version"
    elif passport is None:
        stage, next_action = "version_ready", "upsert_passport"
    else:
        stage, next_action = "passport_ready", "confirm_publish"
    return {
        "track_id": t.id,
        "stage": stage,
        "next_action": next_action,
        "title": t.title,
        "status": t.status,
        "has_version": version is not None,
        "has_passport": passport is not None,
        "version": {
            "id": version.id, "version_no": version.version_no,
            "audio_asset_key": version.audio_asset_key,
        } if version else None,
    }


@router.get("/creators/{creator_id}/drafts")
def creator_drafts(creator_id: str, db: Db, actor_id: str | None = Depends(actor_user_id)):
    """My drafts — draft/archived tracks with derived completion stage."""
    c = _require_owner(db, creator_id, actor_id)
    rows = db.scalars(
        select(Track).where(Track.creator_id == creator_id, Track.status.in_(["draft", "archived"]))
        .order_by(Track.updated_at.desc()).limit(100)
    )
    return {
        "creator_id": creator_id,
        "drafts": [_draft_stage(db, t) for t in rows],
    }


@router.get("/drafts/{track_id}/resume")
def resume_draft(track_id: str, db: Db, actor_id: str | None = Depends(actor_user_id)):
    """Resume state for one draft — server facts decide the next step."""
    t = _get_track(db, track_id)
    _require_owner(db, t.creator_id, actor_id)
    stage = _draft_stage(db, t)
    version = db.get(TrackVersion, t.current_version_id) if t.current_version_id else None
    passport = db.scalar(select(CreationPassport).where(CreationPassport.track_id == track_id))
    media = None
    if version and version.audio_asset_key:
        meta = version.metadata_json or {}
        media = {
            "asset_key": version.audio_asset_key,
            "sha256": meta.get("sha256"),
            "bytes": meta.get("bytes"),
            "mime_type": meta.get("mime_type"),
        }
    return {
        "track": _track_dict(t, version),
        "stage": stage["stage"],
        "next_action": stage["next_action"],
        "media": media,
        "passport": {
            "origin_type": passport.origin_type,
            "generation_tool": passport.generation_tool,
            "generation_model": passport.generation_model,
            "prompt_disclosure": passport.prompt_disclosure,
            "human_editing_notes": passport.human_editing_notes,
            "rights_statement": passport.rights_statement,
        } if passport else None,
    }


@router.post("/drafts/{track_id}/abandon")
def abandon_draft(track_id: str, db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    """Abandon a draft: status -> archived (media untouched, subject to orphan audit)."""
    t = _get_track(db, track_id)
    _require_owner(db, t.creator_id, actor_id)
    if t.status == "published":
        raise error(409, "CANNOT_ABANDON_PUBLISHED", "published tracks cannot be abandoned")
    if t.status == "archived":
        return {"track_id": track_id, "status": "archived", "already": True}
    prev = t.status
    t.status = "archived"
    t.updated_at = utcnow()
    audit.record(db, actor_type="user", actor_id=actor_id or t.creator_id, action="track.abandoned",
                 resource_type="track", resource_id=t.id, request_id=request_id(request), metadata={"from": prev})
    db.commit()
    return {"track_id": track_id, "status": "archived"}


# ============================================================
# MFY_MUSIC_LIBRARY_AND_CREATOR_CONSOLE_001 — creator console
# ============================================================

@router.get("/creators/{creator_id}/tracks")
def creator_tracks(creator_id: str, db: Db, actor_id: str | None = Depends(actor_user_id), status: str | None = None):
    """All tracks for a creator grouped by status (console)."""
    _require_owner(db, creator_id, actor_id)
    cond = [Track.creator_id == creator_id, Track.deleted_at.is_(None)]
    if status:
        if status not in ("draft", "published", "archived", "unlisted"):
            raise error(400, "INVALID_STATUS", "status must be draft/published/archived/unlisted")
        cond.append(Track.status == status)
    rows = db.scalars(select(Track).where(*cond).order_by(Track.updated_at.desc()).limit(200))
    return {
        "creator_id": creator_id,
        "tracks": [
            {
                "id": t.id, "title": t.title, "status": t.status, "visibility": t.visibility,
                "primary_language": t.primary_language, "duration_ms": t.duration_ms,
                "published_at": t.published_at.isoformat() if t.published_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                "stage": _draft_stage(db, t)["stage"],
            }
            for t in rows
        ],
    }


@router.post("/tracks/{track_id}/unpublish")
def unpublish_track(track_id: str, db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    """Take a published track off the public catalogue (-> archived, no deletion)."""
    t = _get_track(db, track_id)
    _require_owner(db, t.creator_id, actor_id)
    if t.status != "published":
        raise error(409, "NOT_PUBLISHED", "only published tracks can be unpublished")
    t.status = "archived"
    t.updated_at = utcnow()
    audit.record(db, actor_type="user", actor_id=actor_id or t.creator_id, action="track.unpublished",
                 resource_type="track", resource_id=t.id, request_id=request_id(request))
    db.commit()
    return {"track_id": track_id, "status": "archived", "public_url_live": False}
