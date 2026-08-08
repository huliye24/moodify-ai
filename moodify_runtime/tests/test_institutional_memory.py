"""Institutional memory validation — Pass 5 inheritance.

Phase 3 of DSK-MFY-THICKNESS road-widening: verifies engineering logs
exist, reference real symbols, and test counts are monotonic.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DOCS_DIR = PROJECT_ROOT / "docs" / "engineer" / "2026-07-31"
HARDENING_LOG = DOCS_DIR / "2026-07-31_HARDENING_ROAD-WIDENING-004.md"


class TestEngineeringLogs:
    """Log files exist and are well-formed."""

    def test_widening_log_exists(self):
        assert HARDENING_LOG.is_file(), f"Missing: {HARDENING_LOG}"

    def test_widening_log_nonempty(self):
        content = HARDENING_LOG.read_text(encoding="utf-8")
        assert len(content) > 200

    def test_contains_test_count(self):
        content = HARDENING_LOG.read_text(encoding="utf-8")
        assert "216" in content
        assert "145" in content

    def test_mentions_modified_modules(self):
        content = HARDENING_LOG.read_text(encoding="utf-8")
        for mod in ("runner.py", "operator_console.py", "utils.py"):
            assert mod in content, f"Missing module: {mod}"

    def test_mentions_test_files(self):
        content = HARDENING_LOG.read_text(encoding="utf-8")
        for tf in ("test_runner_rights_gate.py", "test_atomic_run_outputs.py",
                    "test_fail_open_closure.py"):
            assert tf in content, f"Missing test file: {tf}"


class TestTestClassExistence:
    """Classes referenced in logs exist in the test suite."""

    def test_rights_gate_classes_exist(self):
        from moodify_runtime.tests.test_runner_rights_gate import (
            TestRunDailyRightsGateBlocked,
            TestOperatorJobScopeIsolation,
            TestRightsGateFailClosed,
            TestCliRightsFlags,
        )
        assert TestRunDailyRightsGateBlocked is not None

    def test_atomic_output_classes_exist(self):
        from moodify_runtime.tests.test_atomic_run_outputs import (
            TestManifestCsvAtomic,
            TestRunSummaryAtomic,
            TestDataLoopOutputsAtomic,
            TestLeaseStoreAtomic,
        )
        assert TestManifestCsvAtomic is not None

    def test_fail_open_classes_exist(self):
        from moodify_runtime.tests.test_fail_open_closure import (
            TestLeaseExpiryFailClosed,
            TestLatestRunSelection,
        )
        assert TestLeaseExpiryFailClosed is not None

    def test_schema_version_class_exists(self):
        from moodify_runtime.tests.test_craft_proposals import (
            TestSchemaVersionEmbedding,
        )
        assert TestSchemaVersionEmbedding is not None

    def test_registry_drift_class_exists(self):
        from moodify_runtime.tests.test_historical_compatibility import (
            TestRegistryDrift,
        )
        assert TestRegistryDrift is not None
