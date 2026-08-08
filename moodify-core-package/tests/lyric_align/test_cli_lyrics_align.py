"""case lyrics-align CLI registration test (no ffmpeg required — pipeline is stubbed)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

from moodify.cli_v2.main import cmd_case_lyrics_align

FAKE_MANIFEST = {
    "backend": "heuristic",
    "backend_version": "0.1",
    "status": "DRAFT_ONLY",
    "alignment_sha256": "abc123",
    "rerun_delta_ms": 0.0,
}


def _args(tmp_path: Path) -> argparse.Namespace:
    project = tmp_path / "project"
    project.mkdir()
    valid_project = {
        "schema_version": "1.0.0",
        "title": "test",
        "project_id": "p-test",
        "assets": {}, "plans": {}, "runs": {},
    }
    (project / "project.json").write_text(json.dumps(valid_project), encoding="utf-8")
    audio = tmp_path / "song.wav"
    audio.write_bytes(b"RIFF-fake")
    lyrics = tmp_path / "lyrics.txt"
    lyrics.write_text("line one\nline two\n", encoding="utf-8")
    return argparse.Namespace(
        project_dir=str(project),
        case_id="LYRIC-001",
        audio=str(audio),
        lyrics=str(lyrics),
        translation=None,
        language="fr",
        backend="heuristic",
        separate_vocals="auto",
        device="cpu",
        granularity=None,
    )


def test_case_lyrics_align_registered(tmp_path: Path) -> None:
    with patch("moodify.lyric_align.service.run_lyric_alignment", return_value=FAKE_MANIFEST) as mocked:
        result = cmd_case_lyrics_align(_args(tmp_path))
    assert result["status"] == "ok"
    assert result["result_status"] == "LYRIC_ALIGNMENT_COMPLETED"
    assert result["case_id"] == "LYRIC-001"
    assert result["alignment_sha256"] == "abc123"
    assert mocked.call_count == 1
    output_dir = Path(result["output_dir"])
    assert output_dir.name == "05_lyric_align"


def test_case_lyrics_align_missing_audio(tmp_path: Path) -> None:
    args = _args(tmp_path)
    args.audio = str(tmp_path / "missing.wav")
    from moodify.cli_v2.main import CLIError

    try:
        cmd_case_lyrics_align(args)
        raise AssertionError("expected CLIError")
    except CLIError as exc:
        assert exc.code == "AUDIO_NOT_FOUND"


def test_case_lyrics_align_manifest_written_through_service(tmp_path: Path) -> None:
    """End-to-end through the real service with a stubbed pipeline run."""
    from moodify.lyric_align.service import run_lyric_alignment

    project = tmp_path / "project"
    project.mkdir()
    valid_project = {
        "schema_version": "1.0.0",
        "title": "test",
        "project_id": "p-test",
        "assets": {}, "plans": {}, "runs": {},
    }
    (project / "project.json").write_text(json.dumps(valid_project), encoding="utf-8")
    case_root = project / "cases" / "LYRIC-002"
    case_root.mkdir(parents=True)

    with patch("moodify.lyric_align.service.run_alignment", return_value=FAKE_MANIFEST) as mocked:
        result = run_lyric_alignment(
            case_id="LYRIC-002",
            case_root=case_root,
            audio_path=Path("song.wav"),
            lyrics_path=Path("lyrics.txt"),
            language="fr",
        )
    assert result["status"] == "DRAFT_ONLY"
    assert mocked.call_count == 1
    assert (case_root / "05_lyric_align").is_dir()
