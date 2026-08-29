# Local Scratch Contract

## Root

Recommended:

`scratch/{job_id}/{attempt_id}/`

## Allowed Content

- downloaded source
- temporary stems
- intermediate files
- render temp
- transient diagnostics

## Not Authoritative

Local scratch is not durable asset storage.

## Required Controls

- path traversal prevention
- per-job directory isolation
- disk budget
- cleanup on success
- cleanup on handled failure
- startup recovery cleanup policy
- preserve-on-debug must be explicit
- no secrets in filenames

## Lease

Before durable upload, worker revalidates active attempt/fencing.
