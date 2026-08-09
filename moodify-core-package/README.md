# Moodify Core

`moodify-core-package` is the current Python implementation of Moodify's local auditory-analysis and intervention engine.

Moodify's product identity is:

> **The Ear of AI — an Auditory Intelligence System.**

Its organizing question is **Can machines learn to hear?** The canonical loop
is `Listen → Represent → Judge → Intervene → Verify → Learn`. Existing audio
post-processing remains available only as the Auditory Intervention Laboratory.

This package implements part of that architecture today. It does **not** claim that the entire Auditory Intelligence roadmap is already implemented.

## Current v0.1 Mainline

The stable v0.1 path is intentionally narrow:

```text
Import
  -> Analyze
  -> Diagnose
  -> Process
  -> Export
```

The canonical implementation should continue to preserve a simple, testable mainline while experimental systems evolve separately.

## What the Core Does Today

Depending on the active version, the package includes:

- audio loading and normalization;
- spectral / acoustic metric extraction;
- rule-based diagnosis;
- controlled DSP processing;
- preset-based interventions;
- export and report generation;
- CLI/API entry points;
- test fixtures and regression checks;
- experimental measurement and feedback modules.

## How This Fits the Auditory Intelligence Model

```text
Listen       -> audio I/O and source handling
Represent    -> analysis / metrics / structural representations
Judge        -> diagnosis / scoring / rule evaluation
Intervene    -> DSP and controlled processing
Verify       -> before/after metrics, tests, evidence
Learn        -> records, feedback, benchmarks, rules
```

The current code has stronger coverage in some stages than others.

Do not rename an experimental implementation into a production capability merely to make the diagram look complete.

## Auditory Intervention Laboratory

DSP, presets and post-processing are treated as the **Auditory Intervention Laboratory**.

Their role is to:

- create controlled acoustic changes;
- test hypotheses;
- generate before/after evidence;
- discover failures;
- support production cases.

They are important, but they are not the complete definition of Moodify.

## Installation

Python 3.10+:

```bash
pip install -e .
```

Development:

```bash
pip install -e ".[dev]"
```

## Verification

```bash
python -m ruff check src/moodify
python -m pytest -q
```

## Agent Rule

Before modifying this package, read the repository root:

```text
AGENTS.md
docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md
docs/LEGACY_AND_EXPERIMENTAL_POLICY.md
```

Preserve the verified mainline unless a task explicitly authorizes architectural migration.
