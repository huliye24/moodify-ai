"""Facade contract tests for the 024 demonstrative enclosure.

Boundary: api_cli/cli_daw must reach DSP through the moodify.processing
facade, never through moodify.processing.operators internals. The facade
re-exports the operators used by engine_native; the contract test pins
that so callers stop knowing internal module layout.
"""

from __future__ import annotations

import ast
from pathlib import Path


class TestProcessingFacade:
    def test_facade_exposes_operators_used_by_engine_native(self) -> None:
        import moodify.processing as processing

        assert hasattr(processing, "apply_compressor")
        assert hasattr(processing, "apply_limiter")
        assert hasattr(processing, "apply_rbj_eq")

    def test_engine_native_imports_facade_not_internals(self) -> None:
        engine = (
            Path(__file__).resolve().parents[3]
            / "moodify-core-package" / "src" / "moodify" / "cli_daw" / "engine_native.py"
        )
        tree = ast.parse(engine.read_text(encoding="utf-8"))
        internal_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "moodify.processing.operators":
                internal_imports.append(node.lineno)
        assert internal_imports == [], f"engine_native still imports internals at lines {internal_imports}"

    def test_facade_reexports_do_not_change(self) -> None:
        import moodify.processing as processing

        assert processing.apply_compressor is not None
        assert processing.apply_limiter is not None
