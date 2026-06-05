# MHP-858: Judge Result Schema Shape — Completion Report

**Generated**: 2026-06-05
**Status**: done
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6C

## Key Deliverable

6-gate Judge schema satisfying the E-chain formula:

```text
G_schema * G_scope * G_runtime * G_test * G_evidence * G_arch = 1
```

## Gate Definitions

| Gate | Checks | Fail Condition |
|------|--------|---------------|
| `schema` | JSON parses, required fields present | Missing task_id or any required field |
| `scope` | Modified files ⊆ allowed_files, ∩ forbidden_files = ∅ | Worker touched forbidden file |
| `runtime` | All proof_commands exit 0 | Any command returned non-zero |
| `test` | Specified tests pass | Test failure |
| `evidence` | All expected_outputs have artifacts | Missing deliverable |
| `arch` | Diff risk is low OR Architect approved | High-risk diff without review |

## Verdict Logic

```text
all 6 gates pass → accept
arch risk=high OR scope fails → reject
otherwise → needs_architect_review
```

## Integration

Schema extends `aep_worker_protocol.py` with 4 additional gates (scope, test, evidence, arch) beyond existing task_id/loop/schema validation.
