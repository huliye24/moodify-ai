"""Tests for craft_evidence — 22-process evidence manifest."""
import json
import tempfile
from pathlib import Path

from moodify_runtime.craft_evidence import (
    StepEvidence,
    CraftManifest,
    create_step_evidence,
    create_manifest,
    write_manifest,
    load_manifest,
    can_write_back,
    list_process_categories,
)


class TestStepEvidence:
    def test_create_with_metrics(self):
        before = {"rms_db": -18.0, "dynamic_range_db": 30.0}
        after = {"rms_db": -16.0, "dynamic_range_db": 28.0}
        ev = create_step_evidence(
            "input_normalize", 0,
            metrics_before=before, metrics_after=after,
            duration_s=1.5,
        )
        assert ev.op_id == "input_normalize"
        assert ev.op_name == "Input Normalize"
        assert ev.category == "prepare"
        assert ev.risk == "low"
        assert ev.step_index == 0
        assert ev.delta["rms_db"] == 2.0
        assert ev.delta["dynamic_range_db"] == -2.0
        assert ev.duration_s == 1.5

    def test_create_with_error(self):
        ev = create_step_evidence("input_normalize", 0, error="file not found")
        assert ev.error == "file not found"

    def test_to_dict_round_trip(self):
        ev = create_step_evidence("input_normalize", 0)
        d = ev.to_dict()
        ev2 = StepEvidence.from_dict(d)
        assert ev2.op_id == ev.op_id
        assert ev2.step_index == ev.step_index


class TestCraftManifest:
    def test_create_and_serialize(self):
        steps = [
            create_step_evidence("input_normalize", 0),
            create_step_evidence("silence_trim", 1),
        ]
        manifest = create_manifest("M1", "R1", "standard_chain", steps)
        assert manifest.total_steps >= 22
        assert manifest.manifest_id == "M1"
        assert manifest.run_id == "R1"
        s = manifest.summary()
        assert s["steps_recorded"] == 2

    def test_write_and_load(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "manifest.json"
        manifest = create_manifest("M1", "R1", "test_chain")
        write_manifest(manifest, p)
        loaded = load_manifest(p)
        assert loaded.manifest_id == "M1"
        assert loaded.total_steps == manifest.total_steps


class TestCanWriteBack:
    def test_clean_manifest_with_rights_and_approval_passes(self):
        steps = [
            create_step_evidence("input_normalize", 0),
            create_step_evidence("silence_trim", 1),
        ]
        manifest = create_manifest("M1", "R1", "test_chain", steps)
        manifest.total_steps = 2
        allowed, reason = can_write_back(manifest, rights_cleared=True, human_approved=True)
        assert allowed is True
        assert reason == "ok"

    def test_step_error_rejects(self):
        steps = [
            create_step_evidence("input_normalize", 0),
            create_step_evidence("silence_trim", 1, error="file missing"),
        ]
        manifest = create_manifest("M1", "R1", "test_chain", steps)
        allowed, reason = can_write_back(manifest, rights_cleared=True, human_approved=True)
        assert allowed is False
        assert "error" in reason

    def test_incomplete_steps_rejects(self):
        steps = [create_step_evidence("input_normalize", 0)]
        manifest = create_manifest("M1", "R1", "test_chain", steps)
        allowed, reason = can_write_back(manifest, rights_cleared=True, human_approved=True)
        assert allowed is False
        assert "incomplete" in reason

    def test_no_rights_rejects(self):
        steps = [create_step_evidence("input_normalize", 0)]
        manifest = create_manifest("M1", "R1", "test_chain", steps)
        manifest.total_steps = 1
        allowed, reason = can_write_back(manifest, rights_cleared=False, human_approved=True)
        assert allowed is False
        assert "rights" in reason

    def test_requires_human_approval_flag(self):
        steps = [create_step_evidence("input_normalize", 0)]
        manifest = create_manifest("M1", "R1", "test_chain", steps)
        manifest.total_steps = 1
        manifest.provenance["requires_human_approval"] = True
        allowed, reason = can_write_back(manifest, rights_cleared=True, human_approved=False)
        assert allowed is False
        assert "human approval" in reason

    def test_no_steps_rejects(self):
        manifest = create_manifest("M1", "R1", "test_chain", [])
        allowed, reason = can_write_back(manifest, rights_cleared=True, human_approved=True)
        assert allowed is False

    def test_zero_total_steps_rejects(self):
        steps = [create_step_evidence("input_normalize", 0)]
        manifest = create_manifest("M1", "R1", "test_chain", steps)
        manifest.total_steps = 0
        allowed, reason = can_write_back(manifest, rights_cleared=True, human_approved=True)
        assert allowed is False


class TestListProcessCategories:
    def test_returns_categories(self):
        cats = list_process_categories()
        assert "prepare" in cats
        assert "corrective" in cats
        assert "enhance" in cats
        assert "dynamics" in cats
        assert "spatial" in cats
        total = sum(len(v) for v in cats.values())
        assert total >= 22
