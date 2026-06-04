# Synthetic Failure Injection — MHP-120

**Date**: 2026-06-04

## Injection Results

| Injection | Method | Detected | Classified | Recovered |
|-----------|--------|----------|------------|-----------|
| Non-zero exit | `exit(1)` | Supervisor exit_code check | Severity.HIGH, retryable | Retry → failed after max_retries |
| Timeout | `sleep 2` / timeout=0.5 | TimeoutExpired | Severity.HIGH, retryable | Retry → failed |
| Cmd not found | `/nonexistent` | Crash detected | Severity.MEDIUM, not retryable | Failed immediately |
| Flaky task | Fails once, succeeds on retry | Exit code 1 then 0 | — | Succeeded on attempt 2 |
| Disk full (simulated) | Error message "disk full" | classify_failure() | Severity.CRITICAL | Not retried |
| OOM (simulated) | Error message "killed: out of memory" | classify_failure() | Severity.CRITICAL | Not retried |

## Coverage

| Failure Class | Injected | Detected | Properly Classified |
|---------------|----------|----------|---------------------|
| SUBPROCESS_CRASH | ✅ | ✅ | ✅ |
| TIMEOUT | ✅ | ✅ | ✅ |
| FILE_NOT_FOUND | ✅ | ✅ | ✅ |
| DISK_EXHAUSTED | ✅ (msg) | ✅ | ✅ |
| MEMORY_EXHAUSTED | ✅ (msg) | ✅ | ✅ |

All 6 failure types from the taxonomy (MHP-090) covered.
