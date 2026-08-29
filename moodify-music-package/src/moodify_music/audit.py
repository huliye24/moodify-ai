"""Audit events — key state changes only, secrets redacted by policy."""

from __future__ import annotations

from sqlalchemy.orm import Session

from moodify_music.models import AuditEvent

FORBIDDEN_KEYS = {"password", "token", "authorization", "prompt", "secret", "api_key", "path"}


def _redact(metadata: dict | None) -> dict | None:
    if metadata is None:
        return None
    return {
        k: (f"<redacted-{k}>" if any(f in k.lower() for f in FORBIDDEN_KEYS) else v)
        for k, v in metadata.items()
    }


def record(
    db: Session,
    *,
    actor_type: str,
    actor_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None,
    request_id: str | None = None,
    metadata: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        request_id=request_id,
        metadata_json=_redact(metadata),
    )
    db.add(event)
    db.flush()
    return event
