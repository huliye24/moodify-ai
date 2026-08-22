# P06 Playback Test Plan

- [ ] TST-01 READY-only
- [ ] TST-02 valid playback metadata
- [ ] TST-03 missing object
- [ ] TST-04 URL expiry refresh
- [ ] TST-05 range/seek
- [ ] TST-06 buffering recovery
- [ ] TST-07 unauthorized access
- [ ] TST-08 no client secrets
- [ ] TST-09 playback failure isolation
- [ ] TST-10 stable Track identity
- [ ] TST-11 PLAY/PAUSE
- [ ] TST-12 next/previous/swipe if in scope
- [ ] TST-13 app lifecycle
- [ ] TST-14 audio focus
- [ ] TST-15 playback evidence

## E2E

Authorized/test READY object:

`READY → Metadata → URI → Android → PLAY → seek → pause → resume → finish`

If signed delivery:

`expiry → refresh → resume`
