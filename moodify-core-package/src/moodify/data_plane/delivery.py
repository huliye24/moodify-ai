"""Moodify Playback Delivery (W01-P06).

服务端交付层：READY eligibility → playback metadata → authorized URI → session。
- DLV-INV-01: 只有 READY 对象获得正式播放入口。
- DLV-INV-02: 客户端不持长期云凭据（URI 短期 token 可刷新）。
- DLV-INV-03/04: Track ID 与 URL 分离；URL 可替换。
- DLV-INV-09: 播放失败不污染 compute job（本模块不触碰 jobs 状态）。
- Delivery failure taxonomy 与 P04 compute taxonomy 分离。
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

PLAYBACK_FAILURES = (
    "TRACK_NOT_READY", "TRACK_NOT_FOUND", "ACCESS_DENIED", "DELIVERY_URI_EXPIRED",
    "DELIVERY_URI_INVALID", "NETWORK_UNAVAILABLE", "NETWORK_TIMEOUT", "RANGE_NOT_SUPPORTED",
    "OBJECT_NOT_FOUND", "UNSUPPORTED_MEDIA", "DECODER_ERROR", "AUDIO_FOCUS_LOST",
    "PLAYER_INTERNAL_ERROR", "UNKNOWN_PLAYBACK_ERROR",
)


class DeliveryError(Exception):
    """Playback/delivery failure (not a compute failure)."""

    def __init__(self, code: str, message: str = "") -> None:
        if code not in PLAYBACK_FAILURES:
            raise ValueError(f"unknown playback failure code: {code!r}")
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PlaybackMetadata:
    track_id: str
    playback_version: str
    render_object_id: str
    title: str
    duration_ms: int
    container: str
    codec: str
    sample_rate: int
    channels: int
    content_length: int
    playback_uri: str
    uri_expires_at: str
    supports_range: bool
    etag: str
    ready_at: str
    pipeline_version: str
    profile_version: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> PlaybackMetadata:
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)


@dataclass
class PlaybackSession:
    playback_session_id: str
    track_id: str
    render_object_id: str
    user_scope: str
    issued_at: str
    expires_at: str
    delivery_method: str
    app_version: str | None = None
    device_class: str | None = None
    correlation_id: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class DeliveryService:
    """READY-only authorized playback delivery over the data plane."""

    URI_TTL_SECONDS = 3600  # short TTL; refreshable without reprocessing (DLV-INV-06)

    def __init__(self, repo, store_adapter, *, uri_signer_secret: str = "dev-secret",
                 issuer: str = "moodify-delivery") -> None:
        self.repo = repo
        self.store = store_adapter
        self._secret = uri_signer_secret.encode("utf-8")
        self._issuer = issuer
        self._sessions: dict[str, PlaybackSession] = {}

    # ---------- READY guard (DLV-INV-01) ----------

    def _ready_render(self, track_id: str) -> dict:
        track = self.repo.get_track(track_id)
        if track is None:
            raise DeliveryError("TRACK_NOT_FOUND", track_id)
        # authoritative READY = any job of this track reached READY with a ready_object_id
        conn = self.repo._conn
        row = conn.execute(
            "SELECT job_id, ready_object_id, finished_at FROM jobs"
            " WHERE track_id=? AND current_state='READY' AND ready_object_id IS NOT NULL"
            " ORDER BY finished_at DESC LIMIT 1",
            (track_id,),
        ).fetchone()
        if row is None:
            raise DeliveryError("TRACK_NOT_READY", track_id)
        obj = self.repo.get_object(row["ready_object_id"])
        if obj is None:
            raise DeliveryError("OBJECT_NOT_FOUND", row["ready_object_id"])
        if self.store.head(obj["bucket"], obj["object_key"]) is None:
            # DB says READY but object missing: reconciliation path (DLV-INV-09/03)
            raise DeliveryError("OBJECT_NOT_FOUND", "ready object missing in store")
        return {"job": dict(row), "object": obj, "track": track}

    # ---------- authorization (DLV-INV-05) ----------

    def _check_access(self, track: dict, user_scope: str) -> None:
        owner = track.get("owner_scope")
        if owner is not None and owner not in ("", user_scope):
            raise DeliveryError("ACCESS_DENIED", f"scope {user_scope} cannot access {owner}")

    # ---------- URI signing ----------

    def _sign_uri(self, *, track_id: str, render_object_id: str, expires_at: str,
                  nonce: str | None = None) -> str:
        from moodify.data_plane.ids import uuid7

        nonce = nonce or uuid7().hex[:12]
        payload = f"{track_id}|{render_object_id}|{expires_at}|{nonce}"
        sig = hmac.new(self._secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()[:32]
        # signed locator references the object key via delivery resolver, never a raw OSS key
        return f"moodify://deliver/{track_id}/{render_object_id}?expires={expires_at}&nonce={nonce}&sig={sig}"

    def _verify_uri(self, uri: str, *, track_id: str, render_object_id: str) -> None:
        try:
            _, _, rest = uri.partition("//")
            _, _, query = rest.partition("?")
            params = dict(kv.split("=", 1) for kv in query.split("&"))
            expires = params.get("expires", "")
            nonce = params.get("nonce", "")
            sig = params.get("sig", "")
        except Exception as e:
            raise DeliveryError("DELIVERY_URI_INVALID", str(e)) from e
        if int(time.time()) > int(expires):
            raise DeliveryError("DELIVERY_URI_EXPIRED", "token expired")
        expected = hmac.new(self._secret, f"{track_id}|{render_object_id}|{expires}|{nonce}".encode(),
                            hashlib.sha256).hexdigest()[:32]
        if sig != expected:
            raise DeliveryError("DELIVERY_URI_INVALID", "signature mismatch")

    # ---------- main entry ----------

    def playback_metadata(self, *, track_id: str, user_scope: str = "public",
                          app_version: str | None = None, device_class: str | None = None) -> PlaybackMetadata:
        """GET /tracks/{id}/playback equivalent (READY guard + authorize + sign)."""
        ready = self._ready_render(track_id)
        track, obj, job = ready["track"], ready["object"], ready["job"]
        self._check_access(track, user_scope)
        expires = str(int(time.time()) + self.URI_TTL_SECONDS)
        uri = self._sign_uri(track_id=track_id, render_object_id=obj["object_id"], expires_at=expires)
        self._new_session(track_id=track_id, render_object_id=obj["object_id"],
                          user_scope=user_scope, app_version=app_version, device_class=device_class)
        mime = obj.get("mime_type") or "audio/wav"
        container = mime.rsplit("/", 1)[-1]
        codec = "pcm_s16le" if container == "wav" else container
        return PlaybackMetadata(
            track_id=track_id,
            playback_version=f"{obj.get('pipeline_version') or 'unknown'}",
            render_object_id=obj["object_id"],
            title=track.get("title") or track_id,
            duration_ms=self._duration_ms(obj),
            container=container,
            codec=codec,
            sample_rate=0,  # from VALIDATE metrics when available; 0 = not provided
            channels=0,
            content_length=obj["byte_size"],
            playback_uri=uri,
            uri_expires_at=datetime.fromtimestamp(int(expires), tz=timezone.utc).isoformat(),
            supports_range=True,
            etag=f'"{obj["content_hash"][:16]}"',
            ready_at=job.get("finished_at") or _now_iso(),
            pipeline_version=obj.get("pipeline_version") or "unknown",
            profile_version=obj.get("artifact_role"),
        )

    def _duration_ms(self, obj: dict) -> int:
        return 0  # P05 VALIDATE metrics carry duration; persisted per-object TBD in P07

    def _new_session(self, *, track_id, render_object_id, user_scope, app_version, device_class) -> PlaybackSession:
        from moodify.data_plane.ids import new_id

        session = PlaybackSession(
            playback_session_id=new_id("evidence"),  # prefixed id space reuse
            track_id=track_id, render_object_id=render_object_id, user_scope=user_scope,
            issued_at=_now_iso(),
            expires_at=datetime.fromtimestamp(int(time.time()) + self.URI_TTL_SECONDS, tz=timezone.utc).isoformat(),
            delivery_method="signed_uri", app_version=app_version, device_class=device_class,
        )
        self._sessions[session.playback_session_id] = session
        return session

    def get_session(self, playback_session_id: str) -> PlaybackSession | None:
        return self._sessions.get(playback_session_id)

    def refresh(self, *, track_id: str, user_scope: str = "public") -> PlaybackMetadata:
        """DLV-INV-06: expired URL refresh — no reprocessing, no re-upload, same identity."""
        return self.playback_metadata(track_id=track_id, user_scope=user_scope)

    def resolve_object(self, uri: str, *, track_id: str, render_object_id: str) -> tuple[str, str] | None:
        """Resolve a signed URI to (bucket, object_key) — used by the delivery adapter."""
        self._verify_uri(uri, track_id=track_id, render_object_id=render_object_id)
        obj = self.repo.get_object(render_object_id)
        if obj is None or obj["track_id"] != track_id:
            raise DeliveryError("OBJECT_NOT_FOUND", render_object_id)
        return obj["bucket"], obj["object_key"]
