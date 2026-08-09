"""Recommendation orchestration (DSK-MFY-TASTE-FEED-PATCH-001).

Track registration, For You feed generation, feedback capture, taste
update, and saved-library persistence. Every feed request is traceable
(request_id + ranking_version); events link back to request/track/rank.
Persistence lives under MOODIFY_FEED_ROOT (default outputs/feed/).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from moodify.recommendation.feedback import FeedbackStore, derive_signal, new_event
from moodify.recommendation.models import (
    AuditoryProfile,
    RecommendationCandidate,
    RecommendationRequest,
    Track,
    UserTasteProfile,
)
from moodify.recommendation.policy import RecommendationPolicy
from moodify.recommendation.rank import generate_candidates, rerank_for_session, score_candidates
from moodify.recommendation.taste import apply_signal

DEFAULT_FEED_ROOT = Path(os.environ.get("MOODIFY_FEED_ROOT", "outputs/feed"))

RANKING_VERSION = "rec_v1"


def _atomic_write(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


class FeedService:
    """For You feed facade: tracks, profiles, taste, events, saved."""

    def __init__(self, root: Path = DEFAULT_FEED_ROOT,
                 policy: RecommendationPolicy | None = None) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.policy = policy or RecommendationPolicy.from_yaml()
        self.feedback = FeedbackStore(self.root)
        self._tracks_path = self.root / "tracks.json"
        self._profiles_path = self.root / "profiles.json"
        self._taste_path = self.root / "taste.json"
        self._requests_path = self.root / "requests.jsonl"
        self._saved_path = self.root / "saved.json"

    # -- persistence ---------------------------------------------------------

    def _load_tracks(self) -> list[Track]:
        if not self._tracks_path.is_file():
            return []
        return [Track.from_dict(record) for record in json.loads(self._tracks_path.read_text(encoding="utf-8"))]

    def _save_tracks(self, tracks: list[Track]) -> None:
        _atomic_write(self._tracks_path, [t.to_dict() for t in tracks])

    def _load_profiles(self) -> dict[str, AuditoryProfile]:
        if not self._profiles_path.is_file():
            return {}
        return {pid: AuditoryProfile.from_dict(record)
                for pid, record in json.loads(self._profiles_path.read_text(encoding="utf-8")).items()}

    def _save_profiles(self, profiles: dict[str, AuditoryProfile]) -> None:
        _atomic_write(self._profiles_path, {pid: p.to_dict() for pid, p in profiles.items()})

    def _load_taste(self) -> dict[str, UserTasteProfile]:
        if not self._taste_path.is_file():
            return {}
        return {uid: UserTasteProfile.from_dict(record)
                for uid, record in json.loads(self._taste_path.read_text(encoding="utf-8")).items()}

    def _save_taste(self, taste: dict[str, UserTasteProfile]) -> None:
        _atomic_write(self._taste_path, {uid: t.to_dict() for uid, t in taste.items()})

    def _load_saved(self) -> dict[str, list[str]]:
        if not self._saved_path.is_file():
            return {}
        return json.loads(self._saved_path.read_text(encoding="utf-8"))

    def _save_saved(self, saved: dict[str, list[str]]) -> None:
        _atomic_write(self._saved_path, saved)

    # -- tracks & profiles ----------------------------------------------------

    def register_track(self, track_id: str, source_audio_id: str,
                       feature_vector: list[float] | tuple[float, ...] = (),
                       quality_state: str = "ELIGIBLE",
                       quality_confidence: float = 0.0,
                       availability_state: str = "AVAILABLE",
                       creator_id: str | None = None) -> dict[str, Any]:
        tracks = self._load_tracks()
        if any(t.track_id == track_id for t in tracks):
            return {"track_id": track_id, "created": False}
        profile_id = f"aud-{uuid4().hex[:12]}"
        track = Track(
            track_id=track_id,
            source_audio_id=source_audio_id,
            availability_state=availability_state,
            creator_id=creator_id,
            auditory_profile_id=profile_id,
            quality_state=quality_state,
        )
        tracks.append(track)
        self._save_tracks(tracks)
        profiles = self._load_profiles()
        profiles[track_id] = AuditoryProfile(
            auditory_profile_id=profile_id,
            track_id=track_id,
            feature_vector=tuple(feature_vector),
            quality_confidence=quality_confidence,
            version="1.0",
        )
        self._save_profiles(profiles)
        return {"track_id": track_id, "created": True, "auditory_profile_id": profile_id}

    def track(self, track_id: str) -> Track | None:
        return next((t for t in self._load_tracks() if t.track_id == track_id), None)

    def auditory_profile(self, track_id: str) -> AuditoryProfile | None:
        return self._load_profiles().get(track_id)

    # -- feed ----------------------------------------------------------------

    def get_for_you(self, user_id: str, size: int | None = None,
                    context: dict[str, Any] | None = None) -> dict[str, Any]:
        tracks = self._load_tracks()
        if not tracks:
            raise ValueError("no tracks registered")
        profiles = self._load_profiles()
        taste = self._load_taste().get(user_id, UserTasteProfile(user_id=user_id))
        feed_size = size or self.policy.default_feed_size

        session_played = {event.track_id for event in self.feedback.events_for_user(user_id)
                          if event.playback_session_id and event.event_type in {"PLAY_START", "COMPLETION"}}
        recent_played = {event.track_id for event in self.feedback.events_for_user(user_id)
                         if event.event_type in {"PLAY_START", "COMPLETION"}}

        request = RecommendationRequest(
            request_id=f"req-{uuid4().hex[:12]}",
            user_id=user_id,
            surface="for_you",
            ranking_version=RANKING_VERSION,
            candidate_pool_size=self.policy.candidate_pool_size,
            context=context or {},
        )
        candidates = generate_candidates(tracks, profiles, taste, self.policy,
                                         session_played=session_played)
        scored = score_candidates(candidates, tracks, profiles, taste, self.policy,
                                  session_played=session_played, recent_played=recent_played)
        selected = rerank_for_session(scored, min(feed_size, len(scored)), session_played)

        ranked: list[dict[str, Any]] = []
        for rank, (track_id, score, tokens) in enumerate(selected, start=1):
            ranked.append(RecommendationCandidate(
                request_id=request.request_id,
                track_id=track_id,
                candidate_source=tokens[0].split(":")[1] if tokens else "unknown",
                final_rank=rank,
                final_score=round(score, 6),
                explanation_tokens=tuple(tokens),
            ).to_dict())
            # impression event for traceability (AT-06)
            self.feedback.append(new_event(
                user_id, track_id, "IMPRESSION",
                request_id=request.request_id, rank_position=rank,
            ))

        with self._requests_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(request.to_dict(), ensure_ascii=False) + "\n")
        return {
            "request_id": request.request_id,
            "user_id": user_id,
            "ranking_version": request.ranking_version,
            "feed": ranked,
            "novelty_tolerance": taste.novelty_tolerance,
        }

    # -- feedback --------------------------------------------------------------

    def record_feedback(self, user_id: str, track_id: str, event_type: str,
                        request_id: str = "", playback_session_id: str = "",
                        rank_position: int | None = None, elapsed_ms: int | None = None,
                        duration_ms: int | None = None,
                        metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        event = new_event(
            user_id, track_id, event_type,
            request_id=request_id, playback_session_id=playback_session_id,
            rank_position=rank_position, elapsed_ms=elapsed_ms, metadata=metadata,
        )
        self.feedback.append(event)

        signal = derive_signal(event_type, elapsed_ms, duration_ms)
        profiles = self._load_profiles()
        track_vector = profiles[track_id].feature_vector if track_id in profiles else ()
        taste = self._load_taste().get(user_id, UserTasteProfile(user_id=user_id))
        updated = apply_signal(taste, signal, track_vector, self.policy)
        all_taste = self._load_taste()
        all_taste[user_id] = updated
        self._save_taste(all_taste)
        return {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "derived_signal": signal,
            "request_id": event.request_id,
            "track_id": track_id,
        }

    # -- library ----------------------------------------------------------------

    def save_track(self, user_id: str, track_id: str) -> dict[str, Any]:
        saved = self._load_saved()
        items = saved.setdefault(user_id, [])
        if track_id not in items:
            items.append(track_id)
            self._save_saved(saved)
        return {"user_id": user_id, "track_id": track_id, "saved": True}

    def unsave_track(self, user_id: str, track_id: str) -> dict[str, Any]:
        saved = self._load_saved()
        items = saved.get(user_id, [])
        if track_id in items:
            items.remove(track_id)
            self._save_saved(saved)
        return {"user_id": user_id, "track_id": track_id, "saved": track_id in items}

    def saved_tracks(self, user_id: str) -> list[str]:
        return self._load_saved().get(user_id, [])

    def taste_profile(self, user_id: str) -> UserTasteProfile:
        return self._load_taste().get(user_id, UserTasteProfile(user_id=user_id))
