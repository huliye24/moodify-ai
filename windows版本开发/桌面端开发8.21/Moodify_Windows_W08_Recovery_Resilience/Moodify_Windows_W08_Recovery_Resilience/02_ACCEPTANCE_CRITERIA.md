# W08 Acceptance Criteria

## A. Preflight
- [ ] W07_STATUS = PASS
- [ ] W08_GATE = PASS
- [ ] playback persistence seam read
- [ ] queue persistence seam read
- [ ] current persistence technology known
- [ ] current AppState authority known

## B. Snapshot Contract
- [ ] versioned
- [ ] serializable
- [ ] no runtime objects
- [ ] playback state covered
- [ ] queue state covered
- [ ] navigation covered
- [ ] window state covered
- [ ] timestamps covered

## C. Write Policy
- [ ] no per-timeupdate disk write
- [ ] debounced/throttled position checkpoint
- [ ] track switch checkpoint
- [ ] queue mutation checkpoint
- [ ] pause checkpoint
- [ ] volume checkpoint
- [ ] graceful close flush
- [ ] atomic/transaction-safe

## D. Playback Restore
- [ ] current Track restored
- [ ] position restored
- [ ] volume restored
- [ ] no auto-play on launch
- [ ] position clamp
- [ ] unavailable source safe
- [ ] missing Track safe

## E. Queue Restore
- [ ] order restored
- [ ] current item restored
- [ ] duplicate Track items safe
- [ ] invalid item repaired/dropped
- [ ] missing Track does not crash
- [ ] partial recovery supported

## F. Navigation
- [ ] active view restored or safe default
- [ ] active playlist restored if valid
- [ ] missing playlist falls back
- [ ] search query not required
- [ ] temporary selection not restored

## G. Window
- [ ] bounds restored
- [ ] maximized restored
- [ ] off-screen coordinates clamped
- [ ] monitor removal safe
- [ ] min size safe

## H. Schema / Migration
- [ ] schema_version exists
- [ ] old version handled
- [ ] repeated migration idempotent
- [ ] future version safe
- [ ] mismatch does not clear Library/Playlist

## I. Corruption
- [ ] empty snapshot
- [ ] truncated snapshot
- [ ] invalid types
- [ ] unknown Track
- [ ] malformed QueueItem
- [ ] app still starts
- [ ] durable data preserved

## J. Crash Recovery
- [ ] interrupted write simulated
- [ ] forced restart simulated
- [ ] renderer/process crash scenario tested as feasible
- [ ] last-known-good or atomic write strategy documented

## K. UI / Logging
- [ ] no recovery dashboard
- [ ] minimal user-facing error only
- [ ] recovery logs present
- [ ] no secrets/private audio data logged

## L. Regression
- [ ] Library
- [ ] Playlist
- [ ] Playback
- [ ] Queue
- [ ] Favorites/History
- [ ] Desktop interaction

## PASS Rule

只有证明：

```text
Restart restores useful state safely
and corrupted state cannot take the app down
```

才允许：

```text
W08_STATUS = PASS
W09_GATE = PASS
```
