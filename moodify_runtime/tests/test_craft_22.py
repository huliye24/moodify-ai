"""Tests for CRAFT-22-012 — chain, selector, processes, memory, probes."""
import pytest
from moodify_runtime.craft_chain import (
    ChainStep, ChainPlan, ChainManifest, ChainResult,
    CraftChainExecutor, preset_to_chain, get_preset_names,
)
from moodify_runtime.craft_selector import (
    CraftSelectionInput, SelectionResult, select_craft,
    check_dangerous_combinations, filter_by_risk,
)
from moodify_runtime.craft_processes import (
    RiskLevel, OpCategory, CraftOperation, OpResult,
    get_registry, get_active_operations, get_operation,
    list_operation_ids,
)


class TestChainStep:
    def test_default_step(self):
        s = ChainStep(op_id="input_normalize")
        assert s.op_id == "input_normalize"
        assert s.enabled

    def test_step_with_params(self):
        s = ChainStep(op_id="bass_body_shaping",
                      params={"freq_hz": 200, "gain_db": 2.5})
        assert s.params["freq_hz"] == 200

    def test_step_has_step_id(self):
        s = ChainStep(op_id="test")
        assert len(s.step_id) > 0


class TestChainPlan:
    def test_empty_plan(self):
        cp = ChainPlan(chain_id="test-chain", steps=[])
        assert cp.chain_id == "test-chain"
        assert len(cp.steps) == 0

    def test_add_step(self):
        cp = ChainPlan(chain_id="master", steps=[], risk_level="medium")
        s = ChainStep(op_id="input_normalize")
        cp.steps.append(s)
        assert len(cp.steps) == 1

    def test_multiple_steps_ordered(self):
        cp = ChainPlan(chain_id="full", steps=[], source_audio="test.wav",
                       estimated_steps=3, risk_level="low")
        for oid in ["input_normalize", "silence_trim", "bass_body_shaping"]:
            cp.steps.append(ChainStep(op_id=oid))
        assert cp.steps[0].op_id == "input_normalize"
        assert len(cp.steps) == 3


class TestPresetToChain:
    def test_warm_vocal_returns_steps(self):
        steps = preset_to_chain("warm_vocal")
        assert isinstance(steps, list)
        assert len(steps) > 0

    def test_clean_master_returns_steps(self):
        steps = preset_to_chain("clean_master")
        assert len(steps) > 0

    def test_wide_space_returns_steps(self):
        steps = preset_to_chain("wide_space")
        assert len(steps) > 0

    def test_get_preset_names(self):
        names = get_preset_names()
        assert "warm_vocal" in names


class TestChainManifest:
    def test_manifest_fields(self):
        m = ChainManifest(
            chain_id="CHAIN-001",
            source_audio="input.wav",
            output_audio="output.wav",
            steps_executed=3, steps_succeeded=3, steps_failed=0,
            steps=[], total_risk="low",
        )
        assert m.chain_id == "CHAIN-001"
        assert m.steps_executed == 3
        assert m.total_risk == "low"

    def test_version_default(self):
        m = ChainManifest(chain_id="C1", source_audio="s.wav",
                          output_audio="o.wav",
                          steps_executed=0, steps_succeeded=0,
                          steps_failed=0, steps=[], total_risk="low")
        assert m.version is not None


class TestChainExecutor:
    def test_executor_defaults(self):
        ex = CraftChainExecutor(keep_artifacts=False)
        assert ex.max_chain_time_s == 300.0

    def test_execute_with_steps_no_input(self):
        ex = CraftChainExecutor(keep_artifacts=False)
        steps = [ChainStep(op_id="loudness_landing")]
        # execute() expects real files; verify it at least raises
        # a predictable error on missing input
        with pytest.raises(FileNotFoundError):
            ex.execute(input_path="/nonexistent/test.wav", steps=steps)


class TestCraftSelector:
    def test_input_defaults(self):
        inp = CraftSelectionInput()
        assert inp.max_risk == "medium"

    def test_input_with_findings(self):
        inp = CraftSelectionInput(
            ct_findings=[{"issue": "over_dark", "severity": "warn"}],
            mrs_score=0.45, genre="rock",
        )
        assert len(inp.ct_findings) == 1

    def test_select_returns_result(self):
        inp = CraftSelectionInput(
            ct_findings=[{"issue": "over_dark", "severity": "critical"}],
            mrs_score=0.25, max_risk="high",
        )
        result = select_craft(inp)
        assert isinstance(result, SelectionResult)
        assert len(result.steps) > 0
        assert result.risk_level == "high"

    def test_dangerous_combinations(self):
        warnings = check_dangerous_combinations(["overdark_fix", "clarity_boost"])
        assert isinstance(warnings, list)

    def test_filter_by_risk_basic(self):
        ops = ["input_normalize", "silence_trim", "loudness_landing"]
        filtered = filter_by_risk(ops, max_risk="low")
        assert "input_normalize" in filtered


class TestCraftProcesses:
    def test_registry_populated(self):
        reg = get_registry()
        assert len(reg) > 0

    def test_get_operation(self):
        ids = list_operation_ids()
        if ids:
            op = get_operation(ids[0])
            assert op is not None

    def test_get_operation_missing(self):
        op = get_operation("nonexistent_v99")
        assert op is None

    def test_list_operation_ids_count(self):
        ids = list_operation_ids()
        assert len(ids) >= 5

    def test_risk_level_enum(self):
        assert RiskLevel.LOW is not None
        assert RiskLevel.MEDIUM is not None
        assert RiskLevel.HIGH is not None

    def test_active_operations(self):
        active = get_active_operations()
        assert len(active) > 0

    def test_craft_operation_fields(self):
        op = CraftOperation(
            op_id="test_op", name="Test Operation",
            category=OpCategory.DYNAMICS,
            risk=RiskLevel.LOW,
        )
        assert op.op_id == "test_op"
        assert op.name == "Test Operation"
        assert op.risk == RiskLevel.LOW
