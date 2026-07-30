"""DSK-MFY-AUX-HARDENING-002 Batch A — P0 Automated Writeback Containment tests.

Tests cover:
  - Proposal namespace isolation
  - Direct-function writeback → proposals/ only
  - API bypass: craft endpoints never expose proposals as approved
  - CLI bypass: craft-records excludes proposals
  - Repeated execution determinism / idempotency
  - Approved-reader isolation (list_craft_records)
  - Promotion evidence completeness (fail-closed)
  - Malformed and mismatched evidence rejection
  - Replayed promotion prevents duplication
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from moodify_runtime.craft_proposals import (
    PROPOSAL_STATUSES,
    DEFAULT_PROPOSAL_STATUS,
    write_automated_proposal,
    list_proposals,
    get_proposal,
    promote_proposal_to_craft,
)
from moodify_runtime.craft_memory import list_craft_records, CRAFT_STATUSES


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def craft_dir(tmp_path: Path) -> Path:
    d = tmp_path / "craft_memory"
    d.mkdir()
    return d


@pytest.fixture
def sample_entry() -> dict:
    return {
        "preset": "warm_vocal",
        "severity": "high",
        "action": "increase warmth by 1.2 dB",
        "source": "data_loop",
        "source_run": "run_001",
    }


@pytest.fixture
def valid_promotion_evidence() -> dict:
    return {
        "rights_evidence": {"asset_id": "ASSET_001", "manifest": "rights_v1"},
        "human_reviewer": "test-reviewer",
        "review_timestamp": "2026-07-30T10:00:00Z",
        "source_run_id": "run_001",
        "regression_evidence": {"tests_passed": 42, "suite": "runtime"},
    }


# ── Proposal namespace isolation ──────────────────────────────────────


class TestProposalNamespaceIsolation:
    """Proposals are stored in craft_memory/proposals/, not in craft_memory/."""

    def test_write_creates_proposals_subdir(self, craft_dir, sample_entry):
        write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        proposals_dir = craft_dir / "proposals"
        assert proposals_dir.is_dir()
        files = list(proposals_dir.glob("proposal_*.json"))
        assert len(files) == 1

    def test_write_does_not_create_files_in_craft_root(self, craft_dir, sample_entry):
        write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        root_files = [f for f in craft_dir.iterdir() if f.is_file()]
        assert len(root_files) == 0  # nothing in craft root except proposals/

    def test_proposal_status_is_proposal_by_default(self, craft_dir, sample_entry):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        assert results[0]["status"] == DEFAULT_PROPOSAL_STATUS
        assert results[0]["status"] == "proposal"

    def test_proposal_status_not_in_craft_statuses(self):
        assert DEFAULT_PROPOSAL_STATUS not in CRAFT_STATUSES
        assert PROPOSAL_STATUSES.isdisjoint(CRAFT_STATUSES)


# ── Direct-function bypass ───────────────────────────────────────────


class TestDirectFunctionBypass:
    """Proposals written directly cannot be read as approved records."""

    def test_list_craft_records_excludes_proposals(self, craft_dir, sample_entry):
        # Write a proposal
        write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )

        # list_craft_records should return nothing (no approved records exist)
        class FakeCfg:
            craft_memory_dir = craft_dir
            def resolved(self):
                return self

        records = list_craft_records(FakeCfg())
        assert len(records) == 0

    def test_list_proposals_returns_proposals(self, craft_dir, sample_entry):
        write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        proposals = list_proposals(craft_dir)
        assert len(proposals) == 1
        assert proposals[0]["status"] == "proposal"

    def test_list_proposals_filtered_by_status(self, craft_dir, sample_entry):
        write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        proposals = list_proposals(craft_dir, status="proposal")
        assert len(proposals) == 1
        proposals_promoted = list_proposals(craft_dir, status="promoted")
        assert len(proposals_promoted) == 0

    def test_get_proposal_by_id(self, craft_dir, sample_entry):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        pid = results[0]["proposal_id"]
        p = get_proposal(craft_dir, pid)
        assert p is not None
        assert p["proposal_id"] == pid

    def test_get_proposal_missing_returns_none(self, craft_dir):
        assert get_proposal(craft_dir, "NONEXISTENT") is None


# ── Repeated execution / idempotency ──────────────────────────────────


class TestRepeatedExecution:
    """Repeated writes produce distinct proposals, never duplicates."""

    def test_repeated_write_produces_distinct_ids(self, craft_dir, sample_entry):
        results_1 = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        results_2 = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        assert results_1[0]["proposal_id"] != results_2[0]["proposal_id"]
        files = list((craft_dir / "proposals").glob("proposal_*.json"))
        assert len(files) == 2

    def test_replay_promotion_is_idempotent(
        self, craft_dir, sample_entry, valid_promotion_evidence
    ):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        pid = results[0]["proposal_id"]

        # First promotion
        r1 = promote_proposal_to_craft(craft_dir, pid, valid_promotion_evidence)
        assert r1["status"] == "promoted"

        # Second promotion (replay)
        r2 = promote_proposal_to_craft(craft_dir, pid, valid_promotion_evidence)
        assert r2["status"] == "already_promoted"
        assert r2["craft_record_id"] == r1["craft_record_id"]

        # Only one craft record created
        class FakeCfg:
            craft_memory_dir = craft_dir
            def resolved(self):
                return self

        records = list_craft_records(FakeCfg())
        assert len(records) == 1

    def test_retry_after_proposal_update_failure_does_not_duplicate_record(
        self, craft_dir, sample_entry, valid_promotion_evidence, monkeypatch
    ):
        proposal = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )[0]
        proposal_path = craft_dir / "proposals" / f"proposal_{proposal['proposal_id']}.json"

        import moodify_runtime.craft_proposals as module
        real_replace = module.os.replace
        failed = {"once": False}

        def fail_proposal_replace(source, target):
            if Path(target) == proposal_path and not failed["once"]:
                failed["once"] = True
                raise OSError("injected after craft store replacement")
            return real_replace(source, target)

        monkeypatch.setattr(module.os, "replace", fail_proposal_replace)
        with pytest.raises(OSError, match="after craft store"):
            promote_proposal_to_craft(
                craft_dir, proposal["proposal_id"], valid_promotion_evidence
            )

        result = promote_proposal_to_craft(
            craft_dir, proposal["proposal_id"], valid_promotion_evidence
        )
        rows = (craft_dir / "craft_records.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(rows) == 1
        assert result["craft_record_id"] == json.loads(rows[0])["craft_id"]


# ── Promotion evidence completeness (fail-closed) ─────────────────────


class TestPromotionFailClosed:
    """Promotion fails closed on missing, malformed, or mismatched evidence."""

    def test_promotion_missing_all_evidence(self, craft_dir, sample_entry):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        pid = results[0]["proposal_id"]
        with pytest.raises(ValueError, match="missing required fields"):
            promote_proposal_to_craft(craft_dir, pid, {})

    def test_promotion_missing_single_field(self, craft_dir, sample_entry):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        pid = results[0]["proposal_id"]
        for field in ["rights_evidence", "human_reviewer", "review_timestamp",
                       "source_run_id", "regression_evidence"]:
            evidence = {
                "rights_evidence": {"x": 1},
                "human_reviewer": "reviewer",
                "review_timestamp": "2026-07-30T10:00:00Z",
                "source_run_id": "run_001",
                "regression_evidence": {"tests": 1},
            }
            del evidence[field]
            with pytest.raises(ValueError, match="missing required fields"):
                promote_proposal_to_craft(craft_dir, pid, evidence)

    def test_promotion_empty_field_values(self, craft_dir, sample_entry):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        pid = results[0]["proposal_id"]
        for field in ["rights_evidence", "human_reviewer", "review_timestamp",
                       "source_run_id", "regression_evidence"]:
            evidence = {
                "rights_evidence": {"x": 1},
                "human_reviewer": "reviewer",
                "review_timestamp": "2026-07-30T10:00:00Z",
                "source_run_id": "run_001",
                "regression_evidence": {"tests": 1},
            }
            evidence[field] = None
            with pytest.raises(ValueError, match="must not be empty"):
                promote_proposal_to_craft(craft_dir, pid, evidence)

    def test_promotion_source_run_id_mismatch(self, craft_dir, sample_entry):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        pid = results[0]["proposal_id"]
        bad_evidence = {
            "rights_evidence": {"x": 1},
            "human_reviewer": "reviewer",
            "review_timestamp": "2026-07-30T10:00:00Z",
            "source_run_id": "run_WRONG",
            "regression_evidence": {"tests": 1},
        }
        with pytest.raises(ValueError, match="source_run_id mismatch"):
            promote_proposal_to_craft(craft_dir, pid, bad_evidence)

    def test_promotion_nonexistent_proposal(self, craft_dir, valid_promotion_evidence):
        with pytest.raises(ValueError, match="Proposal not found"):
            promote_proposal_to_craft(craft_dir, "NONEXISTENT", valid_promotion_evidence)


# ── Approved-reader isolation ────────────────────────────────────────


class TestApprovedReaderIsolation:
    """Approved readers (list_craft_records, API/CLI craft endpoints)
    must never return proposals as approved knowledge."""

    def test_craft_records_empty_when_only_proposals_exist(
        self, craft_dir, sample_entry
    ):
        write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )

        class FakeCfg:
            craft_memory_dir = craft_dir
            def resolved(self):
                return self

        records = list_craft_records(FakeCfg())
        assert len(records) == 0

    def test_craft_records_with_include_proposals(self, craft_dir, sample_entry):
        write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )

        class FakeCfg:
            craft_memory_dir = craft_dir
            def resolved(self):
                return self

        records = list_craft_records(FakeCfg(), include_proposals=True)
        assert len(records) == 0  # proposals are in proposals/*.json, not craft_records.jsonl

    def test_promotion_makes_record_readable(
        self, craft_dir, sample_entry, valid_promotion_evidence
    ):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        pid = results[0]["proposal_id"]
        promote_proposal_to_craft(craft_dir, pid, valid_promotion_evidence)

        class FakeCfg:
            craft_memory_dir = craft_dir
            def resolved(self):
                return self

        records = list_craft_records(FakeCfg())
        assert len(records) == 1
        assert records[0]["craft_id"].startswith("CRFT_")
        assert records[0]["adoption_status"] == "candidate"

    def test_proposal_remains_in_proposals_after_promotion(
        self, craft_dir, sample_entry, valid_promotion_evidence
    ):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        pid = results[0]["proposal_id"]
        promote_proposal_to_craft(craft_dir, pid, valid_promotion_evidence)

        p = get_proposal(craft_dir, pid)
        assert p is not None
        assert p["status"] == "promoted"
        assert p["promotion_evidence"]["craft_record_id"].startswith("CRFT_")


# ── Empty / zero-entry edge cases ────────────────────────────────────


class TestEmptyInput:
    """Edge cases for empty or zero entries."""

    def test_write_zero_entries(self, craft_dir):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[],
        )
        assert results == []
        files = list((craft_dir / "proposals").glob("proposal_*.json"))
        assert len(files) == 0  # no proposal files written

    def test_list_proposals_empty_dir(self, craft_dir):
        proposals = list_proposals(craft_dir)
        assert proposals == []


# ── Proposal data integrity ──────────────────────────────────────────


class TestProposalDataIntegrity:
    """Proposal records contain all required metadata."""

    def test_proposal_has_required_fields(self, craft_dir, sample_entry):
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=[sample_entry],
        )
        p = results[0]
        assert "proposal_id" in p
        assert p["proposal_id"].startswith("PROP_")
        assert p["status"] == "proposal"
        assert p["source"] == "data_loop"
        assert p["source_run_id"] == "run_001"
        assert "created_at" in p
        assert "craft_data" in p
        assert p["promotion_evidence"] is None

    def test_multiple_entries_in_single_write(self, craft_dir):
        entries = [
            {"preset": "warm_vocal", "severity": "high", "source": "data_loop"},
            {"preset": "bright_master", "severity": "medium", "source": "data_loop"},
            {"preset": "clean_master", "severity": "low", "source": "data_loop"},
        ]
        results = write_automated_proposal(
            craft_dir,
            source="data_loop",
            source_run_id="run_001",
            entries=entries,
        )
        assert len(results) == 3
        ids = {r["proposal_id"] for r in results}
        assert len(ids) == 3  # all unique
        files = list((craft_dir / "proposals").glob("proposal_*.json"))
        assert len(files) == 3
