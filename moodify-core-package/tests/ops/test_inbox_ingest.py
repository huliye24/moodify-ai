from __future__ import annotations

import importlib.util
import os
import stat
import sys
import time
from pathlib import Path


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


MODULE = load_module(
    Path(__file__).parents[3] / "ops" / "data_node" / "inbox_ingest.py",
    "inbox_ingest",
)


def _fake_node_cli(tmp_path: Path) -> str:
    """Return a moodify-node stand-in runnable on this platform."""
    py = tmp_path / "fake_node.py"
    py.write_text(
        "import json, sys\n"
        "print(json.dumps({'job_id':'job_test','source_path':sys.argv[-1]}))\n",
        encoding="utf-8",
    )
    if os.name == "nt":
        bat = tmp_path / "moodify-node.bat"
        bat.write_text(
            f'@echo off\n"{sys.executable}" "{py}" %*\n', encoding="utf-8"
        )
        return str(bat)
    cli = tmp_path / "moodify-node"
    cli.write_text(
        "#!/usr/bin/env python3\nimport json,sys\n"
        "sys.argv[0]='moodify-node'\n"
        "print(json.dumps({'job_id':'job_test','source_path':sys.argv[-1]}))\n",
        encoding="utf-8",
    )
    cli.chmod(cli.stat().st_mode | stat.S_IEXEC)
    return str(cli)


def test_ingest_and_deduplicate(tmp_path: Path):
    inbox = tmp_path / "inbox"
    store = tmp_path / "sources"
    ledger = tmp_path / "ops" / "ingest.sqlite3"
    inbox.mkdir()
    src = inbox / "a.wav"
    src.write_bytes(b"audio-test")
    old = time.time() - 300
    os.utime(src, (old, old))

    cli = _fake_node_cli(tmp_path)

    first = MODULE.scan_inbox(inbox, store, ledger, cli, 120, {".wav"})
    assert first[0]["status"] == "enqueued"
    stored = Path(first[0]["stored_path"])
    assert stored.exists()
    assert stored.read_bytes() == b"audio-test"

    second = MODULE.scan_inbox(inbox, store, ledger, cli, 120, {".wav"})
    assert second[0]["status"] == "duplicate"
    assert second[0]["job_id"] == "job_test"


def test_young_file_is_ignored(tmp_path: Path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "new.wav").write_bytes(b"x")
    result = MODULE.scan_inbox(
        inbox, tmp_path / "store", tmp_path / "ledger.sqlite3",
        "/does/not/matter", 120, {".wav"}
    )
    assert result == []
