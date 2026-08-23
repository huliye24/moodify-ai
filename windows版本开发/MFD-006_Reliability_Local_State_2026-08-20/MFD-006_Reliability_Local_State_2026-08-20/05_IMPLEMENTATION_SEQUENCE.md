# MFD-006 Implementation Sequence

## Step 1 — Gate

- [ ] MFD-005 GO
- [ ] Desktop repo clean
- [ ] auth strategy known
- [ ] manifest strategy known

## Step 2 — State inventory

- [ ] durable
- [ ] ephemeral
- [ ] sensitive
- [ ] remove duplicate storage paths

## Step 3 — LocalStateStore

- [ ] schema
- [ ] validation
- [ ] version
- [ ] migration
- [ ] safe write
- [ ] reset

## Step 4 — Secure session storage

- [ ] abstraction
- [ ] OS-backed implementation
- [ ] no plaintext token
- [ ] refresh flow

## Step 5 — Playback continuity

- [ ] last track
- [ ] position
- [ ] volume
- [ ] fresh manifest
- [ ] seek restore

## Step 6 — Window continuity

- [ ] bounds
- [ ] visible screen validation
- [ ] monitor change recovery

## Step 7 — Retry/recovery

- [ ] retryable classification
- [ ] bounded retry
- [ ] session single-flight
- [ ] manifest single-flight

## Step 8 — Race guards

- [ ] cancellation
- [ ] stale response rejection
- [ ] duplicate playback prevention

## Step 9 — Failure tests

- [ ] corruption
- [ ] kill
- [ ] offline
- [ ] expired session
- [ ] expired manifest

## Step 10 — Stress

- [ ] 50 switches
- [ ] rapid control input
- [ ] memory/listener sanity

## Step 11 — Evidence

- [ ] test logs
- [ ] persistence schema
- [ ] recovery diagram
- [ ] limitations

## Step 12 — Final audit

- [ ] no secret leak
- [ ] no offline-library scope creep
- [ ] no duplicate authority
