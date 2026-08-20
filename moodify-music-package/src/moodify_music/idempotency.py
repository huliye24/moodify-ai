"""Idempotency-Key handling for critical writes (Rev.2 Phase E)."""

from __future__ import annotations

import hashlib
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from moodify_music.models import IdempotencyKey, utcnow

DEFAULT_TTL = timedelta(hours=24)


def _hash(payload: dict | list | None) -> str:
    import json

    blob = json.dumps(payload if payload is not None else {}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def begin(db: Session, scope: str, key: str, request_hash: str) -> IdempotencyKey:
    row = db.scalar(select(IdempotencyKey).where(
        IdempotencyKey.scope == scope,
        IdempotencyKey.idempotency_key == key,
    ))
    if row is not None:
        if row.request_hash != request_hash:
            raise IdempotencyConflict(key)
        return row
    row = IdempotencyKey(scope=scope, idempotency_key=key, request_hash=request_hash)
    db.add(row)
    try:
        db.flush()
    except IntegrityError:
        # Concurrent request claimed the same key first (uq_idempotency).
        # MFY_PRODUCTION_DATA_PLANE_001: replay the winner instead of failing.
        db.rollback()
        row = db.scalar(select(IdempotencyKey).where(
            IdempotencyKey.scope == scope,
            IdempotencyKey.idempotency_key == key,
        ))
        if row is None:
            raise
        if row.request_hash != request_hash:
            raise IdempotencyConflict(key)
    return row


def finish(
    db: Session,
    row: IdempotencyKey,
    status: int,
    body: dict | None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    ttl: timedelta = DEFAULT_TTL,
) -> None:
    row.response_status = status
    row.response_body_json = body
    row.resource_type = resource_type
    row.resource_id = resource_id
    row.state = "completed"
    row.expires_at = utcnow() + ttl
    db.flush()


def replay(row: IdempotencyKey) -> tuple[int, dict | None] | None:
    if row.state == "completed" and row.response_status is not None:
        return row.response_status, row.response_body_json
    return None


class IdempotencyConflict(Exception):
    def __init__(self, key: str):
        super().__init__(f"idempotency conflict for key {key}")
        self.key = key
