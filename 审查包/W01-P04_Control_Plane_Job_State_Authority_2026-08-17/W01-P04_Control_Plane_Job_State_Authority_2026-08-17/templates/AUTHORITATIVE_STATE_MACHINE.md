# Authoritative State Machine — Decision Template

## Existing Systems Considered

| Candidate | Location | Current Use | Evidence | Decision |
|---|---|---|---|---|

## Selected Authority

- module/service:
- DB authority:
- API authority:
- queue authority:
- migration approach:
- why selected:
- rejected alternatives:

## Lifecycle States

Suggested minimal candidate:

- CREATED
- QUEUED
- RUNNING
- RETRY_WAIT
- VERIFYING
- READY
- FAILED
- CANCELED

Final list:

| State | Meaning | Terminal | Worker-owned | User-visible |
|---|---|---:|---:|---:|

## State vs Stage

- lifecycle state:
- pipeline stage field:
- stage registry owner:
- stage changes emit event?:
- stage changes require state transition?:

## Terminal Policy

- READY:
- FAILED:
- CANCELED:
- replay/reset authority:
