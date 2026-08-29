"""Identity Gate ranking tests (MFY-CR-P05 §16)."""

from __future__ import annotations

from moodify.identity_guard.contract import GuardState
from moodify.identity_guard.guard import guard_candidate
from moodify.identity_guard.ranking import rank_candidates


def _verdicts(src, cand_metrics, names):
    return [guard_candidate(src, cand_metrics[name], candidate_id=name) for name in names]


class TestRankingRules:
    def test_reject_cannot_be_top(self, src_metrics, cand_metrics):
        vs = _verdicts(src_metrics, cand_metrics, ["over_loud", "over_bright", "minimal"])
        ranks = rank_candidates(vs, objective_progress={
            "over_loud": 0.99, "over_bright": 0.5, "minimal": 0.1,
        })
        assert ranks[0].candidate_id == "minimal"  # PASS beats high-progress REJECT
        assert ranks[0].auto_approvable

    def test_reject_never_auto_approvable(self, src_metrics, cand_metrics):
        vs = _verdicts(src_metrics, cand_metrics, ["over_loud", "over_wide", "over_bass"])
        ranks = rank_candidates(vs, objective_progress={})
        assert all(not r.auto_approvable for r in ranks if r.guard_state == GuardState.REJECT)

    def test_human_required_never_auto_approved(self, src_metrics, cand_metrics):
        vs = _verdicts(src_metrics, cand_metrics, ["over_bright"])
        ranks = rank_candidates(vs, objective_progress={"over_bright": 0.9})
        assert ranks[0].guard_state == GuardState.HUMAN_REQUIRED
        assert not ranks[0].auto_approvable

    def test_source_always_eligible(self, src_metrics, cand_metrics):
        vs = _verdicts(src_metrics, cand_metrics, ["over_loud"])
        ranks = rank_candidates(vs, objective_progress={"over_loud": 0.99})
        assert ranks[-1].candidate_id == "source"
        assert ranks[-1].auto_approvable

    def test_technical_improvement_cannot_override_identity(self, src_metrics, cand_metrics):
        """Best objective progress but identity REJECT -> loses to PASS candidate."""
        vs = _verdicts(src_metrics, cand_metrics, ["over_loud", "balanced"])
        ranks = rank_candidates(vs, objective_progress={
            "over_loud": 0.95, "balanced": 0.3,
        })
        assert ranks[0].candidate_id == "balanced"
        assert ranks[0].guard_state == GuardState.PASS

    def test_caution_ranks_below_pass(self, src_metrics, cand_metrics):
        # minimal + loud-ish candidate: minimal PASS, loud CAUTION-or-HUMAN_REQUIRED
        # (IG-03 unmeasured in v0.1 escalates any change to HUMAN_REQUIRED —
        #  CAUTION-only overall is unreachable by design)
        from moodify.identity_guard.guard import guard_candidate as gc

        src = src_metrics
        cand = dict(src)
        cand["integrated_lufs"] = {"value": src["integrated_lufs"]["value"] + 2.0}
        loudish = gc(src, cand, candidate_id="loudish")
        assert loudish.state in {GuardState.CAUTION, GuardState.HUMAN_REQUIRED}
        assert not loudish.state == GuardState.PASS
        ranks = rank_candidates([loudish, gc(src, cand_metrics["minimal"], candidate_id="min")],
                                objective_progress={"loudish": 0.9, "min": 0.2})
        assert ranks[0].candidate_id == "min"
        assert ranks[0].auto_approvable
