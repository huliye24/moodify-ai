"""Tests for knowledge feedback: records, proposals, policy ledger."""

from __future__ import annotations

from pathlib import Path

import pytest

from moodify.capability_registry.knowledge.policy import (
    DEFAULT_MIN_SAMPLES,
    PolicyLedger,
    confirm_proposal,
    meets_sample_threshold,
    propose_rule_change,
)
from moodify.capability_registry.knowledge.records import (
    KnowledgeStore,
    new_judgment,
    new_measurement,
    new_negative,
)


def make_store(tmp_path: Path) -> KnowledgeStore:
    return KnowledgeStore(tmp_path / "knowledge")


def add_measurements(store: KnowledgeStore, case_id: str, n: int = 3, provider: str = "ffmpeg.cli") -> None:
    for i in range(n):
        store.add_measurement(
            new_measurement(
                case_id=case_id,
                capability_id="media.transcode",
                provider_id=provider,
                execution_record_id=f"rec-{i}",
                input_features={"duration_s": 1.0},
                parameters={"format": "flac"},
                measurements={"elapsed": i},
            )
        )


class TestKnowledgeStore:
    def test_roundtrip_records(self, tmp_path: Path) -> None:
        store = make_store(tmp_path)
        store.add_measurement(new_measurement("c1", "cap", "prov", "rec1", {}, {}, {"x": 1}))
        store.add_judgment(new_judgment("c1", "approved", "sounds right", {"rule": "none"}))
        store.add_negative(new_negative("c1", "validation_failure", {"rule_id": "output_exists"}))
        assert store.count("measurements") == 1
        assert store.count("judgments") == 1
        assert store.count("negative") == 1
        assert store.measurements("c1")[0].case_id == "c1"
        assert store.judgments("c1")[0].judgment == "approved"
        assert store.negative("c1")[0].kind == "validation_failure"

    def test_append_only_no_delete(self, tmp_path: Path) -> None:
        store = make_store(tmp_path)
        record = new_measurement("c1", "cap", "prov", "rec1", {}, {}, {"x": 1})
        store.add_measurement(record)
        with pytest.raises(ValueError):
            store.supersede("measurements", "nonexistent", "m-new")
        store.supersede("measurements", record.record_id, "m-new")
        records = store.measurements("c1")
        assert len(records) == 2  # original + superseded marker, both preserved
        assert any(r.superseded_by == "m-new" for r in records)

    def test_negative_knowledge_first_class(self, tmp_path: Path) -> None:
        store = make_store(tmp_path)
        store.add_negative(new_negative("c1", "rejected_candidate", {"reason": "clip" }, linked_rule_id="output_exists"))
        neg = store.negative("c1")
        assert neg[0].linked_rule_id == "output_exists"
        assert neg[0].kind == "rejected_candidate"


class TestProposal:
    def test_proposal_never_auto_applies(self, tmp_path: Path) -> None:
        store = make_store(tmp_path)
        add_measurements(store, "c1")
        proposal = propose_rule_change(
            case_ids=("c1",),
            change_type="provider_preference",
            target="media.transcode",
            proposed_value={"preferred_provider": "ffmpeg.cli"},
            rationale="test",
            evidence_record_ids=tuple(m.record_id for m in store.measurements("c1")),
        )
        assert not proposal.confirmed
        with pytest.raises(ValueError, match="not confirmed"):
            PolicyLedger(tmp_path / "ledger").apply(proposal)

    def test_sample_threshold(self) -> None:
        assert not meets_sample_threshold(1)
        assert not meets_sample_threshold(2)
        assert meets_sample_threshold(3)
        assert DEFAULT_MIN_SAMPLES == 3

    def test_confirmed_proposal_applies_and_versions(self, tmp_path: Path) -> None:
        store = make_store(tmp_path)
        add_measurements(store, "c1")
        proposal = propose_rule_change(
            case_ids=("c1",),
            change_type="provider_preference",
            target="media.transcode",
            proposed_value={"preferred_provider": "ffmpeg.cli"},
            rationale="majority",
            evidence_record_ids=tuple(m.record_id for m in store.measurements("c1")),
            superseded_rule="policy/1",
            superseded_rule_source="historical rule for transcode",
        )
        confirmed = confirm_proposal(proposal, confirmed_by="operator")
        ledger = PolicyLedger(tmp_path / "ledger")
        entry = ledger.apply(confirmed)
        assert entry.policy_version == "policy/1"
        assert entry.superseded_rule == "policy/1"
        assert entry.superseded_rule_source == "historical rule for transcode"
        # second apply -> version 2
        entry2 = ledger.apply(confirmed)
        assert entry2.policy_version == "policy/2"

    def test_policy_ledger_geological_reference(self, tmp_path: Path) -> None:
        store = make_store(tmp_path)
        add_measurements(store, "c1")
        proposal = confirm_proposal(propose_rule_change(
            case_ids=("c1",), change_type="default_parameter", target="media.transcode",
            proposed_value={"format": "flac"}, rationale="r",
            evidence_record_ids=(),
            superseded_rule="old-default",
            superseded_rule_source="the failure that created old-default",
        ))
        ledger = PolicyLedger(tmp_path / "ledger")
        ledger.apply(proposal)
        entries = ledger.entries()
        assert entries[0].superseded_rule == "old-default"
        assert entries[0].superseded_rule_source == "the failure that created old-default"


class TestPolicyLedger:
    def test_empty_ledger_version(self, tmp_path: Path) -> None:
        ledger = PolicyLedger(tmp_path / "ledger")
        assert ledger.current_version() == "policy/0.0"
        assert ledger.entries() == []
