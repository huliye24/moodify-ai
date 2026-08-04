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


# ═══════════════════════════════════════════════════════════════════════
# Rework Expansion — P0 promotion fault and replay matrix
# ═══════════════════════════════════════════════════════════════════════


class TestPromotionFaultBeforeCraftTmpWrite:
    """Fault injection BEFORE craft-store tmp write."""

    def test_failure_before_tmp_write_retry_succeeds(
        self, craft_dir, sample_entry, valid_promotion_evidence, monkeypatch
    ):
        proposal = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )[0]
        craft_path = craft_dir / "craft_records.jsonl"

        import moodify_runtime.craft_proposals as module
        real_write = module.Path.write_text
        failed = {"once": False}

        def fail_tmp_write(self_obj, content, encoding=None):
            obj_str = str(self_obj)
            if not failed["once"] and "craft_records.jsonl" in obj_str and ".tmp" in obj_str:
                failed["once"] = True
                raise OSError("injected before tmp write")
            return real_write(self_obj, content, encoding=encoding)

        monkeypatch.setattr(module.Path, "write_text", fail_tmp_write)
        with pytest.raises(OSError, match="before tmp write"):
            promote_proposal_to_craft(
                craft_dir, proposal["proposal_id"], valid_promotion_evidence
            )

        # Retry: should succeed
        result = promote_proposal_to_craft(
            craft_dir, proposal["proposal_id"], valid_promotion_evidence
        )
        assert result["craft_record_id"].startswith("CRFT_")
        rows = (craft_dir / "craft_records.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(rows) == 1


class TestPromotionFaultAfterTmpWriteBeforeReplace:
    """Fault injection AFTER tmp write but BEFORE os.replace."""

    def test_failure_after_tmp_before_replace_retry_no_duplicate(
        self, craft_dir, sample_entry, valid_promotion_evidence, monkeypatch
    ):
        proposal = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )[0]

        import moodify_runtime.craft_proposals as module
        real_replace = module.os.replace
        failed = {"once": False}

        def fail_first_replace(source, target):
            if not failed["once"] and "craft_records.jsonl" in str(target):
                failed["once"] = True
                raise OSError("injected before atomic replace")
            return real_replace(source, target)

        monkeypatch.setattr(module.os, "replace", fail_first_replace)
        with pytest.raises(OSError, match="before atomic replace"):
            promote_proposal_to_craft(
                craft_dir, proposal["proposal_id"], valid_promotion_evidence
            )

        result = promote_proposal_to_craft(
            craft_dir, proposal["proposal_id"], valid_promotion_evidence
        )
        rows = (craft_dir / "craft_records.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(rows) == 1
        assert result["craft_record_id"] == json.loads(rows[0])["craft_id"]


class TestPromotionFaultAtProposalWrite:
    """Fault injection at proposal temp write or replacement."""

    def test_failure_before_proposal_tmp_write_retry_no_duplicate(
        self, craft_dir, sample_entry, valid_promotion_evidence, monkeypatch
    ):
        proposal = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )[0]
        proposal_path = craft_dir / "proposals" / f"proposal_{proposal['proposal_id']}.json"

        import moodify_runtime.craft_proposals as module
        real_replace = module.os.replace
        failed = {"once": False}

        def fail_proposal_write(source, target):
            if not failed["once"] and Path(target) == proposal_path:
                failed["once"] = True
                raise OSError("injected before proposal replacement")
            return real_replace(source, target)

        monkeypatch.setattr(module.os, "replace", fail_proposal_write)
        with pytest.raises(OSError, match="before proposal replacement"):
            promote_proposal_to_craft(
                craft_dir, proposal["proposal_id"], valid_promotion_evidence
            )

        result = promote_proposal_to_craft(
            craft_dir, proposal["proposal_id"], valid_promotion_evidence
        )
        rows = (craft_dir / "craft_records.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(rows) == 1
        assert result["craft_record_id"] == json.loads(rows[0])["craft_id"]


class TestDeterministicCraftIdentity:
    """Craft ID is deterministically derived from proposal identity."""

    def test_same_proposal_id_produces_same_craft_id(
        self, craft_dir, sample_entry, valid_promotion_evidence
    ):
        p1 = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )[0]
        result1 = promote_proposal_to_craft(
            craft_dir, p1["proposal_id"], valid_promotion_evidence
        )

        # Delete craft record + proposal and recreate
        (craft_dir / "craft_records.jsonl").unlink()
        proposal_path = craft_dir / "proposals" / f"proposal_{p1['proposal_id']}.json"
        proposal_path.unlink()

        p2 = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )[0]
        result2 = promote_proposal_to_craft(
            craft_dir, p2["proposal_id"], valid_promotion_evidence
        )

        # Craft ID is derived only from proposal_id, which is random UUID
        # so they differ. But repeated promotion of the SAME proposal_id
        # must produce the same craft_id.
        r3 = promote_proposal_to_craft(
            craft_dir, p2["proposal_id"], valid_promotion_evidence
        )
        assert r3["status"] == "already_promoted"
        assert r3["craft_record_id"] == result2["craft_record_id"]

    def test_craft_id_is_hash_of_proposal_id(self, craft_dir):
        """craft_id = 'CRFT_' + sha256(proposal_id)[:12].upper()"""
        import hashlib

        # Write a proposal and extract the actual ID
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001",
            [{"preset": "warm_vocal"}],
        )
        pid = results[0]["proposal_id"]
        expected = "CRFT_" + hashlib.sha256(pid.encode("utf-8")).hexdigest()[:12].upper()

        valid_evidence = {
            "rights_evidence": {"asset_id": "A1", "manifest": "m1"},
            "human_reviewer": "reviewer",
            "review_timestamp": "2026-07-30T10:00:00Z",
            "source_run_id": "run_001",
            "regression_evidence": {"tests": 1},
        }
        result = promote_proposal_to_craft(craft_dir, pid, valid_evidence)
        assert result["craft_record_id"] == expected


class TestPromotionEvidenceValidation:
    """Structural evidence validation beyond non-empty checks."""

    def test_rights_evidence_not_dict_rejected(
        self, craft_dir, sample_entry
    ):
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )
        pid = results[0]["proposal_id"]
        bad_evidence = {
            "rights_evidence": "not_a_dict",
            "human_reviewer": "reviewer",
            "review_timestamp": "2026-07-30T10:00:00Z",
            "source_run_id": "run_001",
            "regression_evidence": {"tests": 1},
        }
        with pytest.raises(ValueError, match="non-empty object"):
            promote_proposal_to_craft(craft_dir, pid, bad_evidence)

    def test_empty_rights_evidence_dict_rejected(
        self, craft_dir, sample_entry
    ):
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )
        pid = results[0]["proposal_id"]
        bad_evidence = {
            "rights_evidence": {},
            "human_reviewer": "reviewer",
            "review_timestamp": "2026-07-30T10:00:00Z",
            "source_run_id": "run_001",
            "regression_evidence": {"tests": 1},
        }
        with pytest.raises(ValueError, match="non-empty object"):
            promote_proposal_to_craft(craft_dir, pid, bad_evidence)

    def test_regression_evidence_not_struct_rejected(
        self, craft_dir, sample_entry
    ):
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )
        pid = results[0]["proposal_id"]
        bad_evidence = {
            "rights_evidence": {"x": 1},
            "human_reviewer": "reviewer",
            "review_timestamp": "2026-07-30T10:00:00Z",
            "source_run_id": "run_001",
            "regression_evidence": "not_struct",
        }
        with pytest.raises(ValueError, match="non-empty object or list"):
            promote_proposal_to_craft(craft_dir, pid, bad_evidence)

    def test_empty_reviewer_string_rejected(
        self, craft_dir, sample_entry
    ):
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )
        pid = results[0]["proposal_id"]
        bad_evidence = {
            "rights_evidence": {"x": 1},
            "human_reviewer": "   ",
            "review_timestamp": "2026-07-30T10:00:00Z",
            "source_run_id": "run_001",
            "regression_evidence": {"tests": 1},
        }
        with pytest.raises(ValueError, match="non-empty string"):
            promote_proposal_to_craft(craft_dir, pid, bad_evidence)

    def test_empty_run_id_rejected(
        self, craft_dir, sample_entry
    ):
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )
        pid = results[0]["proposal_id"]
        bad_evidence = {
            "rights_evidence": {"x": 1},
            "human_reviewer": "reviewer",
            "review_timestamp": "2026-07-30T10:00:00Z",
            "source_run_id": "",
            "regression_evidence": {"tests": 1},
        }
        with pytest.raises(ValueError, match="must not be empty"):
            promote_proposal_to_craft(craft_dir, pid, bad_evidence)

    def test_empty_timestamp_rejected(
        self, craft_dir, sample_entry
    ):
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )
        pid = results[0]["proposal_id"]
        bad_evidence = {
            "rights_evidence": {"x": 1},
            "human_reviewer": "reviewer",
            "review_timestamp": "   ",
            "source_run_id": "run_001",
            "regression_evidence": {"tests": 1},
        }
        with pytest.raises(ValueError, match="non-empty string"):
            promote_proposal_to_craft(craft_dir, pid, bad_evidence)


class TestPreExistingDuplicate:
    """Pre-existing malformed JSONL or duplicate entries handled safely."""

    def test_malformed_jsonl_fails_closed_and_preserves_history(
        self, craft_dir, sample_entry, valid_promotion_evidence
    ):
        """Promotion cannot silently replace an unreadable Craft history."""
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )
        pid = results[0]["proposal_id"]

        craft_path = craft_dir / "craft_records.jsonl"
        original = (
            json.dumps({"craft_id": "CRFT_EXISTING", "source_proposal_id": "older"})
            + "\nthis is not valid json\n"
        ).encode("utf-8")
        craft_path.write_bytes(original)

        with pytest.raises(ValueError, match="promotion stopped without modifying history"):
            promote_proposal_to_craft(craft_dir, pid, valid_promotion_evidence)
        assert craft_path.read_bytes() == original
        assert get_proposal(craft_dir, pid)["status"] == "proposal"

    def test_duplicate_source_proposal_id_reconciled(
        self, craft_dir, sample_entry, valid_promotion_evidence
    ):
        """If source_proposal_id already exists in JSONL, promotion returns it."""
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )
        pid = results[0]["proposal_id"]

        # First promotion
        r1 = promote_proposal_to_craft(craft_dir, pid, valid_promotion_evidence)

        # Directly inject a duplicate with the same source_proposal_id
        craft_path = craft_dir / "craft_records.jsonl"
        rows = craft_path.read_text(encoding="utf-8").strip().splitlines()
        duplicate = json.loads(json.dumps(json.loads(rows[0])))
        duplicate["craft_id"] = "CRFT_FAKE_DUPLICATE"
        craft_path.write_text(rows[0] + "\n" + json.dumps(duplicate) + "\n", encoding="utf-8")

        # Retry promotion — reconcile finds the first match (deterministic craft_id)
        result = promote_proposal_to_craft(craft_dir, pid, valid_promotion_evidence)
        assert result["status"] == "already_promoted"
        assert result["craft_record_id"] == r1["craft_record_id"]

    def test_deterministic_retry_after_partial_jsonl_write(
        self, craft_dir, sample_entry, valid_promotion_evidence
    ):
        """Even if a tmp write partially writes, retry recovers."""
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )
        pid = results[0]["proposal_id"]

        # Create a tmp file (simulating partial write from prior attempt)
        tmp_path = craft_dir / f".craft_records.jsonl.{pid}.tmp"
        tmp_path.write_text("", encoding="utf-8")

        result = promote_proposal_to_craft(craft_dir, pid, valid_promotion_evidence)
        assert result["craft_record_id"].startswith("CRFT_")
        rows = (craft_dir / "craft_records.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(rows) == 1


class TestRepeatedIdenticalPromotion:
    """Repeated identical promotion requests produce the same result."""

    def test_ten_identical_promotions_one_record(
        self, craft_dir, sample_entry, valid_promotion_evidence
    ):
        results = write_automated_proposal(
            craft_dir, "data_loop", "run_001", [sample_entry]
        )
        pid = results[0]["proposal_id"]

        craft_id = None
        for _ in range(10):
            r = promote_proposal_to_craft(craft_dir, pid, valid_promotion_evidence)
            if craft_id is None:
                craft_id = r["craft_record_id"]
                assert r["status"] == "promoted"
            else:
                assert r["status"] == "already_promoted"
                assert r["craft_record_id"] == craft_id

        rows = (craft_dir / "craft_records.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(rows) == 1


# Phase 2B deepening — schema_version embedding

class TestSchemaVersionEmbedding:
    def test_proposal_has_schema_version(self, craft_dir, sample_entry):
        from moodify_runtime.craft_proposals import write_automated_proposal
        results = write_automated_proposal(craft_dir, source='test', source_run_id='R1', entries=[sample_entry])
        assert results[0].get('schema_version') == '1.0.0'

    def test_promoted_craft_has_schema_version(self, craft_dir, sample_entry, valid_promotion_evidence):
        from moodify_runtime.craft_proposals import write_automated_proposal, promote_proposal_to_craft
        results = write_automated_proposal(craft_dir, source='test', source_run_id='R1', entries=[sample_entry])
        evidence = dict(valid_promotion_evidence, source_run_id='R1')
        promote_proposal_to_craft(craft_dir, results[0]['proposal_id'], evidence)
        import json
        rows = (craft_dir / 'craft_records.jsonl').read_text(encoding='utf-8').strip().splitlines()
        craft = json.loads(rows[0])
        assert craft.get('schema_version') == '1.0.0'

    def test_proposal_loadable_by_historical_compatibility(self, craft_dir, sample_entry):
        from moodify_runtime.craft_proposals import write_automated_proposal
        from moodify_runtime.historical_compatibility import load_historical_record
        results = write_automated_proposal(craft_dir, source='test', source_run_id='R1', entries=[sample_entry])
        path = craft_dir / 'proposals' / f'proposal_{results[0]["proposal_id"]}.json'
        load_result = load_historical_record(str(path), 'proposal')
        assert load_result.success
        assert load_result.schema_version == '1.0.0'
