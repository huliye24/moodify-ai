"""Shared API dependencies — service auth, session, error model."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from moodify_music.config import MusicConfig
from moodify_music.db import make_session_factory

config = MusicConfig.from_env()
session_factory = make_session_factory(config)


def get_db():
    with session_factory() as session:
        yield session


Db = Annotated[Session, Depends(get_db)]


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def error(status: int, code: str, message: str) -> ApiError:
    return ApiError(status, code, message)


def service_key_required(
    x_moodify_service_key: Annotated[str, Header()] = "",
    authorization: Annotated[str, Header()] = "",
) -> None:
    key = config.internal_api_key
    if not key:
        return  # local/dev: auth disabled
    if x_moodify_service_key == key or authorization == f"Bearer {key}":
        return
    raise ApiError(401, "SERVICE_KEY_REQUIRED", "valid service credential required")


def actor_user_id(
    x_moodify_actor_user_id: Annotated[str, Header()] = "",
) -> str | None:
    return x_moodify_actor_user_id or None


def require_actor_matches(actor_id: str | None, user_id: str) -> None:
    if not actor_id:
        raise error(401, "ACTOR_REQUIRED", "authenticated actor required")
    if actor_id != user_id:
        raise error(403, "OWNERSHIP_DENIED", "actor does not match requested user")


class NotFound(ApiError):
    pass


def require_id(value: str | None, what: str) -> str:
    if not value:
        raise error(400, "VALIDATION_ERROR", f"{what} is required")
    return value
