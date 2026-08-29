# Lease Contract

## Fields

- lease_id:
- job_id:
- attempt_id:
- owner:
- acquired_at:
- expires_at:
- heartbeat_at:
- fencing_token / lease_version:
- released_at:
- release_reason:

## Acquire

Preconditions:

- job is claimable
- no valid lease
- retry schedule allows execution

Atomic writes:

- create attempt
- create/update lease
- set RUNNING
- append event

## Heartbeat

Allowed only if:

- same owner
- same lease
- fencing token current
- lease not expired
- job still RUNNING/allowed

## Expiry

- detector:
- polling cadence:
- grace:
- transition after expiry:
- cleanup:
- event:

## Stale Worker Protection

Describe exactly how old worker output/complete is rejected.
