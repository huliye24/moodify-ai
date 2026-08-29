# MFD-008 Implementation Sequence

## Step 1 — Freeze RC

- [ ] version
- [ ] commit
- [ ] installer
- [ ] SHA256
- [ ] no code drift

## Step 2 — Clean Build

- [ ] fresh dependencies
- [ ] typecheck
- [ ] lint
- [ ] tests
- [ ] package

## Step 3 — Install

- [ ] fresh install
- [ ] first launch
- [ ] app identity
- [ ] icon
- [ ] no dev dependency

## Step 4 — Core Product

- [ ] auth
- [ ] tracks
- [ ] real playback
- [ ] audible
- [ ] pause
- [ ] seek
- [ ] next/previous

## Step 5 — Failure

- [ ] manifest expiry
- [ ] offline
- [ ] reconnect
- [ ] bad state
- [ ] forced kill
- [ ] rapid input

## Step 6 — OS

- [ ] single instance
- [ ] tray
- [ ] background
- [ ] media controls

## Step 7 — Lifecycle

- [ ] restart
- [ ] upgrade
- [ ] uninstall

## Step 8 — Security

- [ ] Electron
- [ ] secrets
- [ ] auth
- [ ] logs
- [ ] media URL
- [ ] update

## Step 9 — Compatibility / resources

- [ ] Windows versions
- [ ] memory
- [ ] CPU
- [ ] logs

## Step 10 — Defects

- [ ] P0
- [ ] P1
- [ ] P2
- [ ] P3

## Step 11 — Artifacts

- [ ] release notes
- [ ] build info
- [ ] checksum
- [ ] evidence
- [ ] known issues
- [ ] security notes
- [ ] rollback

## Step 12 — Decision

- [ ] GO
- [ ] CONDITIONAL GO
- [ ] NO-GO
