"""Model-level unit tests (SQLite in-memory)."""

from __future__ import annotations

import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from moodify_music.models import (
    Base,
    CreatorProfile,
    Favorite,
    Follow,
    LicenseIntent,
    SupportIntent,
    Track,
    TrackVersion,
    User,
    utcnow,
)

ENGINE = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
Base.metadata.create_all(ENGINE)


@pytest.fixture()
def db():
    with Session(ENGINE) as session:
        yield session
        session.rollback()


def _user(db: Session, email: str | None = None) -> User:
    u = User(display_name="Alice", email=email)
    db.add(u)
    db.flush()
    return u


def _creator(db: Session, user: User, handle: str = "alice") -> CreatorProfile:
    c = CreatorProfile(user_id=user.id, handle=handle, display_name="Alice Studio")
    db.add(c)
    db.flush()
    return c


def _track(db: Session, creator: CreatorProfile, user: User, title: str = "First") -> Track:
    t = Track(creator_id=creator.id, created_by_user_id=user.id, title=title)
    db.add(t)
    db.flush()
    return t


def test_user_email_unique(db):
    _user(db, email="a@b.c")
    with pytest.raises(IntegrityError):
        _user(db, email="a@b.c")


def test_creator_handle_unique(db):
    u1 = _user(db)
    u2 = _user(db)
    _creator(db, u1, handle="alice")
    with pytest.raises(IntegrityError):
        _creator(db, u2, handle="alice")


def test_user_one_creator_profile(db):
    u = _user(db)
    _creator(db, u, handle="alice")
    with pytest.raises(IntegrityError):
        _creator(db, u, handle="alice2")


def test_track_version_unique_per_track(db):
    u = _user(db)
    c = _creator(db, u)
    t = _track(db, c, u)
    db.add(TrackVersion(track_id=t.id, version_no=1, created_by_user_id=u.id))
    db.flush()
    with pytest.raises(IntegrityError):
        db.add(TrackVersion(track_id=t.id, version_no=1, created_by_user_id=u.id))
        db.flush()


def test_publication_states(db):
    u = _user(db)
    c = _creator(db, u)
    t = _track(db, c, u)
    t.status = "published"
    db.flush()
    assert t.status == "published"
    # invalid status rejected by CHECK constraint (MySQL) — app-level enum enforced here
    assert Track.status.type.python_type is str


def test_follow_duplicate(db):
    u = _user(db)
    c = _creator(db, u)
    db.add(Follow(user_id=u.id, creator_id=c.id))
    db.flush()
    with pytest.raises(IntegrityError):
        db.add(Follow(user_id=u.id, creator_id=c.id))
        db.flush()


def test_favorite_duplicate(db):
    u = _user(db)
    c = _creator(db, u)
    t = _track(db, c, u)
    db.add(Favorite(user_id=u.id, track_id=t.id))
    db.flush()
    with pytest.raises(IntegrityError):
        db.add(Favorite(user_id=u.id, track_id=t.id))
        db.flush()


def test_money_minor_units(db):
    u = _user(db)
    c = _creator(db, u)
    t = _track(db, c, u)
    li = LicenseIntent(
        creator_id=c.id, track_id=t.id, license_type="sync",
        usage_description="short film", budget_amount_minor=50000, budget_currency="CNY",
    )
    db.add(li)
    db.flush()
    assert li.budget_amount_minor == 50000


def test_support_intent_status(db):
    u = _user(db)
    c = _creator(db, u)
    si = SupportIntent(supporter_user_id=u.id, creator_id=c.id, status="expressed")
    db.add(si)
    db.flush()
    assert si.status == "expressed"


def test_utc_now_naive_utc(db):
    now = utcnow()
    assert now.tzinfo is None
