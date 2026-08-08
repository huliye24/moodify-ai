"""Tests for SHA-256 hashing, path safety, and overwrite protection."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from tools.studio_session_prep.studio_prep import (
    _check_output_dir,
    _check_paths_different,
    _sha256_file,
)


class TestSHA256:
    def test_known_content(self, tmp_path):
        f = tmp_path / "test.bin"
        f.write_bytes(b"hello world")
        h = _sha256_file(f)
        # Known SHA-256 of "hello world"
        assert len(h) == 64
        assert h == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    def test_deterministic(self, tmp_path):
        f = tmp_path / "test.bin"
        f.write_bytes(b"some data")
        h1 = _sha256_file(f)
        h2 = _sha256_file(f)
        assert h1 == h2

    def test_different_content(self, tmp_path):
        f1 = tmp_path / "a.bin"
        f2 = tmp_path / "b.bin"
        f1.write_bytes(b"data A")
        f2.write_bytes(b"data B")
        assert _sha256_file(f1) != _sha256_file(f2)

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.bin"
        f.write_bytes(b"")
        h = _sha256_file(f)
        assert len(h) == 64
        assert h == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            _sha256_file(tmp_path / "nonexistent.bin")


class TestPathSafety:
    def test_same_path_rejected(self, tmp_path):
        p = tmp_path / "same"
        p.mkdir()
        with pytest.raises(ValueError, match="Source and output"):
            _check_paths_different(p, p)

    def test_different_paths_ok(self, tmp_path):
        a = tmp_path / "a"
        b = tmp_path / "b"
        a.mkdir()
        b.mkdir()
        _check_paths_different(a, b)  # should not raise

    def test_resolved_same_rejected(self, tmp_path):
        a = tmp_path / "real_dir"
        b = tmp_path / ".." / tmp_path.name / "real_dir"
        a.mkdir()
        with pytest.raises(ValueError, match="Source and output"):
            _check_paths_different(a, b.resolve())


class TestOutputDirProtection:
    def test_new_dir_ok(self, tmp_path):
        new_dir = tmp_path / "new_output"
        _check_output_dir(new_dir)  # should not raise

    def test_empty_existing_dir_ok(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        _check_output_dir(empty_dir)  # should be OK

    def test_nonempty_dir_rejected(self, tmp_path):
        nonempty = tmp_path / "nonempty"
        nonempty.mkdir()
        (nonempty / "file.txt").write_text("data")
        with pytest.raises(FileExistsError, match="not empty"):
            _check_output_dir(nonempty)

    def test_nonempty_force_allowed(self, tmp_path):
        nonempty = tmp_path / "nonempty"
        nonempty.mkdir()
        (nonempty / "file.txt").write_text("data")
        _check_output_dir(nonempty, allow_nonempty=True)  # should not raise

    def test_path_is_file_rejected(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("data")
        with pytest.raises(NotADirectoryError):
            _check_output_dir(f)
