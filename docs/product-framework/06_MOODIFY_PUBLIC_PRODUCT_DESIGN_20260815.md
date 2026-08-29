# Moodify Public Product Design

**Document ID:** MFY-PUBLIC-PRODUCT-DESIGN-20260815  
**Date:** 2026-08-15  
**Status:** APPROVED DIRECTION / IMPLEMENTATION BOUNDARY  
**Public product:** Moodify Music

## 1. Product statement

Moodify Music is:

> **A player that listens to music before it plays music.**

Public cognition:

> **Moodify listens before you do.**

Chinese expression:

> **Moodify 先听，再为你播放。**

These expressions describe the product direction. Public claims must remain limited to the preparation and playback path actually deployed and verified.

## 2. Public product topology

```text
Official Website
├── explains Moodify briefly
└── sends the user to Music

Moodify Music Web
└── browser playback terminal

Moodify Music App
└── mobile playback terminal
```

The website is not a third product. Web and App are not separate product lines. They are two terminals for one Music truth.

## 3. Surface responsibilities

| Surface | Single responsibility | Must not become |
|---|---|---|
| Official Website | Explain Moodify and enter Music | Ear workstation, technical report or feature catalogue |
| Music Web | Immediate listening without installation | Creator administration suite or public DSP console |
| Music App | Stable, persistent, device-level listening | Ear operator client or parameter editor |

## 4. Moodify Music v1 interaction

The primary surface is organized around:

```text
Library
-> Track
-> Now Playing
-> Play / Pause / Previous / Next
```

Minimum visible information:

- track title;
- artist/creator name;
- artwork or honest default artwork;
- current playback state;
- current track position where useful;
- recoverable playback error.

Primary actions:

- Play;
- Pause;
- Previous;
- Next.

Seek, operating-system Media Session and background playback are supporting interaction capabilities. They must not create a second queue or state authority.

## 5. One playback truth

Web and App must share:

- one catalogue contract;
- one Track identity;
- one current playable version decision;
- one media integrity record;
- one error model;
- one publication authority.

They may render differently, but they may not choose different authoritative audio versions by guessing locally.

## 6. Queue model

Previous and Next operate on an explicit ordered queue.

For v1, the safe queue source is the returned public catalogue order or an explicitly selected result set. Playback history, recommendation and social behavior are not required to define Next.

Rules:

- empty queue -> honest empty state;
- one item -> Previous/Next remain on the item or are disabled consistently;
- end of track -> deterministic Next behavior;
- catalogue failure -> explicit failure, never a hidden fake catalogue;
- queue changes -> preserve or deliberately replace current Track, never silently jump.

## 7. Runtime playback chain

```text
Catalogue
-> ordered queue
-> Track + playable asset reference
-> media delivery with byte ranges
-> browser audio / Media3 player
-> local playback state
```

Play and Pause are player actions. Previous and Next are queue actions. The backend supplies catalogue truth and playable bytes; it does not need four separate action endpoints.

## 8. Internal production dependency

The public player can remain simple because internal Moodify may be complex:

```text
SOURCE
-> identity and integrity
-> listen / represent / judge
-> intervention, gain-only, subtle rendering or BYPASS
-> verify
-> playback-ready version
-> publish to catalogue
```

Users do not need to see ProductionCase, Evidence, measurements, confidence, DSP graph or model version. Internal operators still require them.

## 9. Failure design

The product must distinguish:

- catalogue unavailable;
- media unavailable;
- media format unsupported;
- network interrupted;
- permission unavailable;
- preparation not ready;
- internal result blocked or awaiting human judgment.

No failure may fall back to a fabricated success state. Retry must preserve Track identity and avoid duplicate play or publication records.

## 10. Visual direction

The product surface should be quiet enough for the music to remain primary:

- restrained hierarchy;
- few simultaneous decisions;
- one dominant playback action;
- clear current Track;
- stable controls;
- low visual pressure;
- no technical theatre;
- no visual implication that every track was modified.

The public surface should feel complete with four playback actions, not empty because secondary features were removed.

