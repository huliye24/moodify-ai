"""Retention policy tests (MFY-CR-P08)."""

from __future__ import annotations

import os

import pytest

from moodify.reconstruction_job.contract import RetentionPolicy
from moodify.reconstruction_job.retention import (
    cleanup_tmp,
    cleanup_workspace,
    sweep_workspaces,
)

pytestmark = pytest.mark.v01


def _workspace(root, job_id="job_1") -> dict:
    ws = root / job_id
    dirs = ("input", "tmp", "candidates", "result", "case", "stems")
    for d in dirs:
        (ws / d).mkdir(parents=True, exist_ok=True)
    return {"root": root, "ws": ws}


def _age_dirs(ws, seconds: float) -> None:
    for child in ws.iterdir():
        if child.is_dir():
            stamp = os.path.getmtime(ws) - seconds
            os.utime(child, (stamp, stamp))
    stamp = os.path.getmtime(ws) - seconds
    os.utime(ws, (stamp, stamp))


def test_tmp_removed_immediately(tmp_path):
    env = _workspace(tmp_path)
    assert cleanup_tmp(env["ws"]) is True
    assert not (env["ws"] / "tmp").exists()


def test_fresh_workspace_keeps_substantive_dirs(tmp_path):
    env = _workspace(tmp_path)
    result = cleanup_workspace(env["ws"], RetentionPolicy())
    # tmp/stems carry TTL 0 (delete immediately); substantive dirs are kept
    assert set(result) == {"tmp", "stems"}
    assert (env["ws"] / "input").exists()
    assert (env["ws"] / "candidates").exists()
    assert (env["ws"] / "result").exists()
    assert (env["ws"] / "case").exists()


def test_expired_tmp_and_candidates_removed_evidence_kept(tmp_path):
    env = _workspace(tmp_path)
    _age_dirs(env["ws"], 10 * 86400)
    result = cleanup_workspace(env["ws"], RetentionPolicy())
    assert result.get("tmp") == 1
    assert result.get("candidates") == 1
    assert result.get("evidence") is None
    assert not (env["ws"] / "tmp").exists()
    assert not (env["ws"] / "candidates").exists()
    assert (env["ws"] / "case").exists()  # evidence retained
    assert (env["ws"] / "input").exists()  # source retained (30d > 10d)


def test_expired_source_removed(tmp_path):
    env = _workspace(tmp_path)
    _age_dirs(env["ws"], 45 * 86400)
    result = cleanup_workspace(env["ws"], RetentionPolicy())
    assert result.get("source") == 1
    assert not (env["ws"] / "input").exists()


def test_none_ttl_keeps_indefinitely(tmp_path):
    env = _workspace(tmp_path)
    _age_dirs(env["ws"], 1000 * 86400)
    result = cleanup_workspace(env["ws"], RetentionPolicy(evidence_ttl_s=None))
    assert result.get("evidence") is None
    assert (env["ws"] / "case").exists()


def test_sweep_across_workspaces(tmp_path):
    a = _workspace(tmp_path, "job_a")
    b = _workspace(tmp_path, "job_b")
    _age_dirs(a["ws"], 10 * 86400)
    result = sweep_workspaces(tmp_path, RetentionPolicy())
    assert "job_a" in result
    assert "job_b" in result
    assert not (a["ws"] / "tmp").exists()
    assert not (a["ws"] / "candidates").exists()
    assert (b["ws"] / "case").exists()  # fresh substantive dirs kept


def test_active_job_workspace_skipped(tmp_path):
    env = _workspace(tmp_path, "job_active")
    _age_dirs(env["ws"], 10 * 86400)
    result = sweep_workspaces(tmp_path, RetentionPolicy(), active_job_ids={"job_active"})
    assert result == {}
    assert (env["ws"] / "tmp").exists()  # in-progress scratch never swept


def test_policy_roundtrip():
    policy = RetentionPolicy(source_ttl_s=5, evidence_ttl_s=None)
    clone = RetentionPolicy.from_dict(policy.to_dict())
    assert clone.source_ttl_s == 5
    assert clone.evidence_ttl_s is None
