"""002 relationships / intents tables.

Revision ID: 002_relationships_intents
Revises: 001_identity_creator_catalog
Create Date: 2026-08-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "002_relationships_intents"
down_revision = "001_identity_creator_catalog"
branch_labels = None
depends_on = None

MYSQL_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}


def upgrade() -> None:
    op.create_table(
        "follows",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("creator_id", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("user_id", "creator_id", name="uq_follows"),
        sa.Index("ix_follows_creator", "creator_id"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "favorites",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("track_id", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("user_id", "track_id", name="uq_favorites"),
        sa.Index("ix_favorites_track", "track_id"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "play_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("track_id", sa.String(36), nullable=False),
        sa.Column("session_id", sa.String(64), nullable=True),
        sa.Column("played_ms", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Index("ix_play_events_track_created", "track_id", "created_at"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "license_intents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("requester_user_id", sa.String(36), nullable=True),
        sa.Column("requester_name", sa.String(120), nullable=True),
        sa.Column("requester_email", sa.String(320), nullable=True),
        sa.Column("creator_id", sa.String(36), nullable=False),
        sa.Column("track_id", sa.String(36), nullable=False),
        sa.Column("license_type", sa.String(64), nullable=False),
        sa.Column("usage_description", sa.String(4000), nullable=False),
        sa.Column("territory", sa.String(128), nullable=True),
        sa.Column("term_description", sa.String(1000), nullable=True),
        sa.Column("budget_amount_minor", sa.BigInteger(), nullable=True),
        sa.Column("budget_currency", sa.String(3), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="submitted"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(
            "status IN ('submitted','reviewing','contacted','accepted','declined','closed')",
            name="ck_license_intents_status",
        ),
        sa.Index("ix_license_intents_creator_status", "creator_id", "status"),
        sa.Index("ix_license_intents_track", "track_id"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "support_intents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("supporter_user_id", sa.String(36), nullable=True),
        sa.Column("creator_id", sa.String(36), nullable=False),
        sa.Column("track_id", sa.String(36), nullable=True),
        sa.Column("amount_minor", sa.BigInteger(), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("message", sa.String(2000), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="expressed"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(
            "status IN ('expressed','contact_requested','cancelled')",
            name="ck_support_intents_status",
        ),
        sa.Index("ix_support_intents_creator", "creator_id"),
        **MYSQL_ARGS,
    )


def downgrade() -> None:
    op.drop_table("support_intents")
    op.drop_table("license_intents")
    op.drop_table("play_events")
    op.drop_table("favorites")
    op.drop_table("follows")
