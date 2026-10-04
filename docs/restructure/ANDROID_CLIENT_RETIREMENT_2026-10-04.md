# Android Client Retirement — 2026-10-04

**CANON_CHANGE:** YES

**Human decision:** Moodify has one ecosystem App: the released Android player.

**Canonical implementation:** `apps/music-android/` (`com.moodify.music`)

**Retired implementation:** `apps/android/` (`com.moodify.app`)

## Decision basis

1. `apps/music-android/README.md` defines the project as the public Android player and gives it the primary action `PLAY`.
2. `.github/workflows/release.yml` builds and signs the APK from `apps/music-android` only.
3. The retained implementation supports Media3 playback, MediaSession, cloud catalogue playback, local files, and external audio intents.
4. The retired implementation described real service integration as future work and duplicated the Android application authority.

## Change

- Removed all 70 tracked files under `apps/android/`.
- Kept `apps/music-android/` unchanged as the sole Android App source.
- Added `apps/android/` to the repository structure guard so the duplicate path cannot silently return.
- Updated current Canon and repository status. Historical audits retain their original observations.

## Evidence boundary

This retirement does not claim that every useful behavior from the removed candidate has been ported. It resolves product and release authority. Any future feature addition must be implemented in `apps/music-android/` and verified there.

## Rollback

The deletion can be reverted from Git history. The immediate pre-change baseline is `1dd5b2e14cdc67e673c26a2aa62e556c12066b20`. Restoring the retired tree would recreate dual App authority and therefore requires a new explicit human decision.
