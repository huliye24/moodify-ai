"""Runtime configuration from environment — pattern mirrors moodify.node.config."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MusicConfig:
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    internal_api_key: str
    db_pool_size: int = 2
    db_max_overflow: int = 2
    db_pool_recycle: int = 1800

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    @classmethod
    def from_env(cls) -> "MusicConfig":
        return cls(
            db_host=os.environ.get("MOODIFY_DB_HOST", "127.0.0.1"),
            db_port=int(os.environ.get("MOODIFY_DB_PORT", "3306")),
            db_user=os.environ.get("MOODIFY_DB_USER", "moodify_app"),
            db_password=os.environ.get("MOODIFY_DB_PASSWORD", ""),
            db_name=os.environ.get("MOODIFY_DB_NAME", "moodify_dev"),
            internal_api_key=os.environ.get("MOODIFY_INTERNAL_API_KEY", ""),
            db_pool_size=int(os.environ.get("MOODIFY_DB_POOL_SIZE", "2")),
            db_max_overflow=int(os.environ.get("MOODIFY_DB_MAX_OVERFLOW", "2")),
            db_pool_recycle=int(os.environ.get("MOODIFY_DB_POOL_RECYCLE", "1800")),
        )
