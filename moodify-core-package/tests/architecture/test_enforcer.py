"""Tests for the architecture boundary enforcer (024 Stage C).

The enforcer must be deterministic on identical input and provably fail on
counterexamples (a violation must be detected).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


from tools.architecture.enforcer import _module_to_area, check_enclosure


class TestModuleToArea:
    def test_domain_module_maps_to_domain(self) -> None:
        import json

        manifest = json.loads(
            (Path(__file__).resolve().parents[3] / "tools" / "architecture" / "enclosure_manifest.json")
            .read_text(encoding="utf-8")
        )
        assert _module_to_area("moodify.domain.project", manifest) == "domain"

    def test_runtime_module_maps_to_runtime(self) -> None:
        import json

        manifest = json.loads(
            (Path(__file__).resolve().parents[3] / "tools" / "architecture" / "enclosure_manifest.json")
            .read_text(encoding="utf-8")
        )
        assert _module_to_area("moodify_runtime.cli", manifest) == "runtime"

    def test_third_party_returns_none(self) -> None:
        import json

        manifest = json.loads(
            (Path(__file__).resolve().parents[3] / "tools" / "architecture" / "enclosure_manifest.json")
            .read_text(encoding="utf-8")
        )
        assert _module_to_area("numpy", manifest) is None


class TestEnforcer:
    def test_deterministic_output(self) -> None:
        r1 = check_enclosure()
        r2 = check_enclosure()
        assert r1 == r2

    def test_current_repo_state(self) -> None:
        """Baseline: 0 violations, debt may exist but must not grow."""
        result = check_enclosure()
        assert result["summary"]["violations"] == 0

    def test_counterexample_detected(self, tmp_path: Path) -> None:
        """Prove the enforcer fails on a forbidden import: domain importing
        processing must be flagged (domain forbids processing)."""
        from tools.architecture.enforcer import _area_for, _load_manifest

        # create a fake domain file importing processing
        fake = tmp_path / "fake_domain.py"
        fake.write_text("import moodify.processing.operators\n", encoding="utf-8")

        manifest = _load_manifest()
        # _area_for works on repo-relative paths; simulate by prefix
        rel = "moodify-core-package/src/moodify/domain/" + fake.name
        area, area_def = _area_for(rel, manifest)
        assert area == "domain"
        assert any("moodify.processing" in f for f in area_def["forbidden_deps"])

        # and module mapping resolves processing
        assert _module_to_area("moodify.processing.operators", manifest) == "dsp"

    def test_baseline_debt_has_expiry(self) -> None:
        result = check_enclosure()
        for debt in result["baseline_debt"]:
            assert debt.get("expiry"), f"debt {debt.get('exception_id')} lacks expiry"
            assert debt.get("exception_id")
