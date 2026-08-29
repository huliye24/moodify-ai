# Control API / Command Contract

> Reuse existing API surface when possible. This is a logical command contract, not a requirement to expose every command publicly.

## Create Job
Input:
- track_id
- job_type
- pipeline/profile request
- idempotency key

Output:
- job_id
- current_state

## Enqueue
Authority:
- control plane only

## Claim
Input:
- worker_id
- capabilities
Output:
- job
- attempt_id
- lease_id
- fencing token
- input refs
- versions

## Heartbeat
Input:
- job_id
- attempt_id
- lease/fencing identity

## Report Stage
Input:
- stage
- safe progress metadata

## Complete
Input:
- attempt identity
- ready/output object refs
- verification refs

## Fail
Input:
- failure class/code
- retryable hint/evidence

## Cancel
Authority:
- authorized control/user path

## Query
- get job
- queue summary
- worker health
