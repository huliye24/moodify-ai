"""Feedback event capture and derived labels (DSK-MFY-TASTE-FEED-PATCH-001).

Raw player events are appended to an append-only JSONL log, then mapped
to derived labels (hard/soft skip, completion, replay, like, save) with
policy weights. The taste updater consumes derived signals, never raw
event names, so weight changes are experiment-safe.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from moodify.recommendation.models import FeedbackEvent

EVENT_TYPES = {
    "IMPRESSION", "PLAY_START", "PROGRESS", "COMPLETION",
    "SKIP", "REPLAY", "LIKE", "SAVE", "SESSION_END",
}

HARD_SKIP_MS = 10_000
HARD_SKIP_FRACTION = 0.25
SOFT_SKIP_FRACTION = 0.75


def derive_signal(event_type: str, elapsed_ms: int | None = None,
                  duration_ms: int | None = None) -> str:
    """Map a raw event to a weighted derived label."""
    if event_type == "SKIP":
        if elapsed_ms is not None and elapsed_ms < HARD_SKIP_MS:
            return "SKIP_HARD"
        if elapsed_ms is not None and duration_ms and elapsed_ms / duration_ms < HARD_SKIP_FRACTION:
            return "SKIP_HARD"
        return "SKIP_SOFT"
    return event_type


class FeedbackStore:
    """Append-only feedback event log with in-memory event index."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._events_path = self.root / "events.jsonl"

    def append(self, event: FeedbackEvent) -> FeedbackEvent:
        with self._events_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
        return event

    def events(self) -> list[FeedbackEvent]:
        if not self._events_path.is_file():
            return []
        return [FeedbackEvent.from_dict(json.loads(line))
                for line in self._events_path.read_text(encoding="utf-8").splitlines()
                if line.strip()]

    def events_for_user(self, user_id: str) -> list[FeedbackEvent]:
        return [event for event in self.events() if event.user_id == user_id]

    def events_for_track(self, track_id: str) -> list[FeedbackEvent]:
        return [event for event in self.events() if event.track_id == track_id]

    def events_for_request(self, request_id: str) -> list[FeedbackEvent]:
        return [event for event in self.events() if event.request_id == request_id]

    def recent_track_events(self, track_id: str, limit: int = 50) -> list[FeedbackEvent]:
        events = [event for event in self.events() if event.track_id == track_id]
        return events[-limit:]


def new_event(user_id: str, track_id: str, event_type: str,
              request_id: str = "", playback_session_id: str = "",
              rank_position: int | None = None, elapsed_ms: int | None = None,
              metadata: dict[str, Any] | None = None) -> FeedbackEvent:
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unknown event type: {event_type}")
    return FeedbackEvent(
        event_id=f"evt-{uuid4().hex[:12]}",
        user_id=user_id,
        track_id=track_id,
        event_type=event_type,
        request_id=request_id,
        playback_session_id=playback_session_id,
        rank_position=rank_position,
        elapsed_ms=elapsed_ms,
        metadata=metadata or {},
    )
