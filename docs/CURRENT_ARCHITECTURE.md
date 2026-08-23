# CURRENT ARCHITECTURE — Moodify Repository Analysis

> **Document Type:** Industrial Architecture Upgrade — Phase 1 Analysis
> **Date:** 2026-08-23
> **Scope:** Full repository scan of `E:\moodify` (local clone of `github.com/huliye24/moodify-ai`)
> **Rule:** This document records the current state as-is. No code was deleted or rewritten during analysis.

---

## 1. Current Project Status

Moodify is a **monolithic AI music application repository** containing research prototypes, product code, cloud deployment configs, and extensive documentation. The repository has grown organically from a research project ("The Ear of AI") into a multi-component system with an Android app, web PWA, Python processing core, and cloud infrastructure.

### Repository Scale

| Metric | Count |
|--------|-------|
| Top-level directories | 79 |
| Python files (excl. cache/node_modules) | ~5,591 |
| TypeScript files | ~57 |
| JavaScript files | ~70 |
| Markdown docs | 236 |
| WAV audio assets | ~1,618 |
| PNG images | ~900+ |

### Identity Status (per Canon v1.1)

- **External product:** Moodify Music / Moodify Player (Android 3.1 APK + music-web PWA)
- **Internal system:** Moodify Ear / Auditory Intelligence (analysis, judgment, verification)
- **Old identity "The Ear of AI" as public product:** Deprecated (Canon W01-P01)
- **Current README positioning:** "auditory intelligence layer for the AI era" (research framing)

---

## 2. Technology Stack

### Backend (Python)

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | >=3.10 |
| Web Framework | FastAPI | 0.136.0 |
| ASGI Server | Uvicorn | 0.44.0 |
| Audio I/O | librosa, soundfile | 0.11.0, 0.13.1 |
| Loudness | pyloudnorm | 0.2.0 |
| DSP Processing | pedalboard | 0.9.23 |
| Numerical | NumPy, SciPy | 2.4.4, 1.17.1 |
| Data Validation | Pydantic | 2.13.2 |
| HTTP Client | httpx | >=0.24.0 |
| Visualization | matplotlib | 3.10.8 |
| Config | PyYAML | 6.0.3 |
| Optional: Stem Separation | demucs, torch | latest |
| Testing | pytest | >=7.0 |
| Linting | ruff | py310 target |

### Frontend (Web)

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js | 16.2.6 |
| UI Library | React | 19.2.6 |
| Styling | Tailwind CSS | 4.2.1 |
| ORM | Drizzle ORM | 0.45.2 |
| Database | SQLite (via D1/Workers) | - |
| Build | Vite | 8.0.13 |
| Deployment | Cloudflare Workers (Wrangler) | 4.92.0 |
| TypeScript | 5.9.3 | - |

### Frontend (Desktop — moodify-pulse)

| Component | Technology |
|-----------|-----------|
| Framework | Electron + Vite + React |
| Language | TypeScript |

### Mobile (Android)

| Component | Technology |
|-----------|-----------|
| Build System | Gradle (Kotlin DSL) |
| Min SDK | Android 8.0+ |
| Current Version | 2.0.0 / 3.1 |

### Infrastructure

| Component | Technology |
|-----------|-----------|
| Containerization | Docker (multi-stage build, Python 3.11-slim) |
| Orchestration | docker-compose (api + worker services) |
| Cloud Servers | 2 VPS (LA core 4C/8G + Hangzhou data worker 2C/1.6G) |
| Database (Cloud) | PolarDB (MySQL 8.0 + PostgreSQL 16) — currently empty/unused |
| Storage | Local disk only (no OSS/S3/R2 provisioned) |
| CDN/Tunnel | Cloudflare (cloudflared tunnel) |
| Reverse Proxy | nginx |
| GPU/AI Inference | None (no GPU, no model serving) |

---

## 3. Code Structure — Module Map

### 3.1 Core Engine (`moodify-core-package/src/moodify/`)

This is the heart of the system — a Python package with 30+ sub-modules:

```
moodify-core-package/src/moodify/
├── api/                    # FastAPI application
│   ├── main.py            # App entry, health, job endpoints
│   ├── routes/            # analyze, evaluate, process, reviews, stems, calibration, sessions
│   ├── schemas/           # API request/response schemas
│   └── services/          # Audio service layer
├── auditory/              # Acoustic analysis engine (26 modules)
│   ├── comparison.py      # Before/after comparison
│   ├── decode.py          # Audio decoding
│   ├── identity.py        # Audio identity/fingerprinting
│   ├── inventory.py       # Feature inventory
│   ├── judgment.py        # Listening judgment
│   ├── loudness.py        # LUFS measurement
│   ├── measurement_layers.py  # Multi-layer measurement
│   ├── measurement_registry.py # Measurement registry
│   ├── metrics.py         # Acoustic metrics
│   ├── models.py          # Data models
│   ├── profiles.py        # Audio profiles
│   ├── reports.py         # Analysis reports
│   ├── spectrogram.py     # Spectral analysis
│   ├── stereo.py          # Stereo analysis
│   ├── structure.py       # Musical structure
│   ├── timeline.py        # Temporal analysis
│   ├── true_peak.py       # True peak measurement
│   └── uncertainty.py     # Uncertainty quantification
├── authority/             # Decision authority & escalation
│   ├── escalation.py      # Human escalation logic
│   ├── pipeline.py        # Authority pipeline
│   ├── review_store.py    # Review storage
│   └── scope_contract.py  # Scoped authority contracts
├── calibration/           # System calibration
├── contracts/             # Data contracts (evidence, provenance, rules)
├── data_factory/          # Data production pipeline
│   ├── algorithmic_review.py  # Algorithmic quality review
│   ├── case_runner.py     # Case execution
│   ├── dataset_builder.py # Dataset construction
│   ├── human_review.py    # Human review integration
│   ├── intervention.py    # Data-side intervention
│   ├── plan_generator.py  # Production planning
│   ├── runner.py          # Pipeline runner
│   └── verification_contract.py # Verification contracts
├── data_plane/            # Data storage & delivery plane
├── diagnosis/             # Audio defect diagnosis
│   ├── defect_classifier.py
│   ├── engine.py
│   ├── health_scorer.py
│   ├── metrics.py
│   ├── preprocessing.py
│   └── quality_gate.py
├── era_diagnostic/        # ERA diagnostic engine
├── evaluation/            # Evaluation framework
│   ├── batch.py           # Batch evaluation
│   └── judges.py          # Judge models
├── identity_guard/        # Identity preservation guard
├── intervention/          # DSP intervention pipeline
│   ├── identity_gate.py
│   ├── pipeline.py
│   ├── primitives.py
│   └── registry.py
├── knowledge/             # Domain knowledge base
│   ├── craft_chain_match.py
│   ├── craft_chains.py
│   ├── emotion_targets.py
│   ├── mpl_library.py
│   └── risk_model.py
├── listening/             # Listening test protocol
├── llm/                   # LLM integration
├── memory/                # Session memory
├── mrs/                   # Moodify Reality Score
│   ├── benchmark.py
│   ├── config.py
│   ├── metrics.py
│   └── scoring.py
├── node/                  # Distributed worker node
│   ├── cli.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── queue.py
│   ├── resources.py
│   ├── runner_adapter.py
│   └── worker.py
├── optimizer/             # Parameter optimization
├── orchestration/         # Workflow orchestration (legacy)
├── physics/               # Physics-based audio experiments
├── processing/            # DSP processing chain
│   ├── operators.py
│   ├── pedalboard_chain.py  # Pedalboard-based DSP
│   └── spectral_chain.py    # Spectral processing
├── reconstruction/        # Audio reconstruction
├── reconstruction_factory/ # Reconstruction factory
├── reconstruction_job/    # Reconstruction job system
├── reconstruction_objective/ # Reconstruction objective
├── safety/                # Safety bounds & projection
├── stems/                 # Stem separation service
├── v01_*                  # v0.1.0 mainline pipeline
│   ├── v01_pipeline.py    # Main pipeline: Import→Analyze→Diagnose→Process→Export
│   ├── v01_analyzer.py    # Audio analysis
│   ├── v01_diagnostics.py # Diagnostics
│   ├── v01_exporter.py    # Export
│   ├── v01_presets.py     # Processing presets (warm_vocal, clean_master, wide_space)
│   └── v01_types.py       # Type definitions
├── audio_io.py            # Audio I/O utilities
├── cli.py                 # CLI entry
├── release.py             # Release/production entry
├── release_cli.py         # Release CLI
├── fingerprint.py         # Audio fingerprinting
├── icc.py                 # Inter-channel correlation
├── protocol.py            # Communication protocol
├── reality_metrics.py     # Reality metrics
├── uncertainty.py         # Uncertainty modeling
└── conservation.py        # Conservation principles
```

### 3.2 Experimental Modules (`moodify-core-package/src/moodify_experimental/`)

16 experimental MAMSE (Music Analysis & Music Structural Engineering) modules:
- MAMSE-001 through MAMSE-016
- Each contains: config, evidence, algorithm implementation, policy/sketch modules
- Covers: NMF decomposition, RPCA, multilinear analysis, covariance, graph signal processing, gammatone filterbank, masking, object separation, pitch tracking

### 3.3 Frontend Applications (`apps/`)

```
apps/
├── music-web/             # Next.js web application (PWA)
│   ├── app/               # Next.js App Router
│   │   ├── api/v1/        # API routes
│   │   ├── console/       # Admin console
│   │   ├── library/       # Music library
│   │   ├── studio/        # Creator studio
│   │   ├── track/[id]/    # Track detail page
│   │   ├── playlists/     # Playlist management
│   │   ├── inbox/         # User inbox
│   │   ├── drafts/        # Draft management
│   │   └── design/        # Design system
│   ├── components/ui/     # UI components
│   ├── db/                # Drizzle ORM schema (SQLite)
│   ├── drizzle/           # Database migrations
│   ├── scripts/           # Build & deploy scripts
│   └── artifacts/         # Generated artifacts
├── music-android/         # Android application
│   ├── app/               # Android app module
│   └── build.gradle.kts   # Gradle build config
├── ear-workbench/         # Ear diagnostic workbench
└── tools/                 # App-side tools
```

### 3.4 Other Subsystems

| Directory | Description |
|-----------|-------------|
| `moodify-pulse/` | Electron desktop app (Vite + React + TypeScript) |
| `moodify-bridge/` | Bridge service (src + tests) |
| `moodify-system/` | System integration (moodify-client, moodify-cloud, moodify-local, moodify-shared) |
| `moodify-music-package/` | Music package module |
| `moodify-runtime/` | Runtime configuration |
| `sdk/` | Python SDK with examples |
| `models/` | ML models (bsroformer for stem separation) |
| `schemas/` | Canonical schemas |
| `scripts/` | Utility scripts (canon guard, pilot runner, inspector, calibration) |
| `tools/` | Development tools |
| `ops/` | Operations tooling |
| `configs/` | Runtime configuration (JSON) |

### 3.5 Data & Assets

| Directory | Description |
|-----------|-------------|
| `data/` | Datasets, numpy arrays, JSON configs |
| `artifacts/` | Production artifacts (JSON, PNG, WAV, NPZ) |
| `calibration_reports/` | Calibration reports (PNG, JSON, WAV) |
| `inspector_reports/` | Inspector reports (PNG, MD, JSON, WAV, HTML) |
| `experiments/` | Experiment records |
| `listening_test/` | Listening test materials |
| `local_audio_assets/` | Local audio files |
| `treatment_records/` | Treatment/processing records |
| `examples/` | Usage examples |
| `07Music/` | Music assets (MP3, WAV) |
| `music/`, `pre-music/`, `night/` | Additional music assets |

---

## 4. Frontend Structure (Detailed)

### Web App (`apps/music-web/`)

**Framework:** Next.js 16 with App Router, deployed on Cloudflare Workers via Vite plugin.

**Routes:**
- `/` — Home/landing
- `/console` — Admin console
- `/library` — Music library browser
- `/studio` — Creator studio
- `/track/[id]` — Track detail/player
- `/playlists` — Playlist management
- `/inbox` — Notifications
- `/drafts` — Draft tracks
- `/c/[handle]` — Creator profile
- `/design` — Design system showcase
- `/offline` — Offline support
- `/beta-login` — Beta authentication
- `/api/v1/` — Backend API routes

**Database Schema (Drizzle ORM / SQLite):**
- `users` — User accounts (id, authSubject, email, displayName, status)
- `creatorProfiles` — Creator profiles (handle, bio, avatar, heroImage, location)
- `tracks` — Music tracks (title, description, language, status, sourceType, licenseStatus)
- `trackVersions` — Track versions (audioObjectKey, sha256, duration, earProductionCaseId)
- `creationPassports` — AI creation disclosure (aiTool, modelVersion, promptDisclosure, lyricsAuthor)
- `creatorFollows` — Follow relationships

**Key Feature:** Creation Passports — discloses AI tool, model version, prompt disclosure level for each track version. This is a transparency/provenance feature.

---

## 5. Backend Structure (Detailed)

### API Layer (FastAPI)

**Entry:** `moodify-core-package/src/moodify/api/main.py`

**Routes:**
| Route | Module | Function |
|-------|--------|----------|
| `/health` | main.py | Health check |
| `/analyze/*` | routes/analyze.py | Audio analysis |
| `/evaluate/*` | routes/evaluate.py | Quality evaluation |
| `/process/*` | routes/process.py | Audio processing |
| `/reviews/*` | routes/reviews.py | Review management |
| `/stems/*` | routes/stems.py | Stem separation |
| `/calibration/*` | routes/calibration.py | System calibration |
| `/sessions/*` | routes/sessions.py | Listening sessions |
| `/reconstruction/*` | routes_reconstruction.py | Reconstruction jobs |

### Processing Pipeline (v0.1.0 Mainline)

```
Import → Analyze → Diagnose → Process → Export
```

1. **Import:** `audio_io.py` loads WAV/MP3/FLAC/M4A/OGG/AAC
2. **Analyze:** `v01_analyzer.py` extracts wave + spectral features
3. **Diagnose:** `v01_diagnostics.py` identifies issues (loudness, dynamics, spectrum)
4. **Process:** `processing/pedalboard_chain.py` applies DSP via Pedalboard
5. **Export:** `v01_exporter.py` writes processed audio + report

### Data Factory Pipeline

```
SOURCE → LISTEN → REPRESENT → JUDGE → ABC INTERVENTION → VERIFY
       → ALGORITHMIC REVIEW → DATASET → NEXT CASE
```

- 10-song pilot completed (all SUCCEEDED)
- Runs on Hangzhou worker node
- SQLite-based queue system

### Worker Node System

- `node/queue.py` — SQLite job queue
- `node/worker.py` — Background worker
- `node/cli.py` — CLI entry (`moodify-node`)
- Deployed on LA + Hangzhou VPS

### MRS (Moodify Reality Score)

- Reference-based distance metric from configured feature statistics
- `mrs/scoring.py` — Score computation
- `mrs/metrics.py` — Metric definitions
- `mrs/benchmark.py` — Benchmarking
- Status: Research-oriented, not validated universal quality judgment

---

## 6. Database Structure

### Local/Worker Database
- **Engine:** SQLite
- **Location:** `/var/lib/moodify` (cloud), `data/moodify_runtime/` (local)
- **Usage:** Job queue, case records, treatment records, node state

### Web App Database
- **Engine:** SQLite via Cloudflare D1
- **ORM:** Drizzle ORM
- **Schema:** Users, CreatorProfiles, Tracks, TrackVersions, CreationPassports, CreatorFollows

### Cloud Database (PolarDB)
- **MySQL 8.0.13** (172.27.118.106) — Empty shell
- **MySQL 8.0.18** (172.27.118.104) — `moodify_dev` 19 tables, ~0 data
- **PostgreSQL 16.14** (101.133.107.206) — Online but unused
- **Status:** Provisioned but not in active use

---

## 7. Implemented Features

### Canonical (Verified & Tested)

| Feature | Evidence |
|---------|----------|
| Audio ingest (WAV/MP3/FLAC/M4A/OGG/AAC) | `audio_io.py`, v0.1 tests |
| Wave & spectral analysis | `v01_analyzer.py`, analyzer tests |
| Audio diagnosis (loudness, dynamics, spectrum) | `v01_diagnostics.py`, diagnosis tests |
| Controlled DSP intervention (Pedalboard chain) | `v01_pipeline.py`, `processing/pedalboard_chain.py` |
| LUFS loudness measurement | `auditory/loudness.py` |
| True peak measurement | `auditory/true_peak.py` |
| Stereo correlation analysis | `auditory/stereo.py`, `icc.py` |
| Spectrogram analysis | `auditory/spectrogram.py` |
| MRS evaluation framework | `mrs/` module |
| Data factory pipeline (10-song pilot) | `data_factory/`, artifacts |
| Node queue / worker system | `node/`, cloud deployment |
| Algorithmic review | `data_factory/algorithmic_review.py` |
| FastAPI REST API | `api/main.py` + routes |
| Docker containerization | `Dockerfile`, `docker-compose.yml` |
| Next.js web app (PWA) | `apps/music-web/` |
| Android app (v2.0.0/3.1) | `apps/music-android/`, deliverables |
| Creation passport (AI provenance) | `db/schema.ts` |
| Evidence & provenance contracts | `contracts/` module |
| Authority & escalation system | `authority/` module |
| Audio fingerprinting | `fingerprint.py` |
| Uncertainty quantification | `auditory/uncertainty.py`, `uncertainty.py` |

### Experimental (Implemented, Not Merged/Validated)

| Feature | Status |
|---------|--------|
| Reconstruction objective system | IMPLEMENTED_NOT_MERGED |
| Identity guard | IMPLEMENTED_NOT_MERGED |
| ERA diagnostic engine | IMPLEMENTED_NOT_MERGED |
| MAMSE-001 through MAMSE-016 | EXPERIMENTAL_ACCEPTED |
| Before/after verification (Inspector) | EXPERIMENTAL |
| Treatment records & feedback | EXPERIMENTAL |
| Stem separation service | IMPLEMENTED (demucs optional dep) |
| LLM integration | IMPLEMENTED |
| Listening test protocol | IMPLEMENTED |
| Calibration system | IMPLEMENTED |
| Physics-based experiments | IMPLEMENTED |

---

## 8. Incomplete / Unresolved Features

| Feature | Status | Notes |
|---------|--------|-------|
| MSE structural analysis | ABSENT | No canonical score/MIDI/lyrics structural subsystem |
| Cloud runtime (Ear production traffic) | UNRESOLVED | API shell runs, no production traffic |
| Cloud AI inference | ABSENT | No GPU, no model serving |
| Object storage (OSS/S3/R2) | NOT_PROVISIONED | Local disk only |
| PolarDB integration | UNRESOLVED | Provisioned but empty/unused |
| Production-case state machine | LEGACY | `orchestration/workflow_engine.py` — needs unification |
| Human preference learning | RESEARCH | Not implemented |
| Reward model for audio evaluation | RESEARCH | Not implemented |
| Personalized listening | IN_DEVELOPMENT | Web site mentions "In development" |
| Multi-device playback adaptation | PARTIAL | Processing exists, runtime adaptation incomplete |
| Redis task queue | PLANNED | Commented out in docker-compose |
| Nginx load balancer | PLANNED | Commented out in docker-compose |

---

## 9. Technical Debt

### Structural Debt

1. **Monolithic repository** — All components (engine, products, apps, research, data, docs) in one flat repo with no clear layer separation
2. **Duplicate module hierarchies** — `moodify-core-package/`, `moodify-app/moodify-core-package/`, `moodify-system/`, `moodify-runtime/` overlap
3. **Experimental code mixed with canonical** — `moodify_experimental/` sits alongside production code with no isolation boundary
4. **Legacy orchestration** — `orchestration/workflow_engine.py` (938 lines) preserved but not active; creates confusion about authority

### Code Debt

5. **v01_ prefix modules** — `v01_pipeline.py`, `v01_analyzer.py` etc. are the mainline but named as version-specific, creating migration friction
6. **Multiple processing paths** — `processing/pedalboard_chain.py`, `processing/spectral_chain.py`, `reconstruction/pipeline.py` — unclear which is canonical for which use case
7. **Hardcoded paths** — Config relies on environment variables but defaults to local paths (`outputs/moodify_cases`)
8. **No package isolation** — Products don't have separate package manifests; everything depends on `moodify-core-package`

### Infrastructure Debt

9. **Empty cloud database** — PolarDB provisioned but unused; SQLite is the actual data store
10. **No object storage** — Audio assets stored on local disk; doesn't scale
11. **No CI/CD pipeline for deployment** — Manual deployment process
12. **No GPU infrastructure** — Stem separation and AI inference can't run in cloud

### Documentation Debt

13. **236 docs with overlapping authority** — Canon, brand, engineer, design, contracts, metrics docs overlap
14. **Chinese/English mixed** — Inconsistent language across docs
15. **No API documentation** — FastAPI auto-docs exist but no external API documentation

---

## 10. Migratable Modules

The following modules can be directly mapped to the new architecture:

### → Engine Layer (`engine/`)

| Current Module | New Location | Maps To |
|---------------|-------------|---------|
| `auditory/` (26 modules) | `engine/acoustic_analysis/` | Acoustic analysis core |
| `v01_analyzer.py` | `engine/audio_features/` | Feature extraction |
| `diagnosis/` | `engine/music_understanding/` | Audio understanding |
| `mrs/` | `engine/scoring_engine/` | Scoring system |
| `knowledge/emotion_targets.py` | `engine/recommendation_engine/` | Recommendation |
| `evaluation/` | `engine/scoring_engine/` | Evaluation framework |
| `audio_io.py` | `engine/audio_features/` | I/O utilities |
| `fingerprint.py` | `engine/acoustic_analysis/` | Fingerprinting |
| `icc.py` | `engine/acoustic_analysis/` | Stereo analysis |
| `reality_metrics.py` | `engine/scoring_engine/` | Reality metrics |
| `uncertainty.py` | `engine/acoustic_analysis/` | Uncertainty |

### → Product: QA (`products/qa/`)

| Current Module | Maps To |
|---------------|---------|
| `diagnosis/quality_gate.py` | Quality gate |
| `auditory/loudness.py` | LUFS analysis |
| `auditory/true_peak.py` | True peak |
| `auditory/spectrogram.py` | Spectral analysis |
| `mrs/scoring.py` | MRS scoring |
| `era_diagnostic/` | ERA diagnostic |

### → Product: Master (`products/master/`)

| Current Module | Maps To |
|---------------|---------|
| `processing/pedalboard_chain.py` | DSP chain |
| `processing/spectral_chain.py` | Spectral processing |
| `v01_pipeline.py` | Processing pipeline |
| `v01_presets.py` | Mastering presets |
| `intervention/` | Intervention pipeline |
| `reconstruction/` | Audio reconstruction |
| `optimizer/` | Parameter optimization |

### → Product: Rating (`products/rating/`)

| Current Module | Maps To |
|---------------|---------|
| `mrs/` | Music value scoring |
| `knowledge/emotion_targets.py` | Emotion tagging |
| `knowledge/risk_model.py` | Risk assessment |
| `identity_guard/` | Identity ranking |
| `evaluation/judges.py` | Judge models |

### → Product: Supply (`products/supply/`)

| Current Module | Maps To |
|---------------|---------|
| `stems/` | Stem separation |
| `data_factory/` | Supply chain pipeline |
| `data_plane/` | Data delivery |
| `listening/` | Listening protocol |
| `calibration/` | Calibration |

### → Shared Infrastructure

| Current Module | Maps To |
|---------------|---------|
| `contracts/` | Shared contracts |
| `authority/` | Authority system |
| `safety/` | Safety bounds |
| `node/` | Worker infrastructure |
| `api/` | API gateway |

---

## 11. Module Dependency Graph (Simplified)

```
                    ┌─────────────┐
                    │  API Layer   │ (FastAPI)
                    │  api/main.py │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Analyze  │ │ Process  │ │ Evaluate │
        │ routes   │ │ routes   │ │ routes   │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             ▼            ▼            ▼
     ┌─────────────────────────────────────┐
     │         v01_pipeline.py              │
     │  Import → Analyze → Diagnose →       │
     │  Process → Export                    │
     └──────┬──────────┬──────────┬────────┘
            │          │          │
     ┌──────▼──┐ ┌────▼────┐ ┌──▼──────┐
     │auditory/│ │processing│ │ mrs/    │
     │(analysis)│ │(DSP)    │ │(scoring)│
     └────┬────┘ └────┬────┘ └────┬────┘
          │           │           │
     ┌────▼───────────▼───────────▼────┐
     │         contracts/               │
     │  (evidence, provenance, rules)   │
     └────────────┬────────────────────┘
                  │
     ┌────────────▼────────────────────┐
     │         node/ (worker)           │
     │  queue, db, worker, runner       │
     └─────────────────────────────────┘
```

---

## 12. Current Deployment Topology

```
Internet
    │
    ▼
Cloudflare (DNS + Tunnel)
    │
    ▼
LA VPS (103.144.246.242, 4C/8G/98G)
├── nginx :80 (three domains)
├── cloudflared tunnel
├── moodify-api :8000 (FastAPI, 127.0.0.1)
├── moodify-music :3100 (Next.js/vinext)
├── moodify-music-bff :8100
├── moodify-worker (SQLite queue)
└── docker: moodify-audiolla (:18080 → lalal.ai proxy)

Hangzhou VPS (120.55.191.146, 2C/1.6G/40G)
├── moodify-api :8000 (public, service-key auth)
├── moodify-data-worker (node + 4 timers)
└── /var/lib/moodify (SQLite + 6.5GB historical data)

PolarDB (3 instances, BLOCKED from direct verification)
├── MySQL 8.0.13 — empty shell
├── MySQL 8.0.18 — moodify_dev, 19 tables, ~0 data
└── PostgreSQL 16.14 — online, unused

NOT PROVISIONED: OSS/S3/R2, GPU/AI inference
```

---

*End of Phase 1 Analysis. No code was modified or deleted during this analysis.*
