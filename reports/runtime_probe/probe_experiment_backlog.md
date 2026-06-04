# Probe Experiment Backlog — MHP-094

**Date**: 2026-06-04  
**NEM**: NEM-MOODIFY-RUNTIME-PROBE-003  
**Phase**: Probe Plan-6A (Problem Boundary) → Plan-6B (Technical Probe)

## Probe Experiments (Plan-6B: MHP-095→100)

These are the minimal experiments needed to validate or refute the assumptions from the state map, taxonomy, and bottleneck analysis.

### P1: Process Supervisor Probe (MHP-095)
- **Question**: Can we reliably detect and restart a crashed subprocess?
- **Method**: Write a minimal supervisor that wraps subprocess.run() with timeout and retry.
- **Success**: Supervisor catches exit code != 0, restarts task, logs crash.

### P2: Run Heartbeat Experiment (MHP-096)
- **Question**: What's the simplest viable heartbeat mechanism?
- **Method**: File-based heartbeat (touch heartbeat.json every N seconds). External watcher detects staleness.
- **Success**: Heartbeat file age can distinguish "running" from "dead" within 30s.

### P3: Resumable Queue Checkpoint (MHP-097)
- **Question**: Can we resume a run after process death without re-running completed tasks?
- **Method**: Add `claimed` and `completed_at` fields to queue.jsonl. On restart, skip tasks with `completed_at`.
- **Success**: Restarted run skips already-done tasks, picks up remaining.

### P4: Structured Event Schema Spike (MHP-098)
- **Question**: What's the minimal viable event schema for runtime telemetry?
- **Method**: Define 5 event types (task_started, task_completed, task_failed, heartbeat, run_summary). Write events to runtime_events.jsonl.
- **Success**: A simple `jq` query can answer "how many tasks failed in the last hour?"

### P5: Failure Replay Probe (MHP-099)
- **Question**: Can we systematically test recovery paths?
- **Method**: Inject synthetic failures (exit code 1, timeout, OOM kill) into a test run. Verify supervisor handles each.
- **Success**: All injected failures are caught, classified, and either retried or reported.

### P6: Runtime Probe Report (MHP-100)
- **Synthesis**: Combine all 5 probe experiment results into a single decision document.
- **Gate**: Does the evidence support entering Build NEM?

## Next Step

Start MHP-095: Process Supervisor Probe.
