# Runtime Failure Manual — MHP-127

**E-Chain**: ECHAIN-MOODIFY-RUNTIME-001

## Failure Severity Levels

| Severity | Action | Retry? | Alert? |
|----------|--------|--------|--------|
| CRITICAL | Stop run, alert operator | No | Yes |
| HIGH | Retry with backoff | Yes (max 2) | If retries exhausted |
| MEDIUM | Log and skip task | Depends on type | No |
| LOW | Log and continue | Yes | No |

## Classification Map

| Error Pattern | Severity | Retryable | Notes |
|--------------|----------|-----------|-------|
| "disk full" / "no space" | CRITICAL | No | Free disk or abort |
| "killed" / "oom" / "memory" | CRITICAL | No | Reduce concurrency |
| "timeout" | HIGH | Yes | Increase timeout or split task |
| non-zero exit (unknown) | HIGH | Yes | May be transient |
| "not found" | MEDIUM | No | Fix path, don't retry |
| "argument" / "usage:" | MEDIUM | No | Fix template, don't retry |
| "connection" / "network" | LOW | Yes | Transient |

## Retry Policy

- Max retries: 2 (configurable via RuntimeConfig.max_retries_per_task)
- Backoff: exponential (base * 2^attempt), capped at 60s
- After max retries exhausted: mark task as failed, continue with next task
