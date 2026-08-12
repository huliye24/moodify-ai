"""Alembic environment — reads DSN from MOODIFY_DB_* env vars.

Migration runs with a dedicated migration identity (moodify_migration),
not the runtime identity (moodify_app).
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import create_engine

from alembic import context

from moodify_music import models as music_models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = music_models.Base.metadata


def _dsn() -> str:
    override = os.environ.get("MOODIFY_DB_URL", "")
    if override:
        return override
    host = os.environ.get("MOODIFY_DB_HOST", "127.0.0.1")
    port = os.environ.get("MOODIFY_DB_PORT", "3306")
    user = os.environ.get("MOODIFY_DB_USER", "moodify_migration")
    password = os.environ.get("MOODIFY_DB_PASSWORD", "")
    name = os.environ.get("MOODIFY_DB_NAME", "moodify_dev")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"


def run_migrations_offline() -> None:
    context.configure(
        url=_dsn(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # session time zone = UTC so CURRENT_TIMESTAMP defaults store UTC
    connectable = create_engine(
        _dsn(),
        pool_pre_ping=True,
        connect_args={"init_command": "SET time_zone = '+00:00'"},
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
