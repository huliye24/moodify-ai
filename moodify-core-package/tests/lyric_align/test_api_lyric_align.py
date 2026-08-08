"""Lyric alignment API contract tests (Phase F)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from moodify.api.main import app


def _fake_run_alignment(audio_path, lyrics_path, output_dir, language, backend_name,
                        translation_path=None, separate_vocals="auto", device="cpu",
                        config_path=None, granularity=None) -> dict[str, object]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "qc_report.json").write_text(
        json.dumps({
            "coverage": 0.95,
            "mean_word_confidence": 0.8,
            "unaligned_token_ratio": 0.02,
            "review_regions": [{"line_index": 1, "reason": "LOW_LINE_CONFIDENCE"}],
        }),
        encoding="utf-8",
    )
    for name in ("lyrics.lrc", "lyrics.enhanced.lrc", "lyrics.srt", "lyrics.ass"):
        (out / name).write_text("x", encoding="utf-8")
    return {"status": "PUBLISHABLE", "rerun_delta_ms": 0.0}


def test_lyric_alignment_contract(tmp_path: Path) -> None:
    fake_audio = tmp_path / "song.wav"
    fake_audio.write_bytes(b"RIFF-fake")
    with (
        patch("moodify.api.routes.lyric_align._resolve_audio", return_value=fake_audio),
        patch("moodify.api.routes.lyric_align.run_alignment", side_effect=_fake_run_alignment),
        patch("moodify.api.routes.lyric_align._output_root", return_value=tmp_path / "out"),
    ):
        client = TestClient(app)
        response = client.post(
            "/api/v1/lyric-alignments",
            json={
                "audio_asset_id": "up-1",
                "lyrics": "ligne un\nligne deux\n",
                "language": "fr",
                "requested_granularity": ["line", "word"],
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PUBLISHABLE"
    assert body["alignment_asset_id"].startswith("al-")
    assert body["exports"]["lrc"] == "lyrics.lrc"
    assert body["exports"]["ass"] == "lyrics.ass"
    assert body["quality"]["coverage"] == 0.95
    assert body["quality"]["mean_confidence"] == 0.8
    assert body["quality"]["unaligned_token_ratio"] == 0.02
    assert body["review_regions"][0]["reason"] == "LOW_LINE_CONFIDENCE"
    assert "created_at" in body


def test_lyric_alignment_unknown_asset() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/lyric-alignments",
        json={"audio_asset_id": "up-missing", "lyrics": "x", "language": "fr"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_lyric_alignment_score_prior_not_implemented() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/lyric-alignments",
        json={
            "audio_asset_id": "up-1",
            "lyrics": "x",
            "language": "fr",
            "score_asset_id": "score-1",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "NOT_IMPLEMENTED"


def test_lyric_alignment_validation_error() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/lyric-alignments",
        json={"lyrics": "x", "language": "fr"},
    )
    assert response.status_code == 422
