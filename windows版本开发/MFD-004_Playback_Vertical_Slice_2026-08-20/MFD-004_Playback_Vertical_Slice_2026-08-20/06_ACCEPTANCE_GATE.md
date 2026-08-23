# MFD-004 Acceptance Gate

## A. Real Cloud

- [ ] real user session
- [ ] real track
- [ ] real PlaybackManifest
- [ ] real authorized media
- [ ] no mock-only success

## B. Playback

- [ ] load
- [ ] play
- [ ] audible Windows output
- [ ] pause
- [ ] resume
- [ ] seek
- [ ] ended
- [ ] volume
- [ ] next
- [ ] previous

## C. Reliability baseline

- [ ] expired manifest handled
- [ ] media load error handled
- [ ] network interruption does not crash
- [ ] retry/reload possible
- [ ] no overlapping duplicate playback
- [ ] cleanup works

## D. Architecture

- [ ] PlaybackEngine abstraction
- [ ] Chromium engine is implementation, not product authority
- [ ] no Cloud state duplication
- [ ] no Ear duplication
- [ ] no internal credentials

## E. Scope discipline

- [ ] no final Moodify UI
- [ ] no skin
- [ ] no system tray
- [ ] no media keys
- [ ] no offline library
- [ ] no DSP
- [ ] no WASAPI
- [ ] no native addon
- [ ] no bit-perfect claim

## F. Evidence

- [ ] unit tests
- [ ] integration tests
- [ ] Windows smoke
- [ ] 2 real tracks if available
- [ ] human audible verification
- [ ] compatibility facts recorded
- [ ] limitations recorded

---

全部通过：

> **MFD-005 = GO**
