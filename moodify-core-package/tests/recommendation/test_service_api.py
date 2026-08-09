"""FeedService orchestration and API contract tests."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

from moodify.api.main import app
from moodify.recommendation.service import FeedService


def _service(tmp_path: Path) -> FeedService:
    return FeedService(tmp_path / "feed")


def _seed(svc: FeedService, count: int = 4) -> None:
    for i in range(count):
        svc.register_track(
            f"t{i}", f"src-{i}",
            [0.1 * i, 0.2 * i, 0.3 * i, 0.4 * i, 0.1, 0.1, 0.1],
            quality_confidence=0.7 + 0.05 * i,
        )


def test_for_you_returns_ranked_traceable_feed(tmp_path: Path):
    svc = _service(tmp_path)
    _seed(svc)
    feed = svc.get_for_you("u1", size=3)
    assert len(feed["feed"]) == 3
    assert feed["request_id"].startswith("req-")
    assert feed["ranking_version"] == "rec_v1"
    assert all(candidate["final_rank"] >= 1 for candidate in feed["feed"])
    assert all(candidate["explanation_tokens"] for candidate in feed["feed"])


def test_feedback_updates_taste_and_logs(tmp_path: Path):
    svc = _service(tmp_path)
    _seed(svc)
    feed = svc.get_for_you("u1", size=2)
    first = feed["feed"][0]
    result = svc.record_feedback(
        "u1", first["track_id"], "COMPLETION",
        request_id=feed["request_id"], rank_position=first["final_rank"],
        duration_ms=100_000, elapsed_ms=100_000,
    )
    assert result["derived_signal"] == "COMPLETION"
    assert result["event_id"].startswith("evt-")
    assert len(svc.feedback.events_for_request(feed["request_id"])) >= 3  # 2 impressions + completion


def test_saved_library(tmp_path: Path):
    svc = _service(tmp_path)
    _seed(svc)
    svc.save_track("u1", "t1")
    assert svc.saved_tracks("u1") == ["t1"]
    svc.unsave_track("u1", "t1")
    assert svc.saved_tracks("u1") == []


def test_quality_gate_blocks_severe_track(tmp_path: Path):
    svc = _service(tmp_path)
    _seed(svc)
    svc.register_track("bad", "src-bad", [0.5] * 7, quality_state="SEVERE_ISSUES")
    feed = svc.get_for_you("u1", size=5)
    assert all(c["track_id"] != "bad" for c in feed["feed"])


def _client(tmp_path: Path) -> TestClient:
    os.environ["MOODIFY_FEED_ROOT"] = str(tmp_path / "feed")
    return TestClient(app)


def test_api_register_track_and_feed(tmp_path: Path):
    client = _client(tmp_path)
    for i in range(3):
        response = client.post("/api/v1/tracks/register", json={
            "track_id": f"t{i}", "source_audio_id": f"src-{i}",
            "feature_vector": [0.1 * i, 0.2 * i, 0.3 * i, 0.4 * i, 0.1, 0.1, 0.1],
            "quality_confidence": 0.7,
        })
        assert response.status_code == 200
    feed = client.get("/api/v1/feed/for-you", params={"user_id": "api-u", "size": 3})
    assert feed.status_code == 200
    body = feed.json()
    assert body["request_id"].startswith("req-")
    assert len(body["feed"]) == 3


def test_api_feedback_validates_event_type(tmp_path: Path):
    client = _client(tmp_path)
    response = client.post("/api/v1/feed/feedback", json={
        "user_id": "u", "track_id": "t0", "event_type": "BOGUS",
    })
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION"


def test_api_feedback_and_profile_linkage(tmp_path: Path):
    client = _client(tmp_path)
    client.post("/api/v1/tracks/register", json={
        "track_id": "t0", "source_audio_id": "src-0",
        "feature_vector": [0.1, 0.2, 0.3, 0.4, 0.1, 0.1, 0.1],
    })
    profile = client.get("/api/v1/tracks/t0/auditory-profile")
    assert profile.status_code == 200
    assert len(profile.json()["feature_vector"]) == 7
    feedback = client.post("/api/v1/feed/feedback", json={
        "user_id": "u", "track_id": "t0", "event_type": "LIKE",
    })
    assert feedback.status_code == 200
    assert feedback.json()["derived_signal"] == "LIKE"


def test_api_saved_library(tmp_path: Path):
    client = _client(tmp_path)
    client.post("/api/v1/library/save", json={"user_id": "u", "track_id": "t0"})
    saved = client.get("/api/v1/library/saved", params={"user_id": "u"})
    assert saved.json()["saved_track_ids"] == ["t0"]
