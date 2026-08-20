# Listening Environment Architecture

**Part of:** [CLASSIC_RECONSTRUCTION_CONSTITUTION.md](CLASSIC_RECONSTRUCTION_CONSTITUTION.md) (v1.0)
**Status:** LIVE

---

## 1. Definition

The Listening Environment is the layer that determines how a reconstruction source reaches a real device and a real listener. It is **not a player skin** and it is **not the reconstruction engine**.

```text
Reconstruction
  ↓
Rendering
  ↓
Device
  ↓
Human Hearing
```

> **Reconstruction result ≠ final hearing result.**

## 2. Responsibilities (current and future)

The Listening Environment may be responsible for:

- decode;
- playback;
- output adaptation;
- device profile;
- song-specific playback preset;
- streaming;
- offline encrypted cache *(not authorized in P02)*;
- local / private library integration;
- rendering policy.

## 3. Current Boundaries (P02)

In P02 only the following are defined — nothing below is implemented in this phase:

- playback and device/output adaptation remain the Android/Listening Environment client's domain (`apps/music-android`, `apps/android`);
- song-specific rendering is a stated future direction;
- device-specific EQ, HRTF, headphone profiles and adaptive room correction are recorded but **not authorized**:

```text
FUTURE
NOT_AUTHORIZED_IN_P02
```

## 4. Rendering as a Second Moat

The future second core moat of Moodify is **rendering** — the ability to deliver the reconstruction to a specific device and listener faithfully and with intent. This document establishes the architectural boundary so that later phases can invest in rendering without blurring it into reconstruction.

## 5. Public vs Internal

The Listening Environment is the **public** surface of Moodify. Per the constitution:

- public: local music selection, reconstruction state, playback, library, minimal progress/error;
- internal: detailed auditory metrics, spectrograms, evidence artifacts, ProductionCase state machine, stem diagnostics, algorithmic scores, uncertainty details, experimentation tools, research reports.

> **Internal complexity must not leak into the consumer UI merely because it exists.**
