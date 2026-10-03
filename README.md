<p align="center"><img src="brand/assets/moodify-horizontal.png" alt="Moodify — Every voice deserves to be heard" width="100%"></p>

# Moodify

**Moodify Sound Protocol — sound processing through one shared Core**

> **Generated is not finished.** AI and agents can call Moodify through a declarative sound job and CLI; humans retain final listening and release authority.
>
> **生成 ≠ 完成。** Moodify 以声音协议为核心，让 AI / Agent 通过 CLI 调用同一个 Core 处理声音；最终审听与发布由人决定。

```text
             Moodify
          Shared Core
        /                \
Creator Side         Listener Side
Moodify CLI          Moodify App
PROTOCOL / PROCESS   PLAY / REVIEW
```

- **Moodify CLI** — Production Interface（声音生产端，Creator Side）。核心动作 `PROCESS`。**Makes music sound better.**
- **Moodify App / Player** — Listening Interface（声音消费端，Listener Side）。核心动作 `PLAY`。**Makes music play better.**
- **Moodify Core** — 二者共享的声音智能（analysis / dsp / processing / playback / profiles / verification / contracts）。**Powers both.**

首版 [Moodify Sound Protocol 0.1](docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md) 提供可校验 JSON 作业和 `moodify protocol validate|process`。它调用现有 Core 的预设处理，输出参数、诊断及文件哈希；`processed_review_required` 不等于通过专业验证。可编辑 Mix Graph 仍是目标态。

[![Test](https://github.com/huliye24/moodify-ai/actions/workflows/test.yml/badge.svg)](https://github.com/huliye24/moodify-ai/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.10-3776AB?logo=python&logoColor=white)](moodify-core-package/pyproject.toml)
[![License](https://img.shields.io/badge/License-GPL%20v3-blue)](LICENSE)

---

## What Moodify Is

Moodify makes sound processing callable by humans, AI systems and agents. A job describes the input, selected processing preset and output location. The CLI validates the job, runs the shared Core and returns a machine-readable record of what happened.

Moodify is a **sound protocol with a CLI reference runtime**. AI systems and agents submit explicit processing jobs; the CLI executes them through the shared Core and returns machine-readable evidence. The App remains a listening/review interface. The implemented 0.1 path is preset-based processing; a complete Import → Analyze → Diagnose → Plan → Process → Verify → Export finishing session and editable Mix Graph remain targets, not current protocol guarantees.

## Quick start · 协议调用

从仓库根目录安装 CLI（建议使用虚拟环境）：

```bash
python -m pip install -e moodify-core-package
```

将下列内容保存为 `job.json`，并把音频放在同目录的 `audio/source.wav`。作业中的相对路径以 `job.json` 所在目录为基准。

```json
{
  "protocol": "moodify.sound/0.1",
  "source": "audio/source.wav",
  "preset": "clean_master",
  "output_dir": "outputs"
}
```

```bash
moodify protocol validate job.json
moodify protocol process job.json
```

CLI 向标准输出写入 JSON；错误向标准错误输出写入 JSON，退出码为 2。处理结果包含 WAV 路径、输入/输出 SHA-256、实际预设参数和诊断，状态为 `processed_review_required`。**请人工审听后再发布**。当前可选预设：`clean_master`、`warm_vocal`、`wide_space`。完整字段与限制见[协议文档](docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md)。

## Core Capabilities

> 以下 QA / Master / Rating / Supply 不再是四个平级「产品身份」，而是共享 Core 的能力簇（capability clusters），分别由生产端 CLI 与消费端 App 复用。详见 [docs/canon/CURRENT_CANON.md](docs/canon/CURRENT_CANON.md)。

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
- Mix Graph v0.1（目标态，TARGET）：source → EQ → compression → stereo → limiter → verify，可序列化 / 可旁路 / 可回退，见 [docs/MOODIFY_PROFESSIONAL_FINISHING_V1.md](docs/MOODIFY_PROFESSIONAL_FINISHING_V1.md)

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
                    Moodify Core
                 (shared audio intelligence)
                 /                    \
                /                      \
         Moodify CLI               Moodify App
         Production                Playback
             |                         |
    analyze / process /         dynamic playback /
    profile / verify            realtime adaptation
             |                         |
      changes the audio          changes what's heard
```

### Layered Design

| Layer | Directory | Role |
|-------|-----------|------|
| **Core** | `engine/`（→ `core/`，渐进迁移） | 共享声音智能：analysis / dsp / processing / playback / profiles / verification / contracts |
| **Production Interface** | `cli/`（现 `demo/`） | `moodify analyze / process / profile / verify / compare / inspect / render` |
| **Listening Interface** | `apps/` | 消费端：`web/`（Next.js player）、Android、desktop |
| **Research Layer** | `research/` | Papers, benchmarks, whitepapers, experimental modules |
| **Infrastructure** | `shared/` | Contracts, authority, safety, worker nodes, API gateway |

The Core is a pure capability layer — it analyzes, scores, processes, and plays audio. **One Core, multiple interfaces**: both CLI and App call the same Core; an interface must never hold its own copy of a sound algorithm. **Every judgment produces evidence; every score carries uncertainty; every decision is auditable.**

Full architecture specification: [docs/MOODIFY_ARCHITECTURE_V1.md](docs/MOODIFY_ARCHITECTURE_V1.md) · 仓库现实审计：[CURRENT_STATE_AUDIT.md](CURRENT_STATE_AUDIT.md)

## Legacy analysis demo

The older `demo/` analysis path remains in the repository. It is separate from the MSP/0.1 job contract above and is kept for compatibility:

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
