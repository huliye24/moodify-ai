# W01-P04 Acceptance Checklist

## Discovery
- [ ] existing authority scan complete
- [ ] duplicate/legacy systems classified
- [ ] selected authority documented

## State
- [ ] one lifecycle state authority
- [ ] state != stage
- [ ] lease != state
- [ ] event != current-state authority
- [ ] terminal states protected
- [ ] transition matrix complete

## Lease
- [ ] atomic claim
- [ ] one valid owner
- [ ] TTL
- [ ] heartbeat
- [ ] expiry
- [ ] fencing/stale worker protection

## Retry/recovery
- [ ] structured retry policy
- [ ] max attempts
- [ ] permanent vs transient distinction
- [ ] restart recovery
- [ ] partial DB/object failure handling

## Idempotency
- [ ] create idempotent
- [ ] transition idempotent
- [ ] completion idempotent
- [ ] conflict fingerprint behavior

## Evidence/observability
- [ ] append-only job events
- [ ] explicit attempts
- [ ] structured failure record
- [ ] job view
- [ ] queue summary
- [ ] worker health
- [ ] correlation IDs/log context

## Guards
- [ ] READY requires ready object
- [ ] READY verification guard applied where required
- [ ] stale attempt cannot commit
- [ ] worker cannot directly invent state

## Scope
- [ ] no audio compute pipeline expansion
- [ ] no playback implementation
- [ ] no second queue/state authority
- [ ] production deploy blocked unless authorized

## Tests
- [ ] concurrency tests
- [ ] lease tests
- [ ] recovery tests
- [ ] retry tests
- [ ] idempotency tests
- [ ] READY/terminal guard tests

## Handoff
- [ ] P05 handoff complete
- [ ] stop after P04
