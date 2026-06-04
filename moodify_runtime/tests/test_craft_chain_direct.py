"""Direct unit tests for craft_chain module — ChainStep, ChainPlan, executor."""
import tempfile
from pathlib import Path

import pytest

from moodify_runtime.craft_chain import (
    ChainStep, ChainPlan, ChainManifest, ChainResult,
    CraftChainExecutor, preset_to_chain, get_preset_names,
)


class TestChainStep:
    def test_default_creation(self):
        s = ChainStep(op_id="input_normalize")
        assert s.op_id == "input_normalize"
        assert s.enabled
        assert s.step_id

    def test_disabled_step(self):
        s = ChainStep(op_id="test", enabled=False)
        assert not s.enabled

    def test_with_params(self):
        s = ChainStep(op_id="eq_lowshelf", params={"freq_hz": 200, "gain_db": 3.0, "q": 0.7})
        assert s.params["freq_hz"] == 200
        assert s.params["q"] == 0.7

    def test_step_id_unique(self):
        s1 = ChainStep(op_id="a")
        s2 = ChainStep(op_id="b")
        assert s1.step_id != s2.step_id


class TestChainPlan:
    def test_empty_plan(self):
        cp = ChainPlan(chain_id="empty", steps=[])
        assert cp.chain_id == "empty"
        assert len(cp.steps) == 0

    def test_plan_with_steps(self):
        steps = [ChainStep(op_id="normalize"), ChainStep(op_id="compressor")]
        cp = ChainPlan(chain_id="mastering", steps=steps, source_audio="in.wav",
                       estimated_steps=2, risk_level="low")
        assert len(cp.steps) == 2
        assert cp.risk_level == "low"

    def test_plan_is_mutable(self):
        cp = ChainPlan(chain_id="build", steps=[])
        cp.steps.append(ChainStep(op_id="loudness_landing"))
        assert len(cp.steps) == 1


class TestChainManifest:
    def test_manifest_fields(self):
        m = ChainManifest(
            chain_id="M-001", source_audio="src.wav", output_audio="out.wav",
            steps_executed=5, steps_succeeded=5, steps_failed=0,
            steps=[], total_risk="low",
        )
        assert m.chain_id == "M-001"
        assert m.steps_succeeded == 5

    def test_version_default(self):
        m = ChainManifest(
            chain_id="M-002", source_audio="s.wav", output_audio="o.wav",
            steps_executed=0, steps_succeeded=0, steps_failed=0,
            steps=[], total_risk="low",
        )
        assert m.version is not None


class TestChainResult:
    def test_success_result(self):
        r = ChainResult(chain_id="R1", success=True, output_path="/tmp/out.wav",
                        steps=[], manifest=None, error="",
                        artifacts=[])
        assert r.success
        assert r.output_path == "/tmp/out.wav"

    def test_failure_result(self):
        r = ChainResult(chain_id="R2", success=False, output_path="",
                        steps=[], manifest=None, error="DSP crashed",
                        artifacts=[])
        assert not r.success
        assert r.error == "DSP crashed"


class TestPresetToChain:
    def test_all_presets_return_steps(self):
        for name in get_preset_names():
            steps = preset_to_chain(name)
            assert isinstance(steps, list), f"preset {name} did not return list"
            assert len(steps) > 0, f"preset {name} returned 0 steps"

    def test_warm_vocal_chain(self):
        steps = preset_to_chain("warm_vocal")
        op_ids = [s.op_id for s in steps]
        # Should include warmth-related operations
        assert len(op_ids) > 0

    def test_clean_master_chain(self):
        steps = preset_to_chain("clean_master")
        assert len(steps) > 0

    def test_wide_space_chain(self):
        steps = preset_to_chain("wide_space")
        assert len(steps) > 0


class TestCraftChainExecutor:
    def test_default_init(self):
        ex = CraftChainExecutor()
        assert ex.max_chain_time_s >= 0

    def test_keep_artifacts(self):
        ex = CraftChainExecutor(keep_artifacts=True)
        assert ex.keep_artifacts

    def test_execute_empty_chain_no_input(self):
        ex = CraftChainExecutor()
        # Should raise FileNotFoundError for missing input
        with pytest.raises(FileNotFoundError):
            ex.execute(input_path="/nonexistent/test.wav", steps=[])

    def test_max_chain_time_configurable(self):
        ex = CraftChainExecutor(max_chain_time_s=60.0)
        assert ex.max_chain_time_s == 60.0
