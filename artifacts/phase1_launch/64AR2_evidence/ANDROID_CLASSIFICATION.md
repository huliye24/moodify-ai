# Android Classification Note

**Package:** MFY_PUBLIC_MUSIC_INTERNAL_EAR_PROPAGATION_001 (64A-R2), task F
**Date:** 2026-08-15
**Status:** CLASSIFICATION RECORD ONLY — no code moved, no applicationId changed, no projects merged

## Classification (Constitution v2.0 §12, Topology v1.0)

| App | applicationId | Kotlin files | Classification |
|---|---|---|---|
| `apps/android` | `com.moodify.app` | 40 | **INTERNAL EAR OPERATOR** |
| `apps/music-android` | `com.moodify.music` | 4 | **PUBLIC MUSIC CANDIDATE** |

## Current functional difference

`apps/android` (internal Ear operator) today contains a more capable surface and player:
- 16 screens: Home, Processing Hub, Processing, Work Detail, Works, Upload Flow, Search, Now Playing, Creator Center, Copyright Center, Data Center, Collaboration Hub, Notification Center, Profile, Publish Work, Support.
- `data/PlaybackManager.kt` (Media3 ExoPlayer) with queue (`QueueItem`), toggle/next/previous/seekTo, Bearer auth per request, Media Session integration.

`apps/music-android` (public Music candidate) is a minimal shell:
- `MainActivity.kt`, `data/BffClient.kt` (base `https://rongjinwenchuan.xyz/api/v1/music`), `data/Dto.kt`, `data/SecureStore.kt`.
- No dedicated UI screen inventory; no own player surface.

Per `08_MOODIFY_V1_SCOPE_AND_SUBTRACTION_20260815.md` §1: the Android App is not considered ready merely because the internal Ear Android client contains a more capable PlaybackManager.

## Future migratable components (evidence only — not implemented here)

Candidates from `apps/android` that could later serve the public App under Music contracts:
- `PlaybackManager`/`QueueItem` pattern (Media3 queue semantics matching Music's explicit ordered queue; Music queue source = public catalogue order, 06 §6).
- Media Session / background playback integration pattern (06 §4: supporting capability, must not create a second queue or state authority).
- None of these are ported in this package; no code is moved across `applicationId` boundaries.

## Constraints honored

- No code relocation, no applicationId change, no project merge.
- No claim that the public App is launch-ready.
