# Failure Replay Probe — MHP-099

**Date**: 2026-06-04

## Method

Injected 4 synthetic failure modes into test_supervisor.py and verified supervisor response.

## Results

| Failure Mode | Injection | Supervisor Response | Handled? |
|-------------|-----------|---------------------|----------|
| Exit code 1 | `python3 -c "exit(1)"` | Detects crash, retries, marks as failed after max_retries | ✅ |
| Timeout | `sleep 2` with timeout=0.5s | Detects timeout, retries, marks as timed_out | ✅ |
| Command not found | `/nonexistent/cmd` | Detects crash, exit_code != 0 | ✅ |
| Flaky (fails once then succeeds) | Temp script with state file | Retries on first failure, succeeds on retry | ✅ |

## Evidence

All 7 `test_runtime_supervisor.py` tests pass (142 total, 0 failures).

## Gap: SIGKILL Recovery Not Tested

Current probe tests subprocess exit codes but doesn't simulate OS-level kill (SIGKILL).
This requires a separate process + signal, which is Build NEM scope (MHP-120: Synthetic Failure Injection).

## Conclusion

Supervisor pattern works. Retry + timeout detection + crash classification are proven.
Build NEM can build on this foundation.
