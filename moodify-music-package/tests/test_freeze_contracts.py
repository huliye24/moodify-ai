"""Quarterly freeze guards — MFY_QUARTERLY_RELEASE_FREEZE_001.

Machine checks that the frozen contract surfaces did not drift: schema table
set, uniqueness constraints, exchange-state enumeration, BFF route inventory,
environment variable names, error model shape. Any breaking change trips a
guard immediately — freeze is enforced, not just documented.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

os.environ["MOODIFY_INTERNAL_API_KEY"] = "test-service-key"

from fastapi.testclient import TestClient  # noqa: E402

from moodify_music import models as M  # noqa: E402
from moodify_music.api.main import app as internal_app  # noqa: E402
from moodify_music.bff.main import app  # noqa: E402  (public BFF route inventory)

SRC = Path(__file__).resolve().parent.parent / "src" / "moodify_music"

# ---------------------------------------------------------- schema surface

FROZEN_TABLE_SET = {
    "users", "auth_sessions", "evidence_bridge", "user_roles",
    "creator_profiles", "tracks", "track_versions", "creation_passports",
    "albums", "album_tracks", "follows", "favorites", "play_events",
    "license_intents", "support_intents", "cwc_accounts", "cwc_ledger",
    "idempotency_keys", "audit_events", "playlists", "playlist_items",
}


def test_schema_table_set_is_frozen():
    actual = {t.name for t in M.Base.metadata.sorted_tables}
    assert actual == FROZEN_TABLE_SET, f"schema drifted: {actual ^ FROZEN_TABLE_SET}"


def test_idempotency_unique_constraint_is_frozen():
    table = M.Base.metadata.tables["idempotency_keys"]
    constraints = {str(c.name) for c in table.constraints}
    assert "uq_idempotency" in constraints, "idempotency uniqueness constraint removed"


def test_exchange_state_enumeration_is_frozen():
    table = M.Base.metadata.tables["evidence_bridge"]
    check = next(c for c in table.constraints if c.name == "ck_bridge_exchange_status")
    sql = str(check.sqltext)
    for state in ("requested", "processing", "evidence_ready", "human_reviewed",
                  "optionally_attached", "cancelled", "failed", "inconclusive"):
        assert state in sql, f"exchange state {state} missing from constraint"


def test_track_status_enumeration_is_frozen():
    table = M.Base.metadata.tables["tracks"]
    check = next(c for c in table.constraints if c.name == "ck_tracks_status")
    sql = str(check.sqltext)
    for state in ("draft", "published", "unlisted", "archived"):
        assert state in sql, f"track status {state} missing"


# ---------------------------------------------------------- BFF route inventory

FROZEN_BFF_ROUTES = {
    "/api/v1/music/session",
    "/api/v1/music/bootstrap",
    "/api/v1/music/auth/me",
    "/api/v1/music/catalogue",
    "/api/v1/music/media",
    "/api/v1/music/creators",
    "/api/v1/music/tracks",
    "/api/v1/music/tracks/{track_id}",
    "/api/v1/music/tracks/{track_id}/passport",
    "/api/v1/music/tracks/{track_id}/publish",
    "/api/v1/music/tracks/{track_id}/versions",
    "/api/v1/music/drafts/{track_id}/abandon",
}


def test_bff_route_inventory_is_frozen():
    routes = {r.path for r in app.routes if hasattr(r, "path")}
    missing = FROZEN_BFF_ROUTES - routes
    assert not missing, f"frozen routes missing: {missing}"


# ---------------------------------------------------------- env var names

# MOODIFY_BFF_SESSION_SECRET was removed from the frozen set: the 51 rewrite
# to opaque server-stored tokens left it unread anywhere (dead config). The
# guard would have tripped on it; manifests were updated instead.
FROZEN_ENV_NAMES = {
    "MOODIFY_DB_HOST", "MOODIFY_DB_PORT", "MOODIFY_DB_USER", "MOODIFY_DB_PASSWORD",
    "MOODIFY_DB_NAME", "MOODIFY_INTERNAL_API_KEY", "MOODIFY_DB_POOL_SIZE",
    "MOODIFY_DB_MAX_OVERFLOW", "MOODIFY_DB_POOL_RECYCLE",
    "MOODIFY_HANGZHOU_BASE", "MOODIFY_HANGZHOU_KEY", "MOODIFY_BFF_TIMEOUT",
    "MOODIFY_BFF_AUTH_MODE", "MOODIFY_BFF_CORS_ORIGINS",
    "MOODIFY_BFF_BETA_INVITES", "MOODIFY_BFF_MEDIA_ROOT", "MOODIFY_BFF_DEMO_USER_ID",
}


def test_env_variable_names_are_frozen():
    config_src = (SRC / "config.py").read_text(encoding="utf-8")
    bff_src = (SRC / "bff" / "main.py").read_text(encoding="utf-8")
    bff_auth_src = (SRC / "bff" / "auth.py").read_text(encoding="utf-8")
    bff_media_src = (SRC / "bff" / "media.py").read_text(encoding="utf-8")
    source = config_src + bff_src + bff_auth_src + bff_media_src
    found = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") in ("getenv", "environ"):
            # os.environ.get(...) -> node.func is Attribute with value.id == "environ"
            if getattr(node.func, "value", None) and getattr(node.func.value, "id", "") == "os":
                pass  # handled below via attribute form
        if isinstance(node, ast.Attribute) and node.attr == "get":
            parent = getattr(node, "value", None)
            if getattr(parent, "attr", "") == "environ":
                pass
        # direct os.getenv("X", ...) calls
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "getenv" and node.args:
            if isinstance(node.args[0], ast.Constant):
                found.add(node.args[0].value)
        # os.environ.get("X", ...) / os.getenv("X", ...) attribute form
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("get", "getenv"):
            if node.args and isinstance(node.args[0], ast.Constant):
                found.add(node.args[0].value)
    missing = FROZEN_ENV_NAMES - found
    assert not missing, f"frozen env names not read anywhere: {missing}"


# ---------------------------------------------------------- error model

def test_error_model_shape_is_frozen():
    client = TestClient(internal_app)
    r = client.get("/internal/v1/music/catalogue")  # no service key -> ApiError 401
    assert r.status_code == 401
    body = r.json()
    assert "error" in body and {"code", "message", "request_id"} <= set(body["error"]), body
