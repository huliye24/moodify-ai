"""Tests for capability validation rules and candidate selection."""

from __future__ import annotations

from pathlib import Path


from moodify.capability_registry.bootstrap import build_registry
from moodify.capability_registry.execution.envelope import (
    ApprovedExecutionEnvelope,
    EnvelopeInput,
    sign_envelope,
)
from moodify.capability_registry.validation.candidates import (
    Candidate,
    CandidateRanker,
    CandidateSpec,
    RejectionReason,
    reasons_from_validation,
)
from moodify.capability_registry.validation.rules import (
    common_rules,
    rules_for_capability,
    validate_capability,
)


def make_envelope(tmp_path: Path, *, approved: bool = True) -> ApprovedExecutionEnvelope:
    import hashlib

    source = tmp_path / "a.wav"
    source.write_bytes(b"RIFF")
    envelope = ApprovedExecutionEnvelope(
        schema_version="approved-execution-envelope/0.1",
        envelope_id="env-val-1",
        case_id="case-val",
        capability_id="media.probe",
        provider_id="ffprobe.cli",
        inputs=(EnvelopeInput(role="source", path=str(source), sha256=hashlib.sha256(source.read_bytes()).hexdigest()),),
        parameters={},
        output_dir=str((tmp_path / "out").resolve()),
        timeout_s=10.0,
        allow_network=False,
    )
    return sign_envelope(envelope, issuer="op", policy_version="p/1") if approved else envelope


class TestRuleGeology:
    def test_every_common_rule_has_historical_source(self) -> None:
        for rule in common_rules().values():
            assert rule.historical_source, f"{rule.rule_id} lacks historical source"
            assert len(rule.historical_source) > 10

    def test_no_rule_without_source_marks_unproven(self) -> None:
        # all registered common rules carry sources (geological record requirement)
        assert all(len(r.historical_source) > 0 for r in common_rules().values())

    def test_rules_cannot_be_disabled_by_provider(self) -> None:
        # rule set comes from registry + capability binding, not from provider
        registry = build_registry()
        for cap in registry.capabilities:
            rules = rules_for_capability(cap.capability_id, registry)
            assert isinstance(rules, tuple)
        # a rule requested in validation list must appear regardless of provider
        rules = rules_for_capability("media.transcode", registry)
        assert any(r.rule_id == "nonzero_size" for r in rules)


class TestRuleEvaluation:
    def test_output_exists_fails_on_empty(self) -> None:
        report = validate_capability("media.probe", {"artifacts": []})
        assert not report.passed()
        assert any(r.rule_id == "output_exists" for r in report.errors())

    def test_output_exists_passes_with_artifact(self) -> None:
        report = validate_capability("media.probe", {"artifacts": ["x.json"]})
        assert report.passed()

    def test_hash_linked_requires_sha256(self) -> None:
        report = validate_capability(
            "media.transcode",
            {"artifacts": ["x.flac"], "input_hashes": {"source": "abc"}},
        )
        assert not report.passed()

    def test_roundtrip_fail_rejects(self) -> None:
        report = validate_capability(
            "notation.render",
            {"artifacts": ["s.pdf"], "roundtrip_report": {"verdict": "FAIL"}},
        )
        assert not report.passed()
        assert any(r.rule_id == "roundtrip_visible" for r in report.errors())


class TestCandidates:
    def _candidate(self, *, accepted: bool, label: str = "c1") -> Candidate:
        from moodify.capability_registry.execution.envelope import ExecutionRecord
        from moodify.capability_registry.validation.rules import ValidationReport

        record = ExecutionRecord(
            schema_version="execution-record/0.1",
            record_id="r1",
            case_id="c",
            envelope_id="e",
            status="completed" if accepted else "failed",
            provider_id="p",
            capability_id="cap",
            started_at="2026-08-02T00:00:00Z",
        )
        validation = ValidationReport(capability_id="cap", results=())
        return Candidate(
            spec=CandidateSpec(label=label, provider_id="p", parameters={}),
            envelope=None,
            record=record,
            validation=validation,
        )

    def test_ranker_puts_accepted_first(self) -> None:
        ok = self._candidate(accepted=True, label="ok")
        bad = self._candidate(accepted=False, label="bad")
        ranked = CandidateRanker().rank([bad, ok])
        assert ranked[0].spec.label == "ok"

    def test_reasons_structured(self) -> None:
        report = validate_capability("media.probe", {"artifacts": []})
        reasons = reasons_from_validation(report)
        assert reasons
        assert all(r.rule_id for r in reasons)
        assert all(r.measured is not None for r in reasons)

    def test_rejection_reason_has_all_fields(self) -> None:
        r = RejectionReason(rule_id="x", measured=0, expected=">=1", message="empty")
        d = r.to_dict()
        assert d["rule_id"] == "x"
        assert d["measured"] == 0
        assert d["expected"] == ">=1"


class TestValidateAgainstRecord:
    def test_validate_uses_record_evidence(self, tmp_path: Path) -> None:
        from moodify.capability_registry.validation.cli import _load_evidence

        record_path = tmp_path / "rec.json"
        record_path.write_text(
            '{"capability_id":"media.probe","artifacts":["x.json"],'
            '"evidence":{"input_hashes":{"source":"%s"}}}' % ("a" * 64),
            encoding="utf-8",
        )
        context = _load_evidence(record_path)
        report = validate_capability("media.probe", context)
        assert report.passed()
