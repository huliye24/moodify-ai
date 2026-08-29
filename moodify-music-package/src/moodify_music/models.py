"""Moodify Music canonical data model — Rev.2 (16 tables, utf8mb4, UTC).

Authority: MFY-DATA-FOUNDATION-001-REV2 05_DATA_MODEL_SPEC_REV2.md
All IDs are opaque application-generated UUID strings. Times are UTC.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

ID_LEN = 36


def new_id() -> str:
    return uuid.uuid4().hex[:32]


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp(), onupdate=utcnow
    )


class User(Base, TimestampMixin):
    """Moodify Platform Identity (not Music-only account)."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    auth_subject: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    locale: Mapped[str | None] = mapped_column(String(16), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AuthSession(Base, TimestampMixin):
    """Server-side session with revocation (MFY_PLATFORM_IDENTITY_ACCESS_PRIVACY_001).

    Only the SHA-256 hash of the opaque token is stored; the raw token is
    issued once to the BFF and never persisted or logged.
    """

    __tablename__ = "auth_sessions"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(nullable=False, index=True)
    created_from: Mapped[str] = mapped_column(String(32), nullable=False, default="invite")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class EvidenceBridge(Base, TimestampMixin):
    """Ear↔Music evidence exchange — MFY_EAR_MUSIC_EVIDENCE_BRIDGE_001.

    The bridge owns only the *exchange* state, never Ear measurements or
    Music publication authority. Music never stores Ear internal copies as
    authority; Ear never stores Music publication state.
    """

    __tablename__ = "evidence_bridge"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    request_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(nullable=False)
    track_id: Mapped[str] = mapped_column(nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(nullable=False)
    asset_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    asset_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    ear_case_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    exchange_status: Mapped[str] = mapped_column(String(24), nullable=False, default="requested")
    approved_evidence_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    authority_state: Mapped[str | None] = mapped_column(String(24), nullable=True)
    publish_safe: Mapped[bool] = mapped_column(nullable=False, default=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    failure_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    attached: Mapped[bool] = mapped_column(nullable=False, default=False)

    __table_args__ = (
        CheckConstraint(
            "exchange_status IN ('requested','processing','evidence_ready','human_reviewed',"
            "'optionally_attached','cancelled','failed','inconclusive')",
            name="ck_bridge_exchange_status",
        ),
    )


class UserRole(Base, TimestampMixin):
    """Platform roles independent of Creator status (Ear operator/reviewer etc.).

    Roles are grants, not a parallel identity: a user may hold listener +
    creator-derived + ear_operator roles without owning a second account.
    """

    __tablename__ = "user_roles"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    scope: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "role", "scope", name="uq_user_role_scope"),)


class CreatorProfile(Base, TimestampMixin):
    __tablename__ = "creator_profiles"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    handle: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    avatar_asset_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    banner_asset_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")


class Track(Base, TimestampMixin):
    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    creator_id: Mapped[str] = mapped_column(nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")
    visibility: Mapped[str] = mapped_column(String(16), nullable=False, default="public")
    primary_language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cover_asset_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    current_version_id: Mapped[str | None] = mapped_column(String(ID_LEN), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ear_production_case_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    approved_evidence_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','published','unlisted','archived')",
            name="ck_tracks_status",
        ),
    )


class TrackVersion(Base):
    __tablename__ = "track_versions"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    track_id: Mapped[str] = mapped_column(nullable=False)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    audio_asset_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    lyrics_text: Mapped[str | None] = mapped_column(String(20000), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp()
    )

    __table_args__ = (UniqueConstraint("track_id", "version_no", name="uq_track_versions"),)


class CreationPassport(Base, TimestampMixin):
    """Creator-supplied provenance declaration — NOT copyright certification."""

    __tablename__ = "creation_passports"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    track_id: Mapped[str] = mapped_column(nullable=False)
    track_version_id: Mapped[str | None] = mapped_column(nullable=True)
    origin_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    generation_tool: Mapped[str | None] = mapped_column(String(128), nullable=True)
    generation_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    generation_model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_disclosure: Mapped[str | None] = mapped_column(String(16), nullable=True, default="private")
    lyrics_author_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    human_editing_notes: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    rights_statement: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    commercial_use_claim: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    source_metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Album(Base, TimestampMixin):
    __tablename__ = "albums"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    creator_id: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    cover_asset_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AlbumTrack(Base):
    __tablename__ = "album_tracks"

    album_id: Mapped[str] = mapped_column(primary_key=True)
    track_id: Mapped[str] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    added_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp()
    )


class Follow(Base):
    __tablename__ = "follows"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp()
    )

    __table_args__ = (UniqueConstraint("user_id", "creator_id", name="uq_follows"),)


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(nullable=False)
    track_id: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp()
    )

    __table_args__ = (UniqueConstraint("user_id", "track_id", name="uq_favorites"),)


class PlayEvent(Base):
    __tablename__ = "play_events"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    user_id: Mapped[str | None] = mapped_column(nullable=True)
    track_id: Mapped[str] = mapped_column(nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    played_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp()
    )


class LicenseIntent(Base, TimestampMixin):
    """A real lead, not a license grant or completed sale."""

    __tablename__ = "license_intents"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    requester_user_id: Mapped[str | None] = mapped_column(nullable=True)
    requester_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    requester_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    creator_id: Mapped[str] = mapped_column(nullable=False)
    track_id: Mapped[str] = mapped_column(nullable=False)
    license_type: Mapped[str] = mapped_column(String(64), nullable=False)
    usage_description: Mapped[str] = mapped_column(String(4000), nullable=False)
    territory: Mapped[str | None] = mapped_column(String(128), nullable=True)
    term_description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    budget_amount_minor: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    budget_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="submitted")

    __table_args__ = (
        CheckConstraint(
            "status IN ('submitted','reviewing','contacted','accepted','declined','closed')",
            name="ck_license_intents_status",
        ),
    )


class SupportIntent(Base, TimestampMixin):
    """Support expression — never fabricates paid/settled without real payment."""

    __tablename__ = "support_intents"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    supporter_user_id: Mapped[str | None] = mapped_column(nullable=True)
    creator_id: Mapped[str] = mapped_column(nullable=False)
    track_id: Mapped[str | None] = mapped_column(nullable=True)
    amount_minor: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    message: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="expressed")

    __table_args__ = (
        CheckConstraint(
            "status IN ('expressed','contact_requested','cancelled')",
            name="ck_support_intents_status",
        ),
    )


class CwcAccount(Base, TimestampMixin):
    """Compute credit account — credits are not a currency."""

    __tablename__ = "cwc_accounts"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    balance_units: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)


class CwcLedger(Base):
    __tablename__ = "cwc_ledger"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    account_id: Mapped[str] = mapped_column(nullable=False)
    delta_units: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reason: Mapped[str] = mapped_column(String(128), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp()
    )


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    scope: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    state: Mapped[str] = mapped_column(String(16), nullable=False, default="started")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (UniqueConstraint("scope", "idempotency_key", name="uq_idempotency"),)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(ID_LEN), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp()
    )


class Playlist(Base, TimestampMixin):
    """Minimal playlist — container only; deleting it never touches tracks."""

    __tablename__ = "playlists"

    id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True, default=new_id)
    owner_user_id: Mapped[str] = mapped_column(String(ID_LEN), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    visibility: Mapped[str] = mapped_column(String(16), nullable=False, default="private")

    __table_args__ = (
        CheckConstraint("visibility IN ('private','public')", name="ck_playlists_visibility"),
    )


class PlaylistItem(Base):
    __tablename__ = "playlist_items"

    playlist_id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True)
    track_id: Mapped[str] = mapped_column(String(ID_LEN), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    added_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.current_timestamp()
    )
