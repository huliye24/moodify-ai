"""001 identity / creator / catalog tables.

Revision ID: 001_identity_creator_catalog
Revises:
Create Date: 2026-08-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "001_identity_creator_catalog"
down_revision = None
branch_labels = None
depends_on = None

MYSQL_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("auth_subject", sa.String(255), nullable=True),
        sa.Column("email", sa.String(320), nullable=True),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("locale", sa.String(16), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("auth_subject", name="uq_users_auth_subject"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "creator_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, unique=True),
        sa.Column("handle", sa.String(64), nullable=False, unique=True),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("bio", sa.String(2000), nullable=True),
        sa.Column("avatar_asset_key", sa.String(512), nullable=True),
        sa.Column("banner_asset_key", sa.String(512), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        **MYSQL_ARGS,
    )
    op.create_table(
        "tracks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("creator_id", sa.String(36), nullable=False),
        sa.Column("created_by_user_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("slug", sa.String(200), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("visibility", sa.String(16), nullable=False, server_default="public"),
        sa.Column("primary_language", sa.String(16), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("cover_asset_key", sa.String(512), nullable=True),
        sa.Column("current_version_id", sa.String(36), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("ear_production_case_ref", sa.String(128), nullable=True),
        sa.Column("approved_evidence_ref", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("status IN ('draft','published','unlisted','archived')", name="ck_tracks_status"),
        sa.Index("ix_tracks_creator_status", "creator_id", "status"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "track_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("track_id", sa.String(36), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("audio_asset_key", sa.String(512), nullable=True),
        sa.Column("lyrics_text", sa.String(20000), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_by_user_id", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("track_id", "version_no", name="uq_track_versions"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "creation_passports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("track_id", sa.String(36), nullable=False),
        sa.Column("track_version_id", sa.String(36), nullable=True),
        sa.Column("origin_type", sa.String(32), nullable=True),
        sa.Column("generation_tool", sa.String(128), nullable=True),
        sa.Column("generation_model", sa.String(128), nullable=True),
        sa.Column("generation_model_version", sa.String(64), nullable=True),
        sa.Column("prompt_disclosure", sa.String(16), nullable=True, server_default="private"),
        sa.Column("lyrics_author_type", sa.String(32), nullable=True),
        sa.Column("human_editing_notes", sa.String(4000), nullable=True),
        sa.Column("rights_statement", sa.String(4000), nullable=True),
        sa.Column("commercial_use_claim", sa.String(4000), nullable=True),
        sa.Column("source_metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Index("ix_passports_track", "track_id"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "albums",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("creator_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.String(4000), nullable=True),
        sa.Column("cover_asset_key", sa.String(512), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        **MYSQL_ARGS,
    )
    op.create_table(
        "album_tracks",
        sa.Column("album_id", sa.String(36), primary_key=True),
        sa.Column("track_id", sa.String(36), primary_key=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("added_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        **MYSQL_ARGS,
    )


def downgrade() -> None:
    op.drop_table("album_tracks")
    op.drop_table("albums")
    op.drop_table("creation_passports")
    op.drop_table("track_versions")
    op.drop_table("tracks")
    op.drop_table("creator_profiles")
    op.drop_table("users")
