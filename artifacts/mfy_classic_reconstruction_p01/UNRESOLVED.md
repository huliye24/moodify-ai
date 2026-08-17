# MFY-CR-P01 — Unresolved (human decisions for P02+)

Items below do NOT block P01 completion but must be answered before P02 work
depends on them.

## 1. Android dual line (affects P02 scope directly)

`apps/android` (com.moodify.app) produced releases 2.0.0/3.0.0/3.1.0 (2026-08-15/16);
`apps/music-android` (com.moodify.music) produced 2.0.1 and carries the newer Compose
UI (MoodifyMusicApp) and the external-audio/QQ-handoff intents. P01 converged both as
committed source. P02 must pick the canonical product line (or define their relationship).

## 2. Gradle wrapper state for music-android

The working tree deleted gradlew/gradlew.bat/gradle-wrapper. Builds now require a
cached/system gradle 8.14 + Android Studio JBR (JAVA_HOME). Fresh clone buildability
depends on this. Options: (a) keep wrapper-less, document toolchain; (b) restore wrapper
with pinned distributionUrl.

## 3. Large evidence bundles offline storage

ear_pilot_001 (326M), mfy_infra_foundation_001 (244M), production_cases (62M) are not
in git. An authoritative offline location must be chosen (LA server archive? local
archive dir? object storage). Until then they exist only on this machine.

## 4. PR #21 close decision

Head is fully absorbed; closing with auditable note is authorized by the task but the
action is deferred to the human operator (external-visible action).

## 5. Push decision for baseline branch

`codex/moodify-classic-reconstruction-001` is local-only; `codex/moodify-android-2.0`
has 2 unpushed commits (72c47c4d stems, 5bbc4972 evidence) against the moodify remote.
Push/PR strategy for the new baseline is a human decision.

## 6. temp/ credential file

`temp/moodify_audit/polardb_app.env` holds PolarDB credentials (out of git, correct).
Confirm it is also excluded from any future backup/archive.

## 7. music-web npm test wrapper

On Windows, `npm test` fails at `node --test tests/*.test.mjs` (glob passed literally
by cmd -> ERR_UNSUPPORTED_ESM_URL_SCHEME) while direct invocation passes 36/36. A
cross-platform test script fix could be part of a later governance pass.
