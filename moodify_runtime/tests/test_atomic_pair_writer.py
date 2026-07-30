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

    def test_failure_between_promotions_restores_complete_previous_pair(
        self, out_dir, monkeypatch
    ):
        writer = AtomicPairWriter(out_dir)
        writer.write(
            {"generation": "old"}, "summary.json", "generation: old\n", "summary.md"
        )

        import moodify_runtime.atomic_pair_writer as module
        real_move = module.shutil.move
        calls = {"count": 0}

        def fail_second_move(source, target):
            calls["count"] += 1
            if calls["count"] == 2:
                raise OSError("injected between promotions")
            return real_move(source, target)

        monkeypatch.setattr(module.shutil, "move", fail_second_move)
        with pytest.raises(OSError, match="between promotions"):
            writer.write(
                {"generation": "new"}, "summary.json", "generation: new\n", "summary.md"
            )

        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["generation"] == "old"
        assert "generation: old" in markdown

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


# ═══════════════════════════════════════════════════════════════════════
# Rework Expansion — P0 fault matrix boundaries
# ═══════════════════════════════════════════════════════════════════════


class TestFaultInjectionBeforeBackup:
    """Interruption BEFORE first target is backed up to .prev."""

    def test_failure_before_json_backup_restores_nothing(
        self, out_dir, monkeypatch
    ):
        writer = AtomicPairWriter(out_dir)
        writer.write(
            {"gen": "old"}, "summary.json", "generation: old\n", "summary.md"
        )
        old_json_content = (out_dir / "summary.json").read_bytes()
        old_md_content = (out_dir / "summary.md").read_bytes()

        import moodify_runtime.atomic_pair_writer as module
        real_rename = module.Path.rename

        def fail_first_rename(target, bak):
            raise OSError("injected before backup")

        monkeypatch.setattr(module.Path, "rename", fail_first_rename)
        with pytest.raises(OSError, match="before backup"):
            writer.write(
                {"gen": "new"}, "summary.json", "generation: new\n", "summary.md"
            )

        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == "old"
        assert "generation: old" in markdown
        assert (out_dir / "summary.json").read_bytes() == old_json_content
        assert (out_dir / "summary.md").read_bytes() == old_md_content

    def test_failure_before_md_backup_restores_complete_old(
        self, out_dir, monkeypatch
    ):
        writer = AtomicPairWriter(out_dir)
        writer.write(
            {"gen": "old"}, "summary.json", "generation: old\n", "summary.md"
        )

        import moodify_runtime.atomic_pair_writer as module
        real_rename = module.Path.rename
        rename_calls = {"count": 0}

        def fail_md_rename(target, bak):
            rename_calls["count"] += 1
            if rename_calls["count"] == 2:  # second pair in backup loop = md
                raise OSError("injected before md backup")
            return real_rename(target, bak)

        monkeypatch.setattr(module.Path, "rename", fail_md_rename)
        with pytest.raises(OSError, match="before md backup"):
            writer.write(
                {"gen": "new"}, "summary.json", "generation: new\n", "summary.md"
            )

        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == "old"
        assert "generation: old" in markdown


class TestFaultInjectionAfterBackup:
    """Interruption AFTER both .prev backups but before any promotion."""

    def test_failure_after_backup_before_json_promotion(
        self, out_dir, monkeypatch
    ):
        writer = AtomicPairWriter(out_dir)
        writer.write(
            {"gen": "old"}, "summary.json", "generation: old\n", "summary.md"
        )

        import moodify_runtime.atomic_pair_writer as module
        real_move = module.shutil.move
        move_calls = {"count": 0}

        def fail_first_move(source, target):
            move_calls["count"] += 1
            if move_calls["count"] == 1:  # JSON move
                raise OSError("injected after backup before JSON promotion")
            return real_move(source, target)

        monkeypatch.setattr(module.shutil, "move", fail_first_move)
        with pytest.raises(OSError, match="after backup"):
            writer.write(
                {"gen": "new"}, "summary.json", "generation: new\n", "summary.md"
            )

        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == "old"
        assert "generation: old" in markdown

    def test_failure_after_json_promotion_before_md_promotion(
        self, out_dir, monkeypatch
    ):
        writer = AtomicPairWriter(out_dir)
        writer.write(
            {"gen": "old"}, "summary.json", "generation: old\n", "summary.md"
        )

        import moodify_runtime.atomic_pair_writer as module
        real_move = module.shutil.move
        move_calls = {"count": 0}

        def fail_second_move(source, target):
            move_calls["count"] += 1
            if move_calls["count"] == 2:  # MD move
                raise OSError("injected between promotions")
            return real_move(source, target)

        monkeypatch.setattr(module.shutil, "move", fail_second_move)
        with pytest.raises(OSError, match="between promotions"):
            writer.write(
                {"gen": "new"}, "summary.json", "generation: new\n", "summary.md"
            )

        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == "old"
        assert "generation: old" in markdown


class TestFaultInjectionAfterPromotion:
    """Interruption AFTER both files promoted but before marker removal."""

    def test_failure_after_both_promoted_before_marker_removal(
        self, out_dir, monkeypatch
    ):
        writer = AtomicPairWriter(out_dir)
        writer.write(
            {"gen": "old"}, "summary.json", "generation: old\n", "summary.md"
        )

        import moodify_runtime.atomic_pair_writer as module
        real_unlink = module.Path.unlink

        def fail_unlink(self_obj):
            raise OSError("injected after promotion before marker removal")

        monkeypatch.setattr(module.Path, "unlink", fail_unlink)
        with pytest.raises(OSError, match="before marker removal"):
            writer.write(
                {"gen": "new"}, "summary.json", "generation: new\n", "summary.md"
            )

        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == "new"
        assert "generation: new" in markdown

    def test_recover_completes_after_failure_after_both_promoted(
        self, out_dir, monkeypatch
    ):
        writer = AtomicPairWriter(out_dir)
        writer.write(
            {"gen": "old"}, "summary.json", "generation: old\n", "summary.md"
        )

        import moodify_runtime.atomic_pair_writer as module
        real_unlink = module.Path.unlink
        failed = {"once": False}

        def fail_unlink_once(self_obj):
            if not failed["once"] and self_obj.name == ".tx_active":
                failed["once"] = True
                raise OSError("injected")
            return real_unlink(self_obj)

        monkeypatch.setattr(module.Path, "unlink", fail_unlink_once)
        with pytest.raises(OSError):
            writer.write(
                {"gen": "new"}, "summary.json", "generation: new\n", "summary.md"
            )

        # The pair should already be current (both moves completed)
        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == "new"

        # Retry: second write should recover and produce clean state
        r3 = writer.write(
            {"gen": "v3"}, "summary.json", "generation: v3\n", "summary.md"
        )
        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == "v3"
        assert r3["status"] == "ok"


class TestFaultInjectionDuringRecovery:
    """Interruption during recovery boundaries."""

    def test_recovery_fails_on_partial_staging_with_prev_restored(
        self, out_dir
    ):
        writer = AtomicPairWriter(out_dir)
        writer.write(
            {"gen": "old"}, "summary.json", "generation: old\n", "summary.md"
        )

        # Create orphan with valid JSON but no MD
        orphan = out_dir / ".pair_tmp_recovery"
        orphan.mkdir()
        (orphan / "summary.json").write_text(
            json.dumps({"gen": "orphan"}) + "\n", encoding="utf-8"
        )
        (orphan / ".tx_active").write_text(
            json.dumps({"status": "committing"}), encoding="utf-8"
        )
        # No MD file — incomplete staging, rollback

        writer2 = AtomicPairWriter(out_dir)
        result = writer2.write(
            {"gen": "new"}, "summary.json", "generation: new\n", "summary.md"
        )
        assert result["status"] == "ok"
        assert result["recovery"] is not None
        detail = result["recovery"]["details"][0]
        assert detail["action"] == "rolled_back"
        # previous_pair_restored is False when no .prev files exist (first-write
        # case), but the original current pair is preserved by being left in place

        data, markdown = writer2.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == "new"
        assert "generation: new" in markdown

    def test_multiple_orphans_all_cleaned(self, out_dir, sample_json, sample_md):
        for i in range(3):
            orphan = out_dir / f".pair_tmp_{i}"
            orphan.mkdir()
            (orphan / "summary.json").write_text(
                json.dumps({"gen": i}) + "\n", encoding="utf-8"
            )
            (orphan / "summary.md").write_text(f"# orphan {i}\n", encoding="utf-8")
            (orphan / ".tx_active").write_text(
                json.dumps({"status": "committing"}), encoding="utf-8"
            )

        writer = AtomicPairWriter(out_dir)
        result = writer.write(sample_json, "summary.json", sample_md, "summary.md")
        assert result["recovery"]["orphaned_transactions"] == 3
        assert len(list(out_dir.glob(".pair_tmp_*"))) == 0

    def test_repeated_recovery_idempotent(self, out_dir):
        orphan = out_dir / ".pair_tmp_rpt"
        orphan.mkdir()
        (orphan / "summary.json").write_text(
            json.dumps({"x": 1}) + "\n", encoding="utf-8"
        )
        (orphan / "summary.md").write_text("# rpt\n", encoding="utf-8")
        (orphan / ".tx_active").write_text(
            json.dumps({"status": "committing"}), encoding="utf-8"
        )

        writer = AtomicPairWriter(out_dir)
        r1 = writer.recover("summary.json", "summary.md")
        assert r1 is not None
        r2 = writer.recover("summary.json", "summary.md")
        assert r2 is None  # No orphans left


class TestReadCurrentPairContract:
    """read_current_pair() fails closed when no complete pair exists."""

    def test_fails_closed_no_files_exist(self, out_dir):
        writer = AtomicPairWriter(out_dir)
        with pytest.raises(RuntimeError, match="No complete current"):
            writer.read_current_pair("summary.json", "summary.md")

    def test_fails_closed_json_only_exists(self, out_dir):
        writer = AtomicPairWriter(out_dir)
        (out_dir / "summary.json").write_text(
            json.dumps({"x": 1}) + "\n", encoding="utf-8"
        )
        with pytest.raises(RuntimeError, match="No complete current"):
            writer.read_current_pair("summary.json", "summary.md")

    def test_fails_closed_md_only_exists(self, out_dir):
        writer = AtomicPairWriter(out_dir)
        (out_dir / "summary.md").write_text("# only md\n", encoding="utf-8")
        with pytest.raises(RuntimeError, match="No complete current"):
            writer.read_current_pair("summary.json", "summary.md")

    def test_fails_closed_empty_md(self, out_dir):
        writer = AtomicPairWriter(out_dir)
        (out_dir / "summary.json").write_text(
            json.dumps({"x": 1}) + "\n", encoding="utf-8"
        )
        (out_dir / "summary.md").write_text("", encoding="utf-8")
        with pytest.raises(RuntimeError, match="empty"):
            writer.read_current_pair("summary.json", "summary.md")

    def test_recovers_orphan_before_exposing(self, out_dir):
        """read_current_pair recovers a complete staged pair before exposing."""
        orphan = out_dir / ".pair_tmp_rcp"
        orphan.mkdir()
        (orphan / "summary.json").write_text(
            json.dumps({"gen": "recovered"}) + "\n", encoding="utf-8"
        )
        (orphan / "summary.md").write_text("# recovered\n", encoding="utf-8")
        (orphan / ".tx_active").write_text(
            json.dumps({"status": "committing"}), encoding="utf-8"
        )

        writer = AtomicPairWriter(out_dir)
        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == "recovered"
        assert "recovered" in markdown
        assert not orphan.exists()

    def test_fails_closed_orphan_with_invalid_staging(self, out_dir):
        """Recovery rolls back and reader fails closed on invalid staging."""
        orphan = out_dir / ".pair_tmp_bad"
        orphan.mkdir()
        (orphan / ".tx_active").write_text(
            json.dumps({"status": "committing"}), encoding="utf-8"
        )
        # No JSON, no MD — incomplete staging

        writer = AtomicPairWriter(out_dir)
        with pytest.raises(RuntimeError, match="No complete current"):
            writer.read_current_pair("summary.json", "summary.md")
        assert not orphan.exists()


class TestFirstEverWrite:
    """First write with no previous pair handles edge cases correctly."""

    def test_stale_prev_files_ignored_on_first_write(
        self, out_dir, sample_json, sample_md
    ):
        """Stale .prev files from an unrelated context do not affect first write on clean dir."""
        # Write pair with .prev already present (simulating stale state)
        (out_dir / "summary.json.prev").write_text(
            json.dumps({"stale": True}) + "\n", encoding="utf-8"
        )
        (out_dir / "summary.md.prev").write_text("# stale\n", encoding="utf-8")

        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")

        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["count"] == 2
        assert "Test Summary" in markdown

    def test_first_write_with_no_existing_targets(
        self, out_dir, sample_json, sample_md
    ):
        writer = AtomicPairWriter(out_dir)
        result = writer.write(sample_json, "summary.json", sample_md, "summary.md")
        assert result["status"] == "ok"
        assert result["recovery"] is None
        assert not (out_dir / "summary.json.prev").exists()

    def test_first_write_after_recovery_behaves_like_replacement(
        self, out_dir, sample_json, sample_md
    ):
        writer = AtomicPairWriter(out_dir)
        writer.write(sample_json, "summary.json", sample_md, "summary.md")

        # Second write is a replacement
        new_json = {"gen": 2, "count": 2}
        new_md = "# Gen 2\n"
        writer.write(new_json, "summary.json", new_md, "summary.md")

        assert (out_dir / "summary.json.prev").is_file()
        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == 2


class TestWindowsSameVolume:
    """os.replace is atomic on same volume; tests verify clean behaviour."""

    def test_retry_after_recovery_converges(self, out_dir):
        """After any interruption, write converges to clean state."""
        writer = AtomicPairWriter(out_dir)
        for i in range(10):
            j = {"i": i}
            m = f"# Run {i}\n"
            result = writer.write(j, "summary.json", m, "summary.md")
            assert result["status"] == "ok"

        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["i"] == 9
        assert "# Run 9" in markdown
        assert len(list(out_dir.glob(".pair_tmp_*"))) == 0

    def test_partial_temp_file_not_mistaken_for_staging(self, out_dir):
        """A plain .tmp file (not a staging directory) is harmless."""
        (out_dir / ".pair_tmp_plain").write_text("not a dir", encoding="utf-8")

        writer = AtomicPairWriter(out_dir)
        result = writer.write(
            {"gen": 1}, "summary.json", "# Gen 1\n", "summary.md"
        )
        assert result["status"] == "ok"
        # The file (not directory) doesn't match glob for staging dirs
        # but shouldn't break anything either
        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["gen"] == 1

    def test_concurrent_staging_dirs_all_recovered(self, out_dir, sample_json, sample_md):
        """Multiple staging dirs simulate multiple interrupted runs."""
        for i in range(5):
            stage = out_dir / f".pair_tmp_stage_{i}"
            stage.mkdir()
            (stage / "summary.json").write_text(
                json.dumps({"stage": i}) + "\n", encoding="utf-8"
            )
            (stage / "summary.md").write_text(f"# Stage {i}\n", encoding="utf-8")
            (stage / ".tx_active").write_text(
                json.dumps({"status": "committing"}), encoding="utf-8"
            )

        writer = AtomicPairWriter(out_dir)
        result = writer.write(sample_json, "summary.json", sample_md, "summary.md")
        assert result["recovery"]["orphaned_transactions"] == 5
        assert len(list(out_dir.glob(".pair_tmp_*"))) == 0
        data, markdown = writer.read_current_pair("summary.json", "summary.md")
        assert data["count"] == 2
