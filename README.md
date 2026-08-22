# Moodify AI

> **Moodify is building the auditory intelligence layer for the AI era.**
>
> **Moodify 正在构建 AI 时代的听觉智能基础设施。**

Moodify is an open technical entry point for research and engineering around how machines analyze, evaluate, and improve audio. The repository contains a research prototype and supporting product code; it does not claim a deployed auditory-intelligence platform or a general-purpose listening model.

## Vision

AI can increasingly generate sound, speech, and music. It still lacks reliable ways to reason about sound quality, emotion, and human listening experience.

Moodify investigates an auditory intelligence layer built from four connected directions:

- **Audio Understanding** — representing measurable acoustic properties of audio.
- **Audio Evaluation** — making evaluation criteria explicit, inspectable, and testable.
- **Audio Optimization** — applying controlled, rule-based interventions when the evidence supports them.
- **Human Preference Learning** — studying how listening judgments may inform future evaluation systems.

The goal is not generic audio processing. It is to develop a disciplined path from audio evidence to bounded technical decisions, with clear uncertainty and human escalation where needed.

## Why Moodify

Much of music and audio production still relies on skilled human listening. That expertise is essential, but it is difficult to formalize, compare, and scale.

- Audio evaluation is often dependent on individual experience and context.
- AI-generated music is increasing faster than dependable methods for evaluating listening quality.
- Different playback devices, environments, and listeners can require different optimization decisions.

Moodify explores the technical foundations of an **AI Ear**: a system that can measure audio, form bounded judgments, and preserve the evidence behind its decisions. “AI Ear” is a research framing in this repository, not a claim that a complete human-equivalent listener has been built.

## Architecture

```mermaid
flowchart TD
    input[Audio Input] --> analysis[Acoustic Analysis Engine]
    analysis --> mrs[Moodify Reality Score (MRS)]
    mrs --> processing[AI Processing Engine]
    processing --> evaluation[Quality Evaluation]
```

The current implementation covers a narrow, inspectable version of this loop. Analysis, diagnosis, rule-based processing, and measurement are implemented in the core package. MRS and before/after evaluation remain research-oriented components rather than validated universal quality judgments.

## Core Technology

The repository currently includes:

- **Audio analysis** — audio ingest plus wave and spectral analysis.
- **Loudness measurement** — LUFS measurement within the processing chain.
- **Acoustic feature extraction** — band energy, dynamic range, stereo correlation, and related metrics.
- **Rule-based audio optimization** — diagnosis-driven DSP intervention using a Pedalboard processing chain.
- **MRS evaluation framework** — reference-based metric computation and before/after comparison utilities.

These are prototype and engineering capabilities, not claims of a trained audio foundation model, a production reward model, or universally valid audio-quality rankings.

## Moodify Reality Score (MRS)

Moodify Reality Score (MRS) is Moodify’s exploration of a quantitative way to evaluate aspects of an audio experience. The current implementation computes a reference-based distance metric from configured feature statistics and weights; it is useful for research comparison, not a substitute for listener studies or expert review.

Future work may investigate:

- Human preference learning
- Reward models for scoped audio-evaluation tasks
- AI auditory evaluation with explicit benchmarks and uncertainty handling

Any future score must be validated for a defined task and population before it is treated as an authority on perceived quality.

## Roadmap

### Phase 1: Research Prototype

Establish reproducible analysis, diagnosis, controlled processing, and measurement workflows.

### Phase 2: Auditory Intelligence Engine

Develop better representations, evaluation protocols, evidence records, and bounded decision logic.

### Phase 3: AI Music Infrastructure

Connect validated auditory-intelligence components into reusable tools and data workflows for music systems.

### Phase 4: Industry Platform

Explore interoperable evaluation and optimization infrastructure with researchers and industry partners, contingent on validation, governance, and operating evidence.

## Research Direction

Moodify welcomes research on:

- AI listening models
- Audio foundation models
- Music-quality benchmarks
- Personalized listening

The project also maintains an evidence-first engineering posture: machine decisions should remain scoped, versioned, and reviewable; insufficient evidence should result in uncertainty or human review rather than invented certainty.

## Contributing

We welcome contributions from:

- Audio researchers
- AI engineers
- Music producers
- Acoustic engineers

Before contributing, read [AGENTS.md](AGENTS.md), the [current Canon](docs/canon/CURRENT_CANON.md), and [repository status](docs/REPOSITORY_STATUS.md). Contributions should preserve reproducibility, distinguish research work from verified production capability, and avoid introducing private audio or secrets.

## License

Moodify is licensed under **GNU GPL v3.0 only**. See [LICENSE](LICENSE).
