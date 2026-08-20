"""Ear↔Music evidence bridge — MFY_EAR_MUSIC_EVIDENCE_BRIDGE_001.

Exchange states (never Ear case or Music publication authority):
  requested -> processing -> evidence_ready -> human_reviewed
             -> optionally_attached (creator decision)
  terminal: cancelled / failed / inconclusive

Rules:
- requests are idempotent (request_key); retries replay the existing record
- only the track owner may request/attach/detach
- attachment requires publish_safe + a review policy pass
- detach keeps the Ear evidence and the full audit trail
- Ear internal measurements are never copied here as authority
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select

from moodify_music import audit
from moodify_music.api.deps import Db, actor_user_id, error, require_actor_matches, service_key_required
from moodify_music.api.idem import request_id
from moodify_music.models import EvidenceBridge, Track, TrackVersion, new_id

router = APIRouter(prefix="/internal/v1/music/bridge", dependencies=[Depends(service_key_required)])

EXCHANGE_ORDER = ["requested", "processing", "evidence_ready", "human_reviewed", "optionally_attached"]
TERMINAL = {"cancelled", "failed", "inconclusive"}


def _bridge_dict(b: EvidenceBridge) -> dict:
    return {
        "id": b.id,
        "request_key": b.request_key,
        "track_id": b.track_id,
        "version_id": b.version_id,
        "asset_ref": b.asset_ref,
        "asset_sha256": b.asset_sha256,
        "ear_case_ref": b.ear_case_ref,
        "exchange_status": b.exchange_status,
        "approved_evidence_ref": b.approved_evidence_ref,
        "authority_state": b.authority_state,
        "publish_safe": b.publish_safe,
        "reviewed_at": b.reviewed_at.isoformat() if b.reviewed_at else None,
        "reviewer": b.reviewer,
        "failure_code": b.failure_code,
        "attached": b.attached,
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "updated_at": b.updated_at.isoformat() if b.updated_at else None,
    }


def _monotonic(next_status: str, current: str) -> bool:
    if current in TERMINAL:
        return False
    if next_status in TERMINAL:
        return True
    return EXCHANGE_ORDER.index(next_status) > EXCHANGE_ORDER.index(current)


@router.post("/requests", status_code=201)
def create_request(db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    track_id = str(body.get("track_id") or "")
    user_id = str(body.get("user_id") or actor_id or "")
    request_key = str(body.get("request_key") or "")
    asset_sha256 = str(body.get("asset_sha256") or "")
    if not track_id or not user_id or not request_key:
        raise error(422, "BRIDGE_FIELDS_REQUIRED", "track_id, user_id and request_key are required")

    existing = db.scalar(select(EvidenceBridge).where(EvidenceBridge.request_key == request_key))
    if existing is not None:
        if existing.track_id != track_id or existing.user_id != user_id:
            raise error(409, "REQUEST_KEY_REUSED", "request_key is already bound to another request")
        return {"bridge": _bridge_dict(existing), "replayed": True}

    track = db.get(Track, track_id)
    if track is None or track.deleted_at is not None:
        raise error(404, "RESOURCE_NOT_FOUND", "track not found")
    require_actor_matches(actor_id, track.created_by_user_id)
    version = db.get(TrackVersion, str(body.get("version_id") or ""))
    if version is None:
        raise error(404, "RESOURCE_NOT_FOUND", "track version not found")
    version_meta = version.metadata_json or {}
    recorded_hash = version_meta.get("sha256")
    if recorded_hash and asset_sha256 and recorded_hash != asset_sha256:
        raise error(409, "ASSET_HASH_MISMATCH", "asset sha256 does not match the version record")
    if not asset_sha256 and not recorded_hash:
        raise error(422, "ASSET_HASH_REQUIRED", "asset sha256 is required")

    bridge = EvidenceBridge(
        id=new_id(),
        request_key=request_key,
        user_id=user_id,
        creator_id=track.creator_id,
        track_id=track_id,
        version_id=version.id,
        asset_ref=str(body.get("asset_ref") or version.audio_asset_key or ""),
        asset_sha256=asset_sha256 or recorded_hash,
        exchange_status="requested",
    )
    db.add(bridge)
    db.flush()
    audit.record(db, actor_type="user", actor_id=user_id, action="bridge.requested",
                 resource_type="evidence_bridge", resource_id=bridge.id, request_id=request_id(request))
    db.commit()
    return {"bridge": _bridge_dict(bridge)}


@router.get("/requests/{bridge_id}")
def get_request(bridge_id: str, db: Db):
    bridge = db.get(EvidenceBridge, bridge_id)
    if bridge is None:
        raise error(404, "RESOURCE_NOT_FOUND", "bridge request not found")
    return {"bridge": _bridge_dict(bridge)}


@router.get("/requests/by-track/{track_id}")
def requests_for_track(track_id: str, db: Db):
    rows = db.scalars(select(EvidenceBridge).where(EvidenceBridge.track_id == track_id).order_by(EvidenceBridge.created_at.desc())).all()
    return {"bridges": [_bridge_dict(b) for b in rows], "count": len(rows)}


@router.post("/requests/{bridge_id}/update")
def update_request(bridge_id: str, db: Db, request: Request, body: dict):
    """Ear-side status report (service-to-service). Monotonic transitions only."""
    bridge = db.get(EvidenceBridge, bridge_id)
    if bridge is None:
        raise error(404, "RESOURCE_NOT_FOUND", "bridge request not found")
    next_status = str(body.get("exchange_status") or "")
    if not next_status:
        raise error(422, "EXCHANGE_STATUS_REQUIRED", "exchange_status is required")
    if not _monotonic(next_status, bridge.exchange_status):
        raise error(409, "EXCHANGE_STATE_CONFLICT", f"cannot move {bridge.exchange_status} -> {next_status}")
    bridge.exchange_status = next_status
    if "ear_case_ref" in body:
        bridge.ear_case_ref = str(body["ear_case_ref"])[:128]
    if "approved_evidence_ref" in body:
        bridge.approved_evidence_ref = str(body["approved_evidence_ref"])[:128] or None
    if "authority_state" in body:
        bridge.authority_state = str(body["authority_state"])[:24] or None
    if "publish_safe" in body:
        bridge.publish_safe = bool(body["publish_safe"])
    if "reviewed_at" in body and body["reviewed_at"]:
        try:
            bridge.reviewed_at = datetime.fromisoformat(str(body["reviewed_at"]))
        except ValueError:
            raise error(422, "REVIEWED_AT_INVALID", "reviewed_at must be ISO8601") from None
    if "reviewer" in body:
        bridge.reviewer = str(body["reviewer"])[:120] or None
    if "failure_code" in body:
        bridge.failure_code = str(body["failure_code"])[:64] or None
    audit.record(db, actor_type="service", actor_id="ear-service", action=f"bridge.{next_status}",
                 resource_type="evidence_bridge", resource_id=bridge.id, request_id=request_id(request))
    db.commit()
    return {"bridge": _bridge_dict(bridge)}


@router.post("/requests/{bridge_id}/attach")
def attach(bridge_id: str, db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    bridge = db.get(EvidenceBridge, bridge_id)
    if bridge is None:
        raise error(404, "RESOURCE_NOT_FOUND", "bridge request not found")
    require_actor_matches(actor_id, bridge.user_id)
    if bridge.exchange_status not in ("human_reviewed", "optionally_attached"):
        raise error(409, "EXCHANGE_NOT_REVIEWED", "evidence must be human-reviewed before attach")
    if not bridge.publish_safe or not bridge.approved_evidence_ref:
        raise error(403, "EVIDENCE_NOT_PUBLISH_SAFE", "only publish-safe, approved evidence may attach")
    bridge.attached = True
    bridge.exchange_status = "optionally_attached"
    track = db.get(Track, bridge.track_id)
    if track is not None:
        track.approved_evidence_ref = bridge.approved_evidence_ref
        track.ear_production_case_ref = bridge.ear_case_ref
    audit.record(db, actor_type="user", actor_id=bridge.user_id, action="bridge.attached",
                 resource_type="evidence_bridge", resource_id=bridge.id, request_id=request_id(request))
    db.commit()
    return {"bridge": _bridge_dict(bridge)}


@router.post("/requests/{bridge_id}/detach")
def detach(bridge_id: str, db: Db, request: Request, body: dict, actor_id: str | None = Depends(actor_user_id)):
    bridge = db.get(EvidenceBridge, bridge_id)
    if bridge is None:
        raise error(404, "RESOURCE_NOT_FOUND", "bridge request not found")
    require_actor_matches(actor_id, bridge.user_id)
    bridge.attached = False
    track = db.get(Track, bridge.track_id)
    if track is not None:
        track.approved_evidence_ref = None  # display only; Ear evidence retained
    # exchange record + Ear evidence + review audit are never deleted
    audit.record(db, actor_type="user", actor_id=bridge.user_id, action="bridge.detached",
                 resource_type="evidence_bridge", resource_id=bridge.id, request_id=request_id(request))
    db.commit()
    return {"bridge": _bridge_dict(bridge)}


@router.post("/requests/{bridge_id}/cancel")
def cancel(bridge_id: str, db: Db, body: dict):
    bridge = db.get(EvidenceBridge, bridge_id)
    if bridge is None:
        raise error(404, "RESOURCE_NOT_FOUND", "bridge request not found")
    if bridge.exchange_status in TERMINAL:
        raise error(409, "EXCHANGE_STATE_CONFLICT", "already terminal")
    bridge.exchange_status = "cancelled"
    db.commit()
    return {"bridge": _bridge_dict(bridge)}
