"""Shared test DB + app override — prevents cross-file dependency-override pollution."""

from __future__ import annotations

import os

os.environ.setdefault("MOODIFY_INTERNAL_API_KEY", "test-service-key")

from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from moodify_music import models as M
from moodify_music.api.deps import get_db
from moodify_music.api.main import app

ENGINE = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
M.Base.metadata.create_all(ENGINE)


def _override_db():
    with Session(ENGINE) as session:
        yield session


app.dependency_overrides[get_db] = _override_db
