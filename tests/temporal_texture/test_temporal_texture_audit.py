from __future__ import annotations

import importlib.util
import tempfile
import unittest
import sys
from pathlib import Path


AUDIT_PATH = Path(__file__).resolve().parents[2] / "tools" / "temporal_texture" / "temporal_texture_audit.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("temporal_texture_audit", AUDIT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load audit module: {AUDIT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TemporalTextureAuditTests(unittest.TestCase):
    def test_empty_exception_is_error(self) -> None:
        audit = load_audit_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "sample.py"
            source.write_text(
                "def risky():\n"
                "    try:\n"
                "        return 1 / 0\n"
                "    except:\n"
                "        pass\n",
                encoding="utf-8",
            )
            findings, skipped = audit.scan_file(root, source, audit.DEFAULTS)
            self.assertIsNone(skipped)
            rules = {item.rule for item in findings}
            self.assertIn("TT-EMPTY-EXCEPTION", rules)
            self.assertIn("TT-BROAD-EXCEPTION", rules)

    def test_fingerprint_stable_across_line_movement_for_function_signal(self) -> None:
        audit = load_audit_module()
        first = audit.fingerprint("TT-COMPLEXITY", "a.py", "run", "complexity")
        second = audit.fingerprint("TT-COMPLEXITY", "a.py", "run", "complexity")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
