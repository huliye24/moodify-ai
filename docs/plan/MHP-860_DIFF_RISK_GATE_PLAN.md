# MHP-860: Diff Risk Gate Plan

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6C: Worker Contracts / V4
**Depends on**: MHP-849 (AWJ Scope Policy), MHP-858 (Judge Schema)
**Protocol**: AWJ Stack + E-Chain 54

## Context

The Judge `G_arch` gate evaluates diff risk. A Worker AEP that touches core files, changes many lines, or modifies scoring semantics is high-risk and must be rejected or escalated to Architect review.

## Diff Risk Classification

| Risk Level | Criteria | Auto-Ver Acceptable? | Judge Action |
|-----------|----------|---------------------|-------------|
| **low** | ≤ 50 lines changed, only `allowed_files`, no scoring/mrs files | Yes | Accept if all other gates pass |
| **medium** | 51–150 lines OR touches 3+ files OR modifies test assertions | No | Flag `needs_architect_review` |
| **high** | > 150 lines OR touches `forbidden_files` OR changes MRS scoring OR changes quality gate thresholds | No | Reject |

## Forbidden Diff Patterns (Auto-Reject)

A diff that matches any of these patterns is auto-rejected regardless of line count:

| Pattern | Example | Why |
|---------|---------|-----|
| Modifies `_mrs_proxy()` formula | `def _mrs_proxy` body changed | Scoring semantics |
| Changes `_quality_gate()` threshold | `if after.peak_db > -0.1` → `if after.peak_db > -0.5` | Gate policy |
| Removes a `warnings.append()` | Deleted warning line | Evasion |
| Adds import to `forbidden_files` list | `from moodify_runtime.mrs_engine import` | Scope violation |
| Touches `forbidden_files` at all | Any line in `mrs_engine.py`, `operator_api.py`, `supervisor.py`, `scheduler.py` | Policy violation |

## Safe Diff Patterns (Low Risk)

| Pattern | Example | Why Safe |
|---------|---------|----------|
| Adds fields to existing dataclasses | New `Optional[float]` field in `ScanResult` | Backwards compatible |
| Adds new functions | New `_compute_loudness()` helper | No existing callers broken |
| Adds test cases | New `test_scan_loudness_field()` | Only additions |
| Extends report fields | New key in `_save_report()` JSON | Existing keys unchanged |
| Adds CLI flags | New `--loudness` flag with default | Opt-in only |
| Adds schema fields | New optional property in JSON schema | Backwards compatible |

## Risk Evaluation Formula

```python
def evaluate_diff_risk(diff: str, modified_files: list[str], 
                       allowed_files: set[str], forbidden_files: set[str]) -> tuple[str, str]:
    """
    Returns (risk_level, reason).
    """
    lines_changed = _count_changed_lines(diff)
    
    # Auto-reject: forbidden files
    violations = [f for f in modified_files if f in forbidden_files]
    if violations:
        return ("high", f"Forbidden files modified: {', '.join(violations)}")
    
    # Auto-reject: forbidden patterns
    for pattern in FORBIDDEN_DIFF_PATTERNS:
        if pattern in diff:
            return ("high", f"Forbidden diff pattern: {pattern}")
    
    # Scope check
    out_of_scope = [f for f in modified_files if f not in allowed_files]
    if out_of_scope:
        return ("high", f"Files outside allowed scope: {', '.join(out_of_scope)}")
    
    # Line-count based
    if lines_changed > 150:
        return ("high", f"Large diff: {lines_changed} lines changed")
    if lines_changed > 50:
        return ("medium", f"Moderate diff: {lines_changed} lines changed")
    
    # Check for test file changes
    test_files = [f for f in modified_files if "test_" in f or "tests/" in f]
    core_files = [f for f in modified_files if f not in test_files]
    if len(core_files) >= 3:
        return ("medium", f"Multiple core files changed: {len(core_files)}")
    
    return ("low", f"Low risk: {lines_changed} lines in {len(modified_files)} files")
```

## Integration

The diff risk gate is part of Judge `G_arch`. A Judge script:

1. Gets `git diff` for the Worker's branch vs main.
2. Runs `evaluate_diff_risk()`.
3. Sets `gates.arch.passed = (risk == "low")`.
4. Sets `review_required = (risk != "low")`.

## Acceptance Criteria

- [x] 3 risk levels defined with line-count thresholds.
- [x] 5 forbidden diff patterns listed (auto-reject).
- [x] 6 safe diff patterns listed (low risk).
- [x] Risk evaluation formula specified in executable pseudo-code.
- [x] Forbidden patterns include scoring formula changes and gate threshold changes.
