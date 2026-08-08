"""Tests for fusion_scorer — unified artifact/overprocessing/intent loss."""
from moodify_runtime.fusion_scorer import (
    compute_fusion_score,
    compute_artifact_penalty,
    compute_overprocessing_penalty,
    compute_intent_loss_penalty,
    format_fusion_report,
    FusionScore,
)


class TestArtifactPenalty:
    def test_no_artifact(self):
        p, signals = compute_artifact_penalty("none", 0.0, [])
        assert p == 0.0
        assert signals == []

    def test_severe_artifact(self):
        p, signals = compute_artifact_penalty("severe", 0.9, ["low_mid", "mid"])
        assert p >= 40.0
        assert len(signals) == 2

    def test_mild_artifact(self):
        p, signals = compute_artifact_penalty("mild", 0.3, ["sub_bass"])
        assert 10.0 < p < 40.0
        assert len(signals) == 1


class TestOverprocessingPenalty:
    def test_no_overprocessing(self):
        p, flags = compute_overprocessing_penalty(30, 30, 12, 12, -18, -18)
        assert p == 0.0
        assert flags == []

    def test_dr_crush(self):
        p, flags = compute_overprocessing_penalty(30, 5, 12, 12, -18, -18)
        assert p > 30.0
        assert any("dr_crush" in f for f in flags)

    def test_excessive_gain(self):
        p, flags = compute_overprocessing_penalty(30, 30, 12, 12, -18, -5)
        assert p > 15.0
        assert any("excessive_gain" in f for f in flags)

    def test_high_step_count(self):
        p, flags = compute_overprocessing_penalty(30, 30, 12, 12, -18, -18, num_steps=20)
        assert p > 5.0
        assert any("high_step_count" in f for f in flags)


class TestIntentLossPenalty:
    def test_no_intent_loss(self):
        p, flags = compute_intent_loss_penalty(-18, -18)
        assert p == 0.0

    def test_large_eds_drift(self):
        p, flags = compute_intent_loss_penalty(-18, -5)
        assert p > 30.0
        assert any("eds_large_drift" in f for f in flags)

    def test_sign_flip(self):
        p, flags = compute_intent_loss_penalty(-18, 18, emotion="gentle")
        assert p > 20.0
        assert any("emotion_sign_flip" in f for f in flags)


class TestComputeFusionScore:
    def test_clean_sample(self):
        fs = compute_fusion_score(
            sample_id="S1", preset="warm", genre="piano",
            over_dark_level="none",
            dr_before=30, dr_after=30,
            crest_before=12, crest_after=12,
            rms_before=-18, rms_after=-18,
            eds_before=-18, eds_after=-18,
        )
        assert fs.verdict == "PASS"
        assert fs.composite_quality >= 95.0
        assert fs.composite_penalty < 10.0

    def test_problematic_sample(self):
        fs = compute_fusion_score(
            sample_id="S2", preset="aggressive", genre="rock",
            over_dark_level="severe", over_dark_score=0.8,
            over_dark_bands=["low_mid", "mid"],
            dr_before=30, dr_after=5,
            crest_before=12, crest_after=4,
            rms_before=-18, rms_after=-3,
            eds_before=-18, eds_after=-2,
            num_steps=20,
        )
        assert fs.verdict in ("REVIEW", "REJECT")
        assert fs.composite_penalty > 30.0

    def test_to_dict(self):
        fs = compute_fusion_score(sample_id="S1")
        d = fs.to_dict()
        assert d["sample_id"] == "S1"
        assert "artifact_penalty" in d


class TestFormatFusionReport:
    def test_clean_report(self):
        fs = compute_fusion_score(sample_id="S1")
        md = format_fusion_report(fs)
        assert "# Fusion Score Report" in md
        assert "PASS" in md
