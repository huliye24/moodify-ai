"""Invite-only beta sessions for the public Music BFF."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time

COOKIE_NAME = "moodify_music_session"
SESSION_TTL_SECONDS = 12 * 60 * 60


def _secret() -> bytes:
    value = os.environ.get("MOODIFY_BFF_SESSION_SECRET", "")
    return value.encode("utf-8") if len(value) >= 32 else b""


def _invites() -> dict[str, str]:
    try:
        value = json.loads(os.environ.get("MOODIFY_BFF_BETA_INVITES", "{}"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def authenticate_invite(code: str) -> str | None:
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
    for stored_digest, user_id in _invites().items():
        if hmac.compare_digest(digest, stored_digest) and isinstance(user_id, str):
            return user_id
    return None


def issue_session(user_id: str, now: int | None = None) -> str:
    secret = _secret()
    if not secret:
        raise RuntimeError("beta session secret is not configured")
    expires = (now or int(time.time())) + SESSION_TTL_SECONDS
    payload = f"{user_id}.{expires}"
    signature = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_session(token: str | None, now: int | None = None) -> str | None:
    secret = _secret()
    if not token or not secret:
        return None
    try:
        user_id, expires_text, signature = token.rsplit(".", 2)
        expires = int(expires_text)
    except (ValueError, TypeError):
        return None
    payload = f"{user_id}.{expires}"
    expected = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected) or expires <= (now or int(time.time())):
        return None
    return user_id
