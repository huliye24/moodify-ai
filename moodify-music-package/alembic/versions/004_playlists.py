"""004 playlists — additive, backward compatible.

Revision ID: 004_playlists
Revises: 003_cwc_idempotency_audit
Create Date: 2026-08-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "004_playlists"
down_revision = "003_cwc_idempotency_audit"
branch_labels = None
depends_on = None

MYSQL_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}


def upgrade() -> None:
    op.create_table(
        "playlists",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_user_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("visibility", sa.String(16), nullable=False, server_default="private"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("visibility IN ('private','public')", name="ck_playlists_visibility"),
        sa.Index("ix_playlists_owner", "owner_user_id"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "playlist_items",
        sa.Column("playlist_id", sa.String(36), primary_key=True),
        sa.Column("track_id", sa.String(36), primary_key=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("added_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Index("ix_playlist_items_track", "track_id"),
        **MYSQL_ARGS,
    )


def downgrade() -> None:
    op.drop_table("playlist_items")
    op.drop_table("playlists")
