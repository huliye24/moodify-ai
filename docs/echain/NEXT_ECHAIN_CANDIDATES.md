# Next E-Chain Candidates — MHP-140

**Date**: 2026-06-04 | **From**: ECHAIN-MOODIFY-RUNTIME-001

## Candidates

### 1. ECHAIN-MOODIFY-PRESET-002: Preset Library Productionization
- **Phase transition**: 3 presets → continuously evolving sound craft library
- **Why next**: Runtime is stable; next bottleneck is preset quality. MRS-002 hardened scoring but presets haven't been optimized per-genre.
- **Probe**: Preset parameter space exploration, over-dark per preset analysis
- **Build**: safe_air hardening, per-genre preset optimization, parameter grid search
- **System**: Preset development spec, preset risk labels, craft versioning

### 2. ECHAIN-MOODIFY-CLOUD-003: Cloud Worker Integration
- **Phase transition**: local-only → cloud-scheduled multi-worker
- **Why next**: All processing is single-machine. Cloud scheduler models exist (scheduler.py) but no real backend.
- **Probe**: Cloud provider cost analysis, latency benchmarks, security model
- **Build**: Real cloud workers (Tencent Cloud / AWS), queue distribution
- **System**: Cloud ops runbook, cost monitoring, multi-region spec

### 3. ECHAIN-MOODIFY-DESKTOP-004: Electron Desktop Product
- **Phase transition**: internal operator tool → distributable desktop product
- **Why next**: NEM-001 planned desktop app but never built it. Runtime is now stable enough to support a GUI.
- **Probe**: Minimal user workflow, desktop-runtime communication
- **Build**: Electron shell, import→process→export→view flow
- **System**: GitHub release pipeline, user manual, installer packaging

## Recommendation

**ECHN-MOODIFY-PRESET-002** offers the highest leverage: preset quality improvement benefits every downstream use case without requiring infrastructure changes.
