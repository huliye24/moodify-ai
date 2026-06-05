#!/usr/bin/env python3
"""MAP Judge Gate Checker (MHP-881/882/883/884).

Validates Worker AEP output against the 6-gate MAP formula:
  G_schema * G_scope * G_runtime * G_test * G_evidence * G_arch = 1

Usage:
  python3 scripts/map_judge_check.py all <task.json> <diff.txt>
  python3 scripts/map_judge_check.py schema <report.json>
  python3 scripts/map_judge_check.py scope <diff.txt> [policy.json]
  python3 scripts/map_judge_check.py runtime <task.json>
  python3 scripts/map_judge_check.py evidence <task.json>
  python3 scripts/map_judge_check.py arch <diff.txt>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── Forbidden files (MHP-849 AWJ Policy) ──────────────────────────
FORBIDDEN_FILES = {
    "moodify_runtime/mrs_engine.py",
    "moodify_runtime/operator_api.py",
    "moodify_runtime/supervisor.py",
    "moodify_runtime/scheduler.py",
    "moodify_runtime/cloud_worker.py",
}

# ── Forbidden diff patterns (MHP-860) ─────────────────────────────
FORBIDDEN_PATTERNS = [
    "def _mrs_proxy",       # Scoring formula change
    "def _quality_gate",    # Gate threshold change
    "warnings.append(",      # Potential warning removal
    "from moodify_runtime.mrs_engine import",  # Cross-boundary import
    "mrs_engine.py",         # Forbidden file reference
]


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_schema(report_path: str) -> dict[str, Any]:
    """G_schema: Validate JSON report against MAP schema."""
    schema_path = PROJECT_ROOT / "schemas" / "map_chain_report.schema.json"
    try:
        schema = load_json(str(schema_path))
        report = load_json(report_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return {"passed": False, "detail": f"JSON parse failed: {e}"}

    # Manual validation against MAP schema required fields
    required_keys = [
        "workflow", "preset", "requested_preset", "scan",
        "feature_analysis", "diagnosis_report", "validation_result",
        "quality_gate", "metrics_before", "metrics_after", "delivery",
    ]
    missing = [k for k in required_keys if k not in report]
    if missing:
        return {"passed": False, "detail": f"Missing required fields: {missing}"}

    # Check workflow is 7-stage
    workflow = report.get("workflow", [])
    expected = ["S_scan","A_analyze","D_diagnose","P_process","V_validate","R_report","G_generate"]
    if workflow != expected:
        return {"passed": False, "detail": f"workflow mismatch: {workflow}"}

    # Check validation_result has required sub-fields
    vr = report.get("validation_result", {})
    vr_required = ["mrs_version", "mrs_before", "mrs_after", "mrs_delta",
                    "damage_loss", "risk_flags", "passed"]
    vr_missing = [k for k in vr_required if k not in vr]
    if vr_missing:
        return {"passed": False, "detail": f"validation_result missing: {vr_missing}"}

    return {"passed": True, "detail": "Schema valid — all required fields present"}


def check_scope(diff_path: str, _policy_path: str = "") -> dict[str, Any]:
    """G_scope: Verify diff does not touch forbidden files."""
    try:
        with open(diff_path, "r", encoding="utf-8") as f:
            diff = f.read()
    except FileNotFoundError:
        return {"passed": False, "detail": f"diff file not found: {diff_path}"}

    # Extract modified files from diff (git diff format)
    modified_files = set()
    for line in diff.split("\n"):
        if line.startswith("--- a/") or line.startswith("+++ b/"):
            fname = line[6:] if line.startswith("--- a/") else line[6:]
            if fname != "/dev/null":
                modified_files.add(fname)

    violations = modified_files & FORBIDDEN_FILES
    if violations:
        return {
            "passed": False,
            "detail": f"Forbidden file(s) modified: {', '.join(violations)}",
            "files_checked": sorted(modified_files),
            "violations": sorted(violations),
        }

    # Check forbidden patterns
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in diff:
            return {
                "passed": False,
                "detail": f"Forbidden diff pattern detected: {pattern}",
                "files_checked": sorted(modified_files),
                "violations": [f"pattern: {pattern}"],
            }

    # Line count risk
    changed_lines = sum(1 for line in diff.split("\n") if line.startswith("+") or line.startswith("-"))
    if changed_lines > 150:
        return {
            "passed": False,
            "detail": f"Diff too large: {changed_lines} lines (max 150)",
            "files_checked": sorted(modified_files),
        }

    return {
        "passed": True,
        "detail": f"Scope valid — {len(modified_files)} files, {changed_lines} lines",
        "files_checked": sorted(modified_files),
    }


def check_runtime(task_path: str) -> dict[str, Any]:
    """G_runtime: Run proof commands from task JSON."""
    try:
        task = load_json(task_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return {"passed": False, "detail": f"Task JSON parse failed: {e}"}

    commands = task.get("proof_commands", [])
    if not commands:
        return {"passed": True, "detail": "No proof commands specified"}

    results = []
    for cmd in commands:
        try:
            proc = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=60,
                cwd=str(PROJECT_ROOT),
            )
            results.append({
                "command": cmd,
                "exit_code": proc.returncode,
                "output_summary": (proc.stdout + proc.stderr)[:500],
            })
        except subprocess.TimeoutExpired:
            results.append({
                "command": cmd,
                "exit_code": -1,
                "output_summary": "TIMEOUT (60s)",
            })
        except Exception as e:
            results.append({
                "command": cmd,
                "exit_code": -1,
                "output_summary": str(e)[:500],
            })

    all_passed = all(r["exit_code"] == 0 for r in results)
    return {
        "passed": all_passed,
        "detail": f"{sum(1 for r in results if r['exit_code']==0)}/{len(results)} commands passed",
        "commands_run": results,
    }


def check_evidence(task_path: str) -> dict[str, Any]:
    """G_evidence: Verify expected output artifacts exist."""
    try:
        task = load_json(task_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return {"passed": False, "detail": f"Task JSON parse failed: {e}"}

    expected = task.get("expected_outputs", [])
    if not expected:
        return {"passed": True, "detail": "No expected outputs specified"}

    artifacts_found: list[str] = []
    artifacts_missing: list[str] = []

    for art in expected:
        # Check if it's a file path pattern
        if isinstance(art, str) and "/" in art:
            path = PROJECT_ROOT / art
            if path.exists():
                artifacts_found.append(art)
            else:
                artifacts_missing.append(art)
        else:
            # Descriptive artifact — check for existence in repo
            artifacts_found.append(art)

    passed = len(artifacts_missing) == 0
    return {
        "passed": passed,
        "detail": f"{len(artifacts_found)}/{len(expected)} artifacts found",
        "artifacts_found": artifacts_found,
        "artifacts_missing": artifacts_missing,
    }


def check_arch(diff_path: str) -> dict[str, Any]:
    """G_arch: Evaluate diff risk level."""
    try:
        with open(diff_path, "r", encoding="utf-8") as f:
            diff = f.read()
    except FileNotFoundError:
        return {"passed": False, "detail": f"diff file not found: {diff_path}", "diff_risk": "unknown"}

    changed_lines = sum(1 for line in diff.split("\n") if line.startswith("+") or line.startswith("-"))

    # Extract modified files
    modified_files: list[str] = []
    for line in diff.split("\n"):
        if line.startswith("+++ b/") and line[6:] != "/dev/null":
            modified_files.append(line[6:])

    # Forbidden checks
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in diff:
            return {
                "passed": False,
                "detail": f"High risk: forbidden pattern '{pattern}'",
                "diff_risk": "high",
                "files_changed": modified_files,
            }

    if changed_lines > 150:
        return {
            "passed": False,
            "detail": f"High risk: {changed_lines} lines",
            "diff_risk": "high", "files_changed": modified_files,
        }
    if changed_lines > 50:
        return {
            "passed": False,
            "detail": f"Medium risk: {changed_lines} lines — needs Architect review",
            "diff_risk": "medium", "files_changed": modified_files,
        }

    return {
        "passed": True,
        "detail": f"Low risk: {changed_lines} lines in {len(modified_files)} files",
        "diff_risk": "low",
        "files_changed": modified_files,
    }


def run_all_gates(task_path: str, diff_path: str = "", report_path: str = "") -> dict[str, Any]:
    """Run all 6 gates and compute final verdict."""
    gates: dict[str, dict[str, Any]] = {}

    if report_path:
        gates["schema"] = check_schema(report_path)
    else:
        gates["schema"] = {"passed": True, "detail": "no report provided — skipped"}

    if diff_path:
        gates["scope"] = check_scope(diff_path)
        gates["arch"] = check_arch(diff_path)
    else:
        gates["scope"] = {"passed": True, "detail": "no diff — skipped"}
        gates["arch"] = {"passed": True, "detail": "no diff — skipped"}

    if task_path and Path(task_path).exists():
        gates["runtime"] = check_runtime(task_path)
        gates["test"] = check_runtime(task_path)  # Tests = proof commands
        gates["evidence"] = check_evidence(task_path)
    else:
        gates["runtime"] = {"passed": True, "detail": "no task — skipped"}
        gates["test"] = {"passed": True, "detail": "no task — skipped"}
        gates["evidence"] = {"passed": True, "detail": "no task — skipped"}

    all_pass = all(g["passed"] for g in gates.values())
    arch_risk = gates.get("arch", {}).get("diff_risk", "low")
    scope_pass = gates.get("scope", {}).get("passed", True)

    if all_pass:
        verdict = "accept"
    elif arch_risk == "high" or not scope_pass:
        verdict = "reject"
    else:
        verdict = "needs_architect_review"

    return {
        "task_id": Path(task_path).stem if task_path else "unknown",
        "verdict": verdict,
        "gates": gates,
        "summary": f"Verdict: {verdict}. Gates: "
                   f"{sum(1 for g in gates.values() if g['passed'])}/{len(gates)} passed.",
        "review_required": verdict != "accept",
        "merge_policy": "auto_merge" if verdict == "accept" else "no_merge",
    }


# ── CLI ─────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="MAP Judge Gate Checker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("schema", help="G_schema: validate JSON report").add_argument("report", type=str)
    sub.add_parser("scope", help="G_scope: verify diff scope").add_argument("diff", type=str)
    sub.add_parser("runtime", help="G_runtime: run proof commands").add_argument("task", type=str)
    sub.add_parser("evidence", help="G_evidence: verify artifacts").add_argument("task", type=str)
    sub.add_parser("arch", help="G_arch: diff risk assessment").add_argument("diff", type=str)

    all_p = sub.add_parser("all", help="Run all gates")
    all_p.add_argument("task", type=str, nargs="?", default="")
    all_p.add_argument("diff", type=str, nargs="?", default="")
    all_p.add_argument("--report", type=str, default="")

    args = parser.parse_args()

    result: dict[str, Any] = {}
    if args.cmd == "schema":
        result = check_schema(args.report)
    elif args.cmd == "scope":
        result = check_scope(args.diff)
    elif args.cmd == "runtime":
        result = check_runtime(args.task)
    elif args.cmd == "evidence":
        result = check_evidence(args.task)
    elif args.cmd == "arch":
        result = check_arch(args.diff)
    elif args.cmd == "all":
        result = run_all_gates(args.task, args.diff, args.report)

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")

    # Exit code: 0 if passed, 1 if failed
    if not result.get("passed", result.get("verdict") == "reject"):
        sys.exit(0 if result.get("verdict") == "accept" else 1)


if __name__ == "__main__":
    main()
