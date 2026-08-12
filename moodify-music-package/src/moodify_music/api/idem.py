"""Idempotency-Key helper for internal data API writes."""

from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from moodify_music.idempotency import IdempotencyConflict, begin, finish, replay

IDEMPOTENT_SCOPES = {
    "create_user", "create_creator", "create_track", "create_version", "publish",
    "create_album", "follow", "unfollow", "favorite", "unfavorite",
    "license_intent", "support_intent", "cwc_mutation",
}


def request_id(request: Request) -> str:
    return request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16]


def _payload_hash(payload: Any) -> str:
    import hashlib

    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def idempotent_write(
    db: Session,
    request: Request,
    scope: str,
    payload: Any,
    *,
    response: dict | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    status_code: int = 201,
):
    """Run a critical write inside idempotency guard; returns (row, replayed: bool).

    Raises ApiError 409 on same-key-different-payload.
    """
    from moodify_music.api.deps import error

    key = request.headers.get("Idempotency-Key", "")
    if not key:
        # still run, but not idempotent — callers must send a key
        return None, False
    try:
        row = begin(db, scope, key, _payload_hash(payload))
    except IdempotencyConflict:
        raise error(409, "IDEMPOTENCY_CONFLICT", "Idempotency-Key was already used with different payload")
    if replay(row) is not None:
        return row, True
    finish(
        db, row, status_code, response,
        resource_type=resource_type, resource_id=resource_id,
    )
    return row, False


def replay_response(row) -> JSONResponse | None:
    if row is None:
        return None
    result = replay(row)
    if result is None:
        return None
    status, body = result
    return JSONResponse(status_code=status, content=body)
