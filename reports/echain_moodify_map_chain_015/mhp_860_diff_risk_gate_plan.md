# MHP-860: Diff Risk Gate Plan — Completion Report

**Generated**: 2026-06-05
**Status**: done
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6C

## Key Deliverable

3-level diff risk classification with auto-reject patterns for the Judge `G_arch` gate.

## Risk Levels

| Level | Lines | Files | Auto-Accept | Judge Action |
|-------|-------|-------|-------------|-------------|
| low | ≤ 50 | allowed only | Yes | Accept |
| medium | 51–150 | ≤ 3 files | No | Architect review |
| high | > 150 | any | No | Reject |

## Auto-Reject Patterns (5)

1. Modifies `_mrs_proxy()` formula body
2. Changes `_quality_gate()` threshold values
3. Removes a `warnings.append()` call
4. Adds import from forbidden_files list
5. Touches any line in `mrs_engine.py`, `operator_api.py`, `supervisor.py`, `scheduler.py`

## Safe Patterns (6)

1. Adds Optional fields to dataclasses
2. Adds new helper functions
3. Adds test cases
4. Extends report JSON with new keys
5. Adds CLI flags with defaults
6. Adds optional schema properties

## Risk Formula

```python
def evaluate_diff_risk(diff, modified_files, allowed_files, forbidden_files):
    # 1. Check forbidden file violations → high
    # 2. Check forbidden diff patterns → high
    # 3. Check scope boundary → high
    # 4. Check line count thresholds → high/medium
    # 5. Check file count → medium
    # 6. Default → low
```

## Integration

Part of Judge `G_arch` gate. Risk level determines `gates.arch.passed` and `review_required`.
