"""Engine/session factory — small pool for the 1.6GB Hangzhou ECS host."""

from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from moodify_music.config import MusicConfig


def make_engine(config: MusicConfig):
    engine = create_engine(
        config.sqlalchemy_url,
        pool_size=config.db_pool_size,
        max_overflow=config.db_max_overflow,
        pool_recycle=config.db_pool_recycle,
        pool_pre_ping=True,
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def _set_utc(dbapi_connection, _record):
        # MySQL DATETIME has no tz; force UTC so now()/CURRENT_TIMESTAMP are UTC.
        cursor = dbapi_connection.cursor()
        cursor.execute("SET time_zone = '+00:00'")
        cursor.close()

    return engine


def make_session_factory(config: MusicConfig) -> sessionmaker[Session]:
    return sessionmaker(bind=make_engine(config), expire_on_commit=False)
