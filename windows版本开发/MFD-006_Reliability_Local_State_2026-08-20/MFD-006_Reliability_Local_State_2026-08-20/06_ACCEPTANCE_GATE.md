# MFD-006 Acceptance Gate

## A. Local state

- [ ] one authority
- [ ] schema version
- [ ] validation
- [ ] migration
- [ ] corruption fallback
- [ ] atomic/safe write

## B. Playback continuity

- [ ] last track restored
- [ ] position restored
- [ ] volume restored
- [ ] fresh manifest requested
- [ ] signed URL not persisted

## C. Session

- [ ] secure token storage
- [ ] no plaintext token
- [ ] expiry handled
- [ ] refresh handled
- [ ] concurrent refresh deduplicated

## D. Recovery

- [ ] bounded retry
- [ ] retryable/non-retryable separated
- [ ] offline no crash
- [ ] reconnect possible
- [ ] manifest expiry recoverable
- [ ] stale request ignored

## E. Window

- [ ] size restored
- [ ] invalid/off-screen bounds corrected
- [ ] monitor change safe

## F. Concurrency

- [ ] rapid next/previous safe
- [ ] no duplicate audio
- [ ] seek during switch safe
- [ ] quit during request safe

## G. Tests

- [ ] unit
- [ ] integration
- [ ] normal restart
- [ ] forced kill
- [ ] corruption
- [ ] session expiry
- [ ] manifest expiry
- [ ] offline/reconnect
- [ ] 50-switch stress

## H. Scope discipline

- [ ] no full offline library
- [ ] no background audio downloader
- [ ] no new product page
- [ ] no tray/media keys
- [ ] no auto-update
- [ ] no installer
- [ ] no DSP/native audio

---

全部通过：

> **MFD-007 = GO**
