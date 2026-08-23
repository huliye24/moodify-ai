# MFD-004 Implementation Sequence

## Step 1 — Gate

- [ ] MFD-003 GO
- [ ] real session
- [ ] real READY tracks
- [ ] real manifest
- [ ] Windows output works

## Step 2 — Playback domain

- [ ] PlaybackState
- [ ] PlaybackSource
- [ ] PlaybackError
- [ ] PlaybackEngine contract

## Step 3 — Chromium engine

- [ ] load
- [ ] play
- [ ] pause
- [ ] seek
- [ ] stop
- [ ] volume
- [ ] events
- [ ] dispose

## Step 4 — Manifest integration

- [ ] request
- [ ] sanitize source
- [ ] expiry
- [ ] refresh

## Step 5 — Development harness

- [ ] track info
- [ ] state
- [ ] play
- [ ] pause
- [ ] seek
- [ ] volume
- [ ] next
- [ ] previous

## Step 6 — Basic tests

- [ ] unit
- [ ] integration

## Step 7 — Windows real smoke

- [ ] Track A
- [ ] Track B
- [ ] audible
- [ ] pause
- [ ] seek
- [ ] next
- [ ] previous
- [ ] end

## Step 8 — Failure tests

- [ ] expired URL
- [ ] network loss
- [ ] asset missing
- [ ] invalid media

## Step 9 — Human hearing check

- [ ] no obvious playback corruption

## Step 10 — Final audit

- [ ] no native engine
- [ ] no UI scope creep
- [ ] no secrets
- [ ] no internal API exposure
- [ ] evidence complete
