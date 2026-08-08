"""Fail-open closure tests for lease expiry and run-directory selection.

Phase 1C of DSK-MFY-THICKNESS road-widening: corrupt timestamps must not
produce immortal leases; latest-run selection must validate candidates.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════════════
# TestLeaseExpiryFailClosed
# ═══════════════════════════════════════════════════════════════════════


class TestLeaseExpiryFailClosed:
    """WorkerLease.is_expired fails closed — no immortal leases."""

    def test_released_lease_is_expired(self):
        from moodify_runtime.cloud_worker import WorkerLease
        wl = WorkerLease(lease_id="L1", worker_id="W1", task_ids=["t1"],
                         released=True)
        assert wl.is_expired() is True

    def test_blank_timestamps_expired(self):
        from moodify_runtime.cloud_worker import WorkerLease
        wl = WorkerLease(lease_id="L1", worker_id="W1", task_ids=["t1"],
                         acquired_at="", heartbeat_at="")
        assert wl.is_expired() is True

    def test_corrupt_timestamp_expired(self):
        from moodify_runtime.cloud_worker import WorkerLease
        wl = WorkerLease(lease_id="L1", worker_id="W1", task_ids=["t1"],
                         acquired_at="not-a-date", heartbeat_at="")
        assert wl.is_expired() is True

    def test_corrupt_heartbeat_expired(self):
        from moodify_runtime.cloud_worker import WorkerLease
        wl = WorkerLease(lease_id="L1", worker_id="W1", task_ids=["t1"],
                         acquired_at="2026-01-01T00:00:00Z",
                         heartbeat_at="garbage")
        assert wl.is_expired() is True

    def test_fresh_lease_not_expired(self):
        from moodify_runtime.cloud_worker import WorkerLease
        from moodify_runtime.utils import utc_now_iso

        wl = WorkerLease(lease_id="L1", worker_id="W1", task_ids=["t1"],
                         acquired_at=utc_now_iso(),
                         ttl_seconds=999999.0)
        assert wl.is_expired() is False

    def test_expired_lease_is_expired(self):
        from moodify_runtime.cloud_worker import WorkerLease

        wl = WorkerLease(lease_id="L1", worker_id="W1", task_ids=["t1"],
                         acquired_at="2020-01-01T00:00:00Z",
                         ttl_seconds=120.0)
        assert wl.is_expired() is True

    def test_released_overrides_timestamp(self):
        from moodify_runtime.cloud_worker import WorkerLease
        wl = WorkerLease(lease_id="L1", worker_id="W1", task_ids=["t1"],
                         acquired_at="2026-01-01T00:00:00Z",
                         ttl_seconds=999999.0, released=True)
        assert wl.is_expired() is True


# ═══════════════════════════════════════════════════════════════════════
# TestLatestRunSelection
# ═══════════════════════════════════════════════════════════════════════


class TestLatestRunSelection:
    """find_latest_run_dir validates candidates, not just name-sorts."""

    def test_picks_dir_with_manifest(self, tmp_path):
        from moodify_runtime.utils import find_latest_run_dir

        (tmp_path / "run_01").mkdir()
        (tmp_path / "run_02").mkdir()
        (tmp_path / "run_02" / "manifest.csv").write_text("run_id\nr2\n")

        result = find_latest_run_dir(tmp_path)
        assert result.name == "run_02"

    def test_skips_dir_without_manifest(self, tmp_path):
        from moodify_runtime.utils import find_latest_run_dir

        (tmp_path / "run_01").mkdir()
        (tmp_path / "run_02").mkdir()
        (tmp_path / "run_01" / "manifest.csv").write_text("run_id\nr1\n")

        result = find_latest_run_dir(tmp_path)
        assert result.name == "run_01"

    def test_skips_files(self, tmp_path):
        from moodify_runtime.utils import find_latest_run_dir

        (tmp_path / "not_a_dir").write_text("text")
        (tmp_path / "run_01").mkdir()
        (tmp_path / "run_01" / "manifest.csv").write_text("run_id\nr1\n")

        result = find_latest_run_dir(tmp_path)
        assert result.name == "run_01"

    def test_no_runs_raises(self, tmp_path):
        from moodify_runtime.utils import find_latest_run_dir

        with pytest.raises(FileNotFoundError, match="No run directory"):
            find_latest_run_dir(tmp_path)

    def test_no_valid_runs_raises(self, tmp_path):
        from moodify_runtime.utils import find_latest_run_dir

        (tmp_path / "run_01").mkdir()  # No manifest.csv
        (tmp_path / "run_02").mkdir()  # No manifest.csv

        with pytest.raises(FileNotFoundError, match="No run directory"):
            find_latest_run_dir(tmp_path)

    def test_nonexistent_root_raises(self, tmp_path):
        from moodify_runtime.utils import find_latest_run_dir

        with pytest.raises(FileNotFoundError):
            find_latest_run_dir(tmp_path / "nonexistent")
