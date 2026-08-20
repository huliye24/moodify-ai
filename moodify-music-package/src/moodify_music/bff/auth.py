"""BFF session & invite helpers — MFY_PLATFORM_IDENTITY_ACCESS_PRIVACY_001.

The BFF never owns session authority: it issues opaque tokens that the data
API validates against the auth_sessions store (server-side revocation). The
raw token appears only in the HttpOnly cookie; nothing here logs it.

CSRF uses double-submit: a non-HttpOnly `moodify_csrf` cookie is mirrored to
the `X-CSRF-Token` header by the web client on state-changing requests.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets

COOKIE_NAME = "moodify_music_session"
CSRF_COOKIE_NAME = "moodify_csrf"
SESSION_TTL_SECONDS = 12 * 60 * 60


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


def issue_session(_user_id: str, _now: int | None = None) -> str:
    """Opaque token; the data API stores only its SHA-256 hash."""
    return secrets.token_urlsafe(32)


def csrf_token() -> str:
    """Double-submit CSRF token for the non-HttpOnly mirror cookie."""
    return secrets.token_urlsafe(24)


def csrf_valid(cookie_value: str | None, header_value: str | None) -> bool:
    if not cookie_value or not header_value:
        return False
    return hmac.compare_digest(cookie_value, header_value)
