"""003 cwc / idempotency / audit tables.

Revision ID: 003_cwc_idempotency_audit
Revises: 002_relationships_intents
Create Date: 2026-08-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "003_cwc_idempotency_audit"
down_revision = "002_relationships_intents"
branch_labels = None
depends_on = None

MYSQL_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}


def upgrade() -> None:
    op.create_table(
        "cwc_accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, unique=True),
        sa.Column("balance_units", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        **MYSQL_ARGS,
    )
    op.create_table(
        "cwc_ledger",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("account_id", sa.String(36), nullable=False),
        sa.Column("delta_units", sa.BigInteger(), nullable=False),
        sa.Column("reason", sa.String(128), nullable=False),
        sa.Column("reference_type", sa.String(64), nullable=True),
        sa.Column("reference_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Index("ix_cwc_ledger_account", "account_id"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.Column("response_body_json", sa.JSON(), nullable=True),
        sa.Column("resource_type", sa.String(64), nullable=True),
        sa.Column("resource_id", sa.String(64), nullable=True),
        sa.Column("state", sa.String(16), nullable=False, server_default="started"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("scope", "idempotency_key", name="uq_idempotency"),
        **MYSQL_ARGS,
    )
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("actor_type", sa.String(32), nullable=False),
        sa.Column("actor_id", sa.String(36), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", sa.String(64), nullable=True),
        sa.Column("request_id", sa.String(64), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Index("ix_audit_events_resource", "resource_type", "resource_id"),
        sa.Index("ix_audit_events_created", "created_at"),
        **MYSQL_ARGS,
    )


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("idempotency_keys")
    op.drop_table("cwc_ledger")
    op.drop_table("cwc_accounts")
