"""Tests for craft_selector."""
from moodify_runtime.craft_selector import (
    CraftSelectionInput, SelectionResult, select_craft,
    check_dangerous_combinations, filter_by_risk,
)

class TestSelectionInput:
    def test_defaults(self):
        i = CraftSelectionInput()
        assert i.max_risk == "medium"

class TestSelect:
    def test_returns_result(self):
        i = CraftSelectionInput(
            ct_findings=[{"issue": "over_dark", "severity": "critical"}],
            mrs_score=0.25, max_risk="high")
        result = select_craft(i)
        assert isinstance(result, SelectionResult)

class TestFilter:
    def test_basic(self):
        result = filter_by_risk(["input_normalize", "silence_trim"], max_risk="low")
        assert "input_normalize" in result

class TestDangerous:
    def test_checks(self):
        w = check_dangerous_combinations(["overdark_fix", "clarity_boost"])
        assert isinstance(w, list)
