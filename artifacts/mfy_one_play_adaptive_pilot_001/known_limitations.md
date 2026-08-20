# Known Limitations — MFY_ONE_PLAY_ADAPTIVE_PILOT_001 (2026-08-17)

Honest boundary list. The pilot is deliberately device/library-limited and is
never presented as "everything sounds better".

## Device evidence (PENDING per user instruction)

- No new instrumented device run in 73. Long-duration playback, background
  switching, route hot-switch, phone/notification interruption, low-battery
  and thermal stress tests were NOT executed in this package.
- Reused evidence: 69 device run (M2102J2SC Android 12) — identity processor
  54 ns/frame, 0 underruns, thermal NONE, pause/resume/seek cycles clean.
- Performance/battery/thermal acceptance items remain open until the device
  matrix runs.

## Intervention scope

- Intervention is approved for LOCAL_CONTENT only (dc_offset_fix +
  clip_peak_repair, frozen from 71). Cloud songs and QQ/WeChat shares always
  bypass. The actual audio-path DSP is still the 69 identity graph — 71's
  Python-side primitives are NOT compiled into the Android playback chain;
  the decision framework records intent, the DSP runtime remains no-op.
- This means "APPROVED_INTERVENTION" records an approved in-scope intent;
  audible intervention itself awaits the 71/72 pipeline integration decision.

## Human validation

- 72's blind-listening human sessions skipped per user; statistical report is
  DATA_PENDING. No human preference/identity judgment exists yet.

## Claim boundary

- No universal-improvement claim. Pilot evidence is JVM-level + 69 device
  baseline only.

## UI

- Frozen per 3.1; no new states surfaced (visual work skipped per user).
