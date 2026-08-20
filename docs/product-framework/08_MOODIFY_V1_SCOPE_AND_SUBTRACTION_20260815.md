# Moodify v1 Scope and Subtraction

**Document ID:** MFY-V1-SCOPE-SUBTRACTION-20260815  
**Date:** 2026-08-15  
**Status:** CURRENT V1 SCOPE  
**Launch target:** 2026-08-22

## 1. v1 public scope

```text
Official Website
-> Moodify Music Web
-> Moodify Music App when independently ready
```

Public Music core:

- catalogue/library of playable works;
- Track identity;
- one authoritative playable version;
- Play;
- Pause;
- Previous;
- Next;
- deterministic queue;
- byte-range media delivery;
- honest loading, empty and failure states.

The Android App is not considered ready merely because the internal Ear Android client contains a more capable PlaybackManager.

## 2. v1 internal production scope

Keep operationally strong but non-public:

- Moodify Ear;
- Ear API and worker;
- ProductionCase;
- Evidence;
- authority and human review;
- Source integrity;
- Data Factory;
- Auditory Intervention Laboratory;
- verification;
- playback-ready asset preparation;
- backup, recovery, security and observability.

## 3. Disposition model

| Decision | Meaning |
|---|---|
| KEEP | Current v1 public or internal authority |
| INTERNALIZE | Keep active but remove from public product cognition |
| FREEZE | Preserve code and tests; stop adding scope |
| ARCHIVE | Remove from current authority and build discovery; retain recoverably |
| DELETE | Remove only after dependency proof, backup and explicit authorization |

## 4. Current disposition

### KEEP — public runtime

- official website;
- `apps/music-web` playback core;
- `apps/music-android` as the public App candidate;
- `moodify-music-package` catalogue/Track/media contracts;
- production media delivery;
- current playable-version authority;
- playback error recovery;
- deployment, health and rollback for the public playback path.

### INTERNALIZE

- `moodify-core-package`;
- `apps/ear-workbench`;
- `apps/android`;
- Ear public API consumers after reviewed migration;
- ProductionCase, Evidence and Review UI;
- technical measurement and intervention surfaces.

### FREEZE / remove from public prominence

- playlists;
- follow/social;
- licensing intent and Inbox;
- complex Creator Console;
- public Evidence navigation;
- public Ear landing and onboarding;
- presets, metrics and DSP controls;
- recommendation/personalization beyond an explicit v1 queue;
- play-event-driven recent history when not required by the launch journey.

Creator Source intake may remain as a controlled supply path, but it is not the public product's central journey.

### ARCHIVE candidates after launch stability

- superseded public dual-product documents;
- completed historical task packs;
- obsolete visual experiments;
- old release plans no longer acting as ledgers;
- duplicate prototypes and starter examples proven unused;
- experimental roots excluded from production.

Archive work must preserve provenance and must not be mixed into the 2026-08-22 launch critical path.

### DELETE candidates

Only regenerable and dependency-free material may be proposed first:

- build caches;
- `tsconfig.tsbuildinfo`;
- temporary archives;
- duplicate generated test output;
- unused starter examples after build/import audit.

Deletion requires exact target verification and explicit authorization. Private audio, Source, playback-ready media, databases, ProductionCases and Evidence are never casual cleanup targets.

## 5. Playback authority decision required

Current repository reality includes more than one media-delivery implementation:

- Cloudflare/R2 route implementation;
- LA nginx `/audio/` media alias used by the current public Web configuration.

Before GO, one production path must be named authoritative. The other may remain as a deployment alternative but cannot create a second media truth.

## 6. No fake fallback

Production catalogue failure must not silently display a bundled demonstration catalogue as if the live service succeeded.

```text
Catalogue success -> real queue
Catalogue failure -> honest unavailable/retry state
```

Demo fixtures may remain in explicit development or test mode only.

## 7. Release gate

The v1 product is ready only when:

- Website has one primary Music destination;
- Web performs the four actions on real public media;
- App performs the same four actions before being called public-ready;
- Web and App resolve the same Track to the same authoritative playable version;
- media Range and recovery behavior are verified;
- catalogue failure is honest;
- internal Ear remains protected and operational where it affects playback-ready results;
- no future rendering capability is presented as deployed fact;
- Human GO remains unsigned until real production evidence is reviewed.

