# Repository Status

This document separates current verified capability from target architecture.

## Canonical Identity

> Moodify is The Ear of AI — an Auditory Intelligence System.

## Brand / Core Identity vs Public Product (2026-08-14)

Per Constitution v2.0 and Release Topology v1.0:

- **Brand and core identity:** "The Ear of AI — an Auditory Intelligence System." This is Moodify's identity, not a consumer product.
- **Public product:** Moodify Music (web/PWA in `apps/music-web`, mobile candidate in `apps/music-android`, service in `moodify-music-package`). Public axis: Library → Track → Now Playing → Play.
- **Internal systems:** Moodify Ear (`moodify-core-package`, `apps/android`, `apps/ear-workbench`) and the Auditory Intervention Laboratory are internal research/production authority, not public launch surfaces.
- The verified-capability tables below describe internal capability; they are not public product claims.

## Current Verified Mainline

```text
Import -> Analyze -> Diagnose -> Process -> Export
```

The wider legacy orchestration and research modules are preserved but are not the supported orchestration authority.

## Verification Baseline

```text
commit: 0b355e7
branch: codex/moodify-ai-ear-reconstitution-001 (from origin/main)
pytest: 109 passed, 7 warnings
ruff: all checks passed
date: 2026-08-08
```

## Capability Table

| Capability | Status | Evidence / Path |
|---|---|---|
| Audio ingest | CANONICAL | `audio_io.py`; v0.1 tests |
| Wave/spectral analysis | CANONICAL | `v01_analyzer.py`; analyzer tests |
| Diagnosis | CANONICAL | `v01_diagnostics.py`; diagnosis tests |
| Controlled intervention / DSP | CANONICAL | `v01_pipeline.py`, `processing/pedalboard_chain.py` |
| Before/after verification | EXPERIMENTAL | Inspector/treatment scripts; no single canonical comparison contract on main |
| Treatment records | EXPERIMENTAL | `treatment_records/`; aggregation scripts |
| Human feedback | EXPERIMENTAL | Treatment record feedback fields and update script |
| Production-case state machine | LEGACY | `orchestration/workflow_engine.py`; newer alternatives remain branch-only |
| MSE structural analysis | ABSENT | No canonical score/MIDI/lyrics structural subsystem on main |
| Cloud runtime | UNRESOLVED | Branch-only systems; root status utilities are not sufficient authority |
| App integration | UNRESOLVED | Historical frontend branches and Draft PR #15 |

Allowed status values are `CANONICAL`, `EXPERIMENTAL`, `LEGACY`, `HISTORICAL`, `ABSENT`, and `UNRESOLVED`.

Never promote a capability to CANONICAL based only on documentation or an unmerged branch.
