# MHP-859: Command Gate Smoke Plan — Completion Report

**Generated**: 2026-06-05
**Status**: done
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6C

## Key Deliverable

6-level command gate matrix for MAP Worker AEP verification.

## Command Gate Levels

| Level | Commands | Budget | Required For |
|-------|----------|--------|-------------|
| L1: Unit | `pytest test_v01_pipeline.py` | < 10s | Every Worker AEP |
| L2: API | `pytest test_api_v01.py` | < 10s | Every Worker AEP |
| L3: CLI Single | `v01-process --preset clean_master` | < 30s | Implementation MHPs |
| L4: CLI All | `v01-process × 3 presets` | < 60s | Build Gate MHPs |
| L5: Schema | `jsonschema.validate(report)` | < 5s | Schema/contract MHPs |
| L6: Artifacts | `test -f × 5 artifacts` | < 1s | Delivery MHPs |

## Judge Recipe

```python
def command_gate(task):
    results = [run_command(cmd) for cmd in task["proof_commands"]]
    all_passed = all(r.exit_code == 0 for r in results)
    return GateResult(passed=all_passed, commands_run=results)
```

## Applicability

18 Build MHPs mapped to required gate levels. Data Model block uses L1-L2. Validation block adds L3-L5. Delivery block uses all L1-L6.
