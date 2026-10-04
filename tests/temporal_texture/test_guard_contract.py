"""Contract tests for the temporal-texture guard.

These exist because the guard had no tests at all, and consequently rotted: it
reported churn instead of change for weeks, and four findings were silently
invisible to it. Each test below pins one property that a gate must have to be
worth trusting.

The load-bearing one is `test_inserting_a_line_above_a_finding_does_not_rekey_it`:
it fails against the previous line-keyed fingerprint scheme.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = ROOT / "tools" / "temporal_texture"


def _load(module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, TOOL_DIR / f"{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    # Register before exec: the tool's @dataclass needs sys.modules[__module__].
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


audit = _load("temporal_texture_audit")
guard = _load("temporal_texture_guard")

CONFIG = tomllib.loads((ROOT / ".moodify" / "temporal_texture.toml").read_text(encoding="utf-8"))

# Two blocks with identical bodies behind the same method name in different
# classes -- the shape that used to collapse into one fingerprint.
TWIN_SCOPES = (
    "class Alpha:\n"
    "    def run(self):\n"
    "        try:\n"
    "            work()\n"
    "        except Exception:\n"
    "            pass\n"
    "class Beta:\n"
    "    def run(self):\n"
    "        try:\n"
    "            work()\n"
    "        except Exception:\n"
    "            pass\n"
)

# The same handler twice inside one function.
TWIN_HANDLERS = (
    "def f():\n"
    "    try:\n"
    "        a()\n"
    "    except Exception:\n"
    "        pass\n"
    "    try:\n"
    "        b()\n"
    "    except Exception:\n"
    "        pass\n"
)

LONG_LINE = "x = '" + "a" * 130 + "'\n"


def _py(text: str):
    """AST-based rules (complexity, length, nesting, exception handlers)."""
    return audit.scan_python(Path("sample.py"), "sample.py", text, CONFIG)


def _text(text: str):
    """Textual rules (line length, debt markers, empty catch).

    Line length is NOT an AST rule: calling scan_python for it returns an empty
    list, which would make the assertions below vacuous.
    """
    return audit.scan_textual(Path("sample.py"), "sample.py", text, CONFIG)


def _finding(fp: str, severity: str = "error", rule: str = "TT-EMPTY-EXCEPTION", line: int = 1):
    return {
        "fingerprint": fp, "rule": rule, "severity": severity, "path": "a.py",
        "line": line, "column": 0, "symbol": "f", "message": "m", "evidence": {},
    }


def _report(tmp_path: Path, name: str, findings: list) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps({"schema_version": "1.0", "findings": findings}), encoding="utf-8")
    return path


def _run_guard(monkeypatch, baseline: Path, current: Path, tmp_path: Path) -> int:
    monkeypatch.setattr(sys, "argv", [
        "guard", "--baseline", str(baseline), "--current", str(current),
        "--out", str(tmp_path / "guard.md"),
    ])
    return guard.main()


# ── identity is stable under edits that change nothing about the finding ──


def test_inserting_a_line_above_a_finding_does_not_rekey_it():
    """The defect that made the gate unusable.

    Adding one harmless comment above a finding must leave its identity alone.
    Under the previous scheme this re-keyed every line-keyed rule below the
    insertion point, so the guard reported resolved+new for an edit that
    changed nothing.
    """
    before = _text(LONG_LINE)
    after = _text("# harmless comment\n" + LONG_LINE)

    assert before and after, "fixture must produce findings, or this test is vacuous"
    assert [f.fingerprint for f in before] == [f.fingerprint for f in after]
    assert {f.line for f in after} == {f.line + 1 for f in before}


def test_identical_symbols_in_different_scopes_do_not_collide():
    """Repeated method names are different functions and must stay distinct.

    ``finding_map`` is a plain dict, so a collision silently drops a finding —
    this used to hide four findings from the guard.
    """
    findings = _py(TWIN_SCOPES)
    # `except Exception: pass` is both broad and empty, so each block yields two
    # findings; two scopes therefore yield four.
    assert len(findings) == 4
    assert len({f.fingerprint for f in findings}) == 4
    empty = [f for f in findings if f.rule == "TT-EMPTY-EXCEPTION"]
    assert {f.symbol for f in empty} == {"Alpha.run", "Beta.run"}


def test_identical_handlers_in_one_scope_do_not_collide():
    findings = _py(TWIN_HANDLERS)
    assert len(findings) == 4  # two handlers x (broad + empty)
    assert len({f.fingerprint for f in findings}) == 4


def test_textual_findings_do_not_collide_across_lines():
    """Three identical long lines must stay three distinct findings."""
    findings = _text(LONG_LINE * 3)
    assert len(findings) == 3
    assert len({f.fingerprint for f in findings}) == 3


def test_no_finding_pair_shares_a_fingerprint():
    """Generalised guard for the property the two tests above spot-check."""
    for text in (TWIN_SCOPES, TWIN_HANDLERS):
        fingerprints = [f.fingerprint for f in _py(text)]
        assert fingerprints, "fixture must produce findings"
        assert len(fingerprints) == len(set(fingerprints))
    textual = [f.fingerprint for f in _text(LONG_LINE * 3)]
    assert textual and len(textual) == len(set(textual))


# ── the guard's own pass/fail contract ─────────────────────────────────────


def test_guard_passes_when_current_equals_baseline(tmp_path, monkeypatch):
    same = [_finding("fp1"), _finding("fp2", severity="warning")]
    baseline = _report(tmp_path, "b.json", same)
    current = _report(tmp_path, "c.json", same)
    assert _run_guard(monkeypatch, baseline, current, tmp_path) == 0


def test_guard_fails_on_a_newly_introduced_error(tmp_path, monkeypatch):
    baseline = _report(tmp_path, "b.json", [_finding("fp1")])
    current = _report(tmp_path, "c.json", [_finding("fp1"), _finding("fp2")])
    assert _run_guard(monkeypatch, baseline, current, tmp_path) == 1


def test_a_removed_violation_is_resolved_not_new(tmp_path, monkeypatch):
    baseline = _report(tmp_path, "b.json", [_finding("fp1"), _finding("fp2")])
    current = _report(tmp_path, "c.json", [_finding("fp1")])
    assert _run_guard(monkeypatch, baseline, current, tmp_path) == 0


def test_new_warnings_do_not_fail_by_default(tmp_path, monkeypatch):
    baseline = _report(tmp_path, "b.json", [])
    current = _report(tmp_path, "c.json", [_finding("fp1", severity="warning")])
    assert _run_guard(monkeypatch, baseline, current, tmp_path) == 0


def test_guard_rejects_a_report_it_cannot_read(tmp_path, monkeypatch):
    current = tmp_path / "c.json"
    current.write_text("{}", encoding="utf-8")
    baseline = _report(tmp_path, "b.json", [])
    assert _run_guard(monkeypatch, baseline, current, tmp_path) == 2


# ── determinism ────────────────────────────────────────────────────────────


def test_finding_map_is_order_independent():
    findings = [_finding("fp1"), _finding("fp2")]
    assert guard.finding_map({"findings": findings}) == guard.finding_map({"findings": list(reversed(findings))})


def test_audit_output_is_deterministic():
    first = json.dumps([dataclasses.asdict(f) for f in _py(TWIN_SCOPES)], sort_keys=True)
    second = json.dumps([dataclasses.asdict(f) for f in _py(TWIN_SCOPES)], sort_keys=True)
    assert first == second
