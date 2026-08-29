# Pipeline Failure Mapping

| Pipeline Condition | P04 Failure Class | Retryable Default | Evidence |
|---|---|---:|---|
| unreadable/corrupt audio | INPUT_INVALID | false | validation report |
| unsupported format | INPUT_INVALID | false | validation report |
| OSS timeout | STORAGE_TRANSIENT | true | storage diagnostic |
| OSS permanent access failure | STORAGE_PERMANENT | false/decision | safe diagnostic |
| external rate limit | EXTERNAL_API_RATE_LIMIT | true | provider response metadata |
| external timeout/5xx | EXTERNAL_API_TRANSIENT | true | provider metadata |
| external permanent rejection | EXTERNAL_API_PERMANENT | false | provider metadata |
| OOM/resource guard | WORKER_RESOURCE_EXHAUSTED | policy | resource summary |
| stage timeout | PROCESS_TIMEOUT | policy | stage timing |
| tool crash | PROCESS_CRASH | policy | safe crash ref |
| verification reject | VERIFICATION_FAILED | policy | verify evidence |
| invariant violation | INTERNAL_BUG | policy | safe details |
| unknown exception | UNKNOWN_FAILURE | policy | safe details |

## Rule

Do not create new top-level failure classes in pipeline code without P04 authority change.
