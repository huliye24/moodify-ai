"""Tests for mrs_calibration."""
import tempfile
from pathlib import Path
import pytest
from moodify_runtime.mrs_calibration import (
    CalibrationSampleSet, CalibrationReview, GateAudit, _sid,
    create_calibration_sample_set, submit_calibration_review,
    run_gate_audit, list_calibration_sample_sets,
    list_calibration_reviews,
)
from moodify_runtime.config import RuntimeConfig

@pytest.fixture
def cc():
    d = tempfile.mkdtemp()
    c = RuntimeConfig(project_root=Path(d), calibration_data_dir=Path(d) / "cal")
    c.calibration_data_dir.mkdir(parents=True, exist_ok=True)
    return c

class TestIdHelper:
    def test_sid(self):
        assert len(_sid("sample_set")) > 10

class TestCal:
    def test_set(self):
        s = CalibrationSampleSet(set_id="S1", name="Test", description="desc", sample_count=2)
        assert s.set_id == "S1"
    def test_review(self):
        r = CalibrationReview(review_id="R1", set_id="S1", candidate_id="C1",
                             human_decision="better", gate_decision="PASS", reviewer="human")
        assert r.review_id == "R1"
    def test_audit(self):
        a = GateAudit(audit_id="A1", set_id="S1", false_positives=3, false_negatives=1, accuracy=0.92)
        assert a.accuracy == 0.92

class TestCRUD:
    def test_create(self, cc):
        s = create_calibration_sample_set(cc, "Test", "desc", ["s1", "s2"])
        assert s["name"] == "Test"
    def test_review(self, cc):
        s = create_calibration_sample_set(cc, "Set", "desc", ["a", "b"])
        r = submit_calibration_review(cc, s["set_id"], "human", "better", 50, "good")
        assert r["reviewer"] in ("human", "operator")
    def test_audit(self, cc):
        s = create_calibration_sample_set(cc, "A", "desc", ["x"])
        result = run_gate_audit(cc, s["set_id"])
        assert isinstance(result, dict)
    def test_lists(self, cc):
        assert isinstance(list_calibration_sample_sets(cc), list)
