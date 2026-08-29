# Retry Policy

| Failure Class | Retryable | Max Attempts | Backoff | Cleanup Needed | Terminal Mapping | Notes |
|---|---:|---:|---|---:|---|---|
| INPUT_INVALID | false | 1 | none | false | FAILED | |
| STORAGE_TRANSIENT | true | | | | FAILED | |
| STORAGE_PERMANENT | false | 1 | none | | FAILED | |
| DB_TRANSIENT | true | | | | FAILED | |
| EXTERNAL_API_RATE_LIMIT | true | | | | FAILED | |
| EXTERNAL_API_TRANSIENT | true | | | | FAILED | |
| EXTERNAL_API_PERMANENT | false | 1 | none | | FAILED | |
| WORKER_RESOURCE_EXHAUSTED | | | | | FAILED | |
| PROCESS_TIMEOUT | | | | | FAILED | |
| PROCESS_CRASH | | | | | FAILED | |
| VERIFICATION_FAILED | | | | | FAILED | |
| INTERNAL_BUG | | | | | FAILED | |
| CANCELED_BY_USER | false | 1 | none | | CANCELED | |
| UNKNOWN_FAILURE | | | | | FAILED | |

## Retry Rules

- Every retry creates a new attempt.
- Historical failed attempts are preserved.
- Retry budget belongs to job policy, not worker preference.
- A worker cannot reset its own retry budget.
