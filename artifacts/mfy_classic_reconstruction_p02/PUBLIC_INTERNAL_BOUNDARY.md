# MFY-CR-P02 — Public / Internal Boundary

Formally recorded in `docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md` (Article XI)
and `docs/LISTENING_ENVIRONMENT_ARCHITECTURE.md` (§5).

## Public surface

- local music selection
- reconstruction state
- playback
- library
- minimal progress/error

## Internal surface (never surfaced merely because it exists)

- detailed auditory metrics
- spectrogram
- Evidence artifacts
- ProductionCase state machine
- stem diagnostics
- algorithmic score
- uncertainty details
- experimentation tools
- research reports

## Principle

> **Internal complexity must not leak into the consumer UI merely because it exists.**

The user should not be forced to understand stems, LUFS, phase, spectral
descriptors, evidence graphs, model versions or processing plans. The system
handles complexity so the user can press: **Play**.

## Implication for P03+

- Public-facing product surfaces (Android Listening Environment client, web)
  must not expose internal measurement detail as product features.
- Internal capability may exist without any public affordance.
- Future UI work must re-derive what is public from this boundary, not from
  what is technically possible.
