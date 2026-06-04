# Runtime Bottleneck and Risk Brief — MHP-093

**Date**: 2026-06-04

## Top 5 Bottlenecks

### 1. Sequential Processing (throughput bottleneck)
- **Current**: 1 task at a time, blocking subprocess.run()
- **Impact**: 90 tasks × 2s = 3min minimum. Adding parallel processing could reduce to <1min.
- **Fix**: multiprocessing.Pool or asyncio subprocess pool in Build NEM.

### 2. No Crash Recovery (reliability bottleneck)
- **Current**: Runner process killed → all state lost → full re-run required.
- **Impact**: 6h unattended run fails at hour 5 → 5 hours of work wasted.
- **Fix**: Checkpoint queue state after each task completion. On restart, skip done tasks.

### 3. Unstructured Logging (observability bottleneck)
- **Current**: LineLogger writes free-text. Can't query, aggregate, or alert.
- **Impact**: Operator can't answer "what's the failure rate in the last hour?" without grep.
- **Fix**: Structured JSONL events with schema (MHP-098).

### 4. No Timeout Enforcement (safety bottleneck)
- **Current**: subprocess.run() has no timeout. A hung task blocks the entire queue forever.
- **Impact**: One corrupted audio file can kill a 24h run.
- **Fix**: subprocess.run(timeout=N) + SIGKILL escalation in Build NEM.

### 5. No SLO Framework (operations bottleneck)
- **Current**: Zero SLOs. No uptime target, no error budget, no alerting thresholds.
- **Impact**: Can't measure production readiness. "It works" but no one knows how well.
- **Fix**: Define SLOs in MHP-101, implement measurement in Build NEM.

## Risk Matrix

| Risk | Likelihood | Severity | Mitigation Phase |
|------|-----------|----------|------------------|
| Runner crash mid-6h-run | Medium | High | Build NEM: checkpoint |
| Subprocess hang | Low | Critical | Build NEM: timeout |
| Disk exhaustion | Low | High | Build NEM: monitor |
| JSONL corruption from concurrent writes | Low | Medium | System NEM: advisory locks |
| Memory leak in long runs | Unknown | Medium | Probe NEM: 2h probe measures RSS |
| CLI arg regression | Medium | High | Build NEM: startup contract test |
