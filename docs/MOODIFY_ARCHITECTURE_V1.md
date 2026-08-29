# MOODIFY ARCHITECTURE V1 — Industrial Platform Architecture

> **Document Type:** Industrial Architecture Specification
> **Date:** 2026-08-23
> **Status:** Proposed (pending human approval for Canon change)
> **Canon Impact:** CANON_CHANGE = YES — affects external product identity, internal/external capability boundary, and architecture authority
> **Migration Principle:** Progressive migration. No code deletion. No large-scale rewrite. Old Moodify App becomes `apps/web`.

---

## 1. Platform Identity

**Moodify Intelligence Platform**

> AI时代音乐产业的听觉智能基础设施。
> The intelligence layer for the future of music.

Moodify evolves from a monolithic AI music application into a **layered intelligence platform**. The core AI auditory capability becomes a shared engine; product modules build on top; applications deliver end-user experiences.

---

## 2. Architecture Overview

```
                    Moodify
                       |
          Moodify Intelligence Engine
                       |
        ┌──────────┬──────────┬──────────┬──────────┐
        │          │          │          │
       QA        Master      Rating     Supply
```

### Layer Model

```
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│   apps/web · apps/android · apps/desktop                │
│   (End-user products — Play, Studio, Console)           │
├─────────────────────────────────────────────────────────┤
│                  Product Layer                           │
│   products/qa · products/master · products/rating ·     │
│   products/supply                                        │
│   (Industry-facing product modules)                     │
├─────────────────────────────────────────────────────────┤
│                  Engine Layer                            │
│   engine/acoustic_analysis · engine/audio_features ·    │
│   engine/music_understanding · engine/scoring_engine ·  │
│   engine/recommendation_engine                           │
│   (Shared AI auditory intelligence)                     │
├─────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                    │
│   contracts · authority · safety · node · api           │
│   (Cross-cutting infrastructure)                         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Engine Layer — Moodify Intelligence Engine

The engine is the shared AI auditory capability. All future products inherit from this layer.

### Directory Structure

```
engine/
├── acoustic_analysis/         # Acoustic measurement & analysis
│   ├── __init__.py
│   ├── loudness.py            # LUFS measurement
│   ├── true_peak.py           # True peak detection
│   ├── spectrogram.py         # Spectral analysis
│   ├── stereo.py              # Stereo field analysis
│   ├── temporal.py            # Temporal/time-domain analysis
│   ├── frequency.py           # Frequency-domain analysis
│   ├── dynamics.py            # Dynamic range analysis
│   └── fingerprint.py         # Audio fingerprinting
│
├── audio_features/            # Feature extraction & representation
│   ├── __init__.py
│   ├── extractor.py           # Multi-feature extraction
│   ├── wave_features.py       # Waveform features
│   ├── spectral_features.py   # Spectral features
│   ├── rhythm_features.py     # Rhythm/tempo features
│   ├── timbre_features.py     # Timbral features
│   └── io.py                  # Audio I/O utilities
│
├── music_understanding/       # Musical structure & semantics
│   ├── __init__.py
│   ├── structure.py           # Musical structure analysis
│   ├── emotion.py             # Emotion/sentiment detection
│   ├── genre.py               # Genre classification
│   ├── instrument.py          # Instrument recognition
│   └── arrangement.py         # Arrangement analysis
│
├── scoring_engine/            # Scoring & evaluation
│   ├── __init__.py
│   ├── mrs.py                 # Moodify Reality Score
│   ├── quality_score.py       # Quality scoring
│   ├── reference_metrics.py   # Reference-based metrics
│   ├── benchmark.py           # Benchmarking
│   └── uncertainty.py         # Uncertainty quantification
│
├── recommendation_engine/     # Recommendation & matching
│   ├── __init__.py
│   ├── similarity.py          # Audio similarity
│   ├── scene_match.py         # Scene/context matching
│   ├── preference.py          # Preference learning
│   └── ranking.py             # Ranking algorithms
│
├── contracts/                 # Shared contracts (re-exported)
│   ├── __init__.py
│   └── README.md
│
└── README.md
```

### Engine Responsibilities

| Module | Responsibility |
|--------|---------------|
| `acoustic_analysis` | Measure what happened in the sound — LUFS, true peak, spectrum, stereo, dynamics |
| `audio_features` | Extract and represent audio as computable features |
| `music_understanding` | Understand musical structure, emotion, genre, instruments |
| `scoring_engine` | Score audio quality and value with uncertainty bounds |
| `recommendation_engine` | Match audio to contexts, scenes, and preferences |

### Engine Design Principles

1. **Pure functions, no side effects** — Engine modules take audio input, return analysis output
2. **No product logic** — Engine doesn't know about QA, Master, Rating, or Supply
3. **Versioned outputs** — All analysis results are versioned and reproducible
4. **Uncertainty-aware** — Every score carries uncertainty bounds
5. **Evidence-backed** — Every judgment produces evidence artifacts

---

## 4. Product Layer

### 4.1 Product: QA — AI Music Quality Assurance

```
products/qa/
├── __init__.py
├── README.md
├── config.yaml
│
├── analyzers/
│   ├── __init__.py
│   ├── lufs_analyzer.py       # LUFS / loudness compliance
│   ├── spectral_analyzer.py   # Spectral balance analysis
│   ├── dynamic_range.py       # Dynamic range analysis
│   ├── true_peak_checker.py   # True peak compliance
│   ├── stereo_analyzer.py     # Stereo field diagnosis
│   └── defect_detector.py     # Defect classification
│
├── standards/
│   ├── __init__.py
│   ├── streaming.py           # Spotify/Apple/YouTube standards
│   ├── broadcast.py           # Broadcast standards (EBU R128)
│   ├── mastering.py           # Mastering compliance
│   └── platform_specs.py      # Platform-specific specs
│
├── scoring/
│   ├── __init__.py
│   ├── mrs_scorer.py          # MRS scoring for QA
│   ├── quality_gate.py        # Pass/fail quality gate
│   └── report_generator.py    # QA report generation
│
└── api/
    ├── __init__.py
    └── routes.py              # QA-specific API routes
```

**Responsibilities:**
- Audio quality detection and diagnosis
- LUFS analysis (streaming, broadcast compliance)
- Spectral analysis (frequency balance, resonance)
- Dynamic range analysis (DR, crest factor)
- MRS scoring for quality assessment
- Platform compliance checking (Spotify -14 LUFS, Apple -16 LUFS, YouTube -14 LUFS)
- Defect classification (clipping, noise, phase issues)

### 4.2 Product: Master — AI Music Mastering Engine

```
products/master/
├── __init__.py
├── README.md
├── config.yaml
│
├── chain/
│   ├── __init__.py
│   ├── pedalboard_chain.py    # Pedalboard DSP chain
│   ├── spectral_chain.py      # Spectral processing
│   ├── dynamics_chain.py      # Dynamics processing
│   └── stereo_chain.py        # Stereo enhancement
│
├── presets/
│   ├── __init__.py
│   ├── warm_vocal.py          # Warm vocal preset
│   ├── clean_master.py        # Clean master preset
│   ├── wide_space.py          # Wide space preset
│   ├── streaming_optimized.py # Streaming-optimized preset
│   └── custom.py              # Custom preset builder
│
├── intervention/
│   ├── __init__.py
│   ├── pipeline.py            # Intervention pipeline
│   ├── identity_gate.py       # Identity preservation gate
│   ├── primitives.py          # DSP primitives
│   └── registry.py            # Intervention registry
│
├── reconstruction/
│   ├── __init__.py
│   ├── pipeline.py            # Reconstruction pipeline
│   ├── objective.py           # Reconstruction objective
│   └── record.py              # Reconstruction records
│
├── optimization/
│   ├── __init__.py
│   ├── parameter_search.py    # Parameter optimization
│   └── calibration.py         # Chain calibration
│
└── api/
    ├── __init__.py
    └── routes.py              # Master-specific API routes
```

**Responsibilities:**
- AI-driven audio mastering
- Sound optimization (EQ, compression, limiting, stereo widening)
- Commercial release standardization (loudness, dynamics, format)
- Rule-based DSP intervention with identity preservation
- Audio reconstruction and restoration
- Parameter optimization and calibration

### 4.3 Product: Rating — AI Music Asset Rating

```
products/rating/
├── __init__.py
├── README.md
├── config.yaml
│
├── evaluation/
│   ├── __init__.py
│   ├── value_scorer.py        # Music value scoring
│   ├── commercial_potential.py # Commercial potential analysis
│   ├── asset_grade.py         # Asset grading (S/A/B/C/D)
│   └── judge_panel.py         # Multi-judge evaluation
│
├── tagging/
│   ├── __init__.py
│   ├── emotion_tags.py        # Emotion/mood tagging
│   ├── scene_tags.py          # Usage scene tagging
│   ├── genre_tags.py          # Genre classification
│   └── quality_tags.py        # Quality tier tagging
│
├── analysis/
│   ├── __init__.py
│   ├── market_fit.py          # Market fit analysis
│   ├── risk_assessment.py     # Risk assessment
│   ├── identity_ranking.py    # Identity/originality ranking
│   └── trend_analysis.py      # Trend alignment
│
└── api/
    ├── __init__.py
    └── routes.py              # Rating-specific API routes
```

**Responsibilities:**
- Music value scoring (commercial, artistic, technical)
- Commercial potential analysis (market fit, licensing potential)
- Emotion and mood tagging
- Asset grading (S/A/B/C/D tiers)
- Risk assessment (copyright, quality, originality)
- Scene and usage matching tags

### 4.4 Product: Supply — AI Music Supply Chain

```
products/supply/
├── __init__.py
├── README.md
├── config.yaml
│
├── search/
│   ├── __init__.py
│   ├── audio_search.py        # Audio similarity search
│   ├── metadata_search.py     # Metadata-based search
│   ├── semantic_search.py     # Semantic/audio search
│   └── index.py               # Search index management
│
├── matching/
│   ├── __init__.py
│   ├── scene_matcher.py       # Scene/context matching
│   ├── mood_matcher.py        # Mood/emotion matching
│   ├── tempo_matcher.py       # Tempo/BPM matching
│   └── license_matcher.py     # License/rights matching
│
├── pipeline/
│   ├── __init__.py
│   ├── intake.py              # Music intake & registration
│   ├── process.py             # Processing pipeline
│   ├── deliver.py             # Delivery pipeline
│   └── verify.py              # Supply verification
│
├── stems/
│   ├── __init__.py
│   ├── separator.py           # Stem separation
│   ├── store.py               # Stem storage
│   └── service.py             # Stem service
│
└── api/
    ├── __init__.py
    └── routes.py              # Supply-specific API routes
```

**Responsibilities:**
- Music search and discovery (audio similarity, semantic search)
- Scene matching (game, film, advertising, streaming)
- Supply chain pipeline (intake → process → deliver → verify)
- Stem separation and management
- Licensing and rights matching
- Commercial use case fulfillment

---

## 5. Application Layer

```
apps/
├── web/                       # Next.js web application (former moodify-web)
│   ├── app/                   # Next.js App Router
│   ├── components/            # UI components
│   ├── db/                    # Database schema
│   └── package.json
│
├── android/                   # Android application (former music-android)
│   ├── app/
│   └── build.gradle.kts
│
└── desktop/                   # Electron desktop app (former moodify-pulse)
    ├── src/
    └── package.json
```

**Principle:** Applications are thin clients. They call Product APIs. They do not contain business logic. The old Moodify web app is preserved as `apps/web` without modification.

---

## 6. Research Layer

```
research/
├── papers/                    # Research papers
│   ├── WSE-AIM-001_Wave-Spectral_Evolution.pdf
│   ├── WSE-AIM-002_MIDI-Score-Anchored_Post-Production.pdf
│   └── Moodify_Three_Layer_Research_Architecture_Edition_0.1.pdf
│
├── benchmarks/                # Benchmark datasets & results
│   ├── README.md
│   └── mrs_benchmark/
│
├── whitepapers/               # Industry whitepapers
│   └── README.md
│
└── experimental/              # Experimental modules (MAMSE-001..016)
    ├── README.md
    └── mamse/
```

**Principle:** Research code is isolated from production. Experimental modules (MAMSE series) live here, not in the engine.

---

## 7. Shared Infrastructure

Cross-cutting concerns that serve all layers:

| Module | Location | Responsibility |
|--------|----------|---------------|
| Contracts | `shared/contracts/` | Evidence, provenance, rules, serialization |
| Authority | `shared/authority/` | Escalation, scope contracts, review store |
| Safety | `shared/safety/` | Bounds, projection, guardrails |
| Node | `shared/node/` | Worker queue, DB, runner |
| API Gateway | `shared/api/` | FastAPI app, routing, middleware |

---

## 8. Data Flow

```
                    ┌──────────────┐
                    │  Audio Input  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │    Engine     │
                    │  (analysis,   │
                    │   features,   │
                    │   scoring)    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──┐  ┌─────▼─────┐ ┌───▼──────┐
       │   QA    │  │  Master   │ │  Rating  │
       │(quality)│  │(process)  │ │ (value)  │
       └────┬────┘  └─────┬─────┘ └────┬─────┘
            │             │            │
            └─────────────┼────────────┘
                          │
                   ┌──────▼───────┐
                   │   Supply     │
                   │(match, deliver)│
                   └──────┬───────┘
                          │
                   ┌──────▼───────┐
                   │ Applications  │
                   │(web, android) │
                   └──────────────┘
```

---

## 9. API Architecture

Each product exposes its own API namespace:

```
/api/v1/engine/analyze      # Engine: audio analysis
/api/v1/engine/features     # Engine: feature extraction
/api/v1/engine/score        # Engine: scoring

/api/v1/qa/check             # QA: quality check
/api/v1/qa/report            # QA: generate report
/api/v1/qa/compliance        # QA: platform compliance

/api/v1/master/process       # Master: process audio
/api/v1/master/presets       # Master: list presets
/api/v1/master/reconstruct   # Master: reconstruction

/api/v1/rating/score         # Rating: value score
/api/v1/rating/tags          # Rating: emotion/scene tags
/api/v1/rating/grade         # Rating: asset grade

/api/v1/supply/search        # Supply: music search
/api/v1/supply/match         # Supply: scene matching
/api/v1/supply/stems         # Supply: stem separation
/api/v1/supply/deliver       # Supply: delivery
```

---

## 10. Migration Strategy

### Principle: Progressive Migration, No Deletion

```
Phase A (Now):     Create new directories with README + __init__.py
                    Old code stays in moodify-core-package/
                    New code imports from old location

Phase B (Next):    Move modules one by one
                    Each move: update imports → run tests → commit
                    Old location gets compatibility shim

Phase C (Future):  Remove compatibility shims
                    Old moodify-core-package/ becomes legacy reference
```

### Module Migration Map

| Current | New | Phase |
|---------|-----|-------|
| `moodify-core-package/src/moodify/auditory/` | `engine/acoustic_analysis/` | B |
| `moodify-core-package/src/moodify/v01_analyzer.py` | `engine/audio_features/` | B |
| `moodify-core-package/src/moodify/mrs/` | `engine/scoring_engine/` | B |
| `moodify-core-package/src/moodify/diagnosis/` | `products/qa/analyzers/` | B |
| `moodify-core-package/src/moodify/processing/` | `products/master/chain/` | B |
| `moodify-core-package/src/moodify/v01_presets.py` | `products/master/presets/` | B |
| `moodify-core-package/src/moodify/stems/` | `products/supply/stems/` | B |
| `moodify-core-package/src/moodify/data_factory/` | `products/supply/pipeline/` | B |
| `moodify-core-package/src/moodify/evaluation/` | `products/rating/evaluation/` | B |
| `moodify-core-package/src/moodify/knowledge/` | `products/rating/tagging/` | B |
| `apps/music-web/` | `apps/web/` | C (symlink first) |
| `apps/music-android/` | `apps/android/` | C (symlink first) |
| `moodify-pulse/` | `apps/desktop/` | C (symlink first) |
| `moodify_experimental/` | `research/experimental/` | C |

---

## 11. Canon Change Declaration

**CANON_CHANGE = YES**

- **Why:** The repository evolves from a monolithic application to a layered platform. This changes the external product identity boundary and internal architecture authority.
- **Evidence:** Phase 1 analysis (docs/CURRENT_ARCHITECTURE.md) shows 30+ core modules that map cleanly to engine + 4 product modules.
- **Affected authority files:**
  - `docs/canon/CURRENT_CANON.md` — add platform architecture
  - `docs/canon/CURRENT_ARCHITECTURE.md` — update to V1 architecture
  - `docs/canon/PRODUCT_BOUNDARY.md` — add product layer definitions
  - `AGENTS.md` — add engine/products/apps structure
- **Migration:** Progressive (Phase A → B → C as described above)
- **Rollback:** If migration fails, new directories can be removed; old code is untouched.

---

*This document defines the target architecture. Implementation follows the progressive migration plan.*
