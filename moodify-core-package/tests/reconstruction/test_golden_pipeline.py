"""Golden pipeline tests (MFY-CR-P06): objective, gates, blind tooling, record."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    DiagnosticCategory,
    EraDiagnosticFinding,
    FindingStatus,
)
from moodify.reconstruction.blind import make_blind_kit
from moodify.reconstruction.objective import plan_from_findings
from moodify.reconstruction.pipeline import check_hard_gates, run_golden_pipeline
from moodify.reconstruction.record import (
    GOLDEN_PENDING,
    GOLDEN_STATUSES,
    GoldenReconstructionRecord,
)

SR = 48000


def _wav(tmp_path, name, duration_s=4.0, sr=SR) -> Path:
    t = np.arange(int(sr * duration_s)) / sr
    x = 0.2 * np.sin(2 * np.pi * 440 * t)
    x = np.stack([x, x], axis=1)
    p = tmp_path / name
    sf.write(str(p), x.astype(np.float32), sr)
    return p


def _finding(category, status=FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
             confidence=ConfidenceLevel.LOW):
    return EraDiagnosticFinding(
        category=category, status=status, finding_id=f"{category.value}-1",
        reasoning_summary="t", measurement_refs=("m1", "m2"),
        confidence=None if status in {FindingStatus.NOT_APPLICABLE,
                                      FindingStatus.NOT_SUPPORTED_IN_V0_1} else confidence,
        created_at="T",
    )


class TestObjective:
    def test_deterministic_plans(self):
        findings = [_finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION)]
        a = plan_from_findings(findings)
        b = plan_from_findings(findings)
        assert a == b

    def test_source_first_then_abc(self):
        plans = plan_from_findings([])
        assert [p["candidate_id"] for p in plans] == ["SOURCE", "A", "B", "C"]
        assert plans[0]["params"] == {}

    def test_objective_refs_only_from_possible_or_observed(self):
        findings = [
            _finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION),
            _finding(DiagnosticCategory.ED_02_PERSISTENT_NOISE, FindingStatus.LIKELY_ARTISTIC_CHARACTER),
            _finding(DiagnosticCategory.ED_06_TRANSFER_ENCODING_DEGRADATION, FindingStatus.NOT_SUPPORTED_IN_V0_1),
        ]
        plans = plan_from_findings(findings)
        for p in plans[1:]:
            assert any("ED-01" in r for r in p["objective_refs"])
            assert not any("ED-02" in r for r in p["objective_refs"])
            assert not any("ED-06" in r for r in p["objective_refs"])

    def test_plan_hashes_deterministic(self):
        plans = plan_from_findings([])
        assert plans[1]["plan_hash"] == plans[1]["plan_hash"]
        assert plans[1]["plan_hash"] != plans[2]["plan_hash"]


class TestHardGates:
    def _metrics(self, wav_path):
        from moodify.reconstruction.pipeline import _metrics_of
        return _metrics_of(wav_path)

    def test_identical_sources_pass(self, tmp_path):
        a = _wav(tmp_path, "s.wav")
        assert check_hard_gates(self._metrics(a), self._metrics(a)) == []

    def test_new_clipping_fails(self, tmp_path):
        src = _wav(tmp_path, "s.wav")
        t = np.arange(int(SR * 4)) / SR
        x = 0.2 * np.sin(2 * np.pi * 440 * t)
        clipped = np.clip(np.stack([x * 8, x * 8], axis=1), -0.999, 0.999)
        c = tmp_path / "c.wav"
        sf.write(str(c), clipped.astype(np.float32), SR)
        failures = check_hard_gates(self._metrics(src), self._metrics(c))
        assert "NO_NEW_CLIPPING" in failures


class TestBlindTooling:
    def test_labels_hide_candidate_names(self, tmp_path):
        src = _wav(tmp_path, "src.wav")
        cands = {"A": _wav(tmp_path, "a.wav"), "B": _wav(tmp_path, "b.wav"),
                 "C": _wav(tmp_path, "c.wav")}
        out = tmp_path / "kit"
        kit = make_blind_kit(src, cands, out, seed=42)
        listening_files = sorted(p.name for p in (out / "listening").glob("*.wav"))
        assert listening_files == ["X1.wav", "X2.wav", "X3.wav", "X4.wav"]
        assert set(kit.mapping) == {"X1", "X2", "X3", "X4"}
        assert set(kit.mapping.values()) == {"SOURCE", "A", "B", "C"}
        # mapping is recorded but the kit is not finalized
        assert kit.finalized is False

    def test_level_match_aligns_loudness(self, tmp_path):
        src = _wav(tmp_path, "src.wav")
        louder = tmp_path / "loud.wav"
        t = np.arange(int(SR * 4)) / SR
        x_src = (0.2 * np.stack([np.sin(2*np.pi*440*t)]*2, axis=1)).astype(np.float32)
        sf.write(str(src), x_src, SR)
        sf.write(str(louder), (0.8 * np.stack([np.sin(2*np.pi*440*t)]*2, axis=1)).astype(np.float32), SR)
        out = tmp_path / "kit"
        make_blind_kit(src, {"A": louder}, out, seed=1)
        from moodify.auditory.loudness import integrated_loudness_lufs
        import soundfile as _sf
        matched, _ = _sf.read(str(out / "listening" / "X1.wav"), dtype="float32")
        target = integrated_loudness_lufs(x_src, SR)
        got = integrated_loudness_lufs(matched, SR)
        assert abs(got - target) < 1.0

    def test_no_candidate_name_in_listening_files(self, tmp_path):
        src = _wav(tmp_path, "src.wav")
        cands = {"A": _wav(tmp_path, "a.wav"), "B": _wav(tmp_path, "b.wav"),
                 "C": _wav(tmp_path, "c.wav")}
        out = tmp_path / "kit"
        make_blind_kit(src, cands, out, seed=3)
        content = (out / "blind_mapping.json").read_text(encoding="utf-8")
        assert "finalized" in content


class TestRecord:
    def test_round_trip(self):
        rec = GoldenReconstructionRecord(
            record_id="G-1", source_hash="abc", rights_status="OWNED",
            diagnostic_version="v1", objective_version="v1",
            identity_guard_version="v1", candidate_id="B", plan_hash="h",
            engine_version="v1", technical_result={}, human_result={},
            hardware_observations=[], created_at="T",
        )
        payload = json.loads(json.dumps(rec.to_dict(), sort_keys=True))
        assert payload["golden_status"] == GOLDEN_PENDING
        assert GOLDEN_PENDING in GOLDEN_STATUSES

    def test_statuses_are_explicit(self):
        assert set(GOLDEN_STATUSES) == {
            "GOLDEN_CONFIRMED", "PROMISING_NOT_GOLDEN", "SOURCE_WINS",
            "BLOCKED_BY_TECHNICAL_LIMITATION", "BLOCKED_BY_LISTENING_EVIDENCE",
            "PENDING_LISTENING",
        }


class TestPipelineIntegration:
    def test_full_pipeline_on_synthetic_source(self, tmp_path):
        src = _wav(tmp_path, "source.wav")
        out = tmp_path / "run"
        result = run_golden_pipeline(src, out, rights_status="OWNED",
                                     source_alias="TEST-001", created_at="T")
        assert result.source["sha256"]
        assert len(result.diagnostics) == 6
        # SOURCE + A/B/C all rendered and gated
        assert set(result.candidates) == {"SOURCE", "A", "B", "C"}
        for cid in ("A", "B", "C"):
            assert result.candidates[cid]["gates"] == [], cid
            assert (out / "candidates" / f"{cid}.wav").is_file()
        # identity verdicts present
        assert set(result.identity) == {"A", "B", "C"}
        # ranking includes SOURCE
        assert any(r["candidate_id"] == "SOURCE" for r in result.ranking)
        # blind kit exists
        assert (out / "blind_mapping.json").is_file()
        assert (out / "listening" / "X1.wav").is_file()
        # record written with pending status
        record = json.loads((out / "golden_record.json").read_text(encoding="utf-8"))
        assert record["golden_status"] == GOLDEN_PENDING
