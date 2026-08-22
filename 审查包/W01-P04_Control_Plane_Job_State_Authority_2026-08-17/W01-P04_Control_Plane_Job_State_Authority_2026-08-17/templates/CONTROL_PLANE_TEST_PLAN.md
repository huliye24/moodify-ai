# Control Plane Test Plan

- [ ] TST-01 concurrent claim
- [ ] TST-02 lease expiry recovery
- [ ] TST-03 duplicate complete
- [ ] TST-04 retry budget
- [ ] TST-05 permanent failure
- [ ] TST-06 control restart
- [ ] TST-07 object/DB partial failure
- [ ] TST-08 READY guard
- [ ] TST-09 terminal protection
- [ ] TST-10 idempotent create
- [ ] TST-11 idempotency conflict
- [ ] TST-12 event completeness
- [ ] TST-13 stale fencing token
- [ ] TST-14 heartbeat after expiry
- [ ] TST-15 duplicate claim across processes
- [ ] TST-16 cancel vs claim race

## Required Evidence

For each test:

- setup
- command/action
- observed result
- DB rows/state
- event evidence
- logs
- pass/fail
