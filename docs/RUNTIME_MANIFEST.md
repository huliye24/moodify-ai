# Runtime Manifest — MHP-137

**Version**: v0.2.0 | **E-Chain**: ECHAIN-MOODIFY-RUNTIME-001 | **Gate**: ADOPT ✅

## Capabilities

| Capability | Status | Module |
|-----------|--------|--------|
| Supervised execution | ✅ | supervisor.py |
| Heartbeat + liveness | ✅ | runtime_state.py:Heartbeat |
| Resumable state machine | ✅ | runtime_state.py:6-state |
| Structured events | ✅ | runtime_events.py:5 types |
| Failure classification | ✅ | runtime_failures.py:4 severities |
| CLI runtime commands | ✅ | cli.py:3 commands |
| API runtime endpoints | ✅ | operator_api.py:2 routes |
| Operator runbook | ✅ | RUNTIME_OPERATOR_RUNBOOK.md |

## SLOs

| SLO | Target |
|-----|--------|
| Uptime | ≥99% |
| Task success rate | ≥95% |
| Task P99 latency | ≤120s |
| Recovery time | ≤30s |

## Dependencies

- moodify_runtime (runner.py, operator_console.py, operator_api.py)
- moodify-core-package (DSP presets, MRS Open v0.3.1)
- Python 3.12+, numpy, scipy, fastapi, uvicorn
