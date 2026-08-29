"""Platform identity service — server-side sessions with revocation.

MFY_PLATFORM_IDENTITY_ACCESS_PRIVACY_001. Sessions are authoritative in the
data API (Hangzhou); the BFF only holds an opaque cookie. The raw token is
issued exactly once; storage and logs keep only its SHA-256 hash.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from moodify_music.api.deps import ApiError
from moodify_music.models import AuthSession, User, new_id, utcnow

DEFAULT_TTL_SECONDS = 12 * 60 * 60


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _user_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "status": user.status,
        "locale": user.locale,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def ensure_user(db: Session, user_id: str, display_name: str | None = None) -> User:
    """Idempotent user creation — migration from invite/demo identity.

    Never silently claims an existing user for a new owner: if the user_id
    exists it is returned as-is; a new row is created only when the id is
    unknown and display_name is provided.
    """
    user = db.get(User, user_id)
    if user is not None:
        return user
    if not display_name:
        raise ApiError(422, "DISPLAY_NAME_REQUIRED", "a display name is required to create a user")
    user = User(id=user_id, display_name=display_name[:120], status="active")
    db.add(user)
    db.flush()
    return user


def create_session(db: Session, user_id: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> tuple[str, AuthSession]:
    token = secrets.token_urlsafe(32)
    now = utcnow()
    session = AuthSession(
        id=new_id(),
        token_hash=_hash(token),
        user_id=user_id,
        created_from="invite",
        expires_at=now + timedelta(seconds=ttl_seconds),
        last_seen_at=now,
    )
    db.add(session)
    db.flush()
    return token, session


def resolve_session(db: Session, token: str | None) -> User | None:
    """Server-authoritative actor resolution; None on absent/expired/revoked."""
    if not token:
        return None
    row = db.scalar(select(AuthSession).where(AuthSession.token_hash == _hash(token)))
    if row is None:
        return None
    now = utcnow()
    if row.revoked_at is not None or row.expires_at <= now:
        return None
    if row.last_seen_at is None or now - row.last_seen_at > timedelta(minutes=5):
        row.last_seen_at = now
    user = db.get(User, row.user_id)
    if user is None or user.deleted_at is not None or user.status != "active":
        return None
    return user


def revoke_session(db: Session, token: str | None) -> bool:
    if not token:
        return False
    row = db.scalar(select(AuthSession).where(AuthSession.token_hash == _hash(token)))
    if row is None:
        return False
    if row.revoked_at is None:
        row.revoked_at = utcnow()
    return True
