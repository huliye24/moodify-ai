# Moodify

**AI Audio Intelligence Infrastructure**

> Moodify builds the intelligence layer for the future of music.
>
> Moodify 正在构建 AI 时代音乐产业的听觉智能基础设施。

[![Test](https://github.com/huliye24/moodify-ai/actions/workflows/test.yml/badge.svg)](https://github.com/huliye24/moodify-ai/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.10-3776AB?logo=python&logoColor=white)](moodify-core-package/pyproject.toml)
[![License](https://img.shields.io/badge/License-GPL%20v3-blue)](LICENSE)

---

## What Moodify Is

AI can now generate music at scale. The music industry still lacks reliable infrastructure to **listen to, evaluate, and process** that music. Moodify is building the auditory intelligence layer that fills this gap — the "ears" of the AI music economy.

We are not a music app company. We are an **AI audio intelligence infrastructure company**. Our engine measures, understands, scores, and processes audio; our product modules turn that capability into industry-ready services.

## Four Product Pillars

### 1. Moodify QA — AI Music Quality Intelligence

Industrial-grade audio quality assurance.

- LUFS loudness analysis and streaming platform compliance (Spotify / Apple / YouTube)
- Spectral balance, dynamic range, and true-peak diagnostics
- Defect detection: clipping, noise, phase issues
- MRS (Moodify Reality Score) quality scoring with uncertainty bounds

### 2. Moodify Master — AI Music Processing

AI mastering and industrial audio processing.

- Rule-based, evidence-driven DSP intervention (Pedalboard chain)
- Identity preservation gates — processing never destroys musical identity
- Commercial release standardization for streaming distribution
- Audio reconstruction and parameter optimization

### 3. Moodify Rating — AI Music Asset Intelligence

Music as a measurable, tradeable asset class.

- Music value scoring: commercial, artistic, technical dimensions
- Emotion and scene tagging (game / film / advertising / streaming)
- S/A/B/C/D asset grading for catalogs and marketplaces
- Risk assessment: originality, quality, licensing

### 4. Moodify Supply — AI Music Supply Chain

Matching music to where it creates value.

- Audio similarity and semantic music search
- Scene matching for game, film, and advertising licensing
- Stem separation (vocals / drums / bass / other)
- Verified supply pipeline: Intake → Process → Deliver → Verify

## Architecture

```
                    Moodify
                       |
          Moodify Intelligence Engine
                       |
        ┌──────────┬──────────┬──────────┬──────────┐
        │          │          │          │
       QA        Master      Rating     Supply
                       |
        ┌──────────┬──────────┬──────────┐
        │          │          │          │
      Web       Android    Desktop    Partner API
```

### Layered Design

| Layer | Directory | Role |
|-------|-----------|------|
| **Engine Layer** | `engine/` | Shared AI auditory capability: acoustic analysis, audio features, music understanding, scoring, recommendation |
| **Product Layer** | `products/` | Industry modules: `qa/`, `master/`, `rating/`, `supply/` |
| **Application Layer** | `apps/` | End-user products: `web/` (Next.js player), Android, desktop |
| **Research Layer** | `research/` | Papers, benchmarks, whitepapers, experimental modules |
| **Infrastructure** | `shared/` | Contracts, authority, safety, worker nodes, API gateway |

The engine is a pure capability layer — it analyzes, scores, and understands audio. Products package that capability for industry use cases. Applications deliver end-user experiences. **Every judgment produces evidence; every score carries uncertainty; every decision is auditable.**

Full architecture specification: [docs/MOODIFY_ARCHITECTURE_V1.md](docs/MOODIFY_ARCHITECTURE_V1.md)

## Quick Demo

The Intelligence Engine is live. One command turns any music file into a
professional AI audio intelligence report:

```bash
pip install -e demo          # or run without installing (repo root):
moodify analyze demo/input/example.mp3
# python -m demo.cli analyze demo/input/example.mp3
```

```text
==========================================================
             Moodify Intelligence Report
==========================================================
  Track          : example.mp3
  Overall Score  : 63 / 100
  Loudness       : -15.6 LUFS (LRA 3.3 LU)
  Stereo Image   : Narrow
  Detected Issues: ...
  Moodify Analysis:
   "This track has strong emotional potential but requires additional
    mastering optimization for commercial release."
==========================================================
```

**Input:** a music file. **Output:** a Moodify Intelligence Report —
`report.json` (unified schema) + `report.md` (human-readable) — with quality
scores, detected issues with evidence, prioritized recommendations, and a
commercial release-readiness verdict. The same engine chain powers QA,
Master, Rating, and Supply. Details: [docs/MOODIFY_DEMO_PIPELINE.md](docs/MOODIFY_DEMO_PIPELINE.md)

## Core Technology

- **Acoustic analysis** — LUFS / true-peak / spectral / stereo / dynamic-range measurement (ITU-R BS.1770, EBU R128)
- **Feature extraction** — wave, spectral, rhythm, and timbre feature pipelines
- **MRS (Moodify Reality Score)** — reference-based audio quality metric with explicit uncertainty
- **Controlled DSP** — diagnosis-driven intervention via Pedalboard, with safety bounds and identity gates
- **Evidence contracts** — provenance, measurement records, and verification artifacts for every processing case
- **Distributed workers** — SQLite-queued job nodes, Docker-deployed API + worker services

## Repository Structure

```
moodify-ai/
├── engine/                  # Moodify Intelligence Engine (core AI capability)
│   ├── acoustic_analysis/   # LUFS, spectrum, stereo, dynamics, issue detection
│   ├── audio_features/      # Feature extraction
│   ├── music_understanding/ # Structure, emotion, commercial insight
│   ├── scoring_engine/      # MRS, quality scoring, recommendations
│   └── report_schema/       # Unified Intelligence Report contract
│
├── products/                # Industry product modules
│   ├── qa/                  # AI Music Quality Assurance
│   ├── master/              # AI Music Mastering Engine
│   ├── rating/              # AI Music Asset Rating
│   └── supply/              # AI Music Supply Chain
│
├── demo/                    # Intelligence Demo Pipeline (moodify analyze)
│
├── apps/                    # End-user applications
│   └── web/                 # Moodify web player (Next.js)
│
├── research/                # Research output
│   ├── papers/              # WSE-AIM research papers
│   ├── benchmarks/          # Evaluation protocols & datasets
│   └── whitepapers/         # Industry whitepapers
│
├── shared/                  # Cross-cutting infrastructure
├── docs/                    # Architecture, strategy, and canon documentation
├── moodify-core-package/    # Legacy core package (progressive migration in progress)
└── sdk/                     # Python SDK
```

> **Migration note:** The platform is moving from a monolithic structure (`moodify-core-package/`) to the layered architecture above. Migration is progressive — no code is deleted, no functionality is broken. See [docs/CURRENT_ARCHITECTURE.md](docs/CURRENT_ARCHITECTURE.md) for the current state and [docs/MOODIFY_ARCHITECTURE_V1.md](docs/MOODIFY_ARCHITECTURE_V1.md) for the target.

## Roadmap

### Phase 1 — Research Foundation ✅

Reproducible analysis, diagnosis, controlled processing, and measurement workflows. 10-song data-factory pilot completed with full evidence chain.

### Phase 2 — Engine Extraction (Current)

Extract the Moodify Intelligence Engine from the monolith. The engine analysis
facade and unified Intelligence Report schema are **live** (see
[Quick Demo](#quick-demo)); module migration proceeds progressively with test
coverage maintained.

### Phase 3 — Product Modules

Stand up QA, Master, Rating, and Supply as independently deployable services with dedicated API namespaces.

### Phase 4 — Industry Platform

Partner-facing infrastructure: SDK access, verified supply chain integrations, and interoperable evaluation standards for the music industry.

## Research Direction

Moodify's research operates on a simple question: **can machines learn to hear?**

- **Wave-Spectral Evolution (WSE)** — how measurable signal properties evolve through production ([papers](research/papers/))
- **Auditory intelligence architectures** — multi-layer measurement, bounded judgment, uncertainty quantification
- **Human preference learning** — how listening judgments can inform machine evaluation
- **Music asset valuation** — turning subjective quality into measurable, comparable asset metrics

We maintain an evidence-first engineering posture: machine decisions stay scoped, versioned, and reviewable; insufficient evidence produces uncertainty or human escalation — never invented certainty.

## For Partners & Investors

Moodify is building foundational infrastructure for the AI music economy:

- **Quality infrastructure** — as AI-generated music explodes, QA becomes the bottleneck; we automate it
- **Asset intelligence** — music catalogs need machine-readable valuation; we provide the scoring layer
- **Supply chain** — game/film/advertising music licensing is fragmented; we build the matching layer

Documentation: [Product Strategy](docs/01_PRODUCT_STRATEGY.md) · [Business Model](docs/04_BUSINESS_MODEL.md) · [Industrial Roadmap](docs/03_INDUSTRIAL_ROADMAP.md)

## Contributing

We welcome contributions from audio researchers, AI engineers, music producers, and acoustic engineers.

Before contributing, read [AGENTS.md](AGENTS.md), the [current Canon](docs/canon/CURRENT_CANON.md), and [repository status](docs/REPOSITORY_STATUS.md). Contributions should preserve reproducibility, distinguish research work from verified production capability, and avoid introducing private audio or secrets.

## License

Moodify is licensed under **GNU GPL v3.0 only**. See [LICENSE](LICENSE).

---

**Moodify — The Intelligence Layer for the Future of Music.**
