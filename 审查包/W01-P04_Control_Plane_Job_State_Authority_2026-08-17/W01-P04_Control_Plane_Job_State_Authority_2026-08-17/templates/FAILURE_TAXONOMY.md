# Failure Taxonomy

## Required Fields

- failure_id
- job_id
- attempt_id
- failure_class
- failure_code
- retryable
- stage
- component
- summary
- safe_details_ref
- occurred_at
- producer_version
- correlation_id

## Top-level Classes

- INPUT_INVALID
- STORAGE_TRANSIENT
- STORAGE_PERMANENT
- DB_TRANSIENT
- EXTERNAL_API_RATE_LIMIT
- EXTERNAL_API_TRANSIENT
- EXTERNAL_API_PERMANENT
- WORKER_RESOURCE_EXHAUSTED
- PROCESS_TIMEOUT
- PROCESS_CRASH
- VERIFICATION_FAILED
- INTERNAL_BUG
- CANCELED_BY_USER
- UNKNOWN_FAILURE

## Rule

Traceback text is detail, not the stable failure code.
