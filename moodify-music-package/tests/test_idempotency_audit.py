"""Idempotency and audit unit tests (SQLite in-memory)."""

from __future__ import annotations

import pytest
from sqlalchemy import StaticPool, create_engine, select
from sqlalchemy.orm import Session

from moodify_music.audit import record
from moodify_music.idempotency import IdempotencyConflict, begin, finish, replay
from moodify_music.models import AuditEvent, Base

ENGINE = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
Base.metadata.create_all(ENGINE)


@pytest.fixture()
def db():
    with Session(ENGINE) as session:
        yield session
        session.rollback()


def test_idempotency_same_key_same_payload(db):
    k1 = begin(db, "license_intents", "key-1", "hash-a")
    finish(db, k1, 201, {"id": "x1"}, "license_intent", "x1")
    db.commit()
    db.expire_all()
    k2 = begin(db, "license_intents", "key-1", "hash-a")
    assert replay(k2) == (201, {"id": "x1"})


def test_idempotency_conflict_different_payload(db):
    begin(db, "license_intents", "key-2", "hash-a")
    db.commit()
    with pytest.raises(IdempotencyConflict):
        begin(db, "license_intents", "key-2", "hash-b")


def test_audit_redaction(db):
    record(
        db,
        actor_type="user", actor_id="u1", action="track.created",
        resource_type="track", resource_id="t1",
        metadata={"title": "ok", "prompt": "secret prompt"},
    )
    db.commit()
    ev = db.scalar(select(AuditEvent))
    assert ev.metadata_json["title"] == "ok"
    assert ev.metadata_json["prompt"].startswith("<redacted")


def test_audit_key_actions(db):
    for action in ["user.created", "track.published", "license_intent.created", "cwc.changed"]:
        record(db, actor_type="user", actor_id="u1", action=action, resource_type="x", resource_id=None)
    db.commit()
    actions = {a for (a,) in db.execute(select(AuditEvent.action))}
    assert {"user.created", "track.published", "license_intent.created", "cwc.changed"} <= actions
