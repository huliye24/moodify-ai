# Recovery Contract

## Worker crash
- Detection:
- Lease expiry:
- State after recovery:
- Attempt outcome:
- Cleanup:
- Evidence:

## Control/API restart
- Persisted source of truth:
- Recovery startup action:
- In-memory structures rebuilt from:
- Expected downtime behavior:

## Network partition
- Stale owner rejection:
- Fencing:

## DB outage
- Worker behavior:
- Completion behavior:
- Retry behavior:

## Object uploaded / DB commit failed
- Orphan detection:
- READY guard:
- Reconciliation:

## DB reference / object missing
- Delivery guard:
- Reconciliation:

## Manual Recovery Authority
- Who may force replay/reset:
- How it is audited:
