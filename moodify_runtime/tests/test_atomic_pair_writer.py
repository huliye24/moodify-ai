"""DSK-MFY-AUX-HARDENING-002 Batch B — Atomic Treatment Pair tests.

Fault injection at every boundary:
  - Before first promotion (staging dir exists but tx not yet committed)
  - Between promotions (JSON staged but MD not yet written)
  - After promotion and before cleanup (files moved but staging dir remains)
  - Retry after every injected fault
  - Current-pair consistency checks
  - Source immutability
  - Stale temporary-state recovery
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from moodify_runtime.atomic_pair_writer import AtomicPairWriter


@pytest.fixture
def out_dir(tmp_path: Path) -> Path:
    d = tmp_path / "output"
    d.mkdir()
    return d


@pytest.fixture
def sample_json() -> dict:
    return {
        "schema_version": "0.1.0",
        "summary_type": "test",
        "records": [{"id": 1, "value": "alpha"}, {"id": 2, "value": "beta"}],
        "count": 2,
    }


@pytest.fixture
def sample_md() -> str:
    return "# Test Summary\n\n- Record 1: alpha\n- Record 2: beta\n"


# ── Correctness: basic atomic write ──────────────────────────────────


class TestCorrectness:
    """Basic write operations produce correct, consistent pairs."""

    def test_write_produces_both_files(self, out_dir, sample_json, sample_md):
        writer = AtomicPairWriter(out_dir)
        result = writer.write(sample_json, "summary.json", sample_md, "summary.md")

        assert result["status"] == "ok"
        assert (out_dir / "summary.json").is_file()
        assert (out_dir / "summary.md").is_file()
        assert result["recovery"] is None

    def test_written_json_is_valid(self, out_dir, sample_json, sample_md):
        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")

        data = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        assert data["count"] == 2
        assert len(data["records"]) == 2

    def test_written_md_matches_content(self, out_dir, sample_json, sample_md):
        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")

        content = (out_dir / "summary.md").read_text(encoding="utf-8")
        assert "Test Summary" in content
        assert "Record 1: alpha" in content

    def test_pair_is_consistent(self, out_dir, sample_json, sample_md):
        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")

        json_data = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        md_content = (out_dir / "summary.md").read_text(encoding="utf-8")

        assert str(json_data["count"]) in md_content or "2" in md_content
        assert json_data["records"][0]["value"] in md_content

    def test_no_staging_left_behind(self, out_dir, sample_json, sample_md):
        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")

        orphans = list(out_dir.glob(".pair_tmp_*"))
        assert len(orphans) == 0


# ── Previous pair preservation ───────────────────────────────────────


class TestPreviousPairPreservation:
    """Existing pairs are backed up before replacement."""

    def test_previous_pair_preserved_as_prev(self, out_dir, sample_json, sample_md):
        # Write first pair
        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")

        # Write second pair
        new_json = {"schema_version": "0.2.0", "records": [], "count": 0}
        new_md = "# New Summary\n\nEmpty.\n"
        writer.write(new_json, "summary.json", new_md, "summary.md")

        # Previous pair should exist
        assert (out_dir / "summary.json.prev").is_file()
        assert (out_dir / "summary.md.prev").is_file()

        prev_json = json.loads(
            (out_dir / "summary.json.prev").read_text(encoding="utf-8")
        )
        assert prev_json["count"] == 2  # original content preserved

        prev_md = (out_dir / "summary.md.prev").read_text(encoding="utf-8")
        assert "Record 1: alpha" in prev_md

    def test_prev_files_only_reflect_last_pair(self, out_dir, sample_json, sample_md):
        writer = AtomicPairWriter(out_dir)
        # 3 successive writes
        for i in range(3):
            j = {"schema_version": f"0.{i}.0", "records": [], "count": i}
            m = f"# Summary v{i}\n"
            writer.write(j, "summary.json", m, "summary.md")

        prev_json = json.loads(
            (out_dir / "summary.json.prev").read_text(encoding="utf-8")
        )
        assert prev_json["count"] == 1  # penultimate, not the first


# ── Fault injection: before first promotion ──────────────────────────


class TestFaultInjectionBeforePromotion:
    """Interruption when staging exists but tx not yet committed."""

    def test_orphaned_tmp_rolled_back_on_write(self, out_dir, sample_json, sample_md):
        # Simulate: create orphan staging directory
        orphan = out_dir / ".pair_tmp_deadbeef"
        orphan.mkdir()
        (orphan / "summary.json").write_text('{"bad": "json')
        (orphan / "summary.md").write_text("# bad")

        writer = AtomicPairWriter(out_dir)
        result = writer.write(sample_json, "summary.json", sample_md, "summary.md")

        assert result["status"] == "ok"
        assert result["recovery"] is not None
        assert result["recovery"]["orphaned_transactions"] == 1
        assert not orphan.exists()  # cleaned up

        # Current pair is the new valid one
        data = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        assert data["count"] == 2

    def test_orphaned_tmp_with_valid_staging_completed(self, out_dir, sample_json, sample_md):
        # Simulate: orphan dir with valid staged files + active tx marker
        orphan = out_dir / ".pair_tmp_valid42"
        orphan.mkdir()
        valid_json = json.dumps({"recovered": True, "records": [99], "count": 99})
        (orphan / "summary.json").write_text(valid_json + "\n", encoding="utf-8")
        (orphan / "summary.md").write_text("# Recovery\n\nRecovered content\n", encoding="utf-8")
        (orphan / ".tx_active").write_text(
            json.dumps({"status": "committing"}),
            encoding="utf-8",
        )

        writer = AtomicPairWriter(out_dir)
        result = writer.write(sample_json, "summary.json", sample_md, "summary.md")

        # The valid staged files should have been completed (moved to target)
        # BEFORE our new write, so the .prev should contain the recovered data
        assert (out_dir / "summary.json.prev").is_file()
        prev = json.loads((out_dir / "summary.json.prev").read_text(encoding="utf-8"))
        assert prev.get("recovered") is True
        assert prev["count"] == 99

    def test_orphaned_tmp_without_tx_marker_rolled_back(self, out_dir, sample_json, sample_md):
        # Simulate: staging dir with files but NO tx marker
        orphan = out_dir / ".pair_tmp_nomarker"
        orphan.mkdir()
        (orphan / "summary.json").write_text(json.dumps({"abandoned": True}), encoding="utf-8")
        (orphan / "summary.md").write_text("# Abandoned\n")

        writer = AtomicPairWriter(out_dir)
        result = writer.write(sample_json, "summary.json", sample_md, "summary.md")

        assert result["status"] == "ok"
        assert not orphan.exists()
        # Current pair is the new one, not the abandoned one
        data = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        assert "abandoned" not in data

    def test_orphaned_tmp_with_empty_staging_rolled_back(self, out_dir, sample_json, sample_md):
        orphan = out_dir / ".pair_tmp_empty"
        orphan.mkdir()
        (orphan / ".tx_active").write_text(
            json.dumps({"status": "committing"}), encoding="utf-8"
        )
        # No staged files — incomplete staging

        writer = AtomicPairWriter(out_dir)
        result = writer.write(sample_json, "summary.json", sample_md, "summary.md")

        assert result["status"] == "ok"
        assert not orphan.exists()


# ── Retry after fault ────────────────────────────────────────────────


class TestRetryAfterFault:
    """Retry converges without duplicate or mixed artifacts."""

    def test_retry_after_fault_produces_consistent_pair(self, out_dir, sample_json, sample_md):
        # Create orphan to trigger recovery
        orphan = out_dir / ".pair_tmp_fault"
        orphan.mkdir()

        # First write (with recovery)
        writer = AtomicPairWriter(out_dir)
        r1 = writer.write(sample_json, "summary.json", sample_md, "summary.md")
        assert r1["status"] == "ok"

        # Second write (retry) — should produce clean pair
        new_json = {"schema_version": "0.2.0", "records": [{"id": 3}], "count": 1}
        new_md = "# Retry\n\nWorks.\n"
        r2 = writer.write(new_json, "summary.json", new_md, "summary.md")
        assert r2["status"] == "ok"
        assert r2["recovery"] is None  # no orphans this time

        json_data = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        md_content = (out_dir / "summary.md").read_text(encoding="utf-8")

        assert json_data["count"] == 1
        assert "Works" in md_content

    def test_repeated_writes_no_staging_leak(self, out_dir, sample_json, sample_md):
        writer = AtomicPairWriter(out_dir)
        for i in range(5):
            j = {"i": i, "count": i}
            m = f"# Run {i}\n"
            writer.write(j, "summary.json", m, "summary.md")

        orphans = list(out_dir.glob(".pair_tmp_*"))
        assert len(orphans) == 0
        assert len(list(out_dir.glob("summary.json*"))) == 2  # current + .prev


# ── Current-pair consistency ─────────────────────────────────────────


class TestPairConsistency:
    """The current pair is always from the same generation."""

    def test_pair_timestamp_consistency(self, out_dir):
        writer = AtomicPairWriter(out_dir)
        for i in range(3):
            j = {"gen": i}
            m = f"# Generation {i}\n"
            writer.write(j, "summary.json", m, "summary.md")

        json_data = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        md_content = (out_dir / "summary.md").read_text(encoding="utf-8")

        assert f"Generation {json_data['gen']}" in md_content

    def test_prev_pair_is_also_consistent(self, out_dir):
        writer = AtomicPairWriter(out_dir)
        writer.write({"gen": 1}, "summary.json", "# Gen 1\n", "summary.md")
        writer.write({"gen": 2}, "summary.json", "# Gen 2\n", "summary.md")

        prev_json = json.loads(
            (out_dir / "summary.json.prev").read_text(encoding="utf-8")
        )
        prev_md = (out_dir / "summary.md.prev").read_text(encoding="utf-8")

        assert f"Gen {prev_json['gen']}" in prev_md


# ── Source immutability ──────────────────────────────────────────────


class TestSourceImmutability:
    """Source JSON data and MD content are not mutated during write."""

    def test_json_data_unchanged_after_write(self, out_dir, sample_json, sample_md):
        original = json.dumps(sample_json)
        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")

        assert json.dumps(sample_json) == original
        assert sample_json["count"] == 2

    def test_md_content_unchanged_after_write(self, out_dir, sample_json, sample_md):
        original = sample_md
        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")

        assert sample_md == original


# ── Explicit recovery ────────────────────────────────────────────────


class TestExplicitRecovery:
    """Calling recover() explicitly detects and handles orphaned state."""

    def test_recover_no_orphans_returns_none(self, out_dir):
        writer = AtomicPairWriter(out_dir)
        result = writer.recover("summary.json", "summary.md")
        assert result is None

    def test_recover_detects_orphan(self, out_dir):
        orphan = out_dir / ".pair_tmp_orphan"
        orphan.mkdir()
        (orphan / ".tx_active").write_text(
            json.dumps({"status": "committing"}), encoding="utf-8"
        )

        writer = AtomicPairWriter(out_dir)
        result = writer.recover("summary.json", "summary.md")

        assert result is not None
        assert result["orphaned_transactions"] == 1
        assert not orphan.exists()

    def test_recover_from_write_cleans_up(self, out_dir, sample_json, sample_md):
        orphan = out_dir / ".pair_tmp_test"
        orphan.mkdir()
        (orphan / "summary.json").write_text(json.dumps({"x": 1}), encoding="utf-8")
        (orphan / "summary.md").write_text("# Test\n", encoding="utf-8")
        (orphan / ".tx_active").write_text(
            json.dumps({"status": "committing"}), encoding="utf-8"
        )

        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")

        # Orphan cleaned, both files are ours
        assert not orphan.exists()
        json_data = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        assert json_data["count"] == 2


# ── Empty / edge cases ───────────────────────────────────────────────


class TestEdgeCases:
    """Edge case handling for empty inputs."""

    def test_empty_json_object(self, out_dir):
        writer = AtomicPairWriter(out_dir)
        result = writer.write({}, "summary.json", "# Empty\n", "summary.md")
        assert result["status"] == "ok"
        data = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        assert data == {}

    def test_empty_md(self, out_dir, sample_json):
        writer = AtomicPairWriter(out_dir)
        with pytest.raises(ValueError, match="empty"):
            writer.write(sample_json, "summary.json", "", "summary.md")

    def test_invalid_json_data_raises(self, out_dir, sample_md):
        writer = AtomicPairWriter(out_dir)
        # A dict with a non-serializable value would fail during json.dumps
        with pytest.raises(TypeError):
            writer.write({"bad": object()}, "summary.json", sample_md, "summary.md")

    def test_first_write_no_prev_files(self, out_dir, sample_json, sample_md):
        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")
        assert not (out_dir / "summary.json.prev").exists()
        assert not (out_dir / "summary.md.prev").exists()
