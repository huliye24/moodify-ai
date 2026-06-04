# Runtime Probe Report — MHP-100

**Date**: 2026-06-04  
**E-Chain**: ECHAIN-MOODIFY-RUNTIME-001  
**NEM**: NEM-MOODIFY-RUNTIME-PROBE-003  
**Phase**: Probe Plan-6B Synthesis

## Probe Experiment Summary

| MHP | Experiment | Outcome | Evidence |
|-----|-----------|---------|----------|
| 095 | Process Supervisor | ✅ Proven — timeout + retry + crash detection work | 7 tests, 142 total pass |
| 096 | Heartbeat | ✅ Proven — file-based heartbeat distinguishes alive/dead | `runtime_state.py:Heartbeat` |
| 097 | Resumable Queue | ✅ Proven — 6-state machine with abandoned detection | `runtime_state.py:transition_task` |
| 098 | Structured Events | ✅ Proven — 5 event types, JSONL writer | `runtime_events.py:EventWriter` |
| 099 | Failure Replay | ✅ Proven — all 4 injection modes handled | `test_runtime_supervisor.py` |

## Key Findings

1. **Supervisor is feasible**: Minimal wrapper around subprocess with timeout catches all common failure modes. Production supervisor needs SIGKILL escalation and resource monitoring, but the pattern is proven.

2. **Heartbeat is simple**: File-based heartbeat with mtime check is trivially implementable. Production needs a TCP endpoint for remote monitoring, but file-based is sufficient for local runner health.

3. **Resumable queue needs 2 new states**: Adding `claimed` and `abandoned` to the 4 existing states (pending/running/done/failed) enables crash recovery. `find_abandoned_tasks()` can detect stuck tasks.

4. **Structured events are the biggest leverage**: 5 event types (task_started, task_completed, task_failed, heartbeat, run_summary) enable queryable telemetry with minimal code. A `jq` query can replace grep-based log analysis.

5. **No showstoppers found**: All probe experiments validated the feasibility of production-grade unattended runtime. No DROP conditions detected.

## Recommendation

**Gate 1: ADOPT** — Proceed to Build NEM (NEM-MOODIFY-RUNTIME-BUILD-004).

The probe evidence supports the following Build NEM scope:
- Build full supervisor with SIGKILL escalation
- Implement checkpoint-based resumable queue
- Deploy structured event writer in runner.py
- Add heartbeat endpoint to operator API
- 6h unattended run with new infrastructure

## Risks to Monitor in Build NEM

1. SIGKILL recovery requires fork() + signal handling — more complex than subprocess wrapper
2. Checkpoint frequency vs. throughput trade-off
3. JSONL event volume in long runs (est. 10K events/6h run)
