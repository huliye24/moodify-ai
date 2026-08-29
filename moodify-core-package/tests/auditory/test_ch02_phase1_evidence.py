"""Chapter II phase 1: epistemic states, evidence scale, structure context.

DSK-MFY-CH02-PHASE1-001 — Chapter II §6 (temporal scale metadata),
§14 (MSE conditions WSE) and §17 (epistemic states) absorbed into the
evidence layer. All additions are backwards compatible: existing
constructions without the new fields keep prior behavior.
"""

from __future__ import annotations

import hashlib

import numpy as np

from moodify.auditory.evidence import (
    EPISTEMIC_STATES,
    EVIDENCE_SCALES,
    EpistemicState,
    EvidenceScale,
    assemble_judgment_evidence,
    scale_for_duration_ms,
)
from moodify.auditory.evidence.bundle import build_bundle
from moodify.auditory.evidence.models import EvidenceNode
from moodify.auditory.events.engine import run_temporal_hearing
from moodify.auditory.judgment import judge
from moodify.auditory.representation.build import build_representation
from moodify.auditory.structure import Section, StructureContext, annotate_event_with_structure

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


def _full_evidence(x: np.ndarray):
    source_hash = _hash(x)
    events = run_temporal_hearing(x, SR).events
    rep = build_representation(x, SR, source_hash, events=events)
    return assemble_judgment_evidence(
        _judge(), source_hash, representation=rep, events=events,
        rule_versions={"rule:CLIPPING_CLUSTER": "temporal-hearing-v1"},
    )


# ---------------------------------------------------------------------------
# §17 epistemic vocabulary
# ---------------------------------------------------------------------------

def test_epistemic_states_bounded():
    assert EPISTEMIC_STATES == {"OBSERVED", "INFERRED", "ASSOCIATED", "UNKNOWN"}
    state = EpistemicState("INFERRED", "derived from measurements")
    assert state.to_dict() == {"state": "INFERRED", "note": "derived from measurements"}
    assert EpistemicState.from_dict({"state": "OBSERVED"}).state == "OBSERVED"


def test_epistemic_rejects_unknown_state():
    try:
        EpistemicState("GUESSED")
        assert False, "unknown epistemic state must raise"
    except ValueError:
        pass


def test_evidence_node_validates_epistemic_and_scale():
    node = EvidenceNode(node_id="n", kind="MEASUREMENT", ref="m:lufs",
                        scale="WHOLE_TRACK", epistemic_state="OBSERVED")
    assert node.scale == "WHOLE_TRACK"
    assert node.epistemic_state == "OBSERVED"
    for kwargs in ({"epistemic_state": "BAD"}, {"scale": "BAD"}):
        try:
            EvidenceNode(node_id="n", kind="MEASUREMENT", ref="r", **kwargs)
            assert False, "invalid scale/epistemic must raise"
        except ValueError:
            pass


def test_judgment_evidence_epistemic_default_inferred():
    evidence = _full_evidence(_clip_signal())
    assert evidence.epistemic_state == "INFERRED"
    assert evidence.to_dict()["epistemic_state"] == "INFERRED"


def test_fail_closed_judgment_epistemic_unknown():
    x = _clip_signal()
    source_hash = _hash(x)
    events = run_temporal_hearing(x, SR).events
    rep = build_representation(x, SR, source_hash, events=events)
    rep_dict = rep.to_dict()
    rep_dict["global_summary"]["metrics"].pop("integrated_lufs", None)
    from moodify.auditory.representation.models import AuditoryRepresentation

    stripped = AuditoryRepresentation.from_dict(rep_dict)
    evidence = assemble_judgment_evidence(
        _judge(), source_hash, representation=stripped, events=events,
        rule_versions={"rule:CLIPPING_CLUSTER": "v1"},
    )
    assert evidence.epistemic_state == "UNKNOWN"
    assert evidence.evidence_state == "INSUFFICIENT"


# ---------------------------------------------------------------------------
# §6 temporal scale
# ---------------------------------------------------------------------------

def test_scale_taxonomy_bounded():
    assert EVIDENCE_SCALES == {
        "WAVEFORM_FINE", "MICRO_TRANSIENT", "PERCEPTUAL_FRAME",
        "SHORT_TERM", "MUSICAL_UNIT", "LONG_FORM", "WHOLE_TRACK",
    }
    assert EvidenceScale("SHORT_TERM").to_dict() == {"scale": "SHORT_TERM"}
    try:
        EvidenceScale("HALF_SECOND")
        assert False, "unknown scale must raise"
    except ValueError:
        pass


def test_scale_for_duration_boundaries():
    assert scale_for_duration_ms(0.5) == "WAVEFORM_FINE"
    assert scale_for_duration_ms(1.0) == "MICRO_TRANSIENT"
    assert scale_for_duration_ms(50.0) == "PERCEPTUAL_FRAME"
    assert scale_for_duration_ms(600.0) == "SHORT_TERM"
    assert scale_for_duration_ms(2000.0) == "MUSICAL_UNIT"
    assert scale_for_duration_ms(20000.0) == "LONG_FORM"


def test_events_carry_scale_from_duration():
    evidence = _full_evidence(_clip_signal())
    event_nodes = [n for n in evidence.nodes if n.kind == "EVENT"]
    assert event_nodes
    for node in event_nodes:
        duration_ms = node.data["end_ms"] - node.data["start_ms"]
        assert node.scale == scale_for_duration_ms(max(duration_ms, 0.0))
    measurement = [n for n in evidence.nodes if n.kind == "MEASUREMENT"][0]
    assert measurement.scale == "WHOLE_TRACK"
    assert measurement.epistemic_state == "OBSERVED"


def test_correlation_events_are_associated_not_inferred():
    x = np.stack([_sine(8.0), -_sine(8.0)], axis=1)  # anti-phase stereo
    source_hash = _hash(x[:, 0])
    events = run_temporal_hearing(x, SR).events
    correlation_events = [e for e in events
                          if "CORRELATION" in getattr(e, "event_type", "")]
    rep = build_representation(x, SR, source_hash, events=events)
    evidence = assemble_judgment_evidence(
        _judge(), source_hash, representation=rep, events=events,
        rule_versions={f"rule:{e.event_type}": "v1" for e in events},
        channels=2,
    )
    correlated = [n for n in evidence.nodes if n.kind == "EVENT"
                  and "CORRELATION" in n.data.get("event_type", "")]
    if correlation_events:
        assert correlated
        assert all(n.epistemic_state == "ASSOCIATED" for n in correlated)


# ---------------------------------------------------------------------------
# §14 MSE structure context
# ---------------------------------------------------------------------------

def test_section_validation():
    try:
        Section("BAD", 5.0, 2.0)
        assert False, "end before start must raise"
    except ValueError:
        pass
    try:
        Section("BAD", 0.0, 2.0, confidence=1.5)
        assert False, "confidence out of range must raise"
    except ValueError:
        pass


def test_structure_context_rejects_overlaps():
    try:
        StructureContext(
            source="events-v1",
            sections=(Section("A", 0.0, 4.0), Section("B", 3.0, 6.0)),
        )
        assert False, "overlapping sections must raise"
    except ValueError:
        pass


def test_structure_context_queries():
    ctx = StructureContext(
        source="events-v1",
        sections=(Section("INTRO", 0.0, 4.0), Section("CHORUS", 4.0, 8.0)),
        tempo_bpm=120.0,
    )
    assert ctx.section_at(2.0).label == "INTRO"
    assert ctx.section_at(5.5).label == "CHORUS"
    assert ctx.section_at(9.0) is None
    assert ctx.boundary_within(3.9) is True
    assert ctx.boundary_within(2.0) is False
    assert ctx.is_reliable is True


def test_structure_reliability_threshold():
    reliable = StructureContext(
        source="events-v1",
        sections=(Section("A", 0.0, 4.0),),
        confidence=0.9,
    )
    unreliable_conf = StructureContext(
        source="events-v1",
        sections=(Section("A", 0.0, 4.0),),
        confidence=0.5,
    )
    unreliable_section = StructureContext(
        source="events-v1",
        sections=(Section("A", 0.0, 4.0, confidence=0.4),),
    )
    assert reliable.is_reliable
    assert not unreliable_conf.is_reliable
    assert not unreliable_section.is_reliable


def test_event_annotation_label_and_boundary():
    ctx = StructureContext(
        source="events-v1",
        sections=(Section("INTRO", 0.0, 4.0), Section("CHORUS", 4.0, 8.0)),
    )
    from types import SimpleNamespace

    inside = SimpleNamespace(start_ms=2000)
    annotation = annotate_event_with_structure(inside, ctx)
    assert annotation["structure_label"] == "INTRO"
    assert annotation["at_section_boundary"] == "false"
    near_boundary = SimpleNamespace(start_ms=3900)
    assert annotate_event_with_structure(near_boundary, ctx)["at_section_boundary"] == "true"
    outside = SimpleNamespace(start_ms=9000)
    assert "structure_label" not in annotate_event_with_structure(outside, ctx)


def test_resolver_annotates_events_with_reliable_structure():
    x = _clip_signal()
    source_hash = _hash(x)
    events = run_temporal_hearing(x, SR).events
    rep = build_representation(x, SR, source_hash, events=events)
    structure = StructureContext(
        source="events-v1",
        sections=(Section("INTRO", 0.0, 4.0), Section("OUTRO", 4.0, 8.0)),
    )
    evidence = assemble_judgment_evidence(
        _judge(), source_hash, representation=rep, events=events,
        rule_versions={"rule:CLIPPING_CLUSTER": "temporal-hearing-v1"},
        structure=structure,
    )
    annotated = [n for n in evidence.nodes if n.kind == "EVENT"
                 and "structure_label" in n.data]
    assert annotated
    assert all(u.reason != "PROFILE_UNCERTAINTY" for u in evidence.uncertainties)


def test_unreliable_structure_annotates_nothing_and_records_uncertainty():
    x = _clip_signal()
    source_hash = _hash(x)
    events = run_temporal_hearing(x, SR).events
    rep = build_representation(x, SR, source_hash, events=events)
    structure = StructureContext(
        source="events-v1",
        sections=(Section("INTRO", 0.0, 4.0),),
        confidence=0.4,
    )
    evidence = assemble_judgment_evidence(
        _judge(), source_hash, representation=rep, events=events,
        rule_versions={"rule:CLIPPING_CLUSTER": "temporal-hearing-v1"},
        structure=structure,
    )
    assert not any("structure_label" in n.data for n in evidence.nodes)
    assert any(u.reason == "PROFILE_UNCERTAINTY" for u in evidence.uncertainties)


def test_structure_absent_preserves_prior_behavior():
    evidence = _full_evidence(_clip_signal())
    assert not any("structure_label" in n.data for n in evidence.nodes)
    assert not any(u.reason == "PROFILE_UNCERTAINTY" for u in evidence.uncertainties)
    assert evidence.epistemic_state == "INFERRED"


# ---------------------------------------------------------------------------
# bundle semantics carry the new fields
# ---------------------------------------------------------------------------

def test_bundle_semantics_include_scale_and_epistemic():
    evidence = _full_evidence(_clip_signal())
    bundle = build_bundle(evidence)
    assert bundle["logical_hash"].startswith("sha256:")
    ref_nodes = [n for group in bundle["refs"].values() for n in group]
    assert all(n.get("epistemic_state") in EPISTEMIC_STATES for n in ref_nodes)
    assert all(n.get("scale") in EVIDENCE_SCALES | {None} for n in ref_nodes)
    assert bundle["judgment"]["evidence_state"] == "SUPPORTED"


def test_bundle_deterministic_with_new_fields():
    evidence = _full_evidence(_clip_signal())
    first = build_bundle(evidence)
    second = build_bundle(evidence)
    assert first["logical_hash"] == second["logical_hash"]
