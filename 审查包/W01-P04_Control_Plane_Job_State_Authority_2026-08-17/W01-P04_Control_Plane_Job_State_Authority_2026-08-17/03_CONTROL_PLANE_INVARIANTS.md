# Control Plane Invariants

## CP-INV-01 — One State Authority
A job has one authoritative current lifecycle state.

## CP-INV-02 — Transactional Transition
State transition and required attempt/lease/event writes share a consistency boundary.

## CP-INV-03 — No Silent Transition
Every lifecycle state transition emits an audit event.

## CP-INV-04 — Event Is Audit
Event history is not a second current-state authority.

## CP-INV-05 — One Valid Lease
A job has at most one valid lease at a time.

## CP-INV-06 — Expiring Ownership
Worker ownership always expires unless renewed.

## CP-INV-07 — Heartbeat Is Not Business Progress
Heartbeat maintains ownership only.

## CP-INV-08 — Terminal Protection
READY/FAILED/CANCELED cannot be casually reverted by a worker.

## CP-INV-09 — Bounded Retry
Retries have explicit maximum attempts and conditions.

## CP-INV-10 — Idempotent Commands
Repeated identical commands cannot create divergent logical results.

## CP-INV-11 — Deterministic Recovery
Restart recovery comes from persisted facts.

## CP-INV-12 — Structured Failure
Failures have stable class/code/retryability.

## CP-INV-13 — READY Requires Artifact
READY requires a registered ready artifact.

## CP-INV-14 — READY Requires Required Verification
If canonical policy requires verification, READY requires its evidence.

## CP-INV-15 — Worker Uses Commands
Workers do not directly invent lifecycle transitions.

## CP-INV-16 — Stage Is Descriptive
Pipeline stage never becomes an implicit second state machine.

## CP-INV-17 — Stale Attempt Cannot Commit
An expired/replaced attempt cannot commit final authoritative result.

## CP-INV-18 — No In-memory-only Queue Truth
Loss of control process memory must not lose authoritative work state.
