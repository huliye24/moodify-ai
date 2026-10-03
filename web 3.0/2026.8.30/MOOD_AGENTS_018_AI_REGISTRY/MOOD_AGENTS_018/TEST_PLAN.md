# TEST PLAN

## Registry
- create draft agent
- activate only with operator
- unique slug / ID
- retire behavior

## Status
- heartbeat update
- stale heartbeat → offline/degraded according to policy
- no heartbeat → not falsely online

## Security
- public API strips secret fields
- non-operator update rejected
- agent cannot self-approve contribution
- funds actions absent / blocked

## Proof
- valid proof
- oversized payload rejected
- duplicate proof behavior
- secret-like fields not public

## Network
- total count
- active count
- unavailable behavior
- last activity
- no token dependency
