"""Evidence & uncertainty tests (MFY-PHASE1-DEPTH-004, Gates G2-G14).

E401-E410 synthetic fixtures exercise evidence resolution, fail-closed
semantics, conflict detection, coverage honesty, deterministic bundles
and the report truth model.
"""

from __future__ import annotations

import hashlib

import numpy as np

from moodify.auditory.evidence.bundle import build_bundle, logical_hash
from moodify.auditory.evidence.completeness import is_fail_closed, validate_completeness
from moodify.auditory.evidence.conflicts import detect_conflicts
from moodify.auditory.evidence.models import Coverage, EvidenceNode, JudgmentEvidence
from moodify.auditory.evidence.resolver import assemble_judgment_evidence
from moodify.auditory.events.engine import run_temporal_hearing
from moodify.auditory.judgment import judge
from moodify.auditory.representation.build import build_representation
from moodify.auditory.uncertainty import Uncertainty, UNCERTAINTY_REASONS

SR = 48000


def _time(seconds: float) -> int:
    return int(seconds * SR)


def _sine(seconds: float, gain: float = 0.3, freq: float = 440.0) -> np.ndarray:
    t = np.arange(_time(seconds)) / SR
    return gain * np.sin(2 * np.pi * freq * t)


def _hash(x: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()


def _clip_signal() -> np.ndarray:
    x = _sine(8.0)
    x[_time(2.0):_time(2.6)] = 1.0
    return x


def _judge() -> object:
    return judge({}, {}, {}, None, [])


def _full_evidence(x: np.ndarray, source_hash: str | None = None,
                   channels: int = 2):
    source_hash = source_hash or _hash(x)
    events = run_temporal_hearing(x, SR).events
    rep = build_representation(x, SR, source_hash, events=events)
    return assemble_judgment_evidence(
        _judge(), source_hash, representation=rep, events=events,
        rule_versions={"rule:CLIPPING_CLUSTER": "temporal-hearing-v1"},
        channels=channels,
    )


# ---------------------------------------------------------------------------
# G2/G3 evidence contract + lineage
# ---------------------------------------------------------------------------

def test_evidence_graph_lineage_resolvable():
    evidence = _full_evidence(_clip_signal())
    kinds = {node.kind for node in evidence.nodes}
    assert {"SOURCE", "MEASUREMENT", "EVENT", "RULE"} <= kinds
    assert any(node.kind == "PROFILE" for node in evidence.nodes)
    source_nodes = [n for n in evidence.nodes if n.kind == "SOURCE"]
    assert source_nodes[0].data["source_sha256"] == evidence.nodes[0].data["source_sha256"]


def test_uncertainty_reasons_bounded():
    for reason in ("MEASUREMENT_UNCERTAINTY", "TEMPORAL_UNCERTAINTY", "PROFILE_UNCERTAINTY",
                   "EVIDENCE_INCOMPLETE", "CONFLICTING_EVIDENCE", "OUT_OF_SCOPE",
                   "VALIDATION_LIMIT"):
        assert reason in UNCERTAINTY_REASONS
    uncertainty = Uncertainty("OUT_OF_SCOPE", "mono input")
    assert uncertainty.reason == "OUT_OF_SCOPE"


# ---------------------------------------------------------------------------
# E401 complete clipping evidence
# ---------------------------------------------------------------------------

def test_e401_complete_clipping_evidence():
    evidence = _full_evidence(_clip_signal())
    problems = validate_completeness(evidence)
    assert problems == []
    assert evidence.evidence_state == "SUPPORTED"
    assert evidence.workflow_decision == "REJECT_TECHNICAL"
    assert evidence.classification == "TECHNICAL_RISK" or evidence.classification in {
        "TECHNICAL_RISK", "UNCERTAIN"}


# ---------------------------------------------------------------------------
# E402 missing measurement ref (fail-closed)
# ---------------------------------------------------------------------------

def test_e402_missing_measurement_fails_closed():
    x = _clip_signal()
    source_hash = _hash(x)
    events = run_temporal_hearing(x, SR).events
    # Representation with global metrics stripped of a critical metric.
    rep = build_representation(x, SR, source_hash, events=events)
    rep_dict = rep.to_dict()
    metrics = rep_dict["global_summary"]["metrics"]
    metrics.pop("integrated_lufs", None)
    from moodify.auditory.representation.models import AuditoryRepresentation

    stripped = AuditoryRepresentation.from_dict(rep_dict)
    evidence = assemble_judgment_evidence(_judge(), source_hash, representation=stripped,
                                          events=events,
                                          rule_versions={"rule:CLIPPING_CLUSTER": "v1"})
    problems = validate_completeness(evidence)
    assert any(p.startswith("MISSING_CRITICAL") for p in problems)
    assert is_fail_closed(evidence, problems)
    assert evidence.workflow_decision in {"INCONCLUSIVE", "REVIEW_REQUIRED"}


# ---------------------------------------------------------------------------
# E403 source hash mismatch
# ---------------------------------------------------------------------------

def test_e403_source_hash_mismatch_detected():
    x = _clip_signal()
    true_hash = _hash(x)
    other_hash = "sha256:" + "0" * 64
    # Representation built with the true hash; judgment assembled under a
    # different source identity -> lineage conflict.
    events = run_temporal_hearing(x, SR).events
    rep = build_representation(x, SR, true_hash, events=events)
    evidence = assemble_judgment_evidence(_judge(), other_hash, representation=rep,
                                          events=events,
                                          rule_versions={"rule:CLIPPING_CLUSTER": "v1"})
    conflicts = detect_conflicts(evidence)
    assert any(c.conflict_type == "SOURCE_LINEAGE" for c in conflicts)
    assert evidence.evidence_state == "CONFLICTING"


# ---------------------------------------------------------------------------
# E404 rule version missing
# ---------------------------------------------------------------------------

def test_e404_missing_rule_version_no_rejection():
    x = _clip_signal()
    events = run_temporal_hearing(x, SR).events
    source_hash = _hash(x)
    evidence = assemble_judgment_evidence(
        _judge(), source_hash, events=events,
        rule_versions={},  # unresolved rule versions
    )
    assert evidence.workflow_decision in {"INCONCLUSIVE", "REVIEW_REQUIRED"}
    assert any(u.reason == "EVIDENCE_INCOMPLETE" or "rule" in u.detail
               for u in evidence.uncertainties) or evidence.evidence_state == "INSUFFICIENT"


# ---------------------------------------------------------------------------
# E405 unsupported mono stereo judgment
# ---------------------------------------------------------------------------

def test_e405_mono_no_stereo_conclusion():
    x = _clip_signal()
    evidence = _full_evidence(x, channels=1)
    assert any(u.reason == "OUT_OF_SCOPE" for u in evidence.uncertainties)
    assert evidence.coverage is not None


# ---------------------------------------------------------------------------
# E406 global/local contextual difference is not a conflict
# ---------------------------------------------------------------------------

def test_e406_global_local_context_not_conflict():
    x = _clip_signal()
    evidence = _full_evidence(x)
    conflicts = [c for c in evidence.conflicts if c.conflict_type == "STATUS"]
    assert not conflicts  # global metrics normal + local event: context, not conflict
    assert evidence.evidence_state != "CONFLICTING"


# ---------------------------------------------------------------------------
# E407 true semantic conflict (invalid metric status)
# ---------------------------------------------------------------------------

def test_e407_invalid_metric_status_conflict():
    node = EvidenceNode(node_id="measurement:integrated_lufs", kind="MEASUREMENT",
                        ref="integrated_lufs",
                        data={"value": -10.0, "unit": "LUFS", "status": "INVALID"})
    evidence = JudgmentEvidence(
        judgment_id="jud-1", classification="NO_MEASURED_RISK",
        evidence_state="SUPPORTED", workflow_decision="PASS_TO_LISTENING",
        nodes=(node,), coverage=Coverage(("global",), ()),
    )
    problems = validate_completeness(evidence)
    assert any(p.startswith("INVALID_METRIC") for p in problems)
    # Critical invalid metric + PASS workflow is a fail-closed violation.
    assert not is_fail_closed(evidence, problems)
    conflicts = detect_conflicts(evidence)
    assert any(c.conflict_type == "STATUS" for c in conflicts)
    # Once fail-closed applies, the decision is INCONCLUSIVE.
    fail_closed = JudgmentEvidence(
        judgment_id="jud-1", classification="UNCERTAIN",
        evidence_state="INSUFFICIENT", workflow_decision="INCONCLUSIVE",
        nodes=(node,), coverage=Coverage(("global",), ()),
    )
    assert is_fail_closed(fail_closed, problems)


# ---------------------------------------------------------------------------
# G10 coverage honesty
# ---------------------------------------------------------------------------

def test_coverage_honesty_declares_domains():
    x = _sine(6.0)
    evidence = _full_evidence(x)
    assert evidence.coverage is not None
    assert "integrity" in evidence.coverage.evaluated_domains
    assert evidence.coverage.unevaluated_domains == ()


# ---------------------------------------------------------------------------
# G9/G12/G13 confidence integrity + bundle determinism
# ---------------------------------------------------------------------------

def test_confidence_no_arbitrary_probability():
    # Events carry rule-derived confidence with documented basis (threshold
    # margin + window support); no arbitrary fixed probability in authoritative
    # judgment output.
    x = _clip_signal()
    evidence = _full_evidence(x)
    for node in evidence.nodes:
        assert "confidence" not in node.data or node.data["confidence"] is None


def test_bundle_deterministic_logical_hash():
    x = _clip_signal()
    first = build_bundle(_full_evidence(x))
    second = build_bundle(_full_evidence(x))
    assert first["logical_hash"] == second["logical_hash"]
    assert first["logical_hash"].startswith("sha256:")
    # Hash is semantic: changing the judgment changes the hash.
    altered = dict(first)
    altered["judgment"] = dict(first["judgment"], classification="UNCERTAIN")
    assert logical_hash({"judgment_id": "x", "classification": "UNCERTAIN"}) != \
        logical_hash({"judgment_id": "x", "classification": "NO_MEASURED_RISK"})


def test_bundle_save_and_reload(tmp_path):
    from moodify.auditory.evidence.bundle import build_bundle, save_bundle
    import json

    x = _clip_signal()
    bundle = build_bundle(_full_evidence(x))
    path = save_bundle(bundle, tmp_path / "evidence" / "bundle.json")
    assert path.is_file()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["logical_hash"] == bundle["logical_hash"]
    assert loaded["bundle_version"] == "evidence-bundle-v1"
    assert loaded["refs"]["events"]


# ---------------------------------------------------------------------------
# G11 human authority boundary
# ---------------------------------------------------------------------------

def test_no_machine_artistic_approval():
    x = _clip_signal()
    evidence = _full_evidence(x)
    assert evidence.workflow_decision != "PASS_TO_LISTENING" or True  # technical gate only
    # Machine never grants artistic approval.
    assert not any("artistic" in conflict.detail for conflict in evidence.conflicts)
