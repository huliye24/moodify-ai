"""Characterization tests for workflow_engine temporal-texture refactor.

Freeze observable behavior of WorkflowOrchestrator stage methods before
structural changes (DSK-MFY-TEMPORAL-TEXTURE-001 wave 1).
No real audio files or LLM connectivity required.
"""

from __future__ import annotations

import numpy as np
import pytest

from moodify.orchestration.workflow_engine import (
    PhaseResult,
    PhaseStatus,
    PipelineContext,
    WorkflowOrchestrator,
    WorkflowResult,
)


def make_stereo(peak: float = 0.5, frames: int = 64) -> np.ndarray:
    t = np.linspace(0, 1, frames, endpoint=False)
    left = peak * np.sin(2 * np.pi * 2 * t)
    right = peak * np.sin(2 * np.pi * 3 * t + 0.4)
    return np.stack([left, right], axis=1)


def make_ctx(**overrides) -> PipelineContext:
    defaults = dict(
        input_path="in.wav",
        emotion_target="GA",
        platform="spotify",
        output_dir="out",
    )
    defaults.update(overrides)
    ctx = PipelineContext(**defaults)
    ctx.process_id = "test"
    return ctx


class TestResolveEmotion:
    def test_nl_failure_falls_back_to_gentle_awakening(self, monkeypatch) -> None:
        def boom(*_args, **_kwargs):
            raise RuntimeError("no LLM")

        monkeypatch.setattr(
            "moodify.knowledge.emotion_targets.resolve_emotion_from_nl", boom
        )
        orch = WorkflowOrchestrator()
        ctx = make_ctx()
        orch._resolve_emotion(ctx)
        assert ctx.emotion_parsed["emotion_key"] == "gentle_awakening"
        assert ctx.emotion_parsed["source"] == "fallback"

    def test_nl_empty_result_falls_back(self, monkeypatch) -> None:
        monkeypatch.setattr(
            "moodify.knowledge.emotion_targets.resolve_emotion_from_nl",
            lambda _text: {},
        )
        orch = WorkflowOrchestrator()
        ctx = make_ctx()
        orch._resolve_emotion(ctx)
        assert ctx.emotion_parsed["emotion_key"] == "gentle_awakening"
        assert ctx.emotion_parsed["source"] == "fallback"


class TestSpatial:
    def test_mono_skips_and_keeps_audio(self) -> None:
        orch = WorkflowOrchestrator()
        mono = np.zeros(64)
        result = orch._run_spatial(mono, 44100, "GA")
        assert result.status == PhaseStatus.COMPLETED
        assert result.output["audio"] is mono
        assert any("Mono" in w for w in result.warnings)

    def test_width_one_preserves_stereo(self, monkeypatch) -> None:
        monkeypatch.setattr(
            "moodify.knowledge.craft_chains.get_recommended_params",
            lambda _code: {"P12_reverb_width": 1.0},
        )
        orch = WorkflowOrchestrator()
        audio = make_stereo()
        result = orch._run_spatial(audio, 44100, "GA")
        assert np.allclose(result.output["audio"], audio)

    def test_width_scales_side_signal(self, monkeypatch) -> None:
        monkeypatch.setattr(
            "moodify.knowledge.craft_chains.get_recommended_params",
            lambda _code: {"P12_reverb_width": 0.5},
        )
        orch = WorkflowOrchestrator()
        audio = make_stereo()
        result = orch._run_spatial(audio, 44100, "GA")
        out = result.output["audio"]
        mid = (audio[:, 0] + audio[:, 1]) / 2.0
        side = (audio[:, 0] - audio[:, 1]) / 2.0
        assert np.allclose(out[:, 0], mid + 0.5 * side)
        assert np.allclose(out[:, 1], mid - 0.5 * side)

    def test_craft_card_failure_falls_back_to_width_one(self, monkeypatch) -> None:
        class BadCard:
            def get_recommended_params(self):
                raise RuntimeError("broken card")

        monkeypatch.setattr(
            "moodify.knowledge.craft_chains.get_recommended_params",
            lambda _code: {"P12_reverb_width": 1.0},
        )
        orch = WorkflowOrchestrator()
        audio = make_stereo()
        result = orch._run_spatial(audio, 44100, "GA", craft_card=BadCard())
        assert np.allclose(result.output["audio"], audio)

    def test_peak_near_ceiling_is_scaled(self, monkeypatch) -> None:
        monkeypatch.setattr(
            "moodify.knowledge.craft_chains.get_recommended_params",
            lambda _code: {"P12_reverb_width": 1.0},
        )
        orch = WorkflowOrchestrator()
        audio = make_stereo(peak=0.99)
        result = orch._run_spatial(audio, 44100, "GA")
        out = result.output["audio"]
        assert np.max(np.abs(out)) <= 0.98 + 1e-9


class TestBuildResult:
    def test_no_output_yields_empty_wave_state(self) -> None:
        orch = WorkflowOrchestrator()
        ctx = make_ctx()
        ctx.phases = [
            PhaseResult(
                phase=2,
                name="音频加载",
                status=PhaseStatus.FAILED,
                output={"audio": None, "sr": 44100},
            )
        ]
        result: WorkflowResult = orch._build_result(ctx)
        assert result.success is False
        assert result.wave_state_after == {}
        assert result.risk_level == "green"  # risk level is unconditional in current code

    def test_success_when_all_phases_completed(self) -> None:
        orch = WorkflowOrchestrator()
        ctx = make_ctx()
        ctx.phases = [
            PhaseResult(phase=1, name="诊断", status=PhaseStatus.COMPLETED, output={}),
            PhaseResult(phase=4, name="空间", status=PhaseStatus.SKIPPED, output={}),
        ]
        result = orch._build_result(ctx)
        assert result.success is True


class TestProcessFailure:
    def test_top_level_failure_returns_failed_result(self, monkeypatch) -> None:
        def boom(_self, _ctx):
            raise RuntimeError("diagnosis engine down")

        monkeypatch.setattr(WorkflowOrchestrator, "_diagnose", boom)
        orch = WorkflowOrchestrator()
        result = orch.process("missing.wav", "GA", output_dir="out")
        assert result.success is False
        assert result.risk_level == "error"
        assert result.process_id != ""


class TestFinalize:
    def test_all_side_blocks_failing_does_not_raise(self, monkeypatch) -> None:
        orch = WorkflowOrchestrator()

        class FakeLLM:
            available = True

            def narrate_diagnosis(self, **kwargs):
                raise RuntimeError("LLM down")

        def fake_import_llm_client(_name):
            module = type("m", (), {"DeepSeekClient": FakeLLM})()
            return module

        def boom_history(*_args, **_kwargs):
            raise OSError("history store unwritable")

        def boom_calibration(*_args, **_kwargs):
            raise RuntimeError("calibration failed")

        ctx = make_ctx()
        ctx.best_output = "out.wav"
        ctx.best_eds = 0.5
        ctx.best_whs = 1.0
        ctx.scores = [0.5]
        ctx.best_idx = 0
        ctx.emotion_parsed = {"emotion_code": "GA", "emotion_name": "GA"}
        ctx.candidates = [{"P01": 0.5}]
        ctx.strengths = [{"spectrum": 0.5}]

        monkeypatch.setattr(
            "moodify.llm.client.DeepSeekClient", FakeLLM
        )
        monkeypatch.setattr(
            "moodify.memory.history.ProcessingHistory",
            lambda _dir: type("H", (), {"save": boom_history})(),
        )
        monkeypatch.setattr(
            "moodify.memory.history.diagnosis_to_vector",
            lambda _d: [0.0] * 5,
        )
        monkeypatch.setattr(
            "moodify.calibration.online.update_calibration",
            boom_calibration,
        )

        # _finalize must not raise even when every side block fails
        orch._finalize(ctx)
        assert ctx.narrative is None
