# Moodify

> **The Ear of AI.**
>
> Moodify is an **Auditory Intelligence System** for AI-generated audio and music.

Its primary question is: **Can machines learn to hear?**

**中文定位：Moodify 是 AI 的耳朵。**

Moodify is built to help AI systems **listen, represent, judge, intervene, verify, and learn from sound**. It does not generate another song on top of a song. It develops a structured understanding of what is happening in audio, preserves evidence, and turns repeated production cases into reusable auditory knowledge.

```text
Listen
  -> Represent
  -> Judge
  -> Intervene
  -> Verify
  -> Learn
  -> Next Case
```

## Why Moodify Exists

AI can generate enormous amounts of audio, but generation and listening are different capabilities.

A generative model may create a track without having a reliable engineering system that can answer:

- What actually happened in the waveform and spectrum?
- Is the result stable, distorted, unbalanced, phase-problematic, overly dense, or structurally inconsistent?
- What parts of the judgment are measurable?
- If an intervention is made, did it actually improve the target condition?
- Can the evidence from this case improve the next case?

Moodify makes machine judgment explicit and reproducible. Its deterministic
algorithmic reviewer (`moodify.data_factory.algorithmic_review`, formula
`MFY-ALGO-REVIEW-FORMULA-001`) may rank cases inside its validated, versioned
scope. Cases outside that scope, with insufficient evidence, or involving
unresolved perceptual judgment must escalate to human review or close as
inconclusive; automation does not manufacture certainty.

Moodify is designed around those questions.

## Auditory Intelligence

Moodify treats listening as an engineering and research problem.

### 1. Listen

Acquire the audio and establish a trustworthy source identity.

### 2. Represent

Convert sound into measurable and structured representations:

- waveform;
- spectrum;
- loudness;
- dynamics;
- phase;
- channel relationships;
- residuals;
- transients;
- musical structure where available.

### 3. Judge

Produce explicit, inspectable judgments rather than hiding the result behind a single “quality score”.

### 4. Intervene

Apply controlled changes only when there is a reason to do so.

Existing DSP and post-processing functions belong here. They are the **Auditory Intervention Laboratory**, not the identity of Moodify itself.

### 5. Verify

Compare before and after states, preserve evidence, and reject unsupported claims of improvement.

### 6. Learn

Convert production cases into reusable measurements, evidence, rules, benchmarks and research questions.

---

## Three Engineering / Research Disciplines

### WSE — Wave-Spectral Evolution

**Question:** What happened in the sound?

WSE studies waveform, spectrum, loudness, phase, channels, residuals, transients and other measurable acoustic behavior.

### MSE — Musical-Structural Engineering

**Question:** What is the musical structure?

MSE studies MIDI, score, rhythm, phrases, sections, lyrics, roles and structural relationships.

### PPE — Production Process Engineering

**Question:** How can this be produced and verified reliably?

PPE studies production cases, state transitions, evidence artifacts, quality gates, reproducibility, authority boundaries, packaging, failure and recovery.

---

## The Learning / Asset Loop

```text
Production Case
  -> Measurement Record
  -> Evidence Artifact
  -> Theory Update
  -> Moodify Rule Update
  -> Next Production Case
```

Moodify is not only a collection of functions. Its long-term value comes from the accumulation of **traceable auditory evidence and reusable production knowledge**.

---

## Current Implementation Status — August 2026 Data Foundation

Moodify is converging to **Moodify 1.0 — Data Foundation** (freeze target 2026-08-31).
The canonical production loop is:

```text
SOURCE -> LISTEN -> REPRESENT -> JUDGE -> ABC INTERVENTION -> VERIFY
       -> ALGORITHMIC REVIEW -> DATASET -> NEXT CASE
```

One real song produces a versioned `ProductionCase` with before-scan, diagnosis,
A/B/C intervention plans (A=conservative, B=balanced, C=exploratory, derived
from the diagnosis), three candidates, after-scans, source-vs-candidate
comparisons, an algorithmic review record, and deterministic pairwise dataset
rows — without manual file surgery.

Current capabilities:

- standards-backed measurement (BS.1770-4 loudness, EBU 3342 LRA, true-peak,
  clipping, DC, spectral and band-energy descriptors) — see
  [Metric Registry](docs/metrics/METRIC_REGISTRY_V1.md);
- deterministic reference audio suite (10 fixtures, hashes, expected values) —
  [Reference Suite](moodify-core-package/benchmarks/reference_audio/REFERENCE_SUITE.md);
- diagnosis-derived ABC intervention plans and reproducible DSP candidates;
- deterministic algorithmic review within an approved scope, with explicit
  human escalation for unresolved perceptual judgment;
- evidence manifests with artifact hashes; failed jobs fail closed;
- 24/7 unattended data node (single worker, queue survives restarts);
- cross-machine repeatability: 52/52 metrics identical across OS/Python
  versions (2026-08-11);
- API/CLI interfaces and a local-first Android client.

Not every research concept in this repository is production-ready. Experimental
and legacy systems are explicitly distinguished from the canonical mainline
(see [Legacy & Experimental Policy](docs/LEGACY_AND_EXPERIMENTAL_POLICY.md)).

---

## What Moodify Is Not

Moodify is not:

- a text-to-music generation model;
- a DAW replacement;
- an automatic-mastering promise;
- a guarantee that every processed file becomes “better”;
- a collection of presets presented as intelligence;
- a black-box score without evidence.

---

## Repository Authority

The repository is organized conceptually into four layers:

```text
Moodify
├── Auditory Intelligence Core
│   ├── WSE
│   ├── MSE
│   └── PPE
│
├── Production Runtime
│   ├── Cases
│   ├── Evidence
│   ├── Rules
│   ├── Gates
│   └── Recovery
│
├── Application Layer
│   ├── API
│   ├── App
│   └── Cloud
│
└── Asset Layer
    ├── Measurement Records
    ├── Production Cases
    ├── Treatment Records
    ├── Benchmarks
    └── Research Corpus
```

See:

- `docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md`
- `docs/ASSET_MODEL.md`
- `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md`
- `docs/REPOSITORY_STATUS.md`

---

## Scientific Release Assets

- **Repository constitution:** [PHASE1_CONSTITUTION.md](docs/PHASE1_CONSTITUTION.md),
  [CODE_FREEZE_POLICY.md](docs/CODE_FREEZE_POLICY.md)
- **Data protocol:** [DATA_PROTOCOL_V1.md](docs/contracts/DATA_PROTOCOL_V1.md) (frozen)
- **Metric registry:** [METRIC_REGISTRY_V1.md](docs/metrics/METRIC_REGISTRY_V1.md)
- **Reference audio suite:** [REFERENCE_SUITE.md](moodify-core-package/benchmarks/reference_audio/REFERENCE_SUITE.md)
- **Golden Production Case:** [examples/golden_case](examples/golden_case/)
- **Benchmark:** reference-suite expected values + cross-machine report
  (`moodify-core-package/benchmarks/reference_audio/expected/`)
- **Citation:** [CITATION.cff](CITATION.cff)

## Scope and Limitations

- The current mainline measures and intervenes on **audio**; musical-structure
  (MSE) and some research/experimental modules are not part of the frozen
  1.0 surface.
- Metrics are trustworthy only under the frozen scan profile
  (`MFY-WSE-SCAN-PROFILE-001`); any profile change requires a new version and
  explicit data separation.
- The algorithmic reviewer is a deterministic technical ranking within its
  declared validation scope, not a claim about artistic quality. Out-of-scope
  or unresolved perceptual cases require human review or an inconclusive result.
- No private audio, API keys or unauthorized datasets are committed.

---

## Core Python Package

The currently stable local engine lives in:

```text
moodify-core-package/
```

Install:

```bash
cd moodify-core-package
pip install -e .
```

Development installation:

```bash
pip install -e ".[dev]"
```

Example CLI usage:

```bash
moodify presets
moodify analyze song.wav
moodify process song.wav --preset clean_master
```

The CLI examples above represent the current narrow implementation, not the final boundary of Moodify.

---

## Development Principle

> Identity comes before feature expansion.

Before adding a new subsystem, ask:

1. Which part of auditory intelligence does it serve?
2. What evidence does it create?
3. Where does that evidence live?
4. Is it canonical, experimental or legacy?
5. Does it improve the next production case?

A new feature that cannot answer these questions should not automatically become part of the mainline.

---

## Data and Privacy

The core workflow can be local-first.

Do not commit:

- private audio;
- API keys;
- unauthorized datasets;
- generated heavy artifacts;
- local IDE state.

External models, APIs, audio and datasets retain their own licenses and rights.

---

## License

Moodify is licensed under **GNU GPL v3.0 only** unless otherwise stated.

See `LICENSE`.
