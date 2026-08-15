from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "media_audit.py"
SPEC = importlib.util.spec_from_file_location("media_audit", SCRIPT)
assert SPEC and SPEC.loader
media_audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(media_audit)


def test_scan_root_recurses_and_returns_canonical_asset_keys(tmp_path: Path):
    nested = tmp_path / "beta" / "creator" / "sha256" / "ab"
    nested.mkdir(parents=True)
    audio = nested / "abcdef.wav"
    audio.write_bytes(b"RIFF0000WAVE")
    (nested / "ignore.txt").write_text("not audio", encoding="utf-8")
    hidden = tmp_path / ".incoming"
    hidden.mkdir()
    (hidden / "partial.wav").write_bytes(b"partial")

    rows = media_audit.scan_root(str(tmp_path))

    assert len(rows) == 1
    assert rows[0][0] == "beta/creator/sha256/ab/abcdef.wav"
    assert rows[0][1] == str(audio)
