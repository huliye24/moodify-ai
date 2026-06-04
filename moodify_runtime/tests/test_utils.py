"""Tests for utils."""
import tempfile, json, time
from pathlib import Path
from moodify_runtime.utils import (
    utc_now_iso, local_stamp, ensure_parent, check_disk_space,
    read_jsonl, append_jsonl, write_json, read_json,
    atomic_write_jsonl, file_sha1, stable_sample_id,
    discover_audio_files, quote_cmd, render_template_to_argv,
    append_csv, LockFile, LineLogger,
)

class TestTime:
    def test_utc(self): assert "T" in utc_now_iso()
    def test_stamp(self): assert len(local_stamp()) > 0

class TestPath:
    def test_ensure(self):
        d = tempfile.mkdtemp(); p = Path(d) / "sub" / "f.txt"
        ensure_parent(p); assert p.parent.exists()
    def test_disk(self):
        ok, gb = check_disk_space(Path("."), 1.0)
        assert isinstance(ok, bool) and gb > 0

class TestJSON:
    def test_jsonl(self):
        d = tempfile.mkdtemp(); p = Path(d) / "t.jsonl"
        append_jsonl(p, {"a": 1}); assert len(read_jsonl(p)) == 1
    def test_json(self):
        d = tempfile.mkdtemp(); p = Path(d) / "t.json"
        write_json(p, {"k": "v"}); assert read_json(p) == {"k": "v"}

class TestHash:
    def test_sha1(self):
        f = tempfile.NamedTemporaryFile(delete=False); f.write(b"hello"); f.close()
        h = file_sha1(Path(f.name)); Path(f.name).unlink()
        assert len(h) == 40

class TestSampleId:
    def test_id(self):
        f = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        f.write(b"dummy"); f.close()
        sid = stable_sample_id(Path(f.name)); Path(f.name).unlink()
        assert len(sid) > 0

class TestQuote:
    def test_quote(self):
        assert quote_cmd(["echo", "hello"]) == "echo hello"

class TestRender:
    def test_render(self):
        r = render_template_to_argv("{cmd} /tmp/file.wav", {"cmd": "cat"})
        assert "cat" in r

class TestCSV:
    def test_csv(self):
        d = tempfile.mkdtemp(); p = Path(d) / "o.csv"
        append_csv(p, {"a": "1"}, ["a"])
        assert "1" in p.read_text()

class TestLockFile:
    def test_lock(self):
        d = tempfile.mkdtemp()
        lock = LockFile(Path(d) / "t.lock")
        assert lock.acquire() is None; lock.release()

class TestLogger:
    def test_log(self):
        d = tempfile.mkdtemp(); p = Path(d) / "t.log"
        log = LineLogger(p)
        log.write("test msg")
        del log
        assert "test msg" in p.read_text()

class TestDiscover:
    def test_empty(self):
        d = tempfile.mkdtemp()
        assert discover_audio_files([Path(d)], [".wav"], False) == []
