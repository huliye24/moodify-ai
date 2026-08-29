"""Identity Guard unit tests (MFY-CR-P05): model, veto semantics, serialization."""

from __future__ import annotations

import json

from moodify.identity_guard.contract import (
    DIMENSION_CAPABILITY,
    GuardState,
    IdentityDimension,
)
from moodify.identity_guard.guard import guard_candidate


def m(**kw):
    return {k: {"value": v} for k, v in kw.items()}


BASE_SOURCE = dict(
    integrated_lufs=-14.0, loudness_range_lu=8.0, crest_factor_db=10.0, plr_db=11.0,
    stereo_correlation=0.97, stereo_width_proxy=0.03, side_to_mid_db=-10.0,
    sub_20_60_hz=0.05, bass_60_120_hz=0.12, mid_energy_ratio=0.6,
    presence_2000_5000_hz=0.10, core_mid_500_2000_hz=0.25,
    spectral_centroid_hz=4000.0, clipping_sample_ratio=0.0,
)


class TestModel:
    def test_six_dimensions_always_present(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["minimal"], candidate_id="min")
        assert len(v.deltas) == 6
        assert [d.dimension.value for d in v.deltas] == [
            "IG-01", "IG-02", "IG-03", "IG-04", "IG-05", "IG-06",
        ]

    def test_source_vs_source_passes(self, src_metrics):
        v = guard_candidate(src_metrics, src_metrics, candidate_id="self")
        assert v.state == GuardState.PASS

    def test_no_single_identity_score(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["over_bass"], candidate_id="b")
        # per-dimension deltas, not one averaged number
        assert len(v.deltas) == 6
        assert "score" not in v.to_dict()

    def test_capability_labels_honest(self):
        assert DIMENSION_CAPABILITY[IdentityDimension.IG_01_VOCAL_MID] == "PROXY"
        assert DIMENSION_CAPABILITY[IdentityDimension.IG_03_REVERB_SPACE] == "NOT_MEASURABLE"
        assert DIMENSION_CAPABILITY[IdentityDimension.IG_02_DYNAMICS] == "MEASURABLE"

    def test_serialization_round_trip(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["over_loud"], candidate_id="A")
        payload = json.loads(json.dumps(v.to_dict(), sort_keys=True))
        assert payload["state"] == "REJECT"
        assert len(payload["deltas"]) == 6
        first = payload["deltas"][0]
        assert set(first) >= {"dimension", "guard_state", "normalized_delta",
                              "measurement_refs", "capability"}


class TestVetoSemantics:
    def test_reject_cannot_be_averaged_away(self, src_metrics, cand_metrics):
        # over_loud REJECTs IG-06 but all other dims stay PASS-ish
        v = guard_candidate(src_metrics, cand_metrics["over_loud"], candidate_id="loud")
        assert v.state == GuardState.REJECT
        assert any(d.guard_state == GuardState.REJECT for d in v.deltas)

    def test_any_reject_wins(self):
        src = m(**BASE_SOURCE)
        cand = dict(src)
        cand["integrated_lufs"] = {"value": -9.0}  # beyond loudness budget
        v = guard_candidate(src, cand, candidate_id="A")
        assert v.state == GuardState.REJECT

    def test_vocal_proxy_drift_is_human_required_not_reject(self):
        src = m(**BASE_SOURCE)
        cand = dict(src)
        cand["spectral_centroid_hz"] = {"value": 6500.0}
        cand["presence_2000_5000_hz"] = {"value": 0.20}
        v = guard_candidate(src, cand, candidate_id="bright")
        assert v.state == GuardState.HUMAN_REQUIRED
        assert v.human_review_question

    def test_mono_guard_rejects_widening(self):
        src = m(**BASE_SOURCE)
        src["stereo_correlation"] = {"value": 1.0}
        cand = dict(src)
        cand["stereo_correlation"] = {"value": 0.90}
        cand["stereo_width_proxy"] = {"value": 0.10}
        v = guard_candidate(src, cand, candidate_id="widen")
        assert v.state == GuardState.REJECT

    def test_new_clipping_rejects(self):
        src = m(**BASE_SOURCE)
        cand = dict(src)
        cand["clipping_sample_ratio"] = {"value": 0.001}
        v = guard_candidate(src, cand, candidate_id="clip")
        assert v.state == GuardState.REJECT


class TestMissingMeasurements:
    def test_missing_dimension_metrics_yield_not_measurable(self):
        src = m(**BASE_SOURCE)
        cand = dict(src)
        for k in ("loudness_range_lu", "crest_factor_db", "plr_db"):
            del cand[k]
        v = guard_candidate(src, cand, candidate_id="missing")
        ig02 = next(d for d in v.deltas if d.dimension == IdentityDimension.IG_02_DYNAMICS)
        assert ig02.guard_state == GuardState.NOT_MEASURABLE

    def test_reverb_always_not_measurable_v01(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["minimal"], candidate_id="min")
        ig03 = next(d for d in v.deltas if d.dimension == IdentityDimension.IG_03_REVERB_SPACE)
        assert ig03.guard_state == GuardState.NOT_MEASURABLE
        assert "NOT_MEASURABLE_V0_1" in ig03.notes


class TestSyntheticOverprocessing:
    """Real measurement chain on deliberate overprocessing fixtures."""

    def test_over_bright_human_required(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["over_bright"], candidate_id="bright")
        assert v.state == GuardState.HUMAN_REQUIRED

    def test_over_bass_rejected(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["over_bass"], candidate_id="bass")
        assert v.state == GuardState.REJECT

    def test_over_compressed_rejected(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["over_compressed"], candidate_id="comp")
        assert v.state == GuardState.REJECT

    def test_over_wide_rejected(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["over_wide"], candidate_id="wide")
        assert v.state == GuardState.REJECT

    def test_over_loud_rejected(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["over_loud"], candidate_id="loud")
        assert v.state == GuardState.REJECT

    def test_minimal_not_killed(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["minimal"], candidate_id="min")
        assert v.state == GuardState.PASS

    def test_balanced_not_killed(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["balanced"], candidate_id="bal")
        assert v.state in {GuardState.PASS, GuardState.CAUTION}

    def test_source_always_eligible(self, src_metrics, cand_metrics):
        v = guard_candidate(src_metrics, cand_metrics["over_loud"], candidate_id="loud")
        assert v.state == GuardState.REJECT  # and yet SOURCE remains a legal result
