#!/usr/bin/env python3
"""Schema/migration dry-run — MFY_RELEASE_CANDIDATE_INTEGRITY_001.

Renders the canonical SQLAlchemy metadata to SQL text WITHOUT touching any
database (true dry-run), asserts the frozen table set and key columns exist,
and prints the table manifest. Re-runnable in any clean environment.

Usage: python ops/schema_dry_run.py   (run from repo root; moodify_music importable)
Exit: 0 = schema manifest complete; 1 = missing tables/columns.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "moodify-music-package" / "src"))

from sqlalchemy.schema import CreateTable  # noqa: E402

from moodify_music import models as M  # noqa: E402

# frozen table set (data-foundation baseline + 51/52 increments) — verified
# against models.py __tablename__ manifest by this script
REQUIRED_TABLES = {
    "users", "creator_profiles", "tracks", "track_versions", "albums",
    "album_tracks", "creation_passports", "favorites", "follows", "play_events",
    "license_intents", "support_intents", "cwc_accounts", "cwc_ledger",
    "playlists", "playlist_items", "audit_events", "idempotency_keys",
    "auth_sessions", "user_roles", "evidence_bridge",
}

KEY_COLUMNS = {
    "users": {"id", "auth_subject"},
    "tracks": {"id", "creator_id", "status", "current_version_id", "approved_evidence_ref"},
    "track_versions": {"id", "track_id", "version_no", "audio_asset_key"},
    "auth_sessions": {"id", "token_hash", "user_id", "revoked_at"},
    "evidence_bridge": {"id", "request_key", "exchange_status", "publish_safe"},
    "creation_passports": {"track_id", "origin_type"},
}


def main() -> int:
    tables = {t.name for t in M.Base.metadata.sorted_tables}
    missing_tables = sorted(REQUIRED_TABLES - tables)
    if missing_tables:
        print(f"SCHEMA-DRY-RUN: missing tables: {missing_tables}")
        return 1

    missing_cols = []
    for table, cols in KEY_COLUMNS.items():
        actual = {c.name for c in M.Base.metadata.tables[table].columns}
        for col in cols - actual:
            missing_cols.append(f"{table}.{col}")

    if missing_cols:
        print(f"SCHEMA-DRY-RUN: missing columns: {missing_cols}")
        return 1

    print(f"SCHEMA-DRY-RUN: {len(tables)} tables rendered (no database touched)")
    print("table manifest:")
    for t in M.Base.metadata.sorted_tables:
        print(f"  {t.name} ({len(t.columns)} cols)")
    sql = "\n".join(str(CreateTable(t).compile(dialect=None)) for t in M.Base.metadata.sorted_tables)
    print(f"SCHEMA-DRY-RUN: SQL rendered {len(sql)} chars, {sql.count('CREATE TABLE')} CREATE TABLE statements")
    print("SCHEMA-DRY-RUN: PASS — frozen table set and key columns verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
