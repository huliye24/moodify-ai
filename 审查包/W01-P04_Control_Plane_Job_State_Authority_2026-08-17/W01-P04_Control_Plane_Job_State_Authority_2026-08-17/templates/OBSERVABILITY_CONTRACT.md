# Observability Contract

## Job View

Must expose:

- job_id
- track_id
- current_state
- stage
- current_attempt
- retry_count
- lease_owner
- lease_expires_at
- last_failure
- ready_object_id
- updated_at

## Queue Summary

- CREATED count
- QUEUED count
- RUNNING count
- RETRY_WAIT count
- VERIFYING count
- READY count
- FAILED count
- stale lease count

## Worker View

- worker_id
- version
- last heartbeat
- current job
- capacity
- healthy

## Control Health

- build/commit
- DB connectivity
- object-store connectivity
- queue authority health
- migration/schema version

## Logging Context

Every operational log should include when applicable:

- track_id
- job_id
- attempt_id
- correlation_id
- stage
- worker_id
