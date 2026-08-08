"""Output verification: source hashes, render validity."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .engine_native import _hash_file


@dataclass
class VerifyReport:
    project_id: str = ""
    passed: bool = False
    checks: dict[str, bool] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)


def verify_run(run_dir: Path) -> VerifyReport:
    """Verify a rendered run directory."""
    report = VerifyReport()
    ev_path = run_dir / "render_evidence.json"
    if not ev_path.exists():
        report.issues.append("render_evidence.json missing")
        return report

    ev = json.loads(ev_path.read_text(encoding="utf-8"))
    report.project_id = ev.get("project_id", "")
    report.checks["evidence_exists"] = True

    out_path = ev.get("output_path", "")
    if out_path and Path(out_path).exists():
        report.checks["output_exists"] = True
        actual_hash = _hash_file(Path(out_path))
        expected_hash = ev.get("output_hash", "")
        report.checks["output_hash_match"] = actual_hash == expected_hash
        if not report.checks["output_hash_match"]:
            report.issues.append("Output hash mismatch")
    else:
        report.checks["output_exists"] = False
        report.issues.append("Output file missing")

    report.passed = all(report.checks.values())
    return report
